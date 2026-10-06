"""`ti gate`: day gate, anomalous-day detection, city status (docs/03 §6-§7, docs/05 §1a).

Inputs per city-day: the M1 ingest log (`reports/m1/ingest_report.jsonl`: crossing rate, `ok`
share, trip count, provenance), the M0 inventory stats for the two criteria the ingest log does not
carry (`service_date_plausible_share`, `band_hour_coverage`; `reports/m0/stats.jsonl`), and - when
`ti daystats` has been run where L0 exists - per-day recorded band coverage and city speed. Every
threshold comes from `config/metrics.yaml`; nothing numeric lives here.

Day reasons (first failing criterion wins, in this order): `holiday`, `school_break`, `no_tidy`,
`no_static`, `no_gate_stats`, `low_crossing_rate`, `low_ok_share`, `implausible_service_date`,
`recording_gap`, then the anomaly criteria `low_trip_count` and `speed_outlier`.
"""
from __future__ import annotations

import datetime as dt
import json
import statistics
from collections import Counter

import numpy as np

from .config import defects, holidays, metrics_cfg, school_breaks
from .paths import REPORTS, ROOT

NAMED_BANDS = ("am_peak", "midday", "pm_peak", "evening")


# ---- inputs ---------------------------------------------------------------------------------

def _jsonl(path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def load_ingest() -> dict[tuple[str, str], dict]:
    """Latest ingest record per (city, date), except that a later record without gate statistics
    (`cached`, logged after M1's double-run incident) never overrides an earlier one that has them."""
    out: dict[tuple[str, str], dict] = {}
    for r in _jsonl(REPORTS / "ingest_report.jsonl"):
        k = (r["city"], r["date"])
        if k in out and "crossing_rate" in out[k] and "crossing_rate" not in r:
            continue
        out[k] = r
    return out


def load_m0() -> dict[tuple[str, str], dict]:
    return {(r["city"], r["date"]): r for r in _jsonl(ROOT / "reports" / "m0" / "stats.jsonl") if r.get("status") == "ok"}


def weekdays(start: str, end: str) -> list[str]:
    d, last, out = dt.date.fromisoformat(start), dt.date.fromisoformat(end), []
    while d <= last:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def data_through(ingest: dict) -> str | None:
    dates = [d for (_, d) in ingest]
    return max(dates) if dates else None


# ---- day gate -------------------------------------------------------------------------------

def _band_min(date_rec: dict) -> float | None:
    cov = date_rec.get("band_coverage")
    return min(cov.values()) if cov else None


def day_record(city: str, date: str, ingest: dict, m0: dict, daystats_day: dict | None = None) -> dict:
    """Merge of everything known about a city-day. `daystats_day` (from L0) wins for band coverage
    and provides `speed_kmh`; M0 stats are the fallback for band coverage."""
    i, m = ingest.get((city, date), {}), m0.get((city, date), {})
    have_gate = "crossing_rate" in i
    src = i if have_gate else m
    band_cov = (daystats_day or {}).get("band_coverage") or m.get("band_hour_coverage")
    return {
        "date": date, "ingest_status": i.get("status"),
        "crossing_rate": src.get("crossing_rate"), "ok_share": src.get("ok_share"),
        "trips": src.get("trips"), "band_coverage": band_cov,
        "plausible": m.get("service_date_plausible_share"),
        "share_of_obs_in_area": i.get("share_of_obs_in_area"),
        "speed_kmh": (daystats_day or {}).get("speed_kmh"),
        "epoch": i.get("epoch"), "easy_otp_commit": i.get("easy_otp_commit"),
        "tidy_sha256": i.get("tidy_sha256") or m.get("tidy_sha256"), "static_sha256": i.get("static_sha256"),
        "tidy_last_modified": i.get("tidy_last_modified"),
    }


def first_failure(city: str, rec: dict, cfg: dict | None = None) -> tuple[str, str] | None:
    """(reason, detail) of the first failed day-gate criterion, or None."""
    g = (cfg or metrics_cfg())["day_gate"]
    d = rec["date"]
    if d in holidays(city):
        return "holiday", ""
    if d in school_breaks(city):
        return "school_break", ""
    if rec["ingest_status"] == "missing_tidy":
        return "no_tidy", ""
    if rec["ingest_status"] == "missing_static":
        return "no_static", ""
    if rec["ingest_status"] is None and rec["crossing_rate"] is None:
        return "no_tidy", "brak wpisu w logu ingestu"
    if rec["crossing_rate"] is None or rec["ok_share"] is None or rec["band_coverage"] is None:
        return "no_gate_stats", "brak crossing_rate, ok_share albo pokrycia pasm w logu ingestu, M0 i statystykach dziennych"
    if rec["crossing_rate"] < g["min_crossing_rate"]:
        return "low_crossing_rate", f"{rec['crossing_rate']:.3f} < {g['min_crossing_rate']}"
    if rec["ok_share"] < g["min_ok_share"]:
        return "low_ok_share", f"{rec['ok_share']:.3f} < {g['min_ok_share']}"
    if rec["plausible"] is not None and rec["plausible"] < g["min_plausible_service_date"]:
        return "implausible_service_date", f"{rec['plausible']:.3f} < {g['min_plausible_service_date']}"
    bm = _band_min(rec)
    if bm < g["min_band_recorded_share"]:
        worst = min(rec["band_coverage"], key=rec["band_coverage"].get)
        return "recording_gap", f"pasmo {worst}: {bm:.2f} < {g['min_band_recorded_share']}"
    return None


def flag_anomalies(days: list[dict], cfg: dict | None = None) -> dict:
    """Marks days that passed the day gate but are anomalous (docs/03 §7). Mutates `days`
    (`reason`/`detail` set, `valid` False) and returns run statistics for quality.json.

    1. `low_trip_count`: trips < `anomaly_min_trip_ratio` x median trips of the surviving days of the
       same `day_type` (the reference day is WEEKDAY only, so one group).
    2. `speed_outlier`: |daily city speed - median| > `speed_max_dev_share` x median, computed on the
       days that survived criterion 1; skipped when fewer than `min_days_for_median` days survive or no
       daily speeds are available. The MAD stays in the statistics as a diagnostic only (recording gaps are already `recording_gap` in the day gate).
    """
    cfg = cfg or metrics_cfg()
    an, g = cfg["anomaly"], cfg["day_gate"]
    stats: dict = {"trips_median": None, "speed_median": None, "speed_mad": None, "skipped": []}

    alive = [d for d in days if d["valid"]]
    trips = [d["trips"] for d in alive if d["trips"] is not None]
    if trips:
        med = statistics.median(trips)
        stats["trips_median"] = med
        for d in alive:
            if d["trips"] is not None and d["trips"] < g["anomaly_min_trip_ratio"] * med:
                d.update(valid=False, reason="low_trip_count", detail=f"{d['trips']} kursów < {g['anomaly_min_trip_ratio']} x mediana {med:g}")
    else:
        stats["skipped"].append("low_trip_count: brak liczby kursów")

    alive = [d for d in days if d["valid"]]
    speeds = [d["speed_kmh"] for d in alive if d["speed_kmh"] is not None]
    if len(speeds) < an["min_days_for_median"]:
        stats["skipped"].append(
            "speed_outlier: brak dziennych prędkości (uruchom `ti daystats` tam, gdzie jest L0)" if not speeds
            else f"speed_outlier: {len(speeds)} dni z prędkością przy min_days_for_median={an['min_days_for_median']}")
        return stats
    arr = np.array(speeds, dtype=float)
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    stats["speed_median"], stats["speed_mad"] = med, mad
    limit = an["speed_max_dev_share"] * med
    for d in alive:
        if d["speed_kmh"] is not None and abs(d["speed_kmh"] - med) > limit:
            d.update(valid=False, reason="speed_outlier",
                     detail=f"{d['speed_kmh']:.2f} km/h vs mediana {med:.2f} (limit +-{limit:.2f})")
    return stats


def evaluate_days(city: str, start: str, end: str, ingest: dict, m0: dict, daystats: dict | None = None,
                  cfg: dict | None = None) -> dict:
    """Day-level result for a city over the window. Days after the last logged ingest date are
    `not_yet_available` (they have not happened / been ingested), NOT invalid; a past weekday
    without a release is an invalid day (`no_tidy`)."""
    through = data_through(ingest)
    elapsed = [d for d in weekdays(start, end) if through and d <= through]
    not_yet = len([d for d in weekdays(start, end)]) - len(elapsed)
    days = []
    for date in elapsed:
        rec = day_record(city, date, ingest, m0, (daystats or {}).get(date))
        fail = first_failure(city, rec, cfg)
        rec.update(valid=fail is None, reason=fail[0] if fail else None, detail=fail[1] if fail else "")
        days.append(rec)
    anomaly = flag_anomalies(days, cfg)
    return {"days": days, "not_yet_available": not_yet, "anomaly": anomaly, "window_weekdays_elapsed": len(elapsed)}


# ---- city gate ------------------------------------------------------------------------------

def known_defects(city: str) -> list[dict]:
    return [{"id": d["id"], "action": d["action"], "detail": d["detail"]} for d in defects() if d["city"] == city]


def city_status(city: str, days_result: dict, coverage: float | None, has_area: bool, cfg: dict | None = None) -> tuple[str, list[str]]:
    """(status, reasons); reason codes are the enum of schemas/ranking.schema.json. The registry of
    feed defects has precedence over the computed gate (docs/03 §6): `action: exclude` -> excluded."""
    cfg = cfg or metrics_cfg()
    cg = cfg["city_gate"]
    reasons: list[str] = []
    for d in known_defects(city):
        if d["action"] == "exclude":
            reasons.append("no_trip_id" if d["id"] == "no_trip_id" else "feed_defect")
    if not has_area:
        reasons.append("no_area_definition")
    n_valid = sum(1 for d in days_result["days"] if d["valid"])
    if n_valid < cg["limited"]["min_valid_days"]:
        reasons.append("too_few_days")
        by_reason = Counter(d["reason"] for d in days_result["days"] if not d["valid"] and d["reason"] in ("low_crossing_rate", "recording_gap"))
        if by_reason:
            top = by_reason.most_common(1)[0][0]
            reasons.append("low_crossing_rate" if top == "low_crossing_rate" else "recording_window_gap")
    if coverage is None or coverage < cg["limited"]["min_network_coverage"]:
        reasons.append("low_network_coverage")
    if reasons:
        return "excluded", sorted(set(reasons))
    r = cg["ranked"]
    if n_valid >= r["min_valid_days"] and coverage >= r["min_network_coverage"]:
        return "ranked", []
    return "limited", []
