#!/usr/bin/env python3
"""Builds the M4 test site (`_site/`): page + vendored MapLibre/PMTiles + tiles + config.json.

    python scripts/m4_build_testsite.py --geojson-dir site-test/geojson/2026-pilot --out _site [--basemap-dir basemap]

Runs both locally and in GitHub Actions (.github/workflows/m4-test-site.yml). Tiles are rebuilt from
the committed compact GeoJSON (`<city>.geojson.gz`), so the workflow needs no L0/L1/statics. Fails when
the artifact exceeds `tiles.site_ceiling_mb` (docs/06 §5) or when a segment >= 200 m is missing at z14+.
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ti import tiles as T  # noqa: E402
from ti.config import cities, geometry_cfg, metrics_cfg  # noqa: E402


def bounds(geojson_gz: Path) -> list[float]:
    with gzip.open(geojson_gz, "rt", encoding="utf-8") as f:
        feats = json.load(f)["features"]
    xs = [c[0] for x in feats for c in x["geometry"]["coordinates"]]
    ys = [c[1] for x in feats for c in x["geometry"]["coordinates"]]
    return [min(xs), min(ys), max(xs), max(ys)], len(feats)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", default="2026-pilot")
    ap.add_argument("--geojson-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "_site")
    ap.add_argument("--basemap-dir", type=Path, default=None, help="dir with <city>.pmtiles extracts (optional)")
    ap.add_argument("--node-modules", type=Path, default=ROOT / "site-test" / "node_modules")
    ap.add_argument("--report", type=Path, default=ROOT / "reports" / "m4" / "geometry_2026-pilot.json")
    a = ap.parse_args()

    gcfg = geometry_cfg()
    out = a.out
    if out.exists():
        shutil.rmtree(out)
    (out / "vendor").mkdir(parents=True)
    (out / "tokens").mkdir()
    (out / "tiles").mkdir()
    (out / "basemap").mkdir()
    site = ROOT / "site-test"
    for f in ("index.html", "style.css", "app.js"):
        shutil.copy(site / f, out / f)
    nm = a.node_modules
    shutil.copy(nm / "maplibre-gl" / "dist" / "maplibre-gl.js", out / "vendor")
    shutil.copy(nm / "maplibre-gl" / "dist" / "maplibre-gl.css", out / "vendor")
    shutil.copy(nm / "pmtiles" / "dist" / "pmtiles.js", out / "vendor")
    shutil.copy(ROOT / "design" / "tokens" / "colors.css", out / "tokens" / "colors.css")

    rep = json.loads(a.report.read_text(encoding="utf-8"))["cities"] if a.report.exists() else {}
    entries, failures = [], []
    for gz in sorted(a.geojson_dir.glob("*.geojson.gz")):
        city = gz.name.split(".")[0]
        pm = out / "tiles" / f"{city}.pmtiles"
        T.tippecanoe(gz, pm)
        acc = T.acceptance(gz, pm)
        if not acc["pass"]:
            failures.append((city, acc))
        bb, n = bounds(gz)
        base = a.basemap_dir / f"{city}.pmtiles" if a.basemap_dir else None
        has_base = bool(base and base.exists())
        if has_base:
            shutil.copy(base, out / "basemap" / f"{city}.pmtiles")
        r = rep.get(city, {})
        entries.append({
            "id": city, "name": cities()[city]["display_name"], "bounds": bb, "segments": n,
            "tiles": f"tiles/{city}.pmtiles", "tiles_bytes": pm.stat().st_size,
            "basemap": f"basemap/{city}.pmtiles" if has_base else None,
            "basemap_bytes": (out / "basemap" / f"{city}.pmtiles").stat().st_size if has_base else 0,
            "straight_share_length": r.get("geometry_straight_share_length"),
        })
        print(f"{city:10s} segments={n:6d} tiles={pm.stat().st_size/1e6:6.2f} MB accept={acc['pass']}", flush=True)
    cfg = {"edition": a.edition, "speed_classes_kmh": metrics_cfg()["speed_classes_kmh"], "layer": gcfg["tiles"]["layer"], "cities": entries}
    (out / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
    (out / "sizes.json").write_text(json.dumps({"total_mb": round(total, 2), "cities": {e["id"]: {"tiles": e["tiles_bytes"], "basemap": e["basemap_bytes"]} for e in entries}}, indent=1))
    print(f"artifact {total:.1f} MB (ceiling {gcfg['tiles']['site_ceiling_mb']} MB)")
    if total > gcfg["tiles"]["site_ceiling_mb"]:
        print("FAIL: artifact above the ceiling", file=sys.stderr)
        return 1
    if failures:
        print("FAIL: acceptance criterion violated:", failures, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
