#!/usr/bin/env python3
"""Own basemap (docs/06 §1): per-city PMTiles extracts of a Protomaps daily build (OSM, ODbL).

    python scripts/m4_basemap.py --geojson-dir site-test/geojson/2026-pilot --out basemap

Needs network access to build.protomaps.com and the `go-pmtiles` binary (`go install
github.com/protomaps/go-pmtiles@latest`). Extracts use HTTP range requests, so only the bytes of the
city bbox are downloaded. Written for GitHub Actions; the M4 session's sandbox has no route to
build.protomaps.com, so this script has NOT been run end-to-end there (docs/progress.md).
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ti.config import geometry_cfg  # noqa: E402


def newest_build(cfg: dict, today: dt.date) -> tuple[str, str]:
    for back in range(cfg["lookback_days"] + 1):
        date = (today - dt.timedelta(days=back)).strftime("%Y%m%d")
        url = cfg["source_url_template"].format(date=date)
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "curl/8.0"})
        try:
            with urllib.request.urlopen(req, timeout=30):
                return date, url
        except (urllib.error.URLError, OSError):
            continue
    raise SystemExit(f"no Protomaps build found in the last {cfg['lookback_days']} days")


def bbox(geojson_gz: Path, margin: float) -> str:
    with gzip.open(geojson_gz, "rt", encoding="utf-8") as f:
        feats = json.load(f)["features"]
    xs = [c[0] for x in feats for c in x["geometry"]["coordinates"]]
    ys = [c[1] for x in feats for c in x["geometry"]["coordinates"]]
    return ",".join(f"{v:.5f}" for v in (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--geojson-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "basemap")
    ap.add_argument("--tool", default=shutil.which("go-pmtiles") or shutil.which("pmtiles") or "go-pmtiles")
    a = ap.parse_args()
    cfg = geometry_cfg()["basemap"]
    date, url = newest_build(cfg, dt.date.today())
    a.out.mkdir(parents=True, exist_ok=True)
    print("build", date, url, flush=True)
    report, failed = {"build_date": date, "source": url, "cities": {}}, 0
    for gz in sorted(a.geojson_dir.glob("*.geojson.gz")):
        city = gz.name.split(".")[0]
        dest = a.out / f"{city}.pmtiles"
        bb = bbox(gz, cfg["margin_deg"])
        r = subprocess.run([a.tool, "extract", url, str(dest), f"--bbox={bb}", f"--maxzoom={cfg['max_zoom']}"], capture_output=True, text=True)
        ok = r.returncode == 0 and dest.exists()
        failed += not ok
        report["cities"][city] = {"bbox": bb, "ok": ok, "bytes": dest.stat().st_size if ok else None, "stderr": None if ok else r.stderr[-400:]}
        print(f"{city:10s} {'ok ' + format(dest.stat().st_size / 1e6, '.1f') + ' MB' if ok else 'FAILED ' + r.stderr[-200:]}", flush=True)
    (a.out / "basemap_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 1 if failed == len(report["cities"]) else 0  # partial failures keep the page working (it has a no-basemap fallback)


if __name__ == "__main__":
    raise SystemExit(main())
