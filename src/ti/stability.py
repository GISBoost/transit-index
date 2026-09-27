"""docs/decisions-needed.md §3: stop_id / seg_id stability day-to-day, for every candidate city
(M0 only checked Lodz; docs/04 §1 F9: 98.3-99.4% of Lodz's segment keys recur the next day).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import candidate_cities
from .paths import OBS, REPORTS


def compute(city: str) -> pd.DataFrame:
    files = sorted((OBS / city).glob("*.parquet")) if (OBS / city).exists() else []
    rows = []
    prev = None
    for f in files:
        d = pd.read_parquet(f, columns=["stop_id", "seg_id"])
        cur = {"date": f.stem, "stop_id": set(d.stop_id.astype(str).unique()), "seg_id": set(d.seg_id.astype(str).unique())}
        if prev is not None:
            rows.append({
                "city": city, "date": cur["date"], "prev_date": prev["date"],
                "stop_id_overlap_share": round(len(cur["stop_id"] & prev["stop_id"]) / len(cur["stop_id"]), 4) if cur["stop_id"] else 0.0,
                "seg_id_overlap_share": round(len(cur["seg_id"] & prev["seg_id"]) / len(cur["seg_id"]), 4) if cur["seg_id"] else 0.0,
                "n_stop_id": len(cur["stop_id"]), "n_seg_id": len(cur["seg_id"]),
            })
        prev = cur
    return pd.DataFrame(rows)


def run(cities: list[str] | None = None) -> Path:
    cities = cities or candidate_cities()
    out = pd.concat([compute(c) for c in cities], ignore_index=True) if cities else pd.DataFrame()
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "stability.csv"
    out.to_csv(path, index=False)
    if len(out):
        print(out.groupby("city")[["stop_id_overlap_share", "seg_id_overlap_share"]].median().round(3).to_string())
    print(f"written: {path}")
    return path
