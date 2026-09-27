"""Unit tests for M2 (src/ti/aggregate.py, sched.py, metrics.py): no network, synthetic L0-shaped
frames (docs/04 §2 columns)."""
from __future__ import annotations

import zipfile

import pandas as pd
import pytest

import ti.aggregate as aggregate
import ti.config as config
import ti.metrics as metrics
import ti.sched as sched
import ti.static_store as static_store


def _l0_row(**overrides) -> dict:
    row = {
        "city": "testcity", "service_date": "2026-09-24", "day_type": "WEEKDAY",
        "trip_id": "t1", "route_id": "r1", "route_short_name": "1", "mode": "bus",
        "direction_id": 0, "from_stop_id": "A", "stop_id": "B", "seg_id": "A>B",
        "seg_dist_m": 500.0, "seg_time_s": 60.0, "sched_pass_time_s": 60.0,
        "obs_local": "2026-09-24 07:00:00+02:00", "hour": 7, "band": "am_peak",
        "delay_s": 0.0, "is_first_stop": False, "headway_s": 300.0, "sched_headway_s": 300.0,
        "headway_spans_outage": False, "headway_skips_vehicles": 0, "in_area": True,
    }
    row.update(overrides)
    return row


def test_expand_bands_all_day_plus_named_band():
    l0 = pd.DataFrame([
        _l0_row(hour=7, band="am_peak"),   # counts for all_day AND am_peak
        _l0_row(hour=6, band="shoulder"),  # counts for all_day only
        _l0_row(hour=23, band="shoulder"), # outside 6-21: neither
    ])
    b = aggregate.expand_bands(l0)
    assert sorted(b.cell_band.value_counts().to_dict().items()) == [("all_day", 2), ("am_peak", 1)]


def test_build_segment_stats_speed_and_quality():
    rows = [_l0_row(seg_dist_m=1000.0, seg_time_s=100.0 + i, hour=11, band="midday") for i in range(12)]
    l0 = pd.DataFrame(rows)
    stats = aggregate.build_segment_stats(l0)
    midday = stats[stats.band == "midday"].iloc[0]
    assert midday.n_obs == 12 and midday.n_days == 1
    assert midday.q == "thin"  # 12 obs but only 1 day (< segment_min.ok.n_days=5)
    all_day = stats[stats.band == "all_day"].iloc[0]
    assert all_day.n_obs == 12


def test_build_segments_dim_handles_categorical_mode_column():
    """Real L0 parquet files store `mode`/`route_short_name` as pandas Categorical (obs.py).
    groupby.agg with a list-returning lambda on a Categorical column raises TypeError unless the
    column is decategorized first - this reproduces that shape instead of a plain-object frame."""
    l0 = pd.DataFrame([
        _l0_row(seg_id="A>B", route_short_name="1", mode="bus"),
        _l0_row(seg_id="A>B", route_short_name="2", mode="tram"),
    ])
    l0["mode"] = l0["mode"].astype("category")
    l0["route_short_name"] = l0["route_short_name"].astype("category")
    dim = aggregate.build_segments_dim(l0)
    row = dim.set_index("seg_id").loc["A>B"]
    assert row.modes == ["bus", "tram"]
    assert row.routes == ["1", "2"]


def test_reference_day_l0_filters_weekday_and_holiday(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "DATA", tmp_path)
    (tmp_path / "obs" / "testcity").mkdir(parents=True)
    pd.DataFrame([_l0_row(service_date="2026-09-24")]).to_parquet(tmp_path / "obs" / "testcity" / "2026-09-24.parquet")
    pd.DataFrame([_l0_row(service_date="2026-09-25", day_type="SATURDAY")]).to_parquet(tmp_path / "obs" / "testcity" / "2026-09-25.parquet")
    pd.DataFrame([_l0_row(service_date="2026-09-26", in_area=False)]).to_parquet(tmp_path / "obs" / "testcity" / "2026-09-26.parquet")
    monkeypatch.setattr(config, "holidays", lambda city: frozenset({"2026-09-27"}))
    pd.DataFrame([_l0_row(service_date="2026-09-27")]).to_parquet(tmp_path / "obs" / "testcity" / "2026-09-27.parquet")
    pd.DataFrame([_l0_row(service_date="2026-09-28", seg_id="X>Y", mode="other")]).to_parquet(tmp_path / "obs" / "testcity" / "2026-09-28.parquet")
    monkeypatch.setattr(aggregate, "holidays", config.holidays)

    out = aggregate.reference_day_l0("testcity", "2026-09-01", "2026-12-01")
    assert set(out.service_date.astype(str)) == {"2026-09-24"}  # not Saturday, not out-of-area, not the holiday
    # milestone-reviewer M2 finding: metro/rail ("other") must not leak into segment_stats/segments.parquet
    assert set(out["mode"].astype(str)) == {"bus"}


def test_config_holidays_reads_yaml(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CONFIG", tmp_path)
    (tmp_path / "calendars").mkdir()
    (tmp_path / "calendars" / "testcity.yaml").write_text(
        "city: testcity\npublic_holidays:\n- date: '2026-11-01'\n  name: X\n", encoding="utf-8")
    config.holidays.cache_clear()
    assert config.holidays("testcity") == frozenset({"2026-11-01"})
    assert config.holidays("nosuchcity") == frozenset()


def test_sched_active_service_ids_calendar_and_exceptions():
    calendar = pd.DataFrame({
        "service_id": ["wd", "we"], "monday": ["1", "0"], "tuesday": ["1", "0"], "wednesday": ["1", "0"],
        "thursday": ["1", "0"], "friday": ["1", "0"], "saturday": ["0", "1"], "sunday": ["0", "1"],
        "start_date": ["20260901", "20260901"], "end_date": ["20261231", "20261231"],
    })
    calendar_dates = pd.DataFrame({"service_id": ["wd", "extra"], "date": ["20260924", "20260924"], "exception_type": ["2", "1"]})
    # 2026-09-24 is a Thursday: "wd" would normally run, but is removed; "extra" is added for that date only
    active = sched.active_service_ids(calendar, calendar_dates, "2026-09-24")
    assert active == {"extra"}


def test_sched_departures_bus_tram_only_and_excludes_last_stop(tmp_path, monkeypatch):
    monkeypatch.setattr(sched, "STATIC_STORE", tmp_path)
    d = tmp_path / "sha1"
    d.mkdir()
    pd.DataFrame({"route_id": ["r1", "r2"], "route_short_name": ["1", "M1"], "route_type": ["3", "1"]}).to_parquet(d / "routes.parquet")
    pd.DataFrame({"trip_id": ["t1", "t2"], "route_id": ["r1", "r2"], "service_id": ["s1", "s1"], "shape_id": ["sh1", "sh2"]}).to_parquet(d / "trips.parquet")
    pd.DataFrame({
        "trip_id": ["t1", "t1", "t2"], "stop_id": ["A", "B", "A"], "stop_sequence": [1, 2, 1],
        "arrival_time": ["10:00:00", "10:10:00", "10:00:00"], "departure_time": ["10:00:00", "10:10:00", "10:00:00"],
    }).to_parquet(d / "stop_times.parquet")
    pd.DataFrame({"service_id": ["s1"], "monday": ["0"], "tuesday": ["0"], "wednesday": ["0"], "thursday": ["1"],
                  "friday": ["0"], "saturday": ["0"], "sunday": ["0"], "start_date": ["20260101"], "end_date": ["20261231"]}).to_parquet(d / "calendar.parquet")

    dep = sched.departures("sha1", "2026-09-24")  # a Thursday
    assert dep["mode"].tolist() == ["bus"]  # t2 is metro (route_type 1) -> excluded
    assert dep.stop_id.tolist() == ["A"]  # B is t1's last stop -> not a departure
    assert dep.hour.iloc[0] == 10


def test_service_offer_averages_across_days_not_pools_raw_departures(monkeypatch):
    """M2 bug found on real Lodz data: pooling every day's departures into one frame before
    computing the per-stop rate divides by band-hours only, so N days of the same stop's
    departures get counted as if they were N times the departures in one day (71/h instead of
    ~3.75/h). Each day must produce its own rate; the days are combined by taking the median."""
    same_stop_two_days = {
        "2026-09-07": pd.DataFrame({"stop_id": ["A"] * 4, "mode": ["bus"] * 4, "hour": [10, 11, 12, 13]}),
        "2026-09-08": pd.DataFrame({"stop_id": ["A"] * 4, "mode": ["bus"] * 4, "hour": [10, 11, 12, 13]}),
    }
    monkeypatch.setattr(metrics, "static_sha_for", lambda city, date: date)
    monkeypatch.setattr(metrics, "_has_stop_times", lambda sha: True)
    monkeypatch.setattr(metrics.static_store, "load", lambda sha, city: (None, {"A"}))
    monkeypatch.setattr(metrics.sched, "departures", lambda sha, date: same_stop_two_days[sha])

    out = metrics._service_offer("testcity", list(same_stop_two_days), {})
    assert out["bus"]["w12_departures_per_hour"] == pytest.approx(1.0)  # 4 deps / 4h, same every day - not 2.0


def test_static_store_backfills_missing_tables_without_full_redownload(tmp_path, monkeypatch):
    monkeypatch.setattr(static_store, "STATIC_STORE", tmp_path)
    zpath = tmp_path / "gtfs.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("routes.txt", "route_id,route_short_name,route_type\nr1,1,3\n")
        z.writestr("stops.txt", "stop_id,stop_lat,stop_lon\nA,52.0,19.0\n")
        z.writestr("trips.txt", "trip_id,route_id,service_id,shape_id\nt1,r1,s1,sh1\n")
        z.writestr("stop_times.txt", "trip_id,stop_id,stop_sequence,arrival_time,departure_time\nt1,A,1,10:00:00,10:00:00\n")

    # M1 predates C1: only routes/stops/trips/shapes were in TABLES. Simulate that older state,
    # then simulate the M2 code (TABLES grown) re-running store() on the same already-stored sha.
    full_tables = static_store.TABLES
    monkeypatch.setattr(static_store, "TABLES", {k: v for k, v in full_tables.items() if k in ("routes", "stops", "trips")})
    sha = static_store.store(zpath)
    assert not (static_store.STATIC_STORE / sha / "stop_times.parquet").exists()

    monkeypatch.setattr(static_store, "TABLES", full_tables)
    sha2 = static_store.store(zpath)  # top-up: only the new tables are extracted, not a full re-store
    assert sha2 == sha
    assert (static_store.STATIC_STORE / sha / "stop_times.parquet").exists()
    assert (static_store.STATIC_STORE / sha / "routes.parquet").exists()  # untouched, still there
