"""Stage D (docs/04 §3, partial): L0/L1 -> city x mode x band headline values (docs/03 §3-4).

Writes a plain JSON report per city (`reports/m2/metrics/<city>.json`). The schema-bound outputs
(`ranking.json`, `summary.json`, quality gate, bootstrap, city status) are M3's `ti gate` job;
this stage only computes the numbers underneath, city by city, without cross-city gating.

Mode groups (D6): tram, bus (with trolleybuses), and "all" (bus+tram combined = the "street"
group used by the M1 golden test). Metro/rail are out of the index (`mode_from_route_type`).
"""
from __future__ import annotations

import json
import tempfile
from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

from . import aggregate, sched, static_store
from .config import candidate_cities
from .paths import CONFIG, DATA, REPORTS, fx, mr

CFG = yaml.safe_load((CONFIG / "metrics.yaml").read_text(encoding="utf-8"))
MODE_GROUPS = {"bus": ("bus",), "tram": ("tram",), "all": ("bus", "tram")}
M2_REPORTS = REPORTS.parent / "m2"


@lru_cache
def _ingest_log() -> dict[tuple[str, str], dict]:
    path = REPORTS / "ingest_report.jsonl"
    latest: dict[tuple[str, str], dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            latest[(r["city"], r["date"])] = r
    return latest


def static_sha_for(city: str, date: str) -> str | None:
    """Which static a city-day used. Known for free from the M1 ingest log for `status == "ok"`
    entries; a `cached` entry (M1's double-run/memory incident, docs/progress.md) didn't log it,
    so fall back to a fresh fetch (cheap: `static_store.store()` is a per-table no-op once the
    sha is already backfilled, C1)."""
    row = _ingest_log().get((city, date))
    if row and row.get("static_sha256"):
        return row["static_sha256"]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            zpath = Path(tmp) / "static.zip"
            if fx.fetch(fx.url_for(city, date, "static"), zpath) == "missing":
                return None
            return static_store.store(zpath)
    except OSError:
        return None


def _speed(sub: pd.DataFrame, time_col: str = "seg_time_s") -> dict:
    t = sub[sub[time_col] > 0]
    if t.empty:
        return {"n": 0, "v_kmh": None}
    v = float(t.seg_dist_m.sum() / t[time_col].sum() * 3.6)
    return {"n": int(len(t)), "v_kmh": round(v, 2)}


def _mode_metrics(l0_mode: pd.DataFrame, mode_name: str) -> dict:
    pk = CFG["peak_penalty"]
    out: dict = {"bands": {}}

    for cell_band, sub in aggregate.expand_bands(l0_mode).groupby("cell_band", observed=True):
        w1 = _speed(sub)
        w6_sched = _speed(sub, "sched_pass_time_s")
        band_out = {
            "w1_speed_kmh": w1["v_kmh"], "n_obs": w1["n"],
            "w2_min_per_10km": round(mr.minutes_per_10km(w1["v_kmh"]), 2) if w1["v_kmh"] else None,
            "w6_vs_schedule_pct": round((w1["v_kmh"] / w6_sched["v_kmh"] - 1.0) * 100.0, 2) if w1["v_kmh"] and w6_sched["v_kmh"] else None,
        }
        p10 = CFG["punctuality"]
        band_out["w10_punctuality"] = mr.punctuality_shares(sub, tuple(p10["on_time_s"]), p10["late_s"], p10["exclude_first_stop"])
        reg = CFG["regularity"]
        ewt, n_ewt = mr.ewt_minutes(sub, reg["frequent_headway_s"])
        band_out["w11_ewt_min"] = round(ewt, 3) if ewt == ewt else None  # NaN check
        band_out["w11_n_headways"] = n_ewt
        out["bands"][cell_band] = band_out

    for band in ("am_peak", "pm_peak"):
        pct, n, n_seg = mr.peak_penalty_pct(l0_mode, band, tuple(pk["ref_bands"]), pk["min_obs_per_segment"])
        out.setdefault("w3_peak_penalty_pct", {})[band] = {"pct": round(pct, 2) if pct == pct else None, "n_obs": n, "n_segments": n_seg}

    hourly = l0_mode[l0_mode.hour.between(6, 21).fillna(False)]
    w9 = {}
    for h, sub in hourly.groupby("hour", observed=True):
        w9[f"h{int(h):02d}"] = _speed(sub)["v_kmh"]
    out["w9_hourly_profile_kmh"] = w9

    return out


def _has_stop_times(sha: str) -> bool:
    return (DATA / "static" / sha / "stop_times.parquet").exists()


def _service_offer(city: str, dates: list[str], inside_by_sha: dict) -> dict:
    """W12 (docs/03 §4.3, R10): median-per-stop computed one reference day at a time (each day
    has its own static, so departures from different days must not be pooled before dividing by
    band hours - that double-counts days as if they were more stops per hour), then the median of
    those daily city values across the window (docs/03 §1: medians are the norm)."""
    svc = CFG["service"]
    band_hours = tuple(CFG["bands"][svc["band"]])
    per_mode_daily: dict[str, list[float]] = {"bus": [], "tram": []}
    n_days_used = 0
    for date in dates:
        sha = static_sha_for(city, date)
        if sha is None or not _has_stop_times(sha):
            continue
        dep = sched.departures(sha, date)
        if sha not in inside_by_sha:
            _, inside = static_store.load(sha, city)
            inside_by_sha[sha] = inside
        dep = dep[dep.stop_id.isin(inside_by_sha[sha])]
        n_days_used += 1
        for mode in per_mode_daily:
            v, _ = mr.service_offer_per_hour(dep[dep["mode"] == mode], band_hours, svc["min_stop_departures"])
            if v == v:
                per_mode_daily[mode].append(v)
    result = {"n_days": n_days_used}
    for mode, values in per_mode_daily.items():
        v = float(pd.Series(values).median()) if values else float("nan")
        result[mode] = {"w12_departures_per_hour": round(v, 2) if v == v else None, "n_days_with_value": len(values)}
    return result


def city_metrics(city: str, from_date: str, to_date: str) -> dict:
    l0 = aggregate.reference_day_l0(city, from_date, to_date)
    out = {
        "city": city, "window": [from_date, to_date],
        "n_days": int(l0.service_date.nunique()) if len(l0) else 0,
        "modes": {},
    }
    dates = sorted(l0.service_date.astype(str).unique()) if len(l0) else []
    inside_by_sha: dict[str, set] = {}
    offer = _service_offer(city, dates, inside_by_sha) if dates else {"n_days": 0}
    for mode_name, modes in MODE_GROUPS.items():
        sub = l0[l0["mode"].isin(modes)] if len(l0) else l0
        m = _mode_metrics(sub, mode_name)
        if mode_name in offer:
            m["w12_service_offer"] = offer[mode_name]
        out["modes"][mode_name] = m
    out["w12_n_days_with_static"] = offer["n_days"]
    return out


def run(cities: list[str] | None, from_date: str, to_date: str) -> None:
    cities = cities or candidate_cities()
    M2_REPORTS.mkdir(parents=True, exist_ok=True)
    out_dir = M2_REPORTS / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    for city in cities:
        m = city_metrics(city, from_date, to_date)
        (out_dir / f"{city}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        w1 = m["modes"]["all"]["bands"].get("all_day", {}).get("w1_speed_kmh")
        print(f"{city:12s} n_days={m['n_days']:3d}  W1(all,all_day)={w1}")
