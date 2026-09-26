"""Regression: the reference probe must reproduce reference/golden_values.json on real release data.

Downloads Lodz 2026-09-24 (tidy ~19 MB + static) into data/raw (gitignored). If the SHA-256 of the
inputs differs from the golden file the release was rebuilt: recompute the golden values, do not
'fix' the code (see golden_values.json _opis).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import fetch_release_assets as fetch

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GOLDEN = json.loads((ROOT / "reference" / "golden_values.json").read_text(encoding="utf-8"))["lodz_2026-09-24"]
DATE = "2026-09-24"


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    RAW.mkdir(parents=True, exist_ok=True)
    for kind in ("tidy", "static"):
        dest = RAW / fetch.ASSET[kind].format(city="lodz", date=DATE)
        try:
            status = fetch.fetch(fetch.url_for("lodz", DATE, kind), dest)
        except OSError as e:  # no network
            pytest.skip(f"cannot download release assets: {e!r}")
        if status == "missing":
            pytest.skip("release asset missing")
    for name, sha in GOLDEN["inputs"].items():
        if fetch.sha256(RAW / name) != sha:
            pytest.fail(f"{name}: SHA-256 differs from golden_values.json (release rebuilt?)")
    out = tmp_path_factory.mktemp("probe") / "lodz.json"
    cmd = [sys.executable, str(ROOT / "reference" / "probe_release_data.py"), "--city", "lodz",
           "--tidy", str(RAW / f"lodz_tidy_{DATE}.csv.gz"), "--static", str(RAW / f"lodz_static_gtfs_{DATE}.zip"),
           "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(out.read_text(encoding="utf-8"))


@pytest.mark.network
def test_row_counts_and_schema(probe):
    assert probe["per_file"][0]["rows"] == GOLDEN["per_file"][0]["rows"] == 207205
    assert probe["per_file"][0]["schema_ok"] is True


@pytest.mark.network
@pytest.mark.parametrize("mode", ["street", "bus", "tram"])
def test_speed_by_mode(probe, mode):
    assert probe[mode]["n_obs"] == GOLDEN[mode]["n_obs"]
    assert probe[mode]["v_sum_ratio_kmh"] == pytest.approx(GOLDEN[mode]["v_sum_ratio_kmh"], abs=0.01)


@pytest.mark.network
def test_headline_numbers(probe):
    assert probe["street"]["n_obs"] == 168507
    assert probe["street"]["v_sum_ratio_kmh"] == pytest.approx(17.58, abs=0.01)


@pytest.mark.network
def test_bands_and_punctuality(probe):
    for band, v in GOLDEN["speed_by_band_kmh"].items():
        assert probe["speed_by_band_kmh"][band] == pytest.approx(v, abs=0.01)
    for k, v in GOLDEN["punctuality_share"].items():
        assert probe["punctuality_share"][k] == pytest.approx(v, abs=0.001)
