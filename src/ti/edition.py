"""Edition outputs of `ti gate` (docs/03 §6, docs/04 §2 L2/L3, docs/05 §3):
`ranking.json`, `<city>/summary.json`, `<city>/hourly.json`, `<city>/lines.csv`, `quality.json`,
`manifest.json`, all under `data/editions/<edition>/` and validated against `schemas/`.

City values are ratios of sums over the *valid* days (`ti.gate`), taken from `day_stats`
(`ti.daystats`); the uncertainty is the day bootstrap of `ti.uncertainty`. No numeric threshold is
defined here: everything comes from `config/metrics.yaml`.
"""
from __future__ import annotations

import csv
import datetime as dt
import email.utils
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from jsonschema import Draft202012Validator

from . import coverage as cov_mod
from . import daystats, gate, uncertainty
from .config import attributions, candidate_cities, cities, metrics_cfg
from .paths import CONFIG, DATA, REPORTS, ROOT

SCHEMAS = ROOT / "schemas"
BANDS = cov_mod.BANDS
MODE_LABEL = {"street": "autobusy i tramwaje", "bus": "autobusy", "tram": "tramwaje"}
DAY_TYPE = "WEEKDAY"

# dimension -> (metric name, unit, sort, bands, modes)
def _dimensions() -> dict:
    svc_band = metrics_cfg()["service"]["band"]
    return {
        "speed": ("Prędkość komunikacyjna", "km/h", "desc", BANDS, ("street", "bus", "tram")),
        "peak_penalty": ("Kara szczytu", "%", "asc", ("am_peak", "pm_peak"), ("street", "bus", "tram")),
        "punctuality": ("Punktualność (udział przyjazdów o czasie)", "%", "desc", BANDS, ("street", "bus", "tram")),
        "regularity": ("Regularność (nadmiar czasu oczekiwania, EWT)", "min", "asc", BANDS, ("street", "bus", "tram")),
        "service": ("Oferta rozkładowa (odjazdy na godzinę, według rozkładu)", "dep/h", "desc", (svc_band,), ("bus", "tram")),
    }


# ---- values from per-day components ------------------------------------------------------------

_SPEED = ["dist_m", "time_s", "n"]
_PUNCT = ["pu_n", "pu_on", "pu_early", "pu_late", "pu_vlate"]
_REG = ["hw_n", "hw_sum", "hw_sum2", "shw_sum", "shw_sum2"]
_W3 = ["w3_t_s", "w3_exp_s", "n"]


def _stat(dim: str):
    """(component columns, statistic over a (B, k) array of summed components, n column index)."""
    if dim == "speed":
        return _SPEED, (lambda s: s[:, 0] / s[:, 1] * 3.6), 2
    if dim == "peak_penalty":
        return _W3, (lambda s: (s[:, 0] / s[:, 1] - 1.0) * 100.0), 2
    if dim == "punctuality":
        return _PUNCT, (lambda s: s[:, 1] / s[:, 0] * 100.0), 0
    if dim == "regularity":
        return _REG, (lambda s: (s[:, 2] / (2 * s[:, 1]) - s[:, 4] / (2 * s[:, 3])) / 60.0), 0
    raise KeyError(dim)


def _cell(ds: pd.DataFrame, dates: list[str], mode: str, kind: str, key: str, cols: list[str]) -> np.ndarray:
    """(n_valid_days, len(cols)) matrix of per-day sums; a valid day with no rows is a zero row."""
    sub = ds[(ds["mode"] == mode) & (ds.kind == kind) & (ds.key == key) & ds.date.isin(dates)]
    return sub.set_index("date")[cols].fillna(0.0).reindex(dates).fillna(0.0).to_numpy(dtype=float)


def dimension_value(ds: pd.DataFrame, dates: list[str], city: str, dim: str, mode: str, band: str) -> dict | None:
    """{value, ci_low, ci_high, n_obs, n_days} for one city x dimension x mode x band, or None."""
    key = f"{city}|{dim}|{mode}|{band}"
    if dim == "service":
        sub = ds[(ds["mode"] == mode) & (ds.kind == "w12") & (ds.key == band) & ds.date.isin(dates)]
        vals = sub.value.dropna().to_numpy(dtype=float)
        if vals.size == 0:
            return None
        lo, hi = uncertainty.bootstrap_median(vals, key)
        return {"value": float(np.median(vals)), "ci_low": lo, "ci_high": hi, "n_obs": int(sub.n.fillna(0).sum()), "n_days": int(vals.size)}
    cols, stat, n_idx = _stat(dim)
    kind, k = ("w3", band) if dim == "peak_penalty" else ("band", band)
    comp = _cell(ds, dates, mode, kind, k, cols)
    total = comp.sum(axis=0, keepdims=True)
    if total[0, n_idx] <= 0:
        return None
    with np.errstate(divide="ignore", invalid="ignore"):
        value = float(stat(total)[0])
    if not np.isfinite(value):
        return None
    lo, hi = uncertainty.bootstrap_sums(comp, stat, key)
    return {"value": value, "ci_low": lo, "ci_high": hi, "n_obs": int(total[0, n_idx]), "n_days": int((comp[:, n_idx] > 0).sum())}


# ---- per city ---------------------------------------------------------------------------------

def _minmedmax(values: list[float]) -> dict | None:
    v = [x for x in values if x is not None]
    return {"min": min(v), "median": float(np.median(v)), "max": max(v)} if v else None


def build_city(city: str, edition: str, start: str, end: str, ingest: dict, m0: dict) -> dict:
    """Everything the writers need for one city."""
    ds = daystats.load(city, edition)
    days = gate.evaluate_days(city, start, end, ingest, m0, daystats.gate_view(ds))
    l1 = cov_mod.for_city(city, edition)
    has_area = (CONFIG / "areas" / f"{city}.geojson").exists()
    cov_all = l1["street"]["coverage"]["all_day"] if l1 else None
    status, reasons = gate.city_status(city, days, cov_all, has_area)
    return {"city": city, "ds": ds, "days": days, "l1": l1, "coverage": cov_all, "status": status, "reasons": reasons,
            "valid_dates": [d["date"] for d in days["days"] if d["valid"]]}


def _entry_notes(cfg: dict, c: dict, dim: str, mode: str, v: dict, entry_status: str) -> list[str]:
    cg, dg = cfg["city_gate"], cfg["dimension_gate"]
    notes = []
    n_valid = len(c["valid_dates"])
    if n_valid < cg["ranked"]["min_valid_days"]:
        notes.append(f"Mniej niż {cg['ranked']['min_valid_days']} dni ważnych w oknie edycji ({n_valid})")
    if c["coverage"] is not None and c["coverage"] < cg["ranked"]["min_network_coverage"]:
        notes.append(f"Pokrycie sieci poniżej {cg['ranked']['min_network_coverage']:.0%}")
    if v["n_obs"] < dg["min_obs"].get(dim, 0):
        notes.append(f"Mała próba w tym wymiarze (n < {dg['min_obs'][dim]})")
    if dim == "service":
        notes.append("Według rozkładu jazdy, nie wykonania kursów")
        if mode == "tram":
            notes.append("Niepewność metodyczna rankingu oferty tramwajowej (ADR-0006)")
    if dim == "peak_penalty":
        notes.append("Ranking poranny jest mniej stabilny niż popołudniowy (docs/sensitivity-report.md)")
    for d in gate.known_defects(c["city"]):
        if d["action"] != "seg_status_filter":
            notes.append(f"Znana wada źródła: {d['id']}")
    epochs = {x["epoch"] for x in c["days"]["days"] if x["valid"] and x["epoch"]}
    if len(epochs) > 1:
        notes.append("Dni z różnych epok metody tidy (ADR-0004)")
    return notes


ID_NAME = {"speed": "speed", "peak_penalty": "peak_penalty", "punctuality": "punctuality", "regularity": "ewt", "service": "frequency"}


def ranking_id(dim: str, mode: str, band: str) -> str:
    """`<mode>_<dimension>` (pattern of schemas/ranking.schema.json), plus `_<band>` for every band
    except the default view (`all_day`; W12 has its single configured band, so no suffix)."""
    return f"{mode}_{ID_NAME[dim]}" + ("" if band == "all_day" or dim == "service" else f"_{band}")


def build_rankings(results: dict[str, dict], edition: str, cfg: dict | None = None) -> tuple[list[dict], dict[str, dict]]:
    """(rankings, per-city dimension summary). Cities excluded by the gate, or lacking `day_stats`,
    have no entries; a mode below `mode_min` gets no entry for that city."""
    cfg = cfg or metrics_cfg()
    dg = cfg["dimension_gate"]
    disp = {c: v["display_name"] for c, v in cities().items()}
    rankings: list[dict] = []
    dimstat: dict[str, dict] = {c: {} for c in results}
    for dim, (name, unit, sort, bands, modes) in _dimensions().items():
        for mode in modes:
            for band in bands:
                vals: dict[str, dict] = {}
                for city, c in results.items():
                    if c["status"] == "excluded" or c["ds"] is None or not c["valid_dates"]:
                        continue
                    if c["l1"] and not c["l1"][mode]["passes_mode_min"]:
                        continue
                    v = dimension_value(c["ds"], c["valid_dates"], city, dim, mode, band)
                    if v is not None:
                        vals[city] = v
                if not vals:
                    continue
                ind = uncertainty.mark_indistinguishable({k: (v["ci_low"], v["ci_high"]) for k, v in vals.items()})
                ordered = sorted(vals, key=lambda k: (vals[k]["value"] * (-1 if sort == "desc" else 1), k))
                entries = []
                for rank, city in enumerate(ordered, 1):
                    v, c = vals[city], results[city]
                    small = v["n_obs"] < dg["min_obs"].get(dim, 0) or v["n_days"] < dg.get("min_days", {}).get(dim, 0)
                    status = "ranked" if c["status"] == "ranked" and not small else "limited"
                    notes = _entry_notes(cfg, c, dim, mode, v, status)
                    if ind[city]:
                        notes.append(f"Nierozróżnialne od: {', '.join(disp[x] for x in ind[city])} (przedziały {cfg['bootstrap']['interval']:.0%} się nakładają)")
                    if v["ci_low"] is None:
                        notes.append("Brak przedziału niepewności (mniej niż 2 dni)")
                    entries.append({
                        "rank": rank, "city": city, "display_name": disp[city], "value": round(v["value"], 3),
                        "ci_low": None if v["ci_low"] is None else round(v["ci_low"], 3),
                        "ci_high": None if v["ci_high"] is None else round(v["ci_high"], 3),
                        "indistinguishable_with": ind[city], "delta_vs_previous_edition": None, "median_stop_spacing_m": None,
                        "n_days": v["n_days"], "n_obs": v["n_obs"], "network_coverage_share": c["l1"][mode]["coverage"]["all_day"] if c["l1"] else 0.0,
                        "status": status, "notes": notes, "area_definition": "polygon",
                    })
                    prev = dimstat[city].get(dim)
                    dimstat[city][dim] = "ranked" if status == "ranked" or prev == "ranked" else "limited"
                rankings.append({
                    "id": ranking_id(dim, mode, band), "dimension": dim, "mode": mode,
                    "metric": f"{name}, {MODE_LABEL[mode]}", "unit": unit, "band": band, "day_type": DAY_TYPE, "sort": sort,
                    "uncertainty": {"method": "bootstrap po dniach", "n_resamples": cfg["bootstrap"]["n_resamples"], "interval": cfg["bootstrap"]["interval"]},
                    "entries": entries,
                })
    return rankings, dimstat


def build_summary(c: dict, edition: str, method_version: str) -> dict:
    cfg = metrics_cfg()
    city = c["city"]
    valid = [d for d in c["days"]["days"] if d["valid"]]
    modes: dict = {}
    ds = c["ds"]
    if ds is not None and c["valid_dates"] and c["l1"]:
        for mode in ("street", "bus", "tram"):
            if not c["l1"][mode]["passes_mode_min"]:
                continue
            bands = {}
            for band in BANDS:
                v = dimension_value(ds, c["valid_dates"], city, "speed", mode, band)
                bands[band] = {"speed_kmh": None if v is None else round(v["value"], 2), "n_obs": 0 if v is None else v["n_obs"],
                               "coverage_share": c["l1"][mode]["coverage"][band] or 0.0}
            head = dimension_value(ds, c["valid_dates"], city, "speed", mode, "all_day")
            if head is None:
                continue
            m = {"speed_kmh": round(head["value"], 2), "minutes_per_10km": round(600.0 / head["value"], 2), "n_obs": head["n_obs"],
                 "n_segments": c["l1"][mode]["n_ok_segments"], "network_coverage_share": c["l1"][mode]["coverage"]["all_day"] or 0.0, "bands": bands}
            for band, key in (("am_peak", "peak_penalty_am_pct"), ("pm_peak", "peak_penalty_pm_pct")):
                v = dimension_value(ds, c["valid_dates"], city, "peak_penalty", mode, band)
                m[key] = None if v is None else round(v["value"], 2)
            v = dimension_value(ds, c["valid_dates"], city, "regularity", mode, "all_day")
            m["ewt_min"] = None if v is None else round(v["value"], 3)
            if mode != "street":
                v = dimension_value(ds, c["valid_dates"], city, "service", mode, cfg["service"]["band"])
                m["service_dep_per_hour"] = None if v is None else round(v["value"], 2)
            cols = _PUNCT
            tot = _cell(ds, c["valid_dates"], mode, "band", "all_day", cols).sum(axis=0)
            m["punctuality_share"] = None if tot[0] <= 0 else {
                "early": float(tot[2] / tot[0]), "on_time": float(tot[1] / tot[0]), "late": float(tot[3] / tot[0]), "very_late": float(tot[4] / tot[0])}
            modes[mode] = m
    gs = [d for d in valid]
    defects = [d["id"] for d in gate.known_defects(city)]
    return {
        "city": city, "display_name": cities()[city]["display_name"], "edition": edition, "method_version": method_version,
        "status": c["status"],
        "days": {"n_valid": len(valid), "first": valid[0]["date"] if valid else "", "last": valid[-1]["date"] if valid else "",
                 "excluded_days": [{"date": d["date"], "reason": d["reason"]} for d in c["days"]["days"] if not d["valid"]]},
        "modes": modes,
        "quality": {"crossing_rate": float(np.median([d["crossing_rate"] for d in gs])) if gs else 0.0,
                    "recorded_share_of_window": (len(valid) / c["days"]["window_weekdays_elapsed"]) if c["days"]["window_weekdays_elapsed"] else None,
                    "known_defects": defects,
                    "optimistic_bias_note": "Pojazd znikający z feedu nie wnosi obserwacji; wyniki opisują zrekonstruowane przejazdy, nie pełny pomiar (docs/03 §8)."},
        "area": {"definition": "polygon", "source": _area_source(city),
                 "share_of_obs_in_area": float(np.median([d["share_of_obs_in_area"] for d in gs if d["share_of_obs_in_area"] is not None])) if any(d["share_of_obs_in_area"] is not None for d in gs) else None,
                 "n_stops_in_area": None},
    }


def _area_source(city: str) -> str:
    import yaml

    src = yaml.safe_load((CONFIG / "areas" / "sources.yaml").read_text(encoding="utf-8"))
    entry = src.get("cities", {}).get(city, {})
    return {"gisco": "Eurostat GISCO Urban Audit 2024", "osm": "OpenStreetMap contributors (ODbL)"}.get(entry.get("source", src["source_default"]), "unknown")


def build_hourly(c: dict, edition: str, method_version: str) -> dict:
    modes: dict = {}
    ds = c["ds"]
    if ds is not None and c["valid_dates"]:
        for mode in ("street", "bus", "tram"):
            if c["l1"] and not c["l1"][mode]["passes_mode_min"]:
                continue
            rows = []
            for h in range(6, 22):
                comp = _cell(ds, c["valid_dates"], mode, "hour", f"h{h:02d}", _SPEED).sum(axis=0)
                rows.append({"hour": h, "speed_kmh": round(float(comp[0] / comp[1] * 3.6), 2) if comp[1] > 0 else None, "n_obs": int(comp[2])})
            if any(r["n_obs"] for r in rows):
                modes[mode] = rows
    return {"city": c["city"], "edition": edition, "method_version": method_version, "day_type": DAY_TYPE, "unit": "km/h", "modes": modes}


LINES_HEADER = ["city", "mode", "route", "n_days", "n_obs", "speed_kmh", "punctuality_on_time_pct", "n_punctuality_obs", "ewt_min", "n_headways", "status"]


def build_lines(c: dict) -> list[list]:
    """One row per (mode, route_short_name) over the valid days. `status` = `thin` when n_obs is below
    the speed floor of `dimension_gate` (a line is a small sample by nature), else `ok`."""
    ds = c["ds"]
    if ds is None or not c["valid_dates"]:
        return []
    floor = metrics_cfg()["dimension_gate"]["min_obs"]["speed"]
    sub = ds[(ds.kind == "line") & ds.date.isin(c["valid_dates"])]
    rows = []
    for (mode, key), g in sub.groupby(["mode", "key"]):
        s = g[["dist_m", "time_s", "n", "pu_n", "pu_on", "hw_n", "hw_sum", "hw_sum2", "shw_sum", "shw_sum2"]].fillna(0).sum()
        speed = s.dist_m / s.time_s * 3.6 if s.time_s > 0 else None
        pun = s.pu_on / s.pu_n * 100.0 if s.pu_n > 0 else None
        ewt = (s.hw_sum2 / (2 * s.hw_sum) - s.shw_sum2 / (2 * s.shw_sum)) / 60.0 if s.hw_sum > 0 and s.shw_sum > 0 else None
        rows.append([c["city"], mode, key, int(g.date.nunique()), int(s.n), _r(speed, 2), _r(pun, 1), int(s.pu_n), _r(ewt, 3), int(s.hw_n),
                     "ok" if s.n >= floor else "thin"])
    return rows


def _r(x, nd):
    return "" if x is None or not np.isfinite(x) else round(float(x), nd)


# ---- quality / manifest -----------------------------------------------------------------------

def build_quality(results: dict[str, dict], dimstat: dict, edition: str, method_version: str, start: str, end: str, through: str, now: str) -> dict:
    cfg = metrics_cfg()
    out_cities = []
    anomaly = {}
    for city, c in sorted(results.items()):
        days = c["days"]["days"]
        skipped = list(c["days"]["anomaly"]["skipped"])
        if c["ds"] is None:
            skipped.append("wartości wymiarów: brak day_stats (uruchom `ti daystats` tam, gdzie jest L0); ranking i podsumowanie bez wartości")
        if c["l1"] is None:
            skipped.append("pokrycie sieci i tryby: brak L1 (uruchom `ti aggregate`)")
        no_plaus = [d["date"] for d in days if d["plausible"] is None and d["valid"]]
        if no_plaus:
            skipped.append(f"wiarygodność service_date niesprawdzona dla {len(no_plaus)} dni (brak w statystykach M0)")
        valid = [d for d in days if d["valid"]]
        out_cities.append({
            "city": city, "status": c["status"], "reasons": c["reasons"],
            "days": {"window_weekdays_elapsed": c["days"]["window_weekdays_elapsed"], "n_valid": len(valid),
                     "not_yet_available": c["days"]["not_yet_available"],
                     "excluded": [{"date": d["date"], "reason": d["reason"], **({"detail": d["detail"]} if d["detail"] else {})} for d in days if not d["valid"]],
                     "epochs": dict(Counter(d["epoch"] or "unknown" for d in valid))},
            "gate_stats": {"crossing_rate": _minmedmax([d["crossing_rate"] for d in days if d["crossing_rate"] is not None]) if days else None,
                           "ok_share": _minmedmax([d["ok_share"] for d in days if d["ok_share"] is not None]) if days else None,
                           "share_of_obs_in_area": _minmedmax([d["share_of_obs_in_area"] for d in days if d["share_of_obs_in_area"] is not None]) if days else None},
            "network_coverage_share": c["coverage"], "network_coverage_note": cov_mod.NOTE,
            "modes": {m: {"n_routes": v["n_routes"], "n_ok_segments": v["n_ok_segments"], "passes_mode_min": v["passes_mode_min"]} for m, v in (c["l1"] or {}).items()},
            "dimensions": {dim: dimstat[city].get(dim, "none") for dim in _dimensions()},
            "known_defects": gate.known_defects(city), "criteria_skipped": skipped,
        })
        anomaly[city] = {k: c["days"]["anomaly"][k] for k in ("trips_median", "speed_median", "speed_mad")}
    return {"edition": edition, "method_version": method_version, "generated_at": now,
            "window": {"from": start, "to": end, "data_through": through},
            "thresholds": {k: cfg[k] for k in ("day_gate", "city_gate", "anomaly", "bootstrap", "mode_min", "dimension_gate", "segment_min")},
            "cities": out_cities, "anomaly": anomaly}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def config_sha256() -> str:
    """Hash of every file under config/ (yaml and area polygons), path-sorted; reproducible."""
    h = hashlib.sha256()
    for p in sorted(CONFIG.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(CONFIG).as_posix().encode("utf-8"))
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
    return h.hexdigest()


def ti_commit() -> str:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _date_of(last_modified: str | None) -> str | None:
    if not last_modified:
        return None
    try:
        return email.utils.parsedate_to_datetime(last_modified).date().isoformat()
    except (TypeError, ValueError):
        return None


def build_manifest(results: dict[str, dict], edition: str, method_version: str, start: str, end: str, through: str, now: str) -> tuple[dict, list[str]]:
    att = attributions()
    notes: list[str] = []
    commits: dict[tuple[str, str], list[str]] = {}
    man_cities = []
    for city, c in sorted(results.items()):
        valid = [d for d in c["days"]["days"] if d["valid"]]
        lines = sorted(f"{d['date']} tidy={d['tidy_sha256'] or '?'} static={d['static_sha256'] or '?'}" for d in valid)
        unknown = sum(1 for d in valid if not d["tidy_sha256"] or not d["static_sha256"])
        if unknown:
            notes.append(f"{city}: {unknown} dni ważnych bez pełnego skrótu wejść (wpisy `cached` w logu ingestu); inputs_sha256 je oznacza jako '?'")
        n_files = len(valid) + len({d["static_sha256"] for d in valid if d["static_sha256"]})
        for d in valid:
            if d["easy_otp_commit"] and d["epoch"]:
                commits.setdefault((d["easy_otp_commit"], d["epoch"]), []).append(d["date"])
        a = att["cities"][city]
        lm = sorted(x for x in (_date_of(d["tidy_last_modified"]) for d in valid) if x)
        entry = {"source": a["source"], "url": a["url"], "license": a["license"], "verified": bool(a["verified"]),
                 "retrieved_first": lm[0] if lm else None, "retrieved_last": lm[-1] if lm else None, "processing_note": att["processing_note"]}
        for k in ("license_note", "obligations"):
            if a.get(k):
                entry[k] = a[k]
        if a.get("osm"):
            entry["osm_attribution"] = att["osm_attribution"]
        man_cities.append({"city": city, "status": c["status"], "n_valid_days": len(valid), "n_input_files": n_files,
                           "inputs_sha256": _sha("\n".join(lines)), "excluded_days": [{"date": d["date"], "reason": d["reason"]} for d in c["days"]["days"] if not d["valid"]],
                           "attributions": [entry]})
    manifest = {
        "edition": edition, "method_version": method_version, "status": "draft", "license": att["license"],
        "window": {"from": start, "to": end, "day_type": DAY_TYPE}, "data_through": through,
        "code": {"ti_commit": ti_commit(),
                 "easy_otp_commits": [{"commit": k[0], "from": min(v), "to": max(v), "epoch": k[1], "n_days": len(v)} for k, v in sorted(commits.items(), key=lambda kv: min(kv[1]))]},
        "config_sha256": config_sha256(), "cities": man_cities, "created_at": now, "doi": None, "errata": [],
    }
    return manifest, notes


# ---- validation / writing ---------------------------------------------------------------------

def _find_placeholder(o) -> bool:
    if isinstance(o, dict):
        return o.get("placeholder") is True or any(_find_placeholder(v) for v in o.values())
    if isinstance(o, list):
        return any(_find_placeholder(v) for v in o)
    return False


def validate(doc: dict, schema_name: str) -> None:
    """Schema validation plus the M3 rule that nothing marked `placeholder: true` enters an edition."""
    schema = json.loads((SCHEMAS / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        e = errors[0]
        raise ValueError(f"{schema_name}: {'/'.join(map(str, e.path))}: {e.message} (+{len(errors) - 1} more)")
    if _find_placeholder(doc):
        raise ValueError(f"{schema_name}: `placeholder: true` must not enter an edition (dane zastępcze)")


def _write_json(path: Path, doc: dict, schema: str) -> None:
    validate(doc, schema)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(edition: str, start: str, end: str, now: str | None = None) -> dict:
    cfg = metrics_cfg()
    now = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ingest, m0 = gate.load_ingest(), gate.load_m0()
    through = gate.data_through(ingest) or start
    results = {c: build_city(c, edition, start, end, ingest, m0) for c in candidate_cities()}
    rankings, dimstat = build_rankings(results, edition)
    mv = cfg["method_version"]
    out = DATA / "editions" / edition

    excluded = [{"city": c, "display_name": cities()[c]["display_name"], "reasons": r["reasons"],
                 "detail": "; ".join(f"{d['date']} {d['reason']}" for d in r["days"]["days"] if not d["valid"])[:500]}
                for c, r in sorted(results.items()) if r["status"] == "excluded"]
    _write_json(out / "ranking.json", {"edition": edition, "method_version": mv, "generated_at": now, "rankings": rankings, "excluded": excluded}, "ranking")
    for city, c in results.items():
        _write_json(out / city / "summary.json", build_summary(c, edition, mv), "city_summary")
        _write_json(out / city / "hourly.json", build_hourly(c, edition, mv), "hourly")
        with (out / city / "lines.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(LINES_HEADER)
            w.writerows(build_lines(c))
    quality = build_quality(results, dimstat, edition, mv, start, end, through, now)
    _write_json(out / "quality.json", quality, "quality")
    manifest, notes = build_manifest(results, edition, mv, start, end, through, now)
    _write_json(out / "manifest.json", manifest, "edition_manifest")

    # Committed record of the day decisions (small, reviewable; also the input of `ti daystats --valid-only`).
    rep = REPORTS.parent / "m3"
    rep.mkdir(parents=True, exist_ok=True)
    (rep / f"gate_days_{edition}.json").write_text(json.dumps(
        {c: [{k: d[k] for k in ("date", "valid", "reason", "detail")} for d in r["days"]["days"]] for c, r in sorted(results.items())},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"results": results, "rankings": rankings, "quality": quality, "manifest": manifest, "notes": notes, "out": out}
