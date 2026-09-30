#!/usr/bin/env python3
"""Local dev-machine helper: run `ti geometry` with tippecanoe executed via Docker
(`klokantech/tippecanoe`), since no native tippecanoe build exists for this Windows machine and a
plain PATH shim can't work here (Win32 CreateProcess won't launch a bare .cmd without a shell).
CI (GitHub Actions) installs tippecanoe via apt and uses `ti geometry` unmodified; this script is
not part of the pipeline.

    python scripts/bin/tippecanoe_docker.py --cities lodz warszawa ...   (same args as `ti geometry`)

ponytail: quick local shim, not meant to ship; delete once tippecanoe is available another way.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ti import tiles  # noqa: E402

MOUNT = "/work"
_orig_tippecanoe = tiles.tippecanoe


def _docker_tippecanoe(geojson_gz: Path, out: Path) -> None:
    t = tiles.geometry_cfg()["tiles"]
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".geojson")
    import gzip
    import shutil

    with gzip.open(geojson_gz, "rb") as src, open(tmp, "wb") as dst:
        shutil.copyfileobj(src, dst)

    def rel(p: Path) -> str:
        return f"{MOUNT}/{p.resolve().relative_to(ROOT).as_posix()}"

    try:
        subprocess.run(
            ["docker", "run", "--rm", "-v", f"{ROOT}:{MOUNT}", "-w", MOUNT, "ti-tippecanoe:local", "tippecanoe",
             "-f", "-o", rel(out), "-l", t["layer"], f"-Z{t['min_zoom']}", f"-z{t['max_zoom']}",
             "--simplify-only-low-zooms", "--no-feature-limit", "--no-tile-size-limit", "--no-tiny-polygon-reduction",
             rel(tmp)],
            check=True, capture_output=True, text=True,
        )
    finally:
        tmp.unlink(missing_ok=True)


tiles.tippecanoe = _docker_tippecanoe

if __name__ == "__main__":
    from ti.cli import main

    raise SystemExit(main(sys.argv[1:]))
