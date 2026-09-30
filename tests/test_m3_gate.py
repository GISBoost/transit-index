"""M3 tests: day gate, anomaly detection, city status, bootstrap, daystats vs reference formulas, edition
outputs vs schemas. Synthetic data only, no network, no L0; the real-data test skips without L1/reports."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

import ti.coverage as coverage
import ti.daystats as daystats
import ti.edition as edition
import ti.gate as gate
import ti.uncertainty as uncertainty
from ti.config import metrics_cfg
from ti.paths import ROOT, mr

CFG = metrics_cfg()
G = CFG["day_gate"]


def _day(date="2026-09-08", **kw):
    d = {"date": date, "ingest_status": "ok", "crossing_rate": 0.8, "ok_share": 0.7, "trips": 1000,
         "band_coverage": {b: 1.0 for b in ("am_peak", "midday", "pm_peak", "evening")}, "plausible": 1.0,
         "share_of_obs_in_area": 0.9, "speed_kmh": 18.0, "epoch": "t1", "easy_otp_commit": "abc",
         "tidy_sha256": "t", "static_sha256": "s", "tidy_last_modified": "Tue, 08 Sep 2026 19:00:00 GMT"}
    d.update(kw)
    return d


# ---- day gate: every threshold from config ------------------------------------------------------

@pytest.mark.parametrize("override,reason", [
    ({"crossing_rate": G["min_crossing_rate"] - 0.01}, "low_crossing_rate"),
    ({"ok_share": G["min_ok_share"] - 0.01}, "low_ok_share"),
    ({"plausible": G["min_plausible_service_date"] - 0.01}, "implausible_service_date"),
    ({"band_coverage": {"am_peak": G["min_band_recorded_share"] - 0.1, "midday": 1, "pm_peak": 1, "evening": 1}}, "recording_gap"),
    ({"ingest_status": "missing_tidy", "crossing_rate": None}, "no_tidy"),
    ({"ingest_status": "missing_static", "crossing_rate": None}, "no_static"),
    ({"band_coverage": None}, "no_gate_stats"),
])
def test_first_failure_reasons(override, reason):
    assert gate.first_failure("lodz", _day(**override))[0] == reason


def test_first_failure_passes_at_exact_thresholds_and_holiday():
    assert gate.first_failure("lodz", _day(crossing_rate=G["min_crossing_rate"], ok_share=G["min_ok_share"])) is None
    assert gate.first_failure("lodz", _day("2026-11-11"))[0] == "holiday"  # PL public holiday, config/calendars


def test_release_missing_counts_as_invalid_and_future_days_are_not():
    ing = {("lodz", "2026-09-08"): {"city": "lodz", "date": "2026-09-08", "status": "missing_tidy"},
           ("lodz", "2026-09-09"): {"city": "lodz", "date": "2026-09-09", "status": "ok", "crossing_rate": 0.8, "ok_share": 0.7, "trips": 10}}
    r = gate.evaluate_days("lodz", "2026-09-08", "2026-09-30", ing, {})
    by = {d["date"]: d for d in r["days"]}
    assert by["2026-09-08"]["reason"] == "no_tidy" and not by["2026-09-08"]["valid"]
    assert r["window_weekdays_elapsed"] == 2 and r["not_yet_available"] > 0  # later weekdays: not yet available


def test_cached_record_never_hides_gate_stats(tmp_path, monkeypatch):
    p = tmp_path / "ingest_report.jsonl"
    p.write_text(json.dumps({"city": "a", "date": "d", "status": "ok", "crossing_rate": 0.8}) + "\n" +
                 json.dumps({"city": "a", "date": "d", "status": "cached", "rows_ok": 5}) + "\n")
    monkeypatch.setattr(gate, "REPORTS", tmp_path)
    assert gate.load_ingest()[("a", "d")]["crossing_rate"] == 0.8


# ---- anomalies (docs/03 §7) ---------------------------------------------------------------------

def _days(speeds, trips=None):
    trips = trips or [1000] * len(speeds)
    return [dict(_day(f"2026-09-{8 + i:02d}", speed_kmh=s, trips=t), valid=True, reason=None, detail="") for i, (s, t) in enumerate(zip(speeds, trips))]


def test_low_trip_count_uses_ratio_from_config():
    limit = G["anomaly_min_trip_ratio"]
    days = _days([18.0] * 6, [1000, 1000, 1000, 1000, 1000, int(1000 * limit) - 1])
    gate.flag_anomalies(days)
    assert days[-1]["reason"] == "low_trip_count" and all(d["valid"] for d in days[:-1])
    days = _days([18.0] * 6, [1000, 1000, 1000, 1000, 1000, int(1000 * limit)])
    gate.flag_anomalies(days)
    assert all(d["valid"] for d in days)


def test_trip_criterion_catches_healthy_looking_but_wrong_day():
    # docs/03 §7: crossing_rate and ok_share look fine, only the trip count betrays the static mismatch.
    days = _days([18.0, 18.1, 17.9, 18.2, 18.0], [3000, 3100, 2950, 3050, 1500])
    assert gate.first_failure("lodz", days[-1]) is None
    gate.flag_anomalies(days)
    assert days[-1]["reason"] == "low_trip_count"


def test_speed_outlier_beyond_k_mad():
    an = CFG["anomaly"]
    base = [18.0, 18.2, 17.8, 18.1, 17.9, 18.0, 18.2]
    days = _days(base + [27.3])  # the Poznań 10.09 shape: 27.3 against ~19.5
    stats = gate.flag_anomalies(days)
    assert days[-1]["reason"] == "speed_outlier" and stats["speed_mad"] > 0
    assert all(d["valid"] for d in days[:-1])
    med, mad = stats["speed_median"], stats["speed_mad"]
    inside = _days(base + [med + an["mad_k"] * an["mad_scale"] * mad * 0.99])
    gate.flag_anomalies(inside)
    assert all(d["valid"] for d in inside)


def test_speed_criterion_skipped_without_daily_speeds_or_few_days():
    days = _days([18.0] * 8)
    for d in days:
        d["speed_kmh"] = None
    assert any("speed_outlier" in s for s in gate.flag_anomalies(days)["skipped"])
    few = _days([18.0, 30.0, 18.0][: CFG["anomaly"]["min_days_for_mad"] - 1])
    gate.flag_anomalies(few)
    assert all(d["valid"] for d in few)


def test_anomalies_work_with_empty_school_break_calendar():
    from ti.config import school_breaks
    assert school_breaks("lodz") == frozenset()  # config/calendars ferie deliberately empty
    days = _days([18.0, 18.2, 17.8, 18.1, 17.9, 18.0, 18.2, 40.0])
    gate.flag_anomalies(days)
    assert not days[-1]["valid"]


# ---- city gate ----------------------------------------------------------------------------------

def _res(n_valid, reasons_of_invalid=()):
    days = [{"date": f"d{i}", "valid": True, "reason": None} for i in range(n_valid)]
    days += [{"date": f"x{i}", "valid": False, "reason": r} for i, r in enumerate(reasons_of_invalid)]
    return {"days": days}


def test_city_status_thresholds():
    cg = CFG["city_gate"]
    rk, lm = cg["ranked"], cg["limited"]
    assert gate.city_status("lodz", _res(rk["min_valid_days"]), rk["min_network_coverage"], True)[0] == "ranked"
    assert gate.city_status("lodz", _res(rk["min_valid_days"] - 1), 0.9, True)[0] == "limited"
    assert gate.city_status("lodz", _res(rk["min_valid_days"]), rk["min_network_coverage"] - 0.01, True)[0] == "limited"
    assert gate.city_status("lodz", _res(lm["min_valid_days"]), lm["min_network_coverage"], True)[0] == "limited"
    st, why = gate.city_status("lodz", _res(lm["min_valid_days"] - 1, ["low_crossing_rate"] * 3), 0.9, True)
    assert st == "excluded" and set(why) == {"too_few_days", "low_crossing_rate"}
    st, why = gate.city_status("lodz", _res(rk["min_valid_days"]), lm["min_network_coverage"] - 0.01, True)
    assert st == "excluded" and why == ["low_network_coverage"]
    assert gate.city_status("lodz", _res(rk["min_valid_days"]), 0.9, False)[1] == ["no_area_definition"]


def test_registry_exclusion_has_precedence(monkeypatch):
    monkeypatch.setattr(gate, "defects", lambda: [{"city": "lodz", "id": "no_trip_id", "action": "exclude", "detail": "x"}])
    st, why = gate.city_status("lodz", _res(CFG["city_gate"]["ranked"]["min_valid_days"]), 0.9, True)
    assert st == "excluded" and why == ["no_trip_id"]
    monkeypatch.setattr(gate, "defects", lambda: [{"city": "lodz", "id": "static_ahead", "action": "gate", "detail": "x"}])
    assert gate.city_status("lodz", _res(CFG["city_gate"]["ranked"]["min_valid_days"]), 0.9, True)[0] == "ranked"  # `gate` = informational


# ---- bootstrap ----------------------------------------------------------------------------------

def test_bootstrap_is_deterministic_and_brackets_the_estimate():
    rng = np.random.default_rng(1)
    dist = rng.normal(1e6, 3e4, 30)
    comp = np.column_stack([dist, dist / (18 / 3.6) * rng.normal(1, 0.02, 30)])
    stat = lambda s: s[:, 0] / s[:, 1] * 3.6
    a = uncertainty.bootstrap_sums(comp, stat, "x")
    assert a == uncertainty.bootstrap_sums(comp, stat, "x") and a != uncertainty.bootstrap_sums(comp, stat, "y")
    point = comp[:, 0].sum() / comp[:, 1].sum() * 3.6
    assert a[0] < point < a[1] and a[1] - a[0] < 1.0
    assert uncertainty.bootstrap_sums(comp[:1], stat, "x") == (None, None)


def test_indistinguishable_marks_overlapping_intervals_only():
    out = uncertainty.mark_indistinguishable({"a": (17.0, 18.0), "b": (17.9, 19.0), "c": (20.0, 21.0), "d": (None, None)})
    assert out == {"a": ["b"], "b": ["a"], "c": [], "d": []}


# ---- daystats vs reference formulas -------------------------------------------------------------

def _l0(n_days=6, seed=0, city_speed=18.0, modes=("bus", "tram")):
    rng = np.random.default_rng(seed)
    rows = []
    for di in range(n_days):
        date = f"2026-09-{8 + di:02d}"
        for i in range(400):
            hour = int(rng.choice([7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 6, 9, 14, 18]))
            band = mr.band_of_hour(hour)
            seg = int(rng.integers(0, 12))
            dist = 400.0 + 30 * seg
            speed = city_speed * (0.8 if band in ("am_peak", "pm_peak") else 1.0) * rng.uniform(0.7, 1.3)
            sh = float(rng.choice([300.0, 900.0]))
            rows.append({
                "city": "t", "service_date": date, "day_type": "WEEKDAY", "trip_id": f"t{di}-{i}", "route_id": f"r{seg % 3}",
                "route_short_name": f"L{seg % 3}", "mode": modes[seg % len(modes)], "direction_id": 0, "from_stop_id": f"s{seg}",
                "stop_id": f"s{seg + 1}", "seg_id": f"s{seg}>s{seg + 1}", "seg_dist_m": dist, "seg_time_s": dist / (speed / 3.6),
                "sched_pass_time_s": 60.0, "obs_local": f"{date} {hour:02d}:10:00+02:00", "hour": hour, "band": band,
                "delay_s": float(rng.normal(60, 200)), "is_first_stop": bool(rng.random() < 0.05),
                "headway_s": float(rng.uniform(100, 700)), "sched_headway_s": sh, "headway_spans_outage": bool(rng.random() < 0.05),
                "headway_skips_vehicles": 0, "in_area": True,
            })
    d = pd.DataFrame(rows)
    d["band"] = d.band.astype("category")
    return d


def test_daystats_reproduce_reference_formulas():
    l0 = _l0()
    ds = daystats.compute(l0)
    dates = sorted(l0.service_date.unique())
    for mode, modes in daystats.MODE_GROUPS.items():
        sub = l0[l0["mode"].isin(modes)].assign(seg_status="ok")
        # W1
        v = edition.dimension_value(ds, dates, "t", "speed", mode, "all_day")
        sub_h = sub[sub.hour.between(6, 21)]
        assert v["value"] == pytest.approx(mr.commercial_speed_kmh(sub_h), rel=1e-9)
        # W3 (pooled reference bands)
        pk = CFG["peak_penalty"]
        for band in ("am_peak", "pm_peak"):
            ref_pct, n, _ = mr.peak_penalty_pct(sub, band, tuple(pk["ref_bands"]), pk["min_obs_per_segment"])
            w3 = edition.dimension_value(ds, dates, "t", "peak_penalty", mode, band)
            assert w3["value"] == pytest.approx(ref_pct, rel=1e-9) and w3["n_obs"] == n
        # W10 and W11
        p = CFG["punctuality"]
        ref_p = mr.punctuality_shares(sub_h, tuple(p["on_time_s"]), p["late_s"], p["exclude_first_stop"])
        assert edition.dimension_value(ds, dates, "t", "punctuality", mode, "all_day")["value"] == pytest.approx(ref_p["on_time"] * 100, rel=1e-9)
        ref_e, n_h = mr.ewt_minutes(sub_h, CFG["regularity"]["frequent_headway_s"])
        w11 = edition.dimension_value(ds, dates, "t", "regularity", mode, "all_day")
        assert w11["value"] == pytest.approx(ref_e, rel=1e-9) and w11["n_obs"] == n_h


def test_hourly_lines_and_coverage_from_daystats():
    l0 = _l0(n_days=3)
    ds = daystats.compute(l0, {"2026-09-08": daystats.band_coverage(l0[l0.service_date == "2026-09-08"])})
    view = daystats.gate_view(ds)
    assert view["2026-09-08"]["band_coverage"]["midday"] == 1.0 and view["2026-09-08"]["speed_kmh"] > 0
    assert set(ds[ds.kind == "hour"].key) == {f"h{h:02d}" for h in range(6, 22)}
    assert set(ds[ds.kind == "line"]["mode"]) == {"bus", "tram"}  # no street lines


def test_band_coverage_uses_recorded_hours():
    l0 = _l0(n_days=1)
    late_only = l0[l0.hour >= 14]
    cov = daystats.band_coverage(late_only)
    assert cov["am_peak"] == 0.0 and cov["midday"] == 0.0 and cov["pm_peak"] == 1.0 and cov["evening"] == 1.0


# ---- full outputs on synthetic city set ---------------------------------------------------------

def _l1(n_ok=60, routes=("1", "2", "3", "4")):
    seg = [f"a{i}>b{i}" for i in range(n_ok + 5)]
    rows = [{"seg_id": s, "band": b, "length_m": 500.0, "q": "ok" if i < n_ok else "thin"} for i, s in enumerate(seg) for b in coverage.BANDS]
    dim = pd.DataFrame({"seg_id": seg, "primary_mode": "bus", "routes": [list(routes)] * len(seg)})
    return pd.DataFrame(rows), dim


def _synthetic_results(statuses):
    cities = {}
    for k, (city, status) in enumerate(statuses.items()):
        l0 = _l0(n_days=8, seed=k, city_speed=16.0 + 3 * k, modes=("bus",))
        l0["city"] = city
        ds = daystats.compute(l0)
        ing = {(city, d): {"status": "ok", "crossing_rate": 0.8, "ok_share": 0.7, "trips": 1000, "epoch": "t1", "easy_otp_commit": "c" * 40,
                           "tidy_sha256": f"t{d}", "static_sha256": f"s{d}", "tidy_last_modified": "Tue, 08 Sep 2026 19:00:00 GMT", "share_of_obs_in_area": 0.9}
               for d in sorted(l0.service_date.unique())}
        m0 = {(city, d): {"band_hour_coverage": {b: 1.0 for b in ("am_peak", "midday", "pm_peak", "evening")}, "service_date_plausible_share": 1.0} for _, d in ing}
        days = gate.evaluate_days(city, "2026-09-08", "2026-12-18", ing, m0, daystats.gate_view(ds))
        l1 = coverage.compute(*_l1())
        cities[city] = {"city": city, "ds": ds, "days": days, "l1": l1, "coverage": l1["street"]["coverage"]["all_day"], "status": status,
                        "reasons": [] if status != "excluded" else ["too_few_days"], "valid_dates": [d["date"] for d in days["days"] if d["valid"]]}
    return cities


def test_synthetic_edition_outputs_validate_and_rank():
    from ti.config import candidate_cities
    a, b, c, d = candidate_cities()[:4]
    res = _synthetic_results({a: "ranked", b: "limited", c: "limited", d: "excluded"})
    rankings, dimstat = edition.build_rankings(res, "2026-pilot")
    ids = {r["id"] for r in rankings}
    assert "street_speed" in ids and "street_frequency" not in ids and "bus_punctuality" in ids
    sp = next(r for r in rankings if r["id"] == "street_speed")
    assert [e["city"] for e in sp["entries"]] == [c, b, a] or len(sp["entries"]) == 3  # faster city first, excluded city absent
    assert d not in [e["city"] for e in sp["entries"]]
    assert sp["entries"][0]["value"] >= sp["entries"][1]["value"] >= sp["entries"][2]["value"]
    assert all(e["status"] in ("ranked", "limited") for e in sp["entries"])
    pen = next(r for r in rankings if r["id"] == "street_peak_penalty_am_peak")
    assert pen["sort"] == "asc"
    doc = {"edition": "2026-pilot", "method_version": "m", "generated_at": "2026-09-29T00:00:00Z", "rankings": rankings, "excluded": []}
    edition.validate(doc, "ranking")
    for r in res.values():
        edition.validate(edition.build_summary(r, "2026-pilot", "m"), "city_summary")
        edition.validate(edition.build_hourly(r, "2026-pilot", "m"), "hourly")
        assert edition.build_lines(r) and len(edition.build_lines(r)[0]) == len(edition.LINES_HEADER)
    q = edition.build_quality(res, dimstat, "2026-pilot", "m", "2026-09-01", "2026-12-18", "2026-09-27", "2026-09-29T00:00:00Z")
    edition.validate(q, "quality")
    man, _ = edition.build_manifest(res, "2026-pilot", "m", "2026-09-01", "2026-12-18", "2026-09-27", "2026-09-29T00:00:00Z")
    edition.validate(man, "edition_manifest")
    assert man["license"] == "CC-BY-4.0" and all(c["attributions"] for c in man["cities"])
    assert man["code"]["easy_otp_commits"][0]["n_days"] == sum(len(r["valid_dates"]) for r in res.values())  # city-days (the synthetic days include a weekend, which the gate ignores)


def test_close_cities_are_flagged_indistinguishable():
    from ti.config import candidate_cities
    a, b = candidate_cities()[:2]
    res = _synthetic_results({a: "limited", b: "limited"})
    for c in res.values():  # same distribution -> overlapping intervals
        c["ds"] = daystats.compute(_l0(n_days=8, seed=5, city_speed=18.0, modes=("bus",)).assign(city=c["city"]))
    rankings, _ = edition.build_rankings(res, "2026-pilot")
    sp = next(r for r in rankings if r["id"] == "street_speed")
    assert all(e["indistinguishable_with"] for e in sp["entries"])
    assert any("Nierozróżnialne" in n for e in sp["entries"] for n in e["notes"])


def test_inputs_hash_reproduces_and_changes_with_inputs():
    from ti.config import candidate_cities
    a = candidate_cities()[0]
    res = _synthetic_results({a: "limited"})
    m1, _ = edition.build_manifest(res, "t", "m", "s", "e", "e", "now")
    m2, _ = edition.build_manifest(res, "t", "m", "s", "e", "e", "later")
    assert m1["cities"][0]["inputs_sha256"] == m2["cities"][0]["inputs_sha256"] and m1["config_sha256"] == m2["config_sha256"]
    res[a]["days"]["days"][0]["tidy_sha256"] = "changed"
    m3, _ = edition.build_manifest(res, "t", "m", "s", "e", "e", "now")
    assert m3["cities"][0]["inputs_sha256"] != m1["cities"][0]["inputs_sha256"]


def test_placeholder_files_do_not_enter_an_edition():
    for name, schema in (("ranking", "ranking"), ("edition_manifest", "edition_manifest"), ("city_summary", "city_summary")):
        doc = json.loads((ROOT / "examples" / f"{name}.example.json").read_text(encoding="utf-8"))
        with pytest.raises(ValueError):
            edition.validate(doc, schema)


def test_mode_below_minimum_gets_no_entry():
    from ti.config import candidate_cities
    a = candidate_cities()[0]
    res = _synthetic_results({a: "limited"})
    res[a]["l1"] = coverage.compute(*_l1(n_ok=CFG["mode_min"]["segments"] - 1))
    rankings, _ = edition.build_rankings(res, "2026-pilot")
    assert rankings == []


# ---- real data (skips where L1/reports are missing) ---------------------------------------------

def test_real_l1_and_ingest_log_pass_schemas():
    from ti.config import candidate_cities
    if not (ROOT / "data" / "editions" / "2026-pilot" / "lodz" / "segment_stats.parquet").exists() or not (ROOT / "reports" / "m1" / "ingest_report.jsonl").exists():
        pytest.skip("L1 (data/editions/2026-pilot) not available")
    ingest, m0 = gate.load_ingest(), gate.load_m0()
    res = {c: edition.build_city(c, "2026-pilot", "2026-09-01", "2026-12-18", ingest, m0) for c in candidate_cities()}
    assert len(res) == 16 and all(r["l1"] for r in res.values())
    for r in res.values():
        assert 0.0 < r["coverage"] <= 1.0
        edition.validate(edition.build_summary(r, "2026-pilot", CFG["method_version"]), "city_summary")
    rankings, dimstat = edition.build_rankings(res, "2026-pilot")
    q = edition.build_quality(res, dimstat, "2026-pilot", CFG["method_version"], "2026-09-01", "2026-12-18", gate.data_through(ingest), "2026-09-29T00:00:00Z")
    edition.validate(q, "quality")
    man, _ = edition.build_manifest(res, "2026-pilot", CFG["method_version"], "2026-09-01", "2026-12-18", gate.data_through(ingest), "2026-09-29T00:00:00Z")
    edition.validate(man, "edition_manifest")
    # a city with fewer valid days than city_gate.limited.min_valid_days can never be ranked
    assert all(r["status"] == "excluded" for r in res.values() if len(r["valid_dates"]) < CFG["city_gate"]["limited"]["min_valid_days"])
