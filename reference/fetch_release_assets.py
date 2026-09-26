#!/usr/bin/env python3
"""Pobiera załączniki release'ów GISBoost/easy-GTFS-RT bez API GitHub (tylko publiczne adresy).

    python reference/fetch_release_assets.py --city lodz --from 2026-09-14 --to 2026-09-24 \
        --kind tidy --kind static --out data/raw --weekdays-only

Wzorzec adresu (zweryfikowany 2026-09-26 dla 15 miast):
    https://github.com/GISBoost/easy-GTFS-RT/releases/download/<miasto>-realized-<data>-phone/<miasto>_tidy_<data>.csv.gz
    https://github.com/GISBoost/easy-GTFS-RT/releases/download/<miasto>-realized-<data>-phone/<miasto>_static_gtfs_<data>.zip

Zachowanie:
- 404 oznacza brak release'u lub załącznika w tym dniu (np. Turyn 2026-09-24); dzień jest zapisywany
  jako brak, a skrypt idzie dalej (luki dzienne są normalne i są częścią bramki jakości).
- Istniejące pliki nie są pobierane ponownie; po pobraniu zapisywany jest skrót SHA-256 w manifeście
  <out>/fetch_manifest.jsonl (do manifestu edycji, docs/05).
- Tylko biblioteka standardowa. Listę dni z release'ami daje: git ls-remote --tags <repo> (bez API).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = "GISBoost/easy-GTFS-RT"
ASSET = {"tidy": "{city}_tidy_{date}.csv.gz", "static": "{city}_static_gtfs_{date}.zip"}


def url_for(city: str, date: str, kind: str) -> str:
    name = ASSET[kind].format(city=city, date=date)
    return f"https://github.com/{REPO}/releases/download/{city}-realized-{date}-phone/{name}"


def daterange(start: dt.date, end: dt.date, weekdays_only: bool):
    day = start
    while day <= end:
        if not weekdays_only or day.weekday() < 5:
            yield day.isoformat()
        day += dt.timedelta(days=1)


def fetch(url: str, dest: Path, retries: int = 3) -> str:
    """Zwraca 'ok', 'cached' albo 'missing'. Inne błędy po wyczerpaniu prób rzucają wyjątek."""
    if dest.exists() and dest.stat().st_size > 0:
        return "cached"
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as response, open(dest.with_suffix(dest.suffix + ".part"), "wb") as out:
                while chunk := response.read(1 << 20):
                    out.write(chunk)
            dest.with_suffix(dest.suffix + ".part").replace(dest)
            return "ok"
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return "missing"
            if attempt == retries:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries:
                raise
        time.sleep(2 * attempt)
    return "missing"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", action="append", required=True)
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end", required=True)
    ap.add_argument("--kind", action="append", choices=sorted(ASSET), default=None)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--weekdays-only", action="store_true")
    args = ap.parse_args()
    kinds = args.kind or ["tidy", "static"]
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = args.out / "fetch_manifest.jsonl"
    missing = 0
    with open(manifest, "a", encoding="utf-8") as log:
        for city in args.city:
            for date in daterange(dt.date.fromisoformat(args.start), dt.date.fromisoformat(args.end), args.weekdays_only):
                for kind in kinds:
                    dest = args.out / ASSET[kind].format(city=city, date=date)
                    status = fetch(url_for(city, date, kind), dest)
                    record = {"city": city, "date": date, "kind": kind, "status": status}
                    if status in ("ok", "cached"):
                        record.update(bytes=dest.stat().st_size, sha256=sha256(dest))
                    else:
                        missing += 1
                    log.write(json.dumps(record) + "\n")
                    print(f"{status:7s} {dest.name}")
    print(f"brakujących: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
