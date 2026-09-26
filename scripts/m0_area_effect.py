#!/usr/bin/env python3
"""M0 / D12: how much does the choice of city polygon change the numbers?

For one day (default 2026-09-24) and every city with polygons, applies the W0 filter (both stops of a
segment inside the polygon) with each source and reports the share of observations kept and the
commercial speed for bus and tram. Uses only reference/metrics_reference.py definitions.

    py scripts/m0_area_effect.py --date 2026-09-24 --out reports/m0/area_effect.csv

Downloads tidy + static into data/raw (gitignored, reused by M1).
"""
import argparse
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reference"))
import fetch_release_assets as fx  # noqa: E402
import metrics_reference as mr  # noqa: E402

RAW = ROOT / "data" / "raw"
MIN_OBS = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))["inventory"]["min_obs_for_speed"]
POLY = ROOT / "data" / "m0_polygons"
USECOLS = ["route_id", "from_stop_id", "stop_id", "seg_dist_m", "seg_time_s", "seg_status"]


def polygon(city: str, source: str):
    if source == "gisco":
        f = POLY / "gisco" / f"{city}.geojson"
        return gpd.read_file(f).geometry.iloc[0] if f.exists() else None
    import json
    from shapely.geometry import shape
    f = POLY / "osm" / f"{city}.json"
    o = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    return shape(o["geometry"]) if o else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-24")
    ap.add_argument("--out", default=str(ROOT / "reports" / "m0" / "area_effect.csv"))
    a = ap.parse_args()
    cities = [c for c, v in yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"].items()
              if v["tier"] == "candidate"]
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for city in cities:
        paths = {}
        for kind in ("tidy", "static"):
            dest = RAW / fx.ASSET[kind].format(city=city, date=a.date)
            if fx.fetch(fx.url_for(city, a.date, kind), dest) == "missing":
                paths = None
                break
            paths[kind] = dest
        if paths is None:
            print(f"{city}: no release on {a.date}, skipped")
            continue
        z = zipfile.ZipFile(paths["static"])
        routes = pd.read_csv(z.open("routes.txt"), dtype=str)
        mode_of = dict(zip(routes.route_id, routes.route_type.map(mr.mode_from_route_type)))
        stops = pd.read_csv(z.open("stops.txt"), dtype={"stop_id": str}, usecols=["stop_id", "stop_lat", "stop_lon"]).dropna()
        stops_gdf = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat), crs=4326)
        d = pd.read_csv(paths["tidy"], usecols=USECOLS, dtype={"route_id": str, "from_stop_id": str, "stop_id": str}, low_memory=False)
        ok = mr.usable(d)
        ok = ok.assign(mode=ok.route_id.map(mode_of))
        ok = ok[ok["mode"].isin(["bus", "tram"])]
        base = {"city": city, "n_obs_all": len(ok)}
        variants = {"none": None, "gisco": polygon(city, "gisco"), "osm": polygon(city, "osm")}
        for name, poly in variants.items():
            if name != "none" and poly is None:
                continue
            if poly is None:
                keep = ok
            else:
                inside = set(stops_gdf[stops_gdf.within(poly)].stop_id)
                keep = ok[ok.from_stop_id.isin(inside) & ok.stop_id.isin(inside)]
            row = dict(base, source=name, obs_share=round(len(keep) / len(ok), 3))
            for m in ("bus", "tram"):
                g = keep[keep["mode"] == m]
                row[f"{m}_kmh"] = round(mr.commercial_speed_kmh(g), 2) if len(g) >= MIN_OBS else None
                row[f"{m}_n"] = len(g)
            rows.append(row)
        print(f"{city}: done")
    df = pd.DataFrame(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
