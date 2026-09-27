"""Pre-M1 test harness: per-day sufficient statistics ("cells") so that any set of days can be pooled quickly.

Pooling days = summing cells (W1, W10, W3 per segment x band) or concatenating headway pairs (W11); nothing is
recomputed from rows. Used by t26_pooling.py (docs/10 T7, T26), and by the threshold tests T10/T15/T16.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import t_metrics as tm  # noqa: E402

CFG = tm.CFG
CACHE = ROOT / "data" / "l0" / "_cells"
DELAY_BIN_S, DELAY_MIN, DELAY_MAX = 10, -600, 1800  # histogram for W10 threshold tests (edges are multiples of 10 s)
HW_MAX_S = 720  # largest frequent-line threshold tested in T16


def holidays(city: str) -> set[str]:
    f = ROOT / "config" / "calendars" / f"{city}.yaml"
    return {str(x["date"]) if isinstance(x, dict) else str(x) for x in yaml.safe_load(f.read_text(encoding="utf-8"))["public_holidays"]}


def _hist(delay: pd.Series) -> np.ndarray:
    edges = np.arange(DELAY_MIN, DELAY_MAX + DELAY_BIN_S, DELAY_BIN_S)
    return np.histogram(delay.clip(DELAY_MIN, DELAY_MAX - 1e-6), bins=edges)[0]


def _hour_share(d: pd.DataFrame) -> np.ndarray:
    """Share of the day's ok rows per local hour 0..23 (band coverage approximation, as in scripts/m0_inventory.py)."""
    h = d.loc[d.seg_status == "ok", "hour"].dropna().astype(int)
    c = np.bincount(h, minlength=24).astype(float)
    return c / c.sum() if c.sum() else c


def band_coverage(cells: dict) -> float:
    """Minimum over bands of the share of the band's hours that count as recorded."""
    m = CFG["inventory"]["hour_covered_min_share"]
    return min(float(np.mean([cells["hour_share"][h] >= m for h in hrs])) for hrs in CFG["bands"].values())


def day_cells(d: pd.DataFrame) -> dict:
    """d: prepped L0 frame of ONE city-day (bus+tram rows)."""
    ok = d[(d.seg_status == "ok") & d.seg_in_area & (d.seg_time_s > 0) & (d.seg_dist_m > 0)]
    seg = ok.groupby(["seg_id", "band", "mode"], observed=True).agg(
        n=("seg_time_s", "size"), L=("seg_dist_m", "sum"), T=("seg_time_s", "sum")).reset_index()
    seg["seg_id"] = seg.seg_id.astype(str)
    p = d[d.obs & d.in_area & ~d.is_first_stop & d.plausible & d.delay_s.notna()]
    hw = d[d.in_area & d.headway_s.notna() & d.sched_headway_s.notna() & ~d.hs_outage
           & (d.sched_headway_s > 0) & (d.sched_headway_s < HW_MAX_S)]
    return {
        "n_rows": int(len(d)), "n_obs": int(d.obs.sum()), "n_ok_all": int((d.seg_status == "ok").sum()),
        "n_trips": int(d.trip_id.nunique()),
        "hour_share": _hour_share(d),
        "seg": seg,
        "delay_hist": _hist(p.delay_s), "delay_n": int(len(p)),
        "hw": np.column_stack([hw.headway_s.to_numpy(float), hw.sched_headway_s.to_numpy(float), hw.hs_skips.to_numpy(float)]),
    }


def build_store(city: str, force=False) -> dict[str, dict]:
    f = CACHE / f"{city}.pkl"
    stems = {p.stem for p in (tm.L0 / city).glob("*.parquet")}
    if f.exists() and not force:
        cached = pickle.loads(f.read_bytes())
        if set(cached) == stems:  # stale if days were added
            return cached
    out = {}
    for p in sorted((tm.L0 / city).glob("*.parquet")):
        d = tm.prep(pd.read_parquet(p))
        d["band"] = d.band.astype(str)
        out[p.stem] = day_cells(d)
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_bytes(pickle.dumps(out))
    return out


def valid_weekdays(city: str, store: dict, trip_gate: bool = True) -> list[str]:
    """Weekdays (no public holidays) passing the day gate. trip_gate adds the planned anomaly criterion:
    number of trips >= anomaly_min_trip_ratio x median of the weekdays that pass the basic gate."""
    hol = holidays(city)
    g = CFG["day_gate"]
    days = []
    for day, c in sorted(store.items()):
        if pd.Timestamp(day).weekday() >= 5 or day in hol:
            continue
        if (c["n_obs"] / c["n_rows"] >= g["min_crossing_rate"] and c["n_ok_all"] / c["n_rows"] >= g["min_ok_share"]
                and band_coverage(c) >= g["min_band_recorded_share"]):
            days.append(day)
    if trip_gate and days:
        med = float(np.median([store[d]["n_trips"] for d in days]))
        days = [d for d in days if store[d]["n_trips"] >= g["anomaly_min_trip_ratio"] * med]
    return days


def pool_seg(store: dict, days: list[str]) -> pd.DataFrame:
    return pd.concat([store[d]["seg"] for d in days]).groupby(["seg_id", "band", "mode"], as_index=False, observed=True).sum(numeric_only=True)


def w1_from(seg: pd.DataFrame, mode: str | None = None) -> float:
    s = seg if mode is None else seg[seg["mode"] == mode]
    return float(s.L.sum() / s["T"].sum() * 3.6) if len(s) else float("nan")


def w3_from(seg: pd.DataFrame, band: str, ref_bands=None, min_n=None) -> float:
    ref_bands = ref_bands or CFG["peak_penalty"]["ref_bands"]
    min_n = min_n or CFG["peak_penalty"]["min_obs_per_segment"]
    s = seg.groupby(["seg_id", "band"], as_index=False).sum(numeric_only=True)
    r = s[s.band.isin(ref_bands)].groupby("seg_id").agg(Lr=("L", "sum"), Tr=("T", "sum"), nr=("n", "sum"))
    r = r[r.nr >= min_n]
    r["v"] = r.Lr / r.Tr
    b = s[s.band == band].merge(r[["v"]], left_on="seg_id", right_index=True)
    b = b[b.n >= min_n]
    if b.empty:
        return float("nan")
    return float((b["T"].sum() / (b.L / b.v).sum() - 1) * 100)


def w10_from(store: dict, days: list[str], on_time=None) -> float:
    lo, hi = on_time or CFG["punctuality"]["on_time_s"]
    h = sum(store[d]["delay_hist"] for d in days)
    edges = np.arange(DELAY_MIN, DELAY_MAX, DELAY_BIN_S)  # left edges
    on = h[(edges >= lo) & (edges < hi)].sum()  # bin resolution 10 s (thresholds must be multiples of 10)
    return float(on / h.sum() * 100) if h.sum() else float("nan")


def w11_from(store: dict, days: list[str], frequent_s=None, winsor=0.99, drop_skips=False) -> float:
    f = frequent_s or CFG["regularity"]["frequent_headway_s"]
    a = np.vstack([store[d]["hw"] for d in days])
    a = a[a[:, 1] < f]
    if drop_skips:
        a = a[a[:, 2] == 0]
    if len(a) < 30:
        return float("nan")
    h, hs = a[:, 0], a[:, 1]
    if winsor:
        h = np.minimum(h, np.quantile(h, winsor))
    return float(((h ** 2).sum() / (2 * h.sum()) - (hs ** 2).sum() / (2 * hs.sum())) / 60)


METRICS = ["w1", "w3_am", "w3_pm", "w10", "w11"]


def pooled(store: dict, days: list[str]) -> dict:
    seg = pool_seg(store, days)
    return {"w1": w1_from(seg), "w3_am": w3_from(seg, "am_peak"), "w3_pm": w3_from(seg, "pm_peak"),
            "w10": w10_from(store, days), "w11": w11_from(store, days)}


class Dense:
    """Fast pooling over a FIXED list of days: per-day vectors indexed by (segment, band) plus scalar sums.

    W11 uses a per-city winsorisation cap fixed on all given days (a design difference from t_metrics.w11, which
    caps at the pooled sample's own quantile); documented in the T7/T26 report.
    """

    def __init__(self, store: dict, days: list[str], frequent_s=None, winsor=0.99):
        self.days = days
        segs = [store[d]["seg"].groupby(["seg_id", "band"], as_index=False).sum(numeric_only=True) for d in days]
        keys = pd.concat([s[["seg_id", "band"]] for s in segs]).drop_duplicates().reset_index(drop=True)
        keys["k"] = np.arange(len(keys))
        self.n, self.L, self.T = (np.zeros((len(days), len(keys)), dtype=np.float64) for _ in range(3))
        for i, s in enumerate(segs):
            k = s.merge(keys, on=["seg_id", "band"])["k"].to_numpy()
            self.n[i, k], self.L[i, k], self.T[i, k] = s.n.to_numpy(), s.L.to_numpy(), s["T"].to_numpy()
        self.seg_idx = pd.factorize(keys.seg_id)[0]
        self.band = keys.band.to_numpy()
        self.hist = np.array([store[d]["delay_hist"] for d in days])
        f = frequent_s or CFG["regularity"]["frequent_headway_s"]
        allhw = np.vstack([store[d]["hw"] for d in days])
        allhw = allhw[allhw[:, 1] < f]
        cap = np.quantile(allhw[:, 0], winsor) if (len(allhw) and winsor) else np.inf
        rows = []
        for d in days:
            a = store[d]["hw"]
            a = a[a[:, 1] < f]
            h = np.minimum(a[:, 0], cap)
            rows.append([h.sum(), (h ** 2).sum(), a[:, 1].sum(), (a[:, 1] ** 2).sum(), len(a)])
        self.hw = np.array(rows)

    def w1(self, idx):
        return float(self.L[idx].sum() / self.T[idx].sum() * 3.6)

    def w3(self, idx, band, ref_bands=None, min_n=None):
        ref_bands = ref_bands or CFG["peak_penalty"]["ref_bands"]
        min_n = min_n or CFG["peak_penalty"]["min_obs_per_segment"]
        n, L, T = self.n[idx].sum(0), self.L[idx].sum(0), self.T[idx].sum(0)
        isref = np.isin(self.band, ref_bands)
        m = self.seg_idx.max() + 1
        Lr, Tr, nr = (np.bincount(self.seg_idx, weights=x * isref, minlength=m) for x in (L, T, n))
        good = (nr >= min_n) & (Tr > 0)
        v = np.where(good, Lr / np.where(Tr > 0, Tr, 1), np.nan)
        inb = (self.band == band) & (n >= min_n)
        vv = v[self.seg_idx]
        sel = inb & ~np.isnan(vv)
        if not sel.any():
            return float("nan")
        return float((T[sel].sum() / (L[sel] / vv[sel]).sum() - 1) * 100)

    def w10(self, idx, on_time=None):
        lo, hi = on_time or CFG["punctuality"]["on_time_s"]
        h = self.hist[idx].sum(0)
        edges = np.arange(DELAY_MIN, DELAY_MAX, DELAY_BIN_S)
        return float(h[(edges >= lo) & (edges < hi)].sum() / h.sum() * 100)

    def w11(self, idx):
        s = self.hw[idx].sum(0)
        if s[4] < 30:
            return float("nan")
        return float(((s[1] / (2 * s[0])) - (s[3] / (2 * s[2]))) / 60)

    def all(self, idx) -> dict:
        idx = np.asarray(idx)
        return {"w1": self.w1(idx), "w3_am": self.w3(idx, "am_peak"), "w3_pm": self.w3(idx, "pm_peak"),
                "w10": self.w10(idx), "w11": self.w11(idx)}
