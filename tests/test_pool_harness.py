"""The pre-M1 test harness (scripts/t_pool.py) must reproduce the direct computation (scripts/t_metrics.py)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import t_metrics as tm  # noqa: E402
import t_pool as tp  # noqa: E402


def _day(seed: int, date: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = 4000
    hour = rng.choice([7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 20], n)
    seg = rng.integers(0, 40, n)
    dist = 300 + 25 * seg + rng.uniform(0, 50, n)
    speed = rng.uniform(8, 35, n) * np.where(np.isin(hour, [8, 16]), 0.85, 1.0)  # slower peaks
    obs = rng.random(n) < 0.87
    hs = rng.choice([180.0, 300.0, 420.0, 900.0], n)
    return pd.DataFrame({
        "date": date, "mode": "bus", "hour": hour, "seg_status": "ok", "seg_dist_m": dist, "seg_time_s": dist / speed * 3.6,
        "seg_in_area": True, "in_area": True, "obs": obs, "is_first_stop": False, "plausible": True,
        "delay_s": np.where(obs, rng.normal(60, 120, n).round(-1) + 5, np.nan),  # bin centres: no 10 s edge effects
        "headway_s": hs * rng.uniform(0.6, 1.6, n), "sched_headway_s": hs, "hs_outage": False, "hs_skips": 0,
        "from_stop_id": (seg).astype(str), "stop_id": (seg + 1).astype(str), "trip_id": rng.integers(0, 300, n).astype(str),
    })


def test_dense_matches_direct():
    days = ["2026-09-07", "2026-09-08", "2026-09-09"]
    frames = [tm.prep(_day(i, d)) for i, d in enumerate(days)]
    store = {d: tp.day_cells(f.assign(band=f.band.astype(str))) for d, f in zip(days, frames)}
    D = tp.Dense(store, days, winsor=None)
    direct = tm.city_metrics(pd.concat(frames, ignore_index=True))
    got = D.all(range(len(days)))
    assert np.isclose(got["w1"], direct["w1"])
    assert np.isclose(got["w3_pm"], direct["w3_pm"])
    assert np.isclose(got["w3_am"], direct["w3_am"])
    assert abs(got["w10"] - direct["w10"]) < 0.05  # 10 s histogram resolution
    d11 = tm.w11(pd.concat(frames, ignore_index=True), winsor=None)
    assert np.isclose(got["w11"], d11, rtol=1e-6)


def test_pooling_a_subset_equals_direct_subset():
    days = ["2026-09-07", "2026-09-08", "2026-09-09"]
    frames = [tm.prep(_day(i, d)) for i, d in enumerate(days)]
    store = {d: tp.day_cells(f.assign(band=f.band.astype(str))) for d, f in zip(days, frames)}
    D = tp.Dense(store, days)
    assert np.isclose(D.w1([0, 2]), tm.w1(pd.concat([frames[0], frames[2]])))
