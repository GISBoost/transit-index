"""`ti` command-line entry point (docs/04 §3, docs/decisions-needed.md §3)."""
from __future__ import annotations

import argparse

from . import ingest, obs, stability
from .config import candidate_cities


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
