"""T17 (docs/10): W12 service offer (scheduled departures per hour per stop) - source and aggregation variants.

For one weekday per city (static of that day): departures from stop_times of the services active that day
(calendar + calendar_dates, frequencies expanded), bus+tram, stops inside the city polygon, midday window 10-14.
Compares (a) the static as source with (b) the tidy table as source (only trips with >=1 matched observation),
and aggregation variants: median over stops (docs/03), mean, share of stops with >= 4 and >= 6 departures/hour.

    py scripts/t17_service.py [--date 2026-09-24]
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import t_l0  # noqa: E402
import t_metrics as tm  # noqa: E402

RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports" / "tests" / "sens"
import yaml  # noqa: E402

_H = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))["bands"]["midday"]
W0, W1 = min(_H) * 3600, (max(_H) + 1) * 3600  # midday band window from config bands.midday


def secs(t: pd.Series) -> pd.Series:
    if t.empty:
        return pd.Series(dtype=float)
    p = t.str.strip().str.split(":", expand=True).astype("float")
    return p[0] * 3600 + p[1] * 60 + p[2]


def active_services(z: zipfile.ZipFile, day: pd.Timestamp) -> set[str]:
    names = z.namelist()
    active: set[str] = set()
    if "calendar.txt" in names:
        c = pd.read_csv(z.open("calendar.txt"), dtype=str)
        c["s"], c["e"] = pd.to_datetime(c.start_date, format="%Y%m%d"), pd.to_datetime(c.end_date, format="%Y%m%d")
        col = day.day_name().lower()
        active = set(c[(c.s <= day) & (c.e >= day) & (c[col] == "1")].service_id)
    if "calendar_dates.txt" in names:
        d = pd.read_csv(z.open("calendar_dates.txt"), dtype=str)
        d = d[d.date == day.strftime("%Y%m%d")]
        active |= set(d[d.exception_type == "1"].service_id)
        active -= set(d[d.exception_type == "2"].service_id)
    return active


def departures_per_stop(static: Path, city: str, day: pd.Timestamp):
    z = zipfile.ZipFile(static)
    routes = pd.read_csv(z.open("routes.txt"), dtype=str)
    mode_of = dict(zip(routes.route_id, routes.route_type.map(t_l0.mr.mode_from_route_type)))
    trips = pd.read_csv(z.open("trips.txt"), dtype=str, usecols=["route_id", "service_id", "trip_id"])
    act = active_services(z, day)
    trips = trips[trips.service_id.isin(act)]
    print(f"  {city}: active services {len(act)}, trips {len(trips)}", flush=True)
    trips["mode"] = trips.route_id.map(mode_of)
    trips = trips[trips["mode"].isin(["bus", "tram"])]
    st = pd.read_csv(z.open("stop_times.txt"), dtype=str, usecols=["trip_id", "stop_id", "stop_sequence", "arrival_time", "departure_time"])
    st = st[st.trip_id.isin(set(trips.trip_id))]
    st["t"] = secs(st.departure_time.where(st.departure_time.notna() & (st.departure_time != ""), st.arrival_time))
    st["seq"] = st.stop_sequence.astype(int)
    st = st.sort_values(["trip_id", "seq"])
    st = st[st.t.notna()]
    st = st[st.seq != st.groupby("trip_id").seq.transform("max")]  # the last stop is not a departure
    if "frequencies.txt" in z.namelist():
        fq = pd.read_csv(z.open("frequencies.txt"), dtype=str)
        fq = fq[fq.trip_id.isin(set(st.trip_id))]
        if len(fq):
            first = st.groupby("trip_id").t.transform("min")
            st["off"] = st.t - first
            rows = []
            for r in fq.itertuples():
                a, b, h = secs(pd.Series([r.start_time])).iloc[0], secs(pd.Series([r.end_time])).iloc[0], float(r.headway_secs)
                g = st[st.trip_id == r.trip_id]
                for start in np.arange(a, b, h):
                    rows.append(g[["trip_id", "stop_id"]].assign(t=start + g.off.to_numpy()))
            st = pd.concat([st[~st.trip_id.isin(set(fq.trip_id))][["trip_id", "stop_id", "t"]]] + rows)
    st = st[(st.t >= W0) & (st.t < W1)]
    st = st.merge(trips[["trip_id", "mode"]], on="trip_id")
    stops = pd.read_csv(z.open("stops.txt"), dtype={"stop_id": str}, usecols=["stop_id", "stop_lat", "stop_lon"]).dropna()
    pts = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat), crs=4326)
    inside = set(pts[pts.within(t_l0.polygon(city))].stop_id)
    st = st[st.stop_id.isin(inside)]
    return st.groupby("stop_id").size() / ((W1 - W0) / 3600), st


def tidy_source(city: str, date: str) -> pd.Series:
    d = pd.read_parquet(tm.L0 / city / f"{date}.parquet", columns=["mode", "trip_id", "stop_id", "sched_hour", "in_area", "is_first_stop"])
    d = d[d["mode"].isin(["bus", "tram"]) & d.in_area & d.sched_hour.between(10, 13)]
    d = d.drop_duplicates(["trip_id", "stop_id"])
    return d.groupby("stop_id", observed=True).size() / 4.0


def agg(s: pd.Series) -> dict:
    return {"median": float(s.median()), "mean": float(s.mean()), "share_ge4": float((s >= 4).mean()), "share_ge6": float((s >= 6).mean()), "stops": int(len(s))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-24")
    a = ap.parse_args()
    day = pd.Timestamp(a.date)
    rows = []
    cand_days = [a.date, "2026-09-23", "2026-09-22", "2026-09-21", "2026-09-18", "2026-09-16", "2026-09-15"]
    for city in t_l0.CANDIDATES:
        res_ = None
        for date in cand_days:
            f = RAW / f"{city}_static_gtfs_{date}.zip"
            if not f.exists() and t_l0.fx.fetch(t_l0.fx.url_for(city, date, "static"), f) == "missing":
                continue
            s, st = departures_per_stop(f, city, pd.Timestamp(date))
            if len(s):
                res_ = (date, s, st)
                break
            print(f"  {city} {date}: static has no service on that day, trying an earlier day", flush=True)
        if res_ is None:
            print(city, "no usable static"); continue
        date, s, st = res_
        row = {"city": city, "date": date, "static_dep_total": float(s.sum() * 4)}
        for k, v in agg(s).items():
            row[f"static_{k}"] = v
        try:
            t = tidy_source(city, date)
            for k, v in agg(t).items():
                row[f"tidy_{k}"] = v
            row["tidy_dep_total"] = float(t.sum() * 4)
            row["tidy_over_static_departures"] = row["tidy_dep_total"] / row["static_dep_total"]
        except FileNotFoundError:
            pass
        rows.append(row)
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "t17_service_by_city.csv", index=False)
    res = []
    for k in ("median", "mean", "share_ge4", "share_ge6"):
        res.append({"variant": f"static {k} vs static median", "rho": tm.spearman(df[f"static_{k}"], df["static_median"]) if hasattr(tm, "spearman") else np.nan})
    for k in ("median", "share_ge4"):
        if f"tidy_{k}" in df:
            res.append({"variant": f"tidy {k} vs static {k}", "rho": tm.spearman(df[f"tidy_{k}"], df[f"static_{k}"])})
    r = pd.DataFrame(res)
    r.to_csv(OUT / "t17_service_variants.csv", index=False)
    print(r.round(3).to_string(index=False))
    print("tidy/static departures: median", df.tidy_over_static_departures.median().round(3), "min", df.tidy_over_static_departures.min().round(3))


if __name__ == "__main__":
    main()
