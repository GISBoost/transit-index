"""Pre-M1 test harness: city-level dimension metrics from L0-lite frames (see t_l0.py).

Definitions follow docs/03 and reference/metrics_reference.py; every threshold comes from config/metrics.yaml
(overridable per call, which is what the sensitivity tests do). Prototype for the tests in docs/10, not the
production implementation (M2).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reference"))
import metrics_reference as mr  # noqa: E402

CFG = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))
L0 = ROOT / "data" / "l0"
HOUR_BAND = {h: b for b, hs in CFG["bands"].items() for h in hs}


def load_l0(city: str, dates: list[str] | None = None, cols: list[str] | None = None) -> pd.DataFrame:
    files = sorted((L0 / city).glob("*.parquet"))
    if dates is not None:
        files = [f for f in files if f.stem in set(dates)]
    parts = [pd.read_parquet(f, columns=cols) for f in files]
    for p, f in zip(parts, files):
        p["file_date"] = f.stem
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def prep(d: pd.DataFrame) -> pd.DataFrame:
    """Adds band and seg_id; keeps bus+tram rows of the city area only."""
    d = d[d["mode"].isin(["bus", "tram"])].copy()
    d["band"] = d.hour.map(HOUR_BAND).fillna("shoulder")
    d["seg_id"] = d.from_stop_id.astype(str) + ">" + d.stop_id.astype(str)
    d["service_date"] = d["date"].astype(str)
    return d


def w1(d: pd.DataFrame) -> float:
    u = d[(d.seg_status == "ok") & d.seg_in_area & (d.seg_time_s > 0) & (d.seg_dist_m > 0)]
    return float(u.seg_dist_m.sum() / u.seg_time_s.sum() * 3.6) if len(u) else float("nan")


def w3(d: pd.DataFrame, band: str, ref_bands=None, min_n=None) -> float:
    u = d[d.seg_in_area & (d.seg_status == "ok")]
    r = mr.peak_penalty_pct(u, band, tuple(ref_bands or CFG["peak_penalty"]["ref_bands"]), min_n or CFG["peak_penalty"]["min_obs_per_segment"])
    return r[0]


def w10(d: pd.DataFrame, on_time=None) -> float:
    lo, hi = on_time or CFG["punctuality"]["on_time_s"]
    u = d[d.obs & d.in_area & ~d.is_first_stop & d.plausible & d.delay_s.notna()]
    return float(((u.delay_s >= lo) & (u.delay_s <= hi)).mean() * 100) if len(u) else float("nan")


def w11(d: pd.DataFrame, frequent_s=None, winsor=0.99, drop_skips=False) -> float:
    """EWT in minutes (aggregate sums over the city, as for W1). Pairs where both observed and scheduled headway exist."""
    f = frequent_s or CFG["regularity"]["frequent_headway_s"]
    u = d[d.in_area & d.headway_s.notna() & d.sched_headway_s.notna() & ~d.hs_outage & (d.sched_headway_s > 0) & (d.sched_headway_s < f)]
    if drop_skips:
        u = u[u.hs_skips == 0]
    if len(u) < 30:
        return float("nan")
    h = u.headway_s.astype(float)
    if winsor:
        h = h.clip(upper=h.quantile(winsor))
    hs = u.sched_headway_s.astype(float)
    awt = (h ** 2).sum() / (2 * h.sum())
    swt = (hs ** 2).sum() / (2 * hs.sum())
    return float((awt - swt) / 60)


def city_metrics(d: pd.DataFrame) -> dict:
    """d: prepped L0 frame (one or many days) of one city."""
    ok = d[(d.seg_status == "ok") & d.seg_in_area]
    return {
        "n_ok": int(len(ok)),
        "crossing_rate": float(d.obs.mean()),
        "ok_share": float((d.seg_status == "ok").mean()),
        "w1": w1(d),
        "w1_bus": w1(d[d["mode"] == "bus"]),
        "w1_tram": w1(d[d["mode"] == "tram"]),
        "w3_am": w3(d, "am_peak"),
        "w3_pm": w3(d, "pm_peak"),
        "w10": w10(d),
        "w11": w11(d),
    }


def spearman(a: pd.Series, b: pd.Series) -> float:
    m = pd.concat([a, b], axis=1).dropna()
    return float(m.iloc[:, 0].rank().corr(m.iloc[:, 1].rank())) if len(m) >= 3 else float("nan")
