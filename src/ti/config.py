"""Config loaders: config/cities.yaml, config/city_defects.yaml, config/areas/*.geojson."""
from __future__ import annotations

from functools import lru_cache

import geopandas as gpd
import yaml

from .paths import CONFIG


@lru_cache
def cities() -> dict:
    return yaml.safe_load((CONFIG / "cities.yaml").read_text(encoding="utf-8"))["cities"]


def candidate_cities() -> list[str]:
    return sorted(c for c, v in cities().items() if v["tier"] == "candidate")


@lru_cache
def defects() -> list[dict]:
    return yaml.safe_load((CONFIG / "city_defects.yaml").read_text(encoding="utf-8"))["defects"]


@lru_cache
def area_polygon(city: str):
    return gpd.read_file(CONFIG / "areas" / f"{city}.geojson").geometry.union_all()


@lru_cache
def has_window_signal(city: str) -> bool:
    """A2 (docs/decisions-needed.md R7): whether the city's RT feed carries current_stop_sequence
    or stop_id on vehicle positions, so `match` can use FA-12's windowed search.

    This is a property of the operator's feed (constant across days, not measurable from tidy
    alone - it needs raw positions), already registered per city in city_defects.yaml from the
    T2 sensitivity round (docs/sensitivity-report.md §3.1). Cities not listed here are assumed to
    have the signal (the common case); a `no_stop_sequence` entry is the known exception.
    """
    return not any(d["city"] == city and d["id"] == "no_stop_sequence" for d in defects())
