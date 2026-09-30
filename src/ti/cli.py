"""`ti` command-line entry point (docs/04 §3, docs/decisions-needed.md §3)."""
from __future__ import annotations

import argparse

from . import ingest, obs, stability
from .config import candidate_cities

DEFAULT_EDITION = "2026-pilot"  # docs/07 M7 prompt names this edition; M2 uses it for L1 too


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ti")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("ingest", help="release assets -> data/static (deduped) + data/obs/<city>/<date>.parquet")
    i.add_argument("--from", dest="start", required=True, help="YYYY-MM-DD")
    i.add_argument("--to", dest="end", required=True, help="YYYY-MM-DD")
    i.add_argument("--cities", nargs="*", default=None, help="default: all candidate cities")
    i.add_argument("--workers", type=int, default=3)
    i.add_argument("--keep-raw", action="store_true", help="also keep tidy+static under data/raw/ instead of discarding after L0")

    o = sub.add_parser("obs", help="build L0 from an already-downloaded tidy+static pair (debugging/reruns)")
    o.add_argument("--city", required=True)
    o.add_argument("--date", required=True)
    o.add_argument("--tidy", required=True)
    o.add_argument("--static", required=True)
    o.add_argument("--out", required=True)

    s = sub.add_parser("stability", help="day-to-day stop_id/seg_id overlap per city (reports/m1/stability.csv)")
    s.add_argument("--cities", nargs="*", default=None)

    g = sub.add_parser("aggregate", help="L0 -> L1 segment_stats.parquet + segments.parquet (data/editions/<edition>/<city>/)")
    g.add_argument("--city", required=True)
    g.add_argument("--from", dest="start", required=True)
    g.add_argument("--to", dest="end", required=True)
    g.add_argument("--edition", default=DEFAULT_EDITION)

    ge = sub.add_parser("geometry", help="M4: segment geometry + segments.geojson.gz + PMTiles per city (downloads/reduces statics as needed)")
    ge.add_argument("--cities", nargs="*", default=None, help="default: all candidate cities")
    ge.add_argument("--edition", default=DEFAULT_EDITION)
    ge.add_argument("--from", dest="start", default=None)
    ge.add_argument("--to", dest="end", default=None)
    ge.add_argument("--no-accept", action="store_true", help="skip the z14+ acceptance check")

    m = sub.add_parser("metrics", help="city x mode x band headline values (reports/m2/metrics/<city>.json)")
    m.add_argument("--from", dest="start", required=True)
    m.add_argument("--to", dest="end", required=True)
    m.add_argument("--cities", nargs="*", default=None)

    d = sub.add_parser("daystats", help="L0 -> per-day sufficient statistics (data/editions/<edition>/<city>/day_stats.parquet); needs data/obs")
    d.add_argument("--city", required=True)
    d.add_argument("--from", dest="start", required=True)
    d.add_argument("--to", dest="end", required=True)
    d.add_argument("--edition", default=DEFAULT_EDITION)
    d.add_argument("--valid-only", action="store_true", help="W3 reference from days accepted by `ti gate` only (second pass)")

    t = sub.add_parser("gate", help="day/city gate, anomalous days, day-bootstrap, ranking/summary/hourly/lines/quality/manifest (data/editions/<edition>/)")
    t.add_argument("--from", dest="start", required=True, help="window start, YYYY-MM-DD")
    t.add_argument("--to", dest="end", required=True, help="window end, YYYY-MM-DD (days after the last ingested date are 'not yet available')")
    t.add_argument("--edition", default=DEFAULT_EDITION)

    a = ap.parse_args(argv)

    if a.cmd == "ingest":
        ingest.run(a.cities, a.start, a.end, a.workers, a.keep_raw)
    elif a.cmd == "obs":
        from . import static_store

        sha = static_store.store(a.static)
        mode_of, inside = static_store.load(sha, a.city)
        l0, report = obs.build_l0(a.tidy, mode_of, inside)
        l0.to_parquet(a.out, index=False, compression="zstd")
        print(report)
    elif a.cmd == "stability":
        stability.run(a.cities or candidate_cities())
    elif a.cmd == "aggregate":
        from . import aggregate

        stats_path, dim_path = aggregate.run(a.city, a.start, a.end, a.edition)
        print(f"wrote {stats_path}\nwrote {dim_path}")
    elif a.cmd == "daystats":
        from . import daystats

        print("wrote", daystats.run(a.city, a.start, a.end, a.edition, a.valid_only))
    elif a.cmd == "gate":
        from . import edition

        res = edition.run(a.edition, a.start, a.end)
        for city, c in sorted(res["results"].items()):
            print(f"{city:12s} {c['status']:9s} valid={len(c['valid_dates']):2d}/{c['days']['window_weekdays_elapsed']:2d} reasons={','.join(c['reasons']) or '-'}")
        print(f"{len(res['rankings'])} rankings; wrote {res['out']}")
        for n in res["notes"]:
            print("note:", n)
    elif a.cmd == "geometry":
        import json

        from . import geometry, tiles

        rp = geometry.report_path(a.edition)
        for city in a.cities or candidate_cities():
            print(f"== {city}", flush=True)
            entry = tiles.run_city(city, a.edition, a.start, a.end)
            if not a.no_accept:
                entry["acceptance"] = tiles.acceptance(geometry.DATA / "editions" / a.edition / city / "segments.geojson.gz", geometry.DATA / "editions" / a.edition / "tiles" / f"{city}.pmtiles")
            if not a.no_accept:  # segments >= min length that got no geometry vanish from the map too
                acc = entry["acceptance"]
                acc["lost_no_geometry"] = entry["no_geometry_long"]
                acc["pass"] = acc["pass"] and entry["no_geometry_long"] == 0
            # re-read just before writing: parallel invocations (one per city subset) share this file
            rep = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {"edition": a.edition, "cities": {}}
            rep["cities"][city] = entry
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(rep, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
            acc = entry.get("acceptance", {}).get("pass")
            print(f"   segments {entry['segments_in_tiles']}/{entry['segments_l1']} straight(length)={entry['geometry_straight_share_length']} accept={acc} {entry['bytes']}", flush=True)
    elif a.cmd == "metrics":
        from . import metrics

        metrics.run(a.cities, a.start, a.end)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
