"""tidy + same-day static -> L0 (docs/04 §2-3, stage B `ti obs`).

Filters to seg_status == "ok" (family_a's FA-13/14/18/20 already labelled rejections, docs/03
"Filtr jakości"); keeps every mode (bus/tram/other) tagged, so mode selection is a metric-time
decision, not baked into L0 (docs/04 §2 does not restrict L0 to bus/tram).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .paths import TIDY_COLUMNS, mr

USECOLS = [
    "city", "service_date", "day_type", "recording_date", "trip_id", "route_id", "route_short_name",
    "direction_id", "stop_sequence", "stop_id", "from_stop_id", "sched_arr", "obs_time", "obs_local",
    "delay_s", "seg_time_s", "seg_dist_m", "seg_status", "is_first_stop", "headway_s", "sched_headway_s",
    "headway_spans_outage", "headway_skips_vehicles",
]
DTYPES = {"city": str, "trip_id": str, "route_id": str, "route_short_name": str, "stop_id": str, "from_stop_id": str}


def validate_schema(tidy_path: Path) -> bool:
    header = pd.read_csv(tidy_path, nrows=0).columns.tolist()
    return header == TIDY_COLUMNS


def build_l0(tidy_path: Path, mode_of: dict, inside: set) -> tuple[pd.DataFrame, dict]:
    """Returns (L0 rows, report dict for this city-day)."""
    d = pd.read_csv(tidy_path, usecols=USECOLS, dtype=DTYPES, low_memory=False)
    d["sched_pass_time_s"] = mr.sched_pass_time_s(d)  # needs the full (unfiltered) stop sequence
    d["mode"] = d.route_id.map(mode_of).fillna("other")

    report = {
        "rows_tidy": int(len(d)),
        "trips": int(d.trip_id.nunique()),
        "crossing_rate": round(float(d.obs_time.notna().mean()), 4),
        "seg_status_share": {k: round(float(v), 4) for k, v in d.seg_status.value_counts(normalize=True).items()},
    }

    ok = mr.usable(d).copy()
    # Kept even when the golden test's row count depends on it (168 507 for Lodz 2026-09-24):
    # a malformed obs_local must not silently drop an otherwise-"ok" observation from L0.
    ok["hour"] = mr.hour_from_obs_local(ok.obs_local)
    ok["band"] = ok.hour.map(lambda h: mr.band_of_hour(int(h)) if pd.notna(h) else pd.NA)
    ok["seg_id"] = ok.from_stop_id + ">" + ok.stop_id
    ok["in_area"] = (ok.from_stop_id.isin(inside) & ok.stop_id.isin(inside)).to_numpy()

    l0 = pd.DataFrame({
        "city": ok.city.astype("category"),
        "service_date": ok.service_date.astype("category"),
        "day_type": ok.day_type.astype("category"),
        "trip_id": ok.trip_id.astype("category"),
        "route_id": ok.route_id.astype("category"),
        "route_short_name": ok.route_short_name.astype("category"),
        "mode": ok["mode"].astype("category"),
        "direction_id": pd.to_numeric(ok.direction_id, errors="coerce").astype("Int8"),
        "from_stop_id": ok.from_stop_id.astype("category"),
        "stop_id": ok.stop_id.astype("category"),
        "seg_id": ok.seg_id.astype("category"),
        "seg_dist_m": ok.seg_dist_m.astype("float32"),
        "seg_time_s": ok.seg_time_s.astype("float32"),
        "sched_pass_time_s": ok.sched_pass_time_s.astype("float32"),
        "obs_local": ok.obs_local.astype("string"),
        "hour": ok.hour.astype("Int8"),
        "band": ok.band.astype("category"),
        "delay_s": ok.delay_s.astype("float32"),
        "is_first_stop": ok.is_first_stop.astype(bool),
        "headway_s": ok.headway_s.astype("float32"),
        "sched_headway_s": ok.sched_headway_s.astype("float32"),
        "headway_spans_outage": ok.headway_spans_outage.astype(bool),
        "headway_skips_vehicles": ok.headway_skips_vehicles.fillna(0).astype("int16"),
        "in_area": ok["in_area"],
    })
    report["rows_ok"] = int(len(l0))
    report["ok_share"] = round(report["rows_ok"] / report["rows_tidy"], 4) if report["rows_tidy"] else 0.0
    report["share_of_obs_in_area"] = round(float(l0.in_area.mean()), 4) if len(l0) else 0.0
    return l0, report
