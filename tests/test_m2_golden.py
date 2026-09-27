"""M2 smoke test on the real, already-ingested Lodz window (M1's local data/obs/lodz/, no
network needed here - unlike test_m1_golden.py, which downloads). Not a pinned golden test like
M1's: the ingested window keeps growing as `ti ingest` runs again, so this checks plausibility
ranges and structural invariants, not exact values. Skips cleanly on a fresh checkout with no
locally ingested data.
"""
import pytest

import ti.aggregate as aggregate
import ti.metrics as metrics
from ti.paths import DATA

pytestmark = pytest.mark.skipif(not (DATA / "obs" / "lodz").exists(), reason="needs M1's locally ingested data/obs/lodz/")


def test_aggregate_and_metrics_are_plausible_on_the_real_lodz_window():
    l0 = aggregate.reference_day_l0("lodz", "2026-09-01", "2026-12-18")
    assert l0.service_date.nunique() >= 14  # docs/progress.md: M1 ingested through 2026-09-27

    stats = aggregate.build_segment_stats(l0)
    assert set(stats.band.unique()) == {"all_day", "am_peak", "midday", "pm_peak", "evening"}
    assert stats.q.isin(["ok", "thin", "none"]).all()
    assert (stats.n_obs > 0).all()

    dim = aggregate.build_segments_dim(l0)
    assert dim.seg_id.is_unique
    assert set(dim.primary_mode.unique()) <= {"bus", "tram", "other"}

    m = metrics.city_metrics("lodz", "2026-09-01", "2026-12-18")
    band = m["modes"]["all"]["bands"]["all_day"]
    assert 15.0 < band["w1_speed_kmh"] < 20.0  # golden single-day value (docs/09) is 17.58
    on_time = band["w10_punctuality"]["on_time"]
    assert 0.5 < on_time < 0.8  # docs/03 §4.1: 1-day estimate for Lodz was 66.1%

    pen = m["modes"]["all"]["w3_peak_penalty_pct"]
    assert pen["am_peak"]["pct"] < pen["pm_peak"]["pct"]  # docs/03 §3: AM < PM held on every variant tried so far
