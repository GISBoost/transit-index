#!/usr/bin/env python3
"""M0 inventory of easy-GTFS-RT release assets on the pilot window.

Two stages, both resumable (records already in --out are skipped):

  heads  For every city x day: does the release tag exist, size of the tidy and static assets
         (Range GET, no full download), and a cheap fingerprint of the static zip (sha256 of its
         last 256 KiB = zip central directory with CRC32 of every member) to detect unchanged statics.
  stats  For candidate cities x weekdays: stream-download the tidy file, compute quality statistics,
         delete the raw file. Only the small statistics are kept.

    py scripts/m0_inventory.py heads --from 2026-09-01 --to 2026-09-25 --out reports/m0/heads.jsonl
    py scripts/m0_inventory.py stats --from 2026-09-01 --to 2026-09-25 --heads reports/m0/heads.jsonl \
        --out reports/m0/stats.jsonl --tmp data/m0_tmp --workers 3

Raw downloads go to --tmp (gitignored `data/`) and are removed after each file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reference"))
import fetch_release_assets as fx  # noqa: E402

REPO_URL = f"https://github.com/{fx.REPO}.git"
TAIL = 256 * 1024
METRICS = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))
FREQUENT_HEADWAY_S = METRICS["regularity"]["frequent_headway_s"]  # readiness indicator for W11 only
HOUR_MIN_SHARE = METRICS["inventory"]["hour_covered_min_share"]


def cities_cfg() -> dict:
    return yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]


def list_tags() -> set[tuple[str, str]]:
    out = subprocess.run(["git", "ls-remote", "--tags", REPO_URL], capture_output=True, text=True, check=True).stdout
    tags = set()
    for line in out.splitlines():
        ref = line.split("\t")[1].removeprefix("refs/tags/")
        if "-realized-" in ref and ref.endswith("-phone"):
            city, rest = ref.split("-realized-")
            tags.add((city, rest.removesuffix("-phone")))
    return tags


def range_get(url: str, rng: str, retries: int = 4):
    """Returns (status, total_size|None, body). status: 'ok' | 'missing'."""
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers={"Range": rng})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                total = None
                cr = r.headers.get("Content-Range")
                if cr and "/" in cr:
                    total = int(cr.rsplit("/", 1)[1])
                elif r.headers.get("Content-Length"):
                    total = int(r.headers["Content-Length"])
                return "ok", total, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "missing", None, b""
            if e.code == 416:  # empty file
                return "ok", 0, b""
            if e.code in (400, 403, 501) or attempt == retries:  # not worth retrying
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries:
                raise
        time.sleep(2 * attempt)
    return "missing", None, b""


def zip_content_fp(tail: bytes) -> str | None:
    """Content fingerprint of a zip from its central directory: sha256 over (name, crc32, size) of every member.

    A cheap proxy to detect unchanged statics without downloading them. It is NOT the file SHA-256 that
    CLAUDE.md requires for deduplication (M1 computes that on the downloaded file).

    Ignores modification times, so a static feed regenerated daily without changes keeps the same fingerprint.
    Returns None if the central directory is not fully inside `tail` (or the archive is zip64).
    """
    import struct
    eocd = tail.rfind(b"PK")
    if eocd < 0 or len(tail) < eocd + 22:
        return None
    n_entries, cd_size, cd_offset = struct.unpack("<HII", tail[eocd + 10:eocd + 20])
    if n_entries == 0xFFFF or cd_offset == 0xFFFFFFFF:
        return None
    pos = eocd - cd_size  # central directory ends right before the EOCD record
    if pos < 0:
        return None
    entries = []
    for _ in range(n_entries):
        if tail[pos:pos + 4] != b"PK":
            return None
        crc, _csize, usize, nlen, xlen, clen = struct.unpack("<IIIHHH", tail[pos + 16:pos + 34])
        entries.append((tail[pos + 46:pos + 46 + nlen], crc, usize))
        pos += 46 + nlen + xlen + clen
    return hashlib.sha256(repr(sorted(entries)).encode()).hexdigest()[:16]


def head_one(city: str, date: str, tag_exists: bool) -> dict:
    rec = {"city": city, "date": date, "weekday": dt.date.fromisoformat(date).weekday(), "tag": tag_exists}
    if not tag_exists:
        return rec | {"tidy_bytes": None, "static_bytes": None, "static_fp": None}
    st, tidy_total, _ = range_get(fx.url_for(city, date, "tidy"), "bytes=0-0")
    rec["tidy_bytes"] = tidy_total if st == "ok" else None
    st, static_total, _ = range_get(fx.url_for(city, date, "static"), "bytes=0-0")
    rec["static_bytes"] = static_total if st == "ok" else None
    if st == "ok" and static_total:
        start = max(0, static_total - TAIL)  # suffix ranges (bytes=-N) are rejected with 501
        _, _, tail = range_get(fx.url_for(city, date, "static"), f"bytes={start}-{static_total - 1}")
        rec["static_fp"] = zip_content_fp(tail) or "tail:" + hashlib.sha256(tail).hexdigest()[:12]
    else:
        rec["static_fp"] = None
    return rec


def days(start: str, end: str, weekdays_only=False):
    d = dt.date.fromisoformat(start)
    while d <= dt.date.fromisoformat(end):
        if not weekdays_only or d.weekday() < 5:
            yield d.isoformat()
        d += dt.timedelta(days=1)


def load_done(path: Path) -> dict:
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done[(r["city"], r["date"])] = r
    return done


def cmd_heads(a) -> int:
    tags = list_tags()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(out)
    todo = [(c, d) for c in cities_cfg() for d in days(a.start, a.end) if (c, d) not in done]
    print(f"tags: {len(tags)}; to probe: {len(todo)}")
    with open(out, "a", encoding="utf-8") as log, ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(head_one, c, d, (c, d) in tags): (c, d) for c, d in todo}
        for i, f in enumerate(as_completed(futs), 1):
            log.write(json.dumps(f.result()) + "\n")
            log.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}")
    return 0


def cmd_statics(a) -> int:
    """Recompute static_fp for existing heads records (content fingerprint, see zip_content_fp)."""
    path = Path(a.out)
    recs = list(load_done(path).values())

    def refresh(r):
        if r.get("static_bytes"):
            start = max(0, r["static_bytes"] - TAIL)
            _, _, tail = range_get(fx.url_for(r["city"], r["date"], "static"), f"bytes={start}-{r['static_bytes'] - 1}")
            r["static_fp"] = zip_content_fp(tail) or "tail:" + hashlib.sha256(tail).hexdigest()[:12]
        return r

    with ThreadPoolExecutor(max_workers=8) as ex:
        recs = list(ex.map(refresh, recs))
    lines = [json.dumps(r) for r in sorted(recs, key=lambda r: (r["city"], r["date"]))]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("refreshed", sum(bool(r.get("static_bytes")) for r in recs), "static fingerprints")
    return 0


# ---- stats stage (runs in worker processes) -------------------------------------------------------

def tidy_stats(city: str, date: str, tmp: str) -> dict:
    import pandas as pd

    import metrics_reference as mr
    from probe_release_data import TIDY_COLUMNS

    dest = Path(tmp) / fx.ASSET["tidy"].format(city=city, date=date)
    Path(tmp).mkdir(parents=True, exist_ok=True)
    status = fx.fetch(fx.url_for(city, date, "tidy"), dest)
    if status == "missing":
        return {"city": city, "date": date, "status": "missing"}
    try:
        sha = fx.sha256(dest)
        header = pd.read_csv(dest, nrows=0).columns.tolist()
        usecols = ["trip_id", "service_date", "obs_time", "obs_local", "delay_s", "is_first_stop", "seg_status",
                   "headway_s", "sched_headway_s", "headway_spans_outage", "service_date_plausible", "trip_coverage",
                   "seg_dist_m", "seg_time_s"]
        d = pd.read_csv(dest, low_memory=False, usecols=[c for c in usecols if c in header], dtype={"trip_id": str})
        n = len(d)
        st = d.seg_status.value_counts(normalize=True)
        ok = d[d.seg_status == "ok"]
        hours = mr.hour_from_obs_local(ok.obs_local) if len(ok) else pd.Series(dtype=int)
        hshare = hours.value_counts(normalize=True)
        rec_hours = sorted(int(h) for h in hshare[hshare >= HOUR_MIN_SHARE].index)
        band_cov = {b: round(len(set(hs) & set(rec_hours)) / len(hs), 2) for b, hs in mr.BANDS.items()}
        obs = d[d.obs_time.notna()]
        first = obs.is_first_stop.fillna(False).astype(bool) if "is_first_stop" in obs else None
        delay = obs[~first] if first is not None else obs
        sched_h = d.sched_headway_s.dropna()
        res = {
            "city": city, "date": date, "status": "ok", "tidy_sha256": sha,
            "schema_ok": header == TIDY_COLUMNS, "n_cols": len(header),
            "rows": n, "trips": int(d.trip_id.nunique()), "trip_id_missing_share": round(float(d.trip_id.isna().mean()), 3),
            "crossing_rate": round(float(d.obs_time.notna().mean()), 3),
            "ok_share": round(float((d.seg_status == "ok").mean()), 3),
            "seg_status_share": {k: round(float(v), 3) for k, v in st.items()},
            "service_date_is_file_date": round(float((d.service_date.astype(str) == date).mean()), 3),
            "service_date_plausible_share": round(float(d.service_date_plausible.astype(bool).mean()), 3) if "service_date_plausible" in d else None,
            "local_hours_ge1pct": rec_hours, "band_hour_coverage": band_cov,
            "delay_available_share": round(float(delay.delay_s.notna().mean()), 3) if len(delay) else None,
            "headway_available_share": round(float(obs.headway_s.notna().mean()), 3) if len(obs) else None,
            "sched_headway_available_share": round(float(d.sched_headway_s.notna().mean()), 3),
            "frequent_row_share": round(float((sched_h < FREQUENT_HEADWAY_S).mean()), 3) if len(sched_h) else None,
            "trip_coverage_mean": round(float(d.trip_coverage.astype(float).mean()), 3) if "trip_coverage" in d else None,
        }
        return res
    finally:
        dest.unlink(missing_ok=True)


def cmd_stats(a) -> int:
    heads = load_done(Path(a.heads))
    cfg = cities_cfg()
    cities = [c for c, v in cfg.items() if v["tier"] in a.tiers]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(out)
    todo = [(c, d) for c in cities for d in days(a.start, a.end, weekdays_only=True)
            if (c, d) not in done and heads.get((c, d), {}).get("tidy_bytes")]
    total_gb = sum(heads[k]["tidy_bytes"] for k in todo) / 1e9
    print(f"cities: {len(cities)}; files to process: {len(todo)} (~{total_gb:.1f} GB)")
    t0 = time.time()
    with open(out, "a", encoding="utf-8") as log, ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(tidy_stats, c, d, a.tmp): (c, d) for c, d in todo}
        for i, f in enumerate(as_completed(futs), 1):
            c, d = futs[f]
            try:
                rec = f.result()
            except Exception as e:  # keep going; record the failure so it is retried on the next run only if removed
                print(f"  FAIL {c} {d}: {e!r}")
                continue
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"  {i}/{len(todo)} {c} {d} {rec.get('status')} ({time.time() - t0:.0f}s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("heads", "stats", "statics"):
        p = sub.add_parser(name)
        p.add_argument("--from", dest="start", required=True)
        p.add_argument("--to", dest="end", required=True)
        p.add_argument("--out", required=True)
    sub.choices["stats"].add_argument("--heads", required=True)
    sub.choices["stats"].add_argument("--tmp", default=str(ROOT / "data" / "m0_tmp"))
    sub.choices["stats"].add_argument("--workers", type=int, default=3)
    sub.choices["stats"].add_argument("--tiers", nargs="+", default=["candidate"])
    a = ap.parse_args()
    return {"heads": cmd_heads, "stats": cmd_stats, "statics": cmd_statics}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
