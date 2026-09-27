"""ADR-0004 (no easy-OTP pin): resolve which semantic epoch built a given tidy asset.

config/tidy_epochs.yaml lists the commits that changed what a tidy row means. We don't (and
can't, without querying easy-OTP's live history) know the exact commit `main` was at for an
arbitrary build time - only which epoch was in force, from the last semantic commit at or
before that time. That's what ADR-0004 actually needs recorded: whether two days' tidy tables
are comparable, not the literal SHA.
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache

import yaml

from .paths import CONFIG


@lru_cache
def _epochs() -> list[dict]:
    data = yaml.safe_load((CONFIG / "tidy_epochs.yaml").read_text(encoding="utf-8"))
    epochs = []
    for e in data["epochs"]:
        commit = next(c for c in data["commits_since_2026_08_01"] if e["starts_after_commit"].startswith(c["sha"]))
        epochs.append({"id": e["id"], "commit": e["starts_after_commit"], "start_date": commit["date"], "note": e["note"]})
    return sorted(epochs, key=lambda e: e["start_date"])


def resolve(build_time: dt.datetime | dt.date | str) -> dict:
    """Epoch in force at `build_time` (a tidy asset's Last-Modified). None if before every epoch."""
    if isinstance(build_time, str):
        build_date = dt.datetime.fromisoformat(build_time).date()
    elif isinstance(build_time, dt.datetime):
        build_date = build_time.date()
    else:
        build_date = build_time
    current = None
    for e in _epochs():
        if dt.date.fromisoformat(e["start_date"]) <= build_date:
            current = e
    if current is None:
        return {"epoch": None, "easy_otp_commit": None}
    return {"epoch": current["id"], "easy_otp_commit": current["commit"]}
