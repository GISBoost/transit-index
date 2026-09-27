"""Stage A+B orchestration (docs/04 §3): one city-day, release assets -> L0 + report row.

Streamed per day (docs/decisions-needed.md §3): the tidy download is a temp file, deleted once
L0 is built, unless --keep-raw asks to keep it under data/raw/. Static GTFS is deduplicated by
SHA-256 (static_store.py) regardless of --keep-raw, since M1's estimate (~5 GB on disk) assumes
dedup, not one zip per city-day.
"""
from __future__ import annotations

import datetime as dt
import json
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from . import obs, static_store
from .config import candidate_cities, has_window_signal
from .paths import OBS, RAW, REPORTS, fx
from .provenance import resolve as resolve_epoch


def _last_modified(url: str) -> str | None:
    """Best-effort Last-Modified of a release asset (a tiny ranged GET, same trick as a HEAD)."""
    req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.headers.get("Last-Modified")
    except (urllib.error.URLError, TimeoutError):
        return None


def _report_line(**fields) -> str:
    return json.dumps(fields, ensure_ascii=False)


def build_one(city: str, date: str, keep_raw: bool = False) -> dict:
    dest = OBS / city / f"{date}.parquet"
    if dest.exists():
        import pyarrow.parquet as pq

        return {"city": city, "date": date, "status": "cached", "rows_ok": pq.ParquetFile(dest).metadata.num_rows}

    static_url, tidy_url = fx.url_for(city, date, "static"), fx.url_for(city, date, "tidy")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        static_tmp = tmp / "static.zip"
        status = fx.fetch(static_url, static_tmp)
        if status == "missing":
            return {"city": city, "date": date, "status": "missing_static"}

        static_sha = static_store.store(static_tmp)
        mode_of, inside = static_store.load(static_sha, city)

        tidy_tmp = tmp / "tidy.csv.gz"
        status = fx.fetch(tidy_url, tidy_tmp)
        if status == "missing":
            return {"city": city, "date": date, "status": "missing_tidy", "static_sha256": static_sha}

        if not obs.validate_schema(tidy_tmp):
            return {"city": city, "date": date, "status": "schema_mismatch", "static_sha256": static_sha}

        tidy_sha = fx.sha256(tidy_tmp)
        last_modified = _last_modified(tidy_url)
        l0, day_report = obs.build_l0(tidy_tmp, mode_of, inside)

        if keep_raw:
            RAW.mkdir(parents=True, exist_ok=True)
            (RAW / f"{city}_static_gtfs_{date}.zip").write_bytes(static_tmp.read_bytes())
            (RAW / f"{city}_tidy_{date}.csv.gz").write_bytes(tidy_tmp.read_bytes())

    dest.parent.mkdir(parents=True, exist_ok=True)
    l0.to_parquet(dest, index=False, compression="zstd")

    report = {
        "city": city, "date": date, "status": "ok",
        "static_sha256": static_sha, "tidy_sha256": tidy_sha,
        "tidy_last_modified": last_modified,
        "feed_capability_window_signal": has_window_signal(city),
        **day_report,
    }
    if last_modified:
        try:
            report.update(resolve_epoch(dt.datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")))
        except ValueError:
            pass  # keep the raw header; provenance stays unresolved rather than failing the whole day
    return report


def run(cities: list[str] | None, start: str, end: str, workers: int = 3, keep_raw: bool = False) -> None:
    cities = cities or candidate_cities()
    days = list(fx.daterange(dt.date.fromisoformat(start), dt.date.fromisoformat(end), False))
    jobs = [(c, d) for c in cities for d in days]
    REPORTS.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS / "ingest_report.jsonl"
    missing = 0
    with open(report_path, "a", encoding="utf-8") as log, ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(build_one, c, d, keep_raw): (c, d) for c, d in jobs}
        for f in as_completed(futs):
            c, d = futs[f]
            try:
                row = f.result()
            except Exception as e:  # a single city-day's failure must not lose the rest (docs/04 §3: 404 is a gap, not an error)
                row = {"city": c, "date": d, "status": "error", "error": f"{type(e).__name__}: {e}"}
            row.setdefault("logged_at", dt.datetime.now(dt.timezone.utc).isoformat())
            log.write(_report_line(**row) + "\n")
            log.flush()
            if row["status"] not in ("ok", "cached"):
                missing += 1
            print(f"{row['status']:16s} {c} {d}", flush=True)
    print(f"gaps/errors: {missing} / {len(jobs)}; report: {report_path}")
