"""Shared paths and access to the ``reference/`` scratchpad modules (docs/04 §5)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
for _p in (ROOT / "reference",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import fetch_release_assets as fx  # noqa: E402
import metrics_reference as mr  # noqa: E402
from probe_release_data import TIDY_COLUMNS  # noqa: E402

CONFIG = ROOT / "config"
DATA = ROOT / "data"
STATIC_STORE = DATA / "static"
OBS = DATA / "obs"
RAW = DATA / "raw"
REPORTS = ROOT / "reports" / "m1"

__all__ = ["ROOT", "CONFIG", "DATA", "STATIC_STORE", "OBS", "RAW", "REPORTS", "fx", "mr", "TIDY_COLUMNS"]
