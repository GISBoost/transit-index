"""M1 acceptance test (docs/07): `ti ingest` on real release data reproduces golden_values.json
for Lodz 2026-09-24 (168 507 ok rows, Sigma L / Sigma T bus+tram = 17.58 km/h).
"""
import json

import pandas as pd
import pytest

import ti.ingest as ingest
import ti.static_store as static_store
from ti.paths import ROOT

GOLDEN = json.loads((ROOT / "reference" / "golden_values.json").read_text(encoding="utf-8"))["lodz_2026-09-24"]


@pytest.fixture
def isolated_stores(tmp_path, monkeypatch):
    obs_dir = tmp_path / "obs"
    monkeypatch.setattr(ingest, "OBS", obs_dir)
    monkeypatch.setattr(static_store, "STATIC_STORE", tmp_path / "static")
    return obs_dir


@pytest.mark.network
def test_ingest_lodz_reproduces_golden_values(isolated_stores):
    try:
        report = ingest.build_one("lodz", "2026-09-24")
    except OSError as e:
        pytest.skip(f"cannot download release assets: {e!r}")
    if report["status"] != "ok":
        pytest.skip(f"release asset unavailable: {report}")

    assert report["rows_ok"] == GOLDEN["street"]["n_obs"] == 168507
    assert report["feed_capability_window_signal"] is True
    assert report["epoch"] == "t1"

    l0 = pd.read_parquet(isolated_stores / "lodz" / "2026-09-24.parquet")
    assert len(l0) == 168507
    street = l0[l0["mode"].isin(["bus", "tram"])]
    v = street.seg_dist_m.sum() / street.seg_time_s.sum() * 3.6
    assert v == pytest.approx(GOLDEN["street"]["v_sum_ratio_kmh"], abs=0.01)


@pytest.mark.network
def test_ingest_is_idempotent_on_rerun(isolated_stores):
    r1 = ingest.build_one("lodz", "2026-09-24")
    if r1["status"] != "ok":
        pytest.skip(f"release asset unavailable: {r1}")
    r2 = ingest.build_one("lodz", "2026-09-24")
    assert r2["status"] == "cached"
    assert r2["rows_ok"] == r1["rows_ok"]


@pytest.mark.network
def test_missing_release_is_a_gap_not_an_error(isolated_stores):
    # Turin has known missing releases in the pilot window (docs/data-inventory.generated.md).
    report = ingest.build_one("turin", "2026-09-24")
    assert report["status"] in ("missing_static", "missing_tidy")


@pytest.mark.network
def test_ingest_nine_days_matches_corrected_value(isolated_stores):
    """M1 milestone-reviewer finding (2026-09-27): golden_values.json's 9-day entry used a single
    static (24.09) for all 9 days (docs/09 F10: ~1.4% of rows go "unmapped" that way), which
    docs/04 §2 / CLAUDE.md explicitly reject (static must be same-day). With each day's own
    static (what `ti obs` does), the correct value is 17.58 km/h, not the 17.59 in the golden
    file's per-day-static-agnostic fields - see reference/golden_values.json's
    `_uwaga_2026-09-27` note on that entry.
    """
    dates = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18",
             "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]
    reports = [ingest.build_one("lodz", d) for d in dates]
    if any(r["status"] not in ("ok", "cached") for r in reports):
        pytest.skip(f"release asset unavailable: {reports}")

    frames = [pd.read_parquet(isolated_stores / "lodz" / f"{d}.parquet") for d in dates]
    df = pd.concat(frames, ignore_index=True)
    street = df[df["mode"].isin(["bus", "tram"])]
    v = street.seg_dist_m.sum() / street.seg_time_s.sum() * 3.6
    assert len(street) == 1473575
    assert v == pytest.approx(17.58, abs=0.01)
