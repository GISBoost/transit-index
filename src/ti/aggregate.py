"""Stage C (docs/04 §3): L0 (many city-days) -> L1 `segment_stats.parquet` + `segments.parquet`.

Reference day (docs/03 §2.2): `day_type == "WEEKDAY"` minus public holidays from
`config/calendars/<city>.yaml` (school breaks are empty there for now, C4: left as planned,
before M3). Automatic anomaly-day detection and the day/city quality gate (docs/03 §7, §6) are
`ti gate`'s job in M3, not this stage: aggregate does not drop "bad" days on its own.

Bands (docs/03 §2.3): a row can belong to more than one L1 cell (`all_day` covers 6-21 regardless
of the named peak/off-peak band), so each L0 row is expanded into its band memberships before
grouping. Hourly bands (h06..h21) are not built here: W9's profile is a city-level curve
(`ti.metrics`), not a per-segment property, so it is computed straight from L0.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import holidays, metrics_cfg
from .paths import DATA, mr

NAMED_BANDS = ("am_peak", "midday", "pm_peak", "evening")


def _tag_ok(l0: pd.DataFrame) -> pd.DataFrame:
    """reference/metrics_reference.py's usable() filters on seg_status, which L0 no longer
    carries (M1's obs.py already applied that filter before writing L0). Every L0 row is "ok" by
    construction; tag it back on so callers can use the reference formulas unchanged."""
    return l0 if "seg_status" in l0.columns else l0.assign(seg_status="ok")


def apply_config_bands(l0: pd.DataFrame) -> pd.DataFrame:
    """Re-derives `band` from `hour` with the bands of config/metrics.yaml. L0 files keep the `band` that was
    current at ingest; deriving it again on load means a change of the band table needs no re-ingest."""
    if l0.empty or "hour" not in l0.columns:
        return l0
    hour_band = {int(h): name for name, hrs in metrics_cfg()["bands"].items() for h in hrs}
    band = pd.to_numeric(l0["hour"], errors="coerce").map(hour_band).fillna("shoulder")
    return l0.assign(band=band.astype("category"))


def reference_day_l0(city: str, from_date: str, to_date: str) -> pd.DataFrame:
    """Concatenated L0 for `city` in [from_date, to_date], filtered to the reference day
    (WEEKDAY minus public holidays), to W0 (`in_area`), and to bus/tram (docs/03 §1: metro and
    rail are out of the index in every dimension, not just W1 - milestone-reviewer M2 found
    `other`-mode segments leaking into segment_stats/segments.parquet through this shared entry
    point, since `ti.metrics`'s own MODE_GROUPS never selects `other` but nothing upstream of it
    dropped those rows)."""
    obs_dir = DATA / "obs" / city
    holi = holidays(city)
    frames = []
    for f in sorted(obs_dir.glob("*.parquet")) if obs_dir.exists() else []:
        date = f.stem
        if not (from_date <= date <= to_date) or date in holi:
            continue
        frames.append(apply_config_bands(pd.read_parquet(f)))
    if not frames:
        return pd.DataFrame()
    d = pd.concat(frames, ignore_index=True)
    d = d[(d.day_type == "WEEKDAY") & d.in_area & d["mode"].isin(("bus", "tram"))]
    return _tag_ok(d)


def expand_bands(l0: pd.DataFrame) -> pd.DataFrame:
    """Expands each row into its band memberships: `all_day` (hour 6-21) plus its named band."""
    parts = []
    all_day = l0[l0.hour.between(6, 21).fillna(False)]
    if len(all_day):
        parts.append(all_day.assign(cell_band="all_day"))
    named = l0[l0.band.astype(str).isin(NAMED_BANDS)]
    if len(named):
        parts.append(named.assign(cell_band=named.band.astype(str)))
    return pd.concat(parts, ignore_index=True) if parts else l0.iloc[0:0].assign(cell_band=pd.Series(dtype=str))


def build_segment_stats(l0: pd.DataFrame) -> pd.DataFrame:
    """L1 (docs/04 §2): one row per (seg_id, band); day_type is always WEEKDAY here."""
    if l0.empty:
        return pd.DataFrame(columns=["seg_id", "band", "day_type", "n_obs", "n_days", "n_trips",
                                      "v_p20", "v_p50", "v_p80", "v_ff", "v_sched_p50", "slowdown",
                                      "sum_dist_m", "sum_time_s", "length_m", "q"])
    l0 = _tag_ok(l0)
    b = expand_bands(l0).copy()
    b["speed_kmh"] = b.seg_dist_m / b.seg_time_s * 3.6
    b["v_sched_kmh"] = (b.seg_dist_m / b.sched_pass_time_s * 3.6).where(b.sched_pass_time_s > 0)

    g = b.groupby(["seg_id", "cell_band"], observed=True)
    stats = g.agg(
        n_obs=("seg_time_s", "size"),
        n_days=("service_date", "nunique"),
        n_trips=("trip_id", "nunique"),
        v_p20=("speed_kmh", lambda s: float(s.quantile(0.20))),
        v_p50=("speed_kmh", "median"),
        v_p80=("speed_kmh", lambda s: float(s.quantile(0.80))),
        v_sched_p50=("v_sched_kmh", "median"),
        sum_dist_m=("seg_dist_m", "sum"),
        sum_time_s=("seg_time_s", "sum"),
        length_m=("seg_dist_m", "median"),
    ).reset_index().rename(columns={"cell_band": "band"})
    stats["day_type"] = "WEEKDAY"

    ff = mr.free_flow_kmh(l0)  # per seg_id, across all bands (docs/03 §3 "Dlaczego kara szczytu..."): diagnostic only
    stats = stats.merge(ff.rename("v_ff"), left_on="seg_id", right_index=True, how="left")
    t_ff = stats.sum_dist_m / (stats.v_ff / 3.6)
    stats["slowdown"] = ((stats.sum_time_s / t_ff - 1.0) * 100.0).where(t_ff > 0)
    stats["q"] = [mr.segment_quality(int(n), int(nd)) for n, nd in zip(stats.n_obs, stats.n_days)]
    return stats


def build_segments_dim(l0: pd.DataFrame) -> pd.DataFrame:
    """`segments.parquet` (docs/04 §2): one row per `seg_id`, routes/modes for the map legend,
    plus AM/PM peak penalty (docs/04 §4: `pen_pm` is a per-segment tile property)."""
    if l0.empty:
        return pd.DataFrame(columns=["seg_id", "from_stop_id", "stop_id", "primary_mode", "modes", "routes", "n_obs_total", "pen_am", "pen_pm"])
    l0 = _tag_ok(l0)
    # Categorical "mode"/"route_short_name" columns confuse groupby.agg with a list-returning
    # lambda (pandas tries to cast the list result back to the original categorical dtype) -
    # decategorize first.
    plain = l0.assign(mode=l0["mode"].astype(str), route_short_name=l0.route_short_name.astype(str))
    g = plain.groupby("seg_id", observed=True)
    dim = g.agg(
        from_stop_id=("from_stop_id", "first"),
        stop_id=("stop_id", "first"),
        modes=("mode", lambda s: sorted(set(s))),
        routes=("route_short_name", lambda s: sorted(set(s.dropna()))),
        n_obs_total=("seg_time_s", "size"),
    )
    dim["primary_mode"] = g["mode"].agg(lambda s: s.value_counts().idxmax())
    dim = dim.reset_index()
    for band, col in (("am_peak", "pen_am"), ("pm_peak", "pen_pm")):
        pen = mr.peak_penalty_by_segment(l0, band)
        dim = dim.merge(pen.rename(col), left_on="seg_id", right_index=True, how="left")
    return dim


def run(city: str, from_date: str, to_date: str, edition: str) -> tuple[Path, Path]:
    l0 = reference_day_l0(city, from_date, to_date)
    stats = build_segment_stats(l0)
    dim = build_segments_dim(l0)
    out = DATA / "editions" / edition / city
    out.mkdir(parents=True, exist_ok=True)
    stats_path, dim_path = out / "segment_stats.parquet", out / "segments.parquet"
    stats.to_parquet(stats_path, index=False)
    dim.to_parquet(dim_path, index=False)
    return stats_path, dim_path
