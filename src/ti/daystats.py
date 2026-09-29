"""`ti daystats`: L0 -> per-day sufficient statistics (`data/editions/<edition>/<city>/day_stats.parquet`).

Why a separate stage: the city values are ratios of sums over days, and the bootstrap over days
(docs/03 §6) needs the per-day components. L1 (`ti aggregate`) pools the days already, so it cannot
give them. This is the only stage of M3 that reads L0; `ti gate` then runs from `day_stats` +
`reports/` + `data/editions/` alone (e.g. in a session without `data/obs/`).

Long format, one row per (date, mode, kind, key); columns not used by a kind are NaN:

| kind      | key                      | columns                                                            |
|-----------|--------------------------|--------------------------------------------------------------------|
| `band`    | all_day/am_peak/...      | dist_m, time_s, n, pu_*, hw_n, hw_sum, hw_sum2, shw_sum, shw_sum2  |
| `hour`    | h06 ... h21              | dist_m, time_s, n                                                  |
| `line`    | route_short_name         | as `band` (all_day cell only; bus and tram, not street)           |
| `w3`      | am_peak / pm_peak        | w3_t_s (observed time), w3_exp_s (time at reference speed), n      |
| `w12`     | band from `service.band` | value (departures/hour, median over stops), n (stops)              |
| `coverage`| am_peak/midday/...       | value (share of the band's hours recorded; mode `street`)          |

Mode groups: `street` = bus + tram (docs/03 §1), `bus`, `tram`. Reference day: WEEKDAY minus public
holidays and school breaks, inside the city polygon (W0), only `seg_status == ok` (already in L0).

W3 reference speeds pool the reference days handed to `compute`; `run(..., valid_only=...)` restricts
those days to the ones `ti gate` accepted (second pass), so days flagged anomalous do not set the
reference. The W3 penalty is `ΣT_observed / ΣT_expected - 1` with `T_expected = L / v_ref(segment)`;
per-day sums add up to the same ratio as `metrics_reference.peak_penalty_pct` on the pooled days.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import aggregate
from .config import holidays, metrics_cfg, school_breaks
from .paths import DATA, REPORTS, mr

MODE_GROUPS = {"street": ("bus", "tram"), "bus": ("bus",), "tram": ("tram",)}
COLS = ["dist_m", "time_s", "n", "pu_n", "pu_early", "pu_on", "pu_late", "pu_vlate",
        "hw_n", "hw_sum", "hw_sum2", "shw_sum", "shw_sum2", "w3_t_s", "w3_exp_s", "value"]
KEYS = ["date", "mode", "kind", "key"]


def day_stats_path(city: str, edition: str):
    return DATA / "editions" / edition / city / "day_stats.parquet"


def _usable(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df.seg_time_s > 0) & (df.seg_dist_m > 0)]


def _component_frame(rows: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Per-group sums of the speed, W10 and W11 components (config-driven thresholds)."""
    cfg = metrics_cfg()
    pu, reg = cfg["punctuality"], cfg["regularity"]
    on_lo, on_hi = pu["on_time_s"]
    r = _usable(rows)
    d = r.delay_s.astype(float)
    counted = d.notna()
    if pu["exclude_first_stop"]:
        counted &= ~r.is_first_stop.astype(bool)
    h, sh = r.headway_s.astype(float), r.sched_headway_s.astype(float)
    hw_ok = (sh < reg["frequent_headway_s"]) & (~r.headway_spans_outage.astype(bool)) & h.notna() & sh.notna() & (h > 0) & (sh > 0)
    work = pd.DataFrame({
        **{c: r[c].astype(str) if c != "hour" else r[c] for c in group_cols},
        "dist_m": r.seg_dist_m.astype(float), "time_s": r.seg_time_s.astype(float), "n": 1.0,
        "pu_n": counted.astype(float),
        "pu_early": (counted & (d < on_lo)).astype(float),
        "pu_on": (counted & (d >= on_lo) & (d <= on_hi)).astype(float),
        "pu_late": (counted & (d > on_hi) & (d <= pu["late_s"])).astype(float),
        "pu_vlate": (counted & (d > pu["late_s"])).astype(float),
        "hw_n": hw_ok.astype(float),
        "hw_sum": h.where(hw_ok, 0.0), "hw_sum2": (h ** 2).where(hw_ok, 0.0),
        "shw_sum": sh.where(hw_ok, 0.0), "shw_sum2": (sh ** 2).where(hw_ok, 0.0),
    })
    return work.groupby(group_cols, observed=True, sort=True).sum().reset_index()


def w3_pairs(sub: pd.DataFrame, band: str) -> pd.DataFrame:
    """Per-date (w3_t_s, w3_exp_s, n) for `band`, reference speed per segment from the pooled
    reference bands (same definition and thresholds as `mr.peak_penalty_pct`)."""
    pk = metrics_cfg()["peak_penalty"]
    min_n = pk["min_obs_per_segment"]
    u = _usable(sub)
    target = u[u.band.astype(str) == band]
    if target.empty:
        return pd.DataFrame(columns=["service_date", "w3_t_s", "w3_exp_s", "n"])
    ref = u[u.band.astype(str).isin(pk["ref_bands"])].groupby("seg_id", observed=True).agg(
        Lr=("seg_dist_m", "sum"), Tr=("seg_time_s", "sum"), nr=("seg_time_s", "size"))
    ref = ref[ref.nr >= min_n]
    ref["vref"] = ref.Lr.astype(float) / ref.Tr.astype(float)
    p = target.merge(ref[["vref"]], left_on="seg_id", right_index=True)
    p = p[p.groupby("seg_id", observed=True).seg_time_s.transform("size") >= min_n]
    if p.empty:
        return pd.DataFrame(columns=["service_date", "w3_t_s", "w3_exp_s", "n"])
    p = p.assign(service_date=p.service_date.astype(str), exp=p.seg_dist_m.astype(float) / p.vref)
    g = p.groupby("service_date").agg(w3_t_s=("seg_time_s", "sum"), w3_exp_s=("exp", "sum"), n=("seg_time_s", "size"))
    g["w3_t_s"] = g.w3_t_s.astype(float)
    return g.reset_index()


def band_coverage(l0_raw_day: pd.DataFrame) -> dict[str, float]:
    """Share of each named band's hours that the recording covers (docs/03 §6 day gate). An hour
    counts as recorded when it holds >= `inventory.hour_covered_min_share` of the day's `ok` rows:
    the same approximation the M0 inventory used (`scripts/m0_inventory.py`)."""
    cfg = metrics_cfg()
    min_share = cfg["inventory"]["hour_covered_min_share"]
    hours = pd.to_numeric(l0_raw_day.hour, errors="coerce").dropna().astype(int)
    share = hours.value_counts(normalize=True) if len(hours) else pd.Series(dtype=float)
    recorded = {int(h) for h in share[share >= min_share].index}
    out = {}
    for band in ("am_peak", "midday", "pm_peak", "evening"):
        hrs = cfg["bands"][band]
        out[band] = len(recorded & set(hrs)) / len(hrs)
    return out


def compute(l0: pd.DataFrame, coverage_by_date: dict[str, dict[str, float]] | None = None,
            w12_by_date: dict[str, dict[str, tuple[float, int]]] | None = None) -> pd.DataFrame:
    """`l0`: reference-day L0 of one city (WEEKDAY, in_area, bus/tram). Returns the long table."""
    cfg = metrics_cfg()
    parts: list[pd.DataFrame] = []
    if l0.empty:
        l0 = l0.iloc[0:0]
        groups = {}
    else:
        l0 = l0.assign(service_date=l0.service_date.astype(str))
        groups = MODE_GROUPS
    for mode, modes in groups.items():
        sub = l0[l0["mode"].astype(str).isin(modes)]
        if sub.empty:
            continue
        b = aggregate.expand_bands(sub)
        band = _component_frame(b, ["service_date", "cell_band"]).rename(columns={"service_date": "date", "cell_band": "key"})
        band["kind"] = "band"
        parts.append(band.assign(mode=mode))

        hourly = sub[sub.hour.between(6, 21).fillna(False)]
        if len(hourly):
            hr = _component_frame(hourly, ["service_date", "hour"])[["service_date", "hour", "dist_m", "time_s", "n"]]
            hr = hr.rename(columns={"service_date": "date"})
            hr["key"] = hr.pop("hour").map(lambda h: f"h{int(h):02d}")
            parts.append(hr.assign(mode=mode, kind="hour"))

        if mode != "street":
            allday = b[b.cell_band == "all_day"]
            if len(allday):
                ln = _component_frame(allday, ["service_date", "route_short_name"]).rename(columns={"service_date": "date", "route_short_name": "key"})
                parts.append(ln.assign(mode=mode, kind="line"))

        for pb in ("am_peak", "pm_peak"):
            w3 = w3_pairs(sub, pb)
            if len(w3):
                parts.append(w3.rename(columns={"service_date": "date"}).assign(mode=mode, kind="w3", key=pb))

    for date, per_mode in (w12_by_date or {}).items():
        for mode, (v, n_stops) in per_mode.items():
            if v == v:
                parts.append(pd.DataFrame([{"date": date, "mode": mode, "kind": "w12", "key": cfg["service"]["band"], "value": float(v), "n": float(n_stops)}]))
    for date, cov in (coverage_by_date or {}).items():
        for band, share in cov.items():
            parts.append(pd.DataFrame([{"date": date, "mode": "street", "kind": "coverage", "key": band, "value": float(share)}]))

    if not parts:
        return pd.DataFrame(columns=KEYS + COLS)
    out = pd.concat(parts, ignore_index=True)
    for c in COLS:
        if c not in out:
            out[c] = np.nan
    return out[KEYS + COLS].sort_values(KEYS, kind="stable").reset_index(drop=True)


def load(city: str, edition: str) -> pd.DataFrame | None:
    p = day_stats_path(city, edition)
    return pd.read_parquet(p) if p.exists() else None


def gate_view(ds: pd.DataFrame | None) -> dict[str, dict]:
    """Per-date view for `ti.gate`: recorded band coverage and daily city speed (`ΣL/ΣT`, W1)."""
    if ds is None or ds.empty:
        return {}
    out: dict[str, dict] = {}
    cov = ds[ds.kind == "coverage"]
    for date, g in cov.groupby("date"):
        out.setdefault(date, {})["band_coverage"] = dict(zip(g.key, g.value))
    sp = ds[(ds.kind == "band") & (ds["mode"] == "street") & (ds.key == "all_day")]
    for _, r in sp.iterrows():
        if r.time_s > 0:
            out.setdefault(r.date, {})["speed_kmh"] = float(r.dist_m / r.time_s * 3.6)
    return out


def valid_dates_from_gate(city: str, edition: str) -> set[str] | None:
    p = REPORTS.parent / "m3" / f"gate_days_{edition}.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    return {d["date"] for d in doc.get(city, []) if d["valid"]}


def run(city: str, from_date: str, to_date: str, edition: str, valid_only: bool = False) -> str:
    from . import metrics as metrics_mod  # W12 needs static tables (data/static)

    obs_dir = DATA / "obs" / city
    holi, brk = holidays(city), school_breaks(city)
    only = valid_dates_from_gate(city, edition) if valid_only else None
    if valid_only and only is None:
        raise SystemExit("--valid-only: run `ti gate` first (reports/m3/gate_days_<edition>.json missing)")
    frames, cov, dates = [], {}, []
    for f in sorted(obs_dir.glob("*.parquet")) if obs_dir.exists() else []:
        date = f.stem
        if not (from_date <= date <= to_date) or date in holi or date in brk:
            continue
        raw = pd.read_parquet(f)
        if raw.empty or not (raw.day_type.astype(str) == "WEEKDAY").any():
            continue
        cov[date] = band_coverage(raw)
        if only is not None and date not in only:
            continue
        ref = raw[(raw.day_type.astype(str) == "WEEKDAY") & raw.in_area & raw["mode"].astype(str).isin(("bus", "tram"))]
        if len(ref):
            frames.append(ref)
            dates.append(date)
    l0 = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    inside: dict = {}
    w12 = {d: r for d in dates if (r := metrics_mod.service_offer_day(city, d, inside)) is not None}
    table = compute(l0, cov, w12)
    out = day_stats_path(city, edition)
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(out, index=False)
    return str(out)
