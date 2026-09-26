"""Guards for the reference package and the config files (M0 skeleton)."""
import subprocess
import sys
from pathlib import Path

import yaml

import metrics_reference as mr

ROOT = Path(__file__).resolve().parent.parent


def test_reference_selftest():
    mr._self_test()


def test_examples_match_schemas():
    r = subprocess.run([sys.executable, str(ROOT / "reference" / "validate_examples.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_speed_classes_match_design_tokens():
    cfg = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))
    edges = cfg["speed_classes_kmh"]
    assert tuple(edges) == mr.DEFAULT_SPEED_EDGES_KMH
    # design/tokens/colors.css defines --speed-1..5 (5 classes) -> 4 edges
    css = (ROOT / "design" / "tokens" / "colors.css").read_text(encoding="utf-8")
    tokens = {f"--speed-{i}" for i in range(1, 6)}
    assert all(t in css for t in tokens) and "--speed-6" not in css and "--speed-0:" not in css
    assert len(edges) + 1 == len(tokens)


def test_bands_match_reference():
    cfg = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))
    for band, hours in cfg["bands"].items():
        assert {mr.band_of_hour(h) for h in hours} == {band}


def test_cities_and_defects_are_consistent():
    cities = yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]
    assert len(cities) == 27
    assert {c["tier"] for c in cities.values()} == {"candidate", "watch", "out_of_scope"}
    defects = yaml.safe_load((ROOT / "config" / "city_defects.yaml").read_text(encoding="utf-8"))["defects"]
    known = set(cities) | {"*", "helsinki"}
    assert {d["city"] for d in defects} <= known
