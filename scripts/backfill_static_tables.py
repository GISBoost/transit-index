"""One-off M2 migration (C1, docs/decisions-needed.md): M1's static_store only kept
routes/stops/trips/shapes and discarded the zip, so the 398 statics deduplicated in M1 are
missing stop_times/calendar/calendar_dates/frequencies (needed for W12, docs/03 §4.3). Those
zips are gone; re-download the ones still referenced from reports/m1/ingest_report.jsonl and let
static_store.store()'s per-table top-up (M2) fill in just the new tables.

    py scripts/backfill_static_tables.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "reference"))

import ti.static_store as static_store  # noqa: E402
import fetch_release_assets as fx  # noqa: E402

REPORT = ROOT / "reports" / "m1" / "ingest_report.jsonl"


def city_days() -> list[tuple[str, str]]:
    """Dedup by (city, date), latest entry wins; only days that actually produced L0."""
    latest: dict[tuple[str, str], dict] = {}
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        latest[(r["city"], r["date"])] = r
    ok = [k for k, r in latest.items() if r["status"] in ("ok", "cached")]
    return sorted(ok)


def main() -> None:
    pairs = city_days()
    print(f"{len(pairs)} city-days to check")
    done_shas: set[str] = set()
    filled, already, failed = 0, 0, 0
    for city, date in pairs:
        with tempfile.TemporaryDirectory() as tmp:
            zpath = Path(tmp) / "static.zip"
            status = fx.fetch(fx.url_for(city, date, "static"), zpath)
            if status == "missing":
                print(f"missing  {city} {date}")
                failed += 1
                continue
            sha = fx.sha256(zpath)
            if sha in done_shas:
                already += 1
                continue
            has_all = all((static_store.STATIC_STORE / sha / f"{t}.parquet").exists() for t in ("stop_times", "calendar"))
            static_store.store(zpath)
            done_shas.add(sha)
            if has_all:
                already += 1
            else:
                filled += 1
                print(f"filled   {city} {date} ({sha[:12]})")
    print(f"done: {filled} filled, {already} already complete/duplicate sha, {failed} missing")


if __name__ == "__main__":
    main()
