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
def holidays(city: str) -> frozenset[str]:
    """Public holiday dates (ISO, docs/03 §2.2) for `city`, from `config/calendars/<city>.yaml`
    (built in M0 with the `holidays` PyPI package). School breaks (`school_breaks`) are not
    filled in yet (C4, 2026-09-27: left for before M3) so they are not excluded here."""
    path = CONFIG / "calendars" / f"{city}.yaml"
    if not path.exists():
        return frozenset()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return frozenset(h["date"] for h in data.get("public_holidays", []))


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


@lru_cache
def metrics_cfg() -> dict:
    """config/metrics.yaml: the only place for numbers (CLAUDE.md)."""
    return yaml.safe_load((CONFIG / "metrics.yaml").read_text(encoding="utf-8"))


@lru_cache
def attributions() -> dict:
    """config/attributions.yaml: per-city source attributions for the manifest (docs/licenses.md)."""
    return yaml.safe_load((CONFIG / "attributions.yaml").read_text(encoding="utf-8"))


@lru_cache
def school_breaks(city: str) -> frozenset[str]:
    """Weekday dates inside `school_breaks` of config/calendars/<city>.yaml. Entries are
    `{from: YYYY-MM-DD, to: YYYY-MM-DD}` (inclusive). Empty for now (C4): the anomaly detection in
    `ti.gate` deliberately does not depend on this being filled in."""
    import datetime as dt

    path = CONFIG / "calendars" / f"{city}.yaml"
    if not path.exists():
        return frozenset()
    out: set[str] = set()
    for b in yaml.safe_load(path.read_text(encoding="utf-8")).get("school_breaks") or []:
        d, end = dt.date.fromisoformat(str(b["from"])), dt.date.fromisoformat(str(b["to"]))
        while d <= end:
            out.add(d.isoformat())
            d += dt.timedelta(days=1)
    return frozenset(out)
