#!/usr/bin/env python3
"""M0 / D12: fetch city polygons from two sources and compare them.

    py scripts/m0_polygons.py fetch     # GISCO Urban Audit 2024 (local file) + OSM via Nominatim
    py scripts/m0_polygons.py compare   # area, overlap and centroid shift per city -> reports/m0/polygons_compare.csv

Sources
- GISCO: URAU_RG_100K_2024_4326_CITIES.geojson, download it into data/m0_polygons/ first (Eurostat, open licence).
- OSM: Nominatim search, administrative boundary relation (ODbL, attribution required). One request per second,
  identifying User-Agent, results cached in data/m0_polygons/osm/. Never run this in a loop against the service.

Raw polygons stay in data/ (gitignored). The chosen source is copied to config/areas/<city>.geojson after decision D12.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "m0_polygons"
GISCO_FILE = DATA / "URAU_RG_100K_2024_4326_CITIES.geojson"
UA = "GISBoost-transit-index-m0/0.1 (one-off polygon comparison)"
EQ_AREA = "EPSG:3035"

# city id -> (GISCO URAU_CODE, Nominatim query). Przemysl has no Urban Audit city; GZM is a metropolis (D8): skipped.
SOURCES = {
    "lodz": ("PL002C", "Łódź, Poland"), "warszawa": ("PL001C", "Warszawa, Poland"), "krakow": ("PL003C", "Kraków, Poland"),
    "gdansk": ("PL006C", "Gdańsk, Poland"), "poznan": ("PL005C", "Poznań, Poland"), "szczecin": ("PL007C", "Szczecin, Poland"),
    "prague": ("CZ001C", "Praha, Czechia"), "rome": ("IT001C", "Roma, Italy"), "turin": ("IT004C", "Torino, Italy"),
    "vilnius": ("LT001C", "Vilnius, Lithuania"), "sofia": ("BG001C", "Sofia, Bulgaria"), "bucharest": ("RO001C", "București, Romania"),
    "lisbon": ("PT001C", "Lisboa, Portugal"), "zagreb": ("HR001C", "Zagreb, Croatia"), "ljubljana": ("SI001C", "Ljubljana, Slovenia"),
    "nicosia": ("CY001C", "Nicosia, Cyprus"),
    "lublin": ("PL009C", "Lublin, Poland"), "rzeszow": ("PL015C", "Rzeszów, Poland"), "kielce": ("PL012C", "Kielce, Poland"),
    "radom": ("PL025C", "Radom, Poland"), "rybnik": ("PL060C", "Rybnik, Poland"), "elblag": ("PL063C", "Elbląg, Poland"),
    "suwalki": ("PL021C", "Suwałki, Poland"), "przemysl": (None, "Przemyśl, Poland"),
}


def fetch_osm(city: str, query: str) -> dict | None:
    cache = DATA / "osm" / f"{city}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    cache.parent.mkdir(parents=True, exist_ok=True)
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "jsonv2", "polygon_geojson": 1, "extratags": 1, "limit": 8})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        results = json.loads(r.read())
    time.sleep(1.1)  # Nominatim usage policy: max 1 request per second
    admin = [x for x in results if x.get("category") == "boundary" and x.get("type") == "administrative"
             and x.get("osm_type") == "relation" and x["geojson"]["type"] in ("Polygon", "MultiPolygon")]
    pick = admin[0] if admin else None
    out = None if pick is None else {
        "osm_id": pick["osm_id"], "display_name": pick["display_name"], "admin_level": pick.get("extratags", {}).get("admin_level"),
        "wikidata": pick.get("extratags", {}).get("wikidata"), "geometry": pick["geojson"],
        "n_admin_candidates": len(admin)}
    cache.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def cmd_fetch() -> None:
    gis = gpd.read_file(GISCO_FILE).set_index("URAU_CODE")
    for city, (code, query) in SOURCES.items():
        if code:
            (DATA / "gisco").mkdir(parents=True, exist_ok=True)
            gpd.GeoSeries([gis.loc[code, "geometry"]], crs=4326).to_file(DATA / "gisco" / f"{city}.geojson", driver="GeoJSON")
        osm = fetch_osm(city, query)
        print(f"{city:10s} gisco={code} osm={'relation ' + str(osm['osm_id']) + ' admin_level=' + str(osm['admin_level']) if osm else 'NONE'}")


def load_pair(city: str):
    code, _ = SOURCES[city]
    g = None
    if code:
        g = gpd.read_file(DATA / "gisco" / f"{city}.geojson").geometry.iloc[0]
    o = json.loads((DATA / "osm" / f"{city}.json").read_text(encoding="utf-8"))
    o = shape(o["geometry"]) if o else None
    return g, o


def cmd_compare() -> None:
    rows = []
    for city, (code, _) in SOURCES.items():
        g, o = load_pair(city)
        meta = json.loads((DATA / "osm" / f"{city}.json").read_text(encoding="utf-8")) or {}
        row = {"city": city, "gisco_code": code, "osm_relation": meta.get("osm_id"), "osm_admin_level": meta.get("admin_level")}
        gs = gpd.GeoSeries([g, o], crs=4326).to_crs(EQ_AREA) if g is not None and o is not None else None
        if gs is not None:
            ga, oa = gs.iloc[0], gs.iloc[1]
            inter = ga.intersection(oa).area
            row.update(gisco_km2=round(ga.area / 1e6, 1), osm_km2=round(oa.area / 1e6, 1), area_ratio_osm_to_gisco=round(oa.area / ga.area, 3),
                       iou=round(inter / ga.union(oa).area, 3), gisco_only_share=round(ga.difference(oa).area / ga.area, 3),
                       osm_only_share=round(oa.difference(ga).area / oa.area, 3))
        else:
            single = gpd.GeoSeries([g if g is not None else o], crs=4326).to_crs(EQ_AREA).iloc[0]
            row.update({("gisco_km2" if g is not None else "osm_km2"): round(single.area / 1e6, 1)})
        rows.append(row)
    df = pd.DataFrame(rows)
    out = ROOT / "reports" / "m0" / "polygons_compare.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "compare"])
    {"fetch": cmd_fetch, "compare": cmd_compare}[ap.parse_args().cmd]()
