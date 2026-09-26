"""config/areas: provisional city polygons (D12) are present, valid and registered."""
from pathlib import Path

import geopandas as gpd
import yaml

ROOT = Path(__file__).resolve().parent.parent
AREAS = ROOT / "config" / "areas"


def test_registry_matches_files_and_cities():
    reg = yaml.safe_load((AREAS / "sources.yaml").read_text(encoding="utf-8"))
    cities = yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]
    files = {p.stem for p in AREAS.glob("*.geojson")}
    assert files == set(reg["cities"])
    assert files <= {c for c, v in cities.items() if v["tier"] != "out_of_scope"}
    candidates = {c for c, v in cities.items() if v["tier"] == "candidate"}
    assert candidates <= files  # every candidate city has a polygon


def test_polygons_are_valid_and_plausible():
    reg = yaml.safe_load((AREAS / "sources.yaml").read_text(encoding="utf-8"))["cities"]
    for city, meta in reg.items():
        g = gpd.read_file(AREAS / f"{city}.geojson")
        assert len(g) == 1 and g.geometry.iloc[0].is_valid, city
        assert g.geometry.iloc[0].geom_type in ("Polygon", "MultiPolygon")
        km2 = g.to_crs(3035).geometry.area.iloc[0] / 1e6
        assert abs(km2 - meta["area_km2"]) / meta["area_km2"] < 0.02, city
        assert meta["source"] in ("gisco", "osm"), city
