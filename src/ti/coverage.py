"""Network coverage and mode minimums from L1 (`segment_stats.parquet` + `segments.parquet`).

`network_coverage_share` = length of segments with quality `ok` / length of all segments in L1.
The denominator is every segment L1 has *any* observation for (its `all_day` row). L1 does not know
the scheduled network that was never observed, so this is an upper bound of the true coverage; it
is flagged as such in `quality.json`. A stricter denominator needs the same-day static
(`stop_times`), which `ti aggregate` does not carry.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import metrics_cfg
from .paths import DATA

MODES = ("street", "bus", "tram")
BANDS = ("all_day", "am_peak", "midday", "pm_peak", "evening")
NOTE = ("Górne oszacowanie: mianownik to odcinki, na których L1 ma jakąkolwiek obserwację; "
        "sieć rozkładowa bez obserwacji nie jest liczona.")


def _modes_of(mode: str) -> tuple[str, ...]:
    return ("bus", "tram") if mode == "street" else (mode,)


def load_l1(city: str, edition: str) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    d = DATA / "editions" / edition / city
    s, g = d / "segment_stats.parquet", d / "segments.parquet"
    if not (s.exists() and g.exists()):
        return None
    return pd.read_parquet(s), pd.read_parquet(g)


def compute(stats: pd.DataFrame, dim: pd.DataFrame) -> dict:
    """{mode: {"coverage": {band: share|None}, "n_routes", "n_ok_segments", "passes_mode_min"}}.
    Mode = `primary_mode` of the segment (the mode with most observations on it)."""
    mm = metrics_cfg()["mode_min"]
    length = stats[stats.band == "all_day"].set_index("seg_id").length_m.astype(float)
    pm = dim.set_index("seg_id").primary_mode.astype(str)
    out: dict = {}
    for mode in MODES:
        segs = pm.index[pm.isin(_modes_of(mode))]
        seg_len = length.reindex(segs).dropna()
        total = float(seg_len.sum())
        cov: dict[str, float | None] = {}
        for band in BANDS:
            b = stats[(stats.band == band) & (stats.seg_id.isin(seg_len.index))]
            ok_len = float(seg_len.reindex(b.loc[b.q == "ok", "seg_id"]).sum())
            cov[band] = round(ok_len / total, 4) if total > 0 else None
        ok_all = stats[(stats.band == "all_day") & (stats.q == "ok") & stats.seg_id.isin(seg_len.index)]
        routes: set[str] = set()
        for r in dim.loc[dim.seg_id.isin(segs), "routes"]:
            routes.update(str(x) for x in r)
        n_routes, n_ok = len(routes), int(len(ok_all))
        out[mode] = {"coverage": cov, "n_routes": n_routes, "n_ok_segments": n_ok,
                     "passes_mode_min": n_routes >= mm["routes"] and n_ok >= mm["segments"]}
    return out


def for_city(city: str, edition: str) -> dict | None:
    l1 = load_l1(city, edition)
    return compute(*l1) if l1 else None


def path_hint(city: str, edition: str) -> Path:
    return DATA / "editions" / edition / city
