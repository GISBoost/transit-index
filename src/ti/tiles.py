"""L1 -> GeoJSON features (schemas/segment_feature.schema.json) -> PMTiles (docs/04 §4, docs/06 §4).

Feature properties are exactly the schema's; nothing else is added (`additionalProperties: false`)."""
from __future__ import annotations

import gzip
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from . import geometry as G
from .config import geometry_cfg
from .paths import DATA, ROOT

BANDS = {"am": "am_peak", "mid": "midday", "pm": "pm_peak", "eve": "evening"}


def _num(x, nd):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) or pd.isna(x) else round(float(x), nd)


def build_features(stats: pd.DataFrame, dim: pd.DataFrame, geom: dict, names: dict) -> tuple[list[dict], dict]:
    """GeoJSON features for every L1 segment with a geometry, plus counters for the report."""
    cfg = geometry_cfg()
    nd, cd = cfg["value_decimals"], cfg["coordinate_decimals"]
    by = {b: g.set_index("seg_id") for b, g in stats.groupby("band")}
    dim = dim.set_index("seg_id")
    feats, no_geom, no_name, lost, downgraded, no_stats = [], 0, 0, [], 0, 0
    lo, hi = cfg["length_ratio_bounds"]
    min_len = cfg["tiles"]["acceptance_min_length_m"]
    all_len = by["all_day"]["length_m"] if "all_day" in by else pd.Series(dtype=float)
    for sid, row in dim.iterrows():
        if sid not in geom:
            no_geom += 1
            if sid in all_len.index and float(all_len.loc[sid]) >= min_len:
                lost.append(sid)
            continue
        q, coords = geom[sid]
        a, b = row.from_stop_id, row.stop_id
        fn, tn = names.get(a), names.get(b)
        no_name += (fn is None) + (tn is None)
        allr = by["all_day"].loc[sid] if sid in by["all_day"].index else None
        if allr is None:  # no all_day statistics row: no L1 length/quality, so the schema-required fields are missing
            no_geom += 1
            no_stats += 1
            continue
        ratio = G.length_m(coords) / float(allr.length_m)
        if q == "shape" and not lo <= ratio <= hi:  # implausible cut (loop/detour): straight between the cut's ends
            q, coords, downgraded = "straight", coords[[0, -1]], downgraded + 1
        p = {"seg_id": sid, "from_stop_id": a, "to_stop_id": b, "from_name": fn or a, "to_name": tn or b,
             "mode": str(row.primary_mode), "routes": sorted(str(r) for r in row.routes),
             "length_m": round(float(allr.length_m), 1),
             "v_all": _num(allr.v_p50, nd) if allr.q != "none" else None,
             "v_sched": _num(allr.v_sched_p50, nd),
             "n_all": int(allr.n_obs), "n_days": int(allr.n_days), "q_all": str(allr.q),
             "pen_pm": _num(row.pen_pm, nd), "geometry_quality": q}
        for short, band in BANDS.items():
            r = by[band].loc[sid] if band in by and sid in by[band].index else None
            p[f"v_{short}"] = _num(r.v_p50, nd) if r is not None and r.q != "none" else None
            p[f"q_{short}"] = str(r.q) if r is not None else "none"
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": np.round(coords, cd).tolist()},
                      "properties": p})
    return feats, {"segments_no_geometry": no_geom, "stop_names_missing": no_name,
                   "segments_without_all_day_row": no_stats, "shape_downgraded_length_ratio": downgraded, "no_geometry_long": len(lost), "no_geometry_long_examples": sorted(lost)[:5]}


def write_geojson_gz(feats: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, ensure_ascii=False, separators=(",", ":"))


def tippecanoe(geojson_gz: Path, out: Path) -> None:
    """GeoJSON -> PMTiles. No feature/tile-size dropping: an acceptance criterion is that no segment
    >= 200 m disappears at z14+. Simplification was already done (`simplify_tolerance_m`), so the
    maximum zoom keeps geometry as is."""
    t = geometry_cfg()["tiles"]
    if not shutil.which("tippecanoe"):
        raise RuntimeError("tippecanoe not found (apt install tippecanoe)")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".geojson")
    with gzip.open(geojson_gz, "rb") as src, open(tmp, "wb") as dst:
        shutil.copyfileobj(src, dst)
    try:
        subprocess.run(["tippecanoe", "-f", "-o", str(out), "-l", t["layer"], f"-Z{t['min_zoom']}", f"-z{t['max_zoom']}",
                        "--simplify-only-low-zooms", "--no-feature-limit", "--no-tile-size-limit", "--no-tiny-polygon-reduction",
                        str(tmp)], check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)


def tiles_present(pmtiles_path: Path, zoom: int) -> set[str]:
    """seg_ids found in the tiles of `zoom` (decoded with pmtiles + mapbox_vector_tile)."""
    import mapbox_vector_tile
    from pmtiles.reader import Reader, all_tiles, MmapSource

    layer = geometry_cfg()["tiles"]["layer"]
    found: set[str] = set()
    with open(pmtiles_path, "rb") as f:
        src = MmapSource(f)
        rd = Reader(src)
        for (z, x, y), data in all_tiles(src):
            if z != zoom:
                continue
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            for feat in mapbox_vector_tile.decode(data).get(layer, {}).get("features", []):
                found.add(feat["properties"]["seg_id"])
    return found


def run_city(city: str, edition: str, start: str | None = None, end: str | None = None, log=print) -> dict:
    """Geometry + features + tiles for one city; returns the city's report entry."""
    from .coverage import load_l1

    l1 = load_l1(city, edition)
    if l1 is None:
        raise SystemExit(f"no L1 for {city} in edition {edition}: run `ti aggregate` first")
    stats, dim = l1
    needed = set(dim.seg_id)
    day_sha = G.day_static_map(city, start, end)
    unlogged = G.resolve_unlogged(city, start, end, log=log)
    day_sha = dict(sorted({**day_sha, **unlogged}.items()))
    status = G.ensure_extracts(city, day_sha, log=log)
    usable = {d: s for d, s in day_sha.items() if status.get(s) in ("ok", "cached")}
    res = G.build_city(city, needed, usable)
    feats, cnt = build_features(stats, dim, res["geom"], res["names"])
    out_dir = DATA / "editions" / edition / city
    write_geojson_gz(feats, out_dir / "segments.geojson.gz")
    tp = DATA / "editions" / edition / "tiles" / f"{city}.pmtiles"
    tippecanoe(out_dir / "segments.geojson.gz", tp)
    length = np.array([f["properties"]["length_m"] for f in feats])
    straight = np.array([f["properties"]["geometry_quality"] == "straight" for f in feats])
    ratio = np.array([G.length_m(np.array(f["geometry"]["coordinates"])) / f["properties"]["length_m"] for f in feats])
    return {
        "segments_l1": len(needed), "segments_in_tiles": len(feats), **cnt,
        "geometry_straight_share_count": round(float(straight.mean()), 4) if len(feats) else None,
        "geometry_straight_share_length": round(float(length[straight].sum() / length.sum()), 4) if len(feats) else None,
        "geom_length_ratio_median": round(float(np.median(ratio)), 3) if len(feats) else None,
        "geom_length_ratio_p05_p95": [round(float(x), 3) for x in np.quantile(ratio, [0.05, 0.95])] if len(feats) else None,
        "static_versions": {"days_with_static": len(day_sha), "days_resolved_by_download": len(unlogged), "unique": len(set(day_sha.values())),
                            "status": {k: sum(1 for v in status.values() if v == k) for k in sorted(set(status.values()))}},
        **res["report"],
        "bytes": {"geojson_gz": (out_dir / "segments.geojson.gz").stat().st_size, "pmtiles": tp.stat().st_size},
    }


def acceptance(geojson_gz: Path, pm: Path) -> dict:
    """Criterion (docs/04 §4 pt 5): no segment >= acceptance_min_length_m missing at z >= acceptance_zoom."""
    t = geometry_cfg()["tiles"]
    with gzip.open(geojson_gz, "rt", encoding="utf-8") as f:
        feats = json.load(f)["features"]
    long_ids = {x["properties"]["seg_id"] for x in feats if x["properties"]["length_m"] >= t["acceptance_min_length_m"]}
    out = {"min_length_m": t["acceptance_min_length_m"], "n_long": len(long_ids), "zooms": {}}
    for z in range(t["acceptance_zoom"], t["max_zoom"] + 1):
        missing = long_ids - tiles_present(pm, z)
        out["zooms"][str(z)] = {"missing": len(missing), "examples": sorted(missing)[:5]}
    out["pass"] = all(v["missing"] == 0 for v in out["zooms"].values())
    return out
