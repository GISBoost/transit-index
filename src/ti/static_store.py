"""Static GTFS dedup by SHA-256 (docs/decisions-needed.md §3): keep only routes/stops/trips/shapes
as Parquet under data/static/<sha256>/, drop the zip. Deduplicates across days/cities that
republish an unchanged file.
"""
from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd

from .paths import STATIC_STORE, fx, mr

TABLES = {
    "routes": ["route_id", "route_short_name", "route_type"],
    "stops": ["stop_id", "stop_lat", "stop_lon"],
    "trips": ["trip_id", "route_id", "service_id", "shape_id"],
    "shapes": ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"],
    # M2/W12 (docs/03 §4.3, R10: source = same-day static, not tidy): need stop_times for
    # scheduled departures per stop, plus calendar/calendar_dates to know which service_ids run
    # on a given date (stop_times alone doesn't say which day a trip operates).
    "stop_times": ["trip_id", "stop_id", "stop_sequence", "arrival_time", "departure_time"],
    "calendar": ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"],
    "calendar_dates": ["service_id", "date", "exception_type"],
    "frequencies": ["trip_id", "start_time", "end_time", "headway_secs"],  # optional (scripts/t17_service.py precedent)
}


def store(zip_path: Path) -> str:
    """Extracts the needed tables from `zip_path` into data/static/<sha256>/.

    Per-table idempotency (not just per-folder): if `TABLES` grows (M2 added stop_times/calendar/
    calendar_dates after some folders were already stored in M1), a re-`store()` call tops up only
    the missing tables instead of a no-op, so already-deduplicated statics don't need re-download
    from scratch to gain a new table.

    Returns the SHA-256 so callers can point a city-day at it without keeping the zip.
    """
    sha = fx.sha256(zip_path)
    dest = STATIC_STORE / sha
    existing = dest.exists()
    wanted = {t: cols for t, cols in TABLES.items() if not existing or not (dest / f"{t}.parquet").exists()}
    if existing and not wanted:
        return sha
    tmp = dest.with_name(dest.name + f".tmp{os.getpid()}")
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        z = zipfile.ZipFile(zip_path)
        names = set(z.namelist())
        for table, cols in wanted.items():
            fname = f"{table}.txt"
            if fname not in names:
                continue  # e.g. shapes.txt is optional (docs/04 §4.3: fall back to straight lines)
            df = pd.read_csv(z.open(fname), dtype=str, usecols=lambda c: c in cols)
            df.to_parquet(tmp / f"{table}.parquet", index=False)
        if existing:
            for p in tmp.iterdir():
                p.replace(dest / p.name)
            tmp.rmdir()
        else:
            tmp.replace(dest)
    except BaseException:
        # A crash or a hard kill mid-extraction (docs/progress.md M1 incident) must not leave a
        # `.tmp<pid>/` directory behind forever - clean it up and let the caller see the failure.
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return sha


def load(sha: str, city: str) -> tuple[dict, set[str]]:
    """(mode_of route_id, set of stop_ids inside the city polygon) for an already-stored static."""
    d = STATIC_STORE / sha
    routes = pd.read_parquet(d / "routes.parquet")
    mode_of = dict(zip(routes.route_id, routes.route_type.map(mr.mode_from_route_type)))
    stops = pd.read_parquet(d / "stops.parquet").dropna()
    import geopandas as gpd

    pts = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon.astype(float), stops.stop_lat.astype(float)), crs=4326)
    from .config import area_polygon

    inside = set(pts[pts.within(area_polygon(city))].stop_id)
    return mode_of, inside
