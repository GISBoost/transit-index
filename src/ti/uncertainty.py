"""Bootstrap over days and indistinguishable cities (docs/03 §6 [PROPOSAL]).

Every city value is a ratio of sums over days (`ΣL/ΣT`, `ΣT_peak/ΣT_expected`, `Σon_time/Σn`,
pooled EWT), so the bootstrap works on per-day component sums: draw days with replacement, add up
the components, apply the same statistic. W12 (a median of daily values) has its own resampler.
Draw count, interval and seed come from `config/metrics.yaml` (`bootstrap`).
"""
from __future__ import annotations

import zlib
from typing import Callable

import numpy as np

from .config import metrics_cfg


def _rng(key: str) -> np.random.Generator:
    """Seeded per (config seed, key) so a result does not depend on the order cities are processed in."""
    return np.random.default_rng([metrics_cfg()["bootstrap"]["seed"], zlib.crc32(key.encode("utf-8"))])


def _interval(draws: np.ndarray) -> tuple[float, float] | tuple[None, None]:
    draws = draws[np.isfinite(draws)]
    if draws.size == 0:
        return None, None
    a = (1.0 - metrics_cfg()["bootstrap"]["interval"]) / 2.0
    lo, hi = np.quantile(draws, [a, 1.0 - a])
    return float(lo), float(hi)


def bootstrap_sums(components: np.ndarray, stat: Callable[[np.ndarray], np.ndarray], key: str) -> tuple[float | None, float | None]:
    """`components`: (n_days, k) per-day sums. `stat` maps a (B, k) array of resampled sums to B values.
    Fewer than 2 days: no interval (returns None, None)."""
    n_days = components.shape[0]
    if n_days < 2:
        return None, None
    b = metrics_cfg()["bootstrap"]["n_resamples"]
    idx = _rng(key).integers(0, n_days, size=(b, n_days))
    sums = components[idx].sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return _interval(np.asarray(stat(sums), dtype=float))


def bootstrap_median(values: np.ndarray, key: str) -> tuple[float | None, float | None]:
    """Interval for a median of daily values (W12)."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return None, None
    b = metrics_cfg()["bootstrap"]["n_resamples"]
    idx = _rng(key).integers(0, values.size, size=(b, values.size))
    return _interval(np.median(values[idx], axis=1))


def mark_indistinguishable(intervals: dict[str, tuple[float | None, float | None]]) -> dict[str, list[str]]:
    """City -> sorted list of cities whose interval overlaps its own. Cities without an interval
    are never claimed to be distinguishable or not (no entry claims anything about them)."""
    out = {c: [] for c in intervals}
    cities = sorted(c for c, (lo, hi) in intervals.items() if lo is not None and hi is not None)
    for i, a in enumerate(cities):
        for b in cities[i + 1:]:
            (alo, ahi), (blo, bhi) = intervals[a], intervals[b]
            if alo <= bhi and blo <= ahi:
                out[a].append(b)
                out[b].append(a)
    return {c: sorted(v) for c, v in out.items()}
