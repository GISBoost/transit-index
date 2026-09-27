"""Scheduled departures from same-day static GTFS, for W12 (docs/03 §4.3, R10: source = static,
not tidy). Separate from `obs.py` (L0, which comes from tidy): this reads `stop_times.txt` +
`calendar.txt`/`calendar_dates.txt` (which trips run on the date) + optional `frequencies.txt`
(headway-based trips, no explicit per-departure `stop_times` rows) of the static already
deduplicated by `static_store.py`. Mirrors `scripts/t17_service.py` (T17 sensitivity round),
reading from the persisted Parquet tables instead of re-opening the zip.
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from .paths import STATIC_STORE, mr

_WEEKDAY_COLS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def active_service_ids(calendar: pd.DataFrame, calendar_dates: pd.DataFrame, date: str) -> set[str]:
    """GTFS calendar resolution for one date: weekly pattern (`calendar.txt`) plus single-date
    add/remove exceptions (`calendar_dates.txt`, exception_type 1=added, 2=removed)."""
    d = dt.date.fromisoformat(date)
    ymd = d.strftime("%Y%m%d")
    active: set[str] = set()
    if len(calendar):
        col = _WEEKDAY_COLS[d.weekday()]
        in_service = pd.to_numeric(calendar[col], errors="coerce").fillna(0).astype(int) == 1
        in_range = (calendar.start_date <= ymd) & (calendar.end_date >= ymd)
        active |= set(calendar.loc[in_service & in_range, "service_id"])
    if len(calendar_dates):
        cd = calendar_dates[calendar_dates.date == ymd]
        active |= set(cd.loc[cd.exception_type == "1", "service_id"])
        active -= set(cd.loc[cd.exception_type == "2", "service_id"])
    return active


def _to_seconds(s: pd.Series) -> pd.Series:
    """GTFS time-of-day ('HH:MM:SS', hours may exceed 24 for past-midnight trips) -> seconds."""
    parts = s.fillna("").str.strip().str.split(":", expand=True)
    if parts.shape[1] < 3:
        return pd.Series(np.nan, index=s.index)
    h = pd.to_numeric(parts[0], errors="coerce")
    m = pd.to_numeric(parts[1], errors="coerce")
    sec = pd.to_numeric(parts[2], errors="coerce")
    return h * 3600 + m * 60 + sec


def departures(sha: str, date: str) -> pd.DataFrame:
    """Scheduled departures (stop_id, mode, hour) for trips active on `date`, bus+tram only
    (docs/03 §2.4: metro/rail are out of the index regardless of W12). The last stop of a trip
    is excluded (nobody boards there, so it is not a "departure")."""
    d = STATIC_STORE / sha
    trips = pd.read_parquet(d / "trips.parquet")
    routes = pd.read_parquet(d / "routes.parquet")
    stop_times = pd.read_parquet(d / "stop_times.parquet")
    calendar = pd.read_parquet(d / "calendar.parquet") if (d / "calendar.parquet").exists() else pd.DataFrame(columns=["service_id", *_WEEKDAY_COLS, "start_date", "end_date"])
    calendar_dates = pd.read_parquet(d / "calendar_dates.parquet") if (d / "calendar_dates.parquet").exists() else pd.DataFrame(columns=["service_id", "date", "exception_type"])

    active = active_service_ids(calendar, calendar_dates, date)
    mode_of = dict(zip(routes.route_id, routes.route_type.map(mr.mode_from_route_type)))
    t = trips[trips.service_id.isin(active)].copy()
    t["mode"] = t.route_id.map(mode_of)
    t = t[t["mode"].isin(("bus", "tram"))]

    st = stop_times[stop_times.trip_id.isin(set(t.trip_id))].copy()
    st["seq"] = pd.to_numeric(st.stop_sequence, errors="coerce")
    dep = st.departure_time.where(st.departure_time.notna() & (st.departure_time != ""), st.arrival_time)
    st["t_s"] = _to_seconds(dep)
    st = st[st.t_s.notna() & st.seq.notna()].sort_values(["trip_id", "seq"])
    st = st[st.seq != st.groupby("trip_id").seq.transform("max")]
    st = st.merge(t[["trip_id", "mode"]], on="trip_id", how="inner")

    freq_path = d / "frequencies.parquet"
    if freq_path.exists() and len(st):
        fq = pd.read_parquet(freq_path)
        fq = fq[fq.trip_id.isin(set(st.trip_id))]
        if len(fq):
            first = st.groupby("trip_id").t_s.transform("min")
            st["off_s"] = st.t_s - first
            frames = [st[~st.trip_id.isin(set(fq.trip_id))]]
            for r in fq.itertuples():
                a, b = _to_seconds(pd.Series([r.start_time])).iloc[0], _to_seconds(pd.Series([r.end_time])).iloc[0]
                h = pd.to_numeric(pd.Series([r.headway_secs]), errors="coerce").iloc[0]
                g = st[st.trip_id == r.trip_id]
                if not g.empty and h and h > 0 and pd.notna(a) and pd.notna(b):
                    for start in np.arange(a, b, h):
                        frames.append(g.assign(t_s=start + g.off_s.to_numpy()))
            st = pd.concat(frames, ignore_index=True)

    st["hour"] = ((st.t_s // 3600) % 24).astype("Int64")
    return st[["stop_id", "mode", "hour"]].dropna(subset=["hour"])
