"""Pre-M1 test harness: published tidy (+ same-day static) -> narrow observation table ("L0-lite").

Throwaway precursor of the M1 `ti ingest`, written so the sensitivity tests (docs/10) can run before M1.
Reads data files only (never imports easy-OTP code).

    py scripts/t_l0.py build --from 2026-09-07 --to 2026-09-25 --workers 3
    -> data/l0/<city>/<date>.parquet   (tidy is downloaded to a temp file and deleted)
"""
from __future__ import annotations

import argparse
import io
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reference"))
import fetch_release_assets as fx  # noqa: E402
import metrics_reference as mr  # noqa: E402

L0 = ROOT / "data" / "l0"
CITIES = yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]
CANDIDATES = [c for c, v in CITIES.items() if v["tier"] == "candidate"]
USECOLS = [
    "service_date", "day_type", "route_id", "direction_id", "trip_id", "stop_sequence", "stop_id", "from_stop_id",
    "sched_dep", "obs_time", "obs_local", "delay_s", "seg_time_s", "seg_dist_m", "seg_status", "is_first_stop",
    "headway_s", "sched_headway_s", "headway_spans_outage", "headway_skips_vehicles", "trip_coverage",
    "service_date_plausible",
]


class RangeFile(io.RawIOBase):
    """Seekable read-only file over HTTP Range requests (enough for zipfile to read single members)."""

    BLOCK = 256 * 1024

    def __init__(self, url: str):
        self.url, self.pos, self.cache = url, 0, {}
        req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.url = r.geturl()  # signed final URL
            self.size = int(r.headers["Content-Range"].rsplit("/", 1)[1])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = {0: offset, 1: self.pos + offset, 2: self.size + offset}[whence]
        return self.pos

    def _block(self, i: int) -> bytes:
        if i not in self.cache:
            start = i * self.BLOCK
            end = min(start + self.BLOCK, self.size) - 1
            req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(req, timeout=120) as r:
                        self.cache[i] = r.read()
                    break
                except (urllib.error.URLError, TimeoutError):
                    if attempt == 3:
                        raise
        return self.cache[i]

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        out, end = [], self.pos + n
        while self.pos < end:
            i, off = divmod(self.pos, self.BLOCK)
            chunk = self._block(i)[off:off + (end - self.pos)]
            out.append(chunk)
            self.pos += len(chunk)
        return b"".join(out)

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def polygon(city: str):
    return gpd.read_file(ROOT / "config" / "areas" / f"{city}.geojson").geometry.union_all()


def static_maps(static, city: str):
    """(mode_of route_id, set of stop_ids inside the city polygon) from a static GTFS zip (path or file-like)."""
    z = zipfile.ZipFile(static)
    routes = pd.read_csv(z.open("routes.txt"), dtype=str)
    mode_of = dict(zip(routes.route_id, routes.route_type.map(mr.mode_from_route_type)))
    stops = pd.read_csv(z.open("stops.txt"), dtype={"stop_id": str}, usecols=["stop_id", "stop_lat", "stop_lon"]).dropna()
    pts = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat), crs=4326)
    return mode_of, set(pts[pts.within(polygon(city))].stop_id)


def tidy_to_l0(tidy, city: str, mode_of: dict, inside: set) -> pd.DataFrame:
    tz = CITIES[city]["timezone"]
    d = pd.read_csv(tidy, usecols=USECOLS, dtype={"route_id": str, "trip_id": str, "stop_id": str, "from_stop_id": str}, low_memory=False)
    out = pd.DataFrame({
        "date": d.service_date.astype("category"),
        "day_type": d.day_type.astype("category"),
        "route_id": d.route_id.astype("category"),
        "direction_id": pd.to_numeric(d.direction_id, errors="coerce").astype("Int8"),
        "trip_id": d.trip_id.astype("category"),
        "stop_sequence": d.stop_sequence.astype("int16"),
        "stop_id": d.stop_id.astype("category"),
        "from_stop_id": d.from_stop_id.astype("category"),
        "mode": d.route_id.map(mode_of).fillna("other").astype("category"),
        "seg_status": d.seg_status.astype("category"),
        "seg_dist_m": d.seg_dist_m.astype("float32"),
        "seg_time_s": d.seg_time_s.astype("float32"),
        "obs": d.obs_time.notna(),
        "hour": mr.hour_from_obs_local(d.obs_local.astype("string")).astype("Int8"),
        "delay_s": d.delay_s.astype("float32"),
        "is_first_stop": d.is_first_stop.astype(bool),
        "headway_s": d.headway_s.astype("float32"),
        "sched_headway_s": d.sched_headway_s.astype("float32"),
        "hs_outage": d.headway_spans_outage.astype(bool),
        "hs_skips": d.headway_skips_vehicles.fillna(0).astype("int16"),
        "trip_coverage": d.trip_coverage.astype("float32"),
        "plausible": d.service_date_plausible.fillna(True).astype(bool),
        "sched_hour": pd.to_datetime(d.sched_dep, utc=True, format="mixed").dt.tz_convert(tz).dt.hour.astype("Int8"),
    })
    out["in_area"] = d.stop_id.isin(inside).to_numpy()
    out["seg_in_area"] = (d.stop_id.isin(inside) & d.from_stop_id.isin(inside)).to_numpy()
    return out


def build_one(city: str, date: str) -> str:
    dest = L0 / city / f"{date}.parquet"
    if dest.exists():
        return f"{city} {date}: cached"
    tidy_url, static_url = fx.url_for(city, date, "tidy"), fx.url_for(city, date, "static")
    try:
        static = RangeFile(static_url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"{city} {date}: missing"
        raise
    mode_of, inside = static_maps(static, city)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.csv.gz"
        if fx.fetch(tidy_url, p) == "missing":
            return f"{city} {date}: missing tidy"
        l0 = tidy_to_l0(p, city, mode_of, inside)
    dest.parent.mkdir(parents=True, exist_ok=True)
    l0.to_parquet(dest, index=False, compression="zstd")
    return f"{city} {date}: {len(l0):,} rows"


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--from", dest="start", default="2026-09-07")
    b.add_argument("--to", dest="end", default="2026-09-25")
    b.add_argument("--cities", nargs="*", default=CANDIDATES)
    b.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    import datetime as dt
    days = list(fx.daterange(dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end), False))
    jobs = [(c, d) for c in a.cities for d in days]
    with ProcessPoolExecutor(a.workers) as ex:
        futs = {ex.submit(build_one, c, d): (c, d) for c, d in jobs}
        for f in as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # keep going; failures are listed and can be re-run (cached days are skipped)
                print(f"{futs[f][0]} {futs[f][1]}: ERROR {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    main()
