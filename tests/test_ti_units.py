"""Unit tests for src/ti (no network): schema, provenance, feed capability, tidy -> L0 transform."""
import pandas as pd
import pytest

import ti.obs as obs
import ti.provenance as provenance
import ti.static_store as static_store
from ti.config import has_window_signal
from ti.paths import TIDY_COLUMNS


def test_validate_schema(tmp_path):
    good = tmp_path / "good.csv.gz"
    pd.DataFrame(columns=TIDY_COLUMNS).to_csv(good, index=False, compression="gzip")
    assert obs.validate_schema(good) is True

    bad = tmp_path / "bad.csv.gz"
    pd.DataFrame(columns=TIDY_COLUMNS[:-1]).to_csv(bad, index=False, compression="gzip")
    assert obs.validate_schema(bad) is False


def test_provenance_resolves_pilot_window_to_epoch_t1():
    r = provenance.resolve("2026-09-24")
    assert r["epoch"] == "t1"
    assert r["easy_otp_commit"].startswith("86929f6d")


def test_provenance_before_any_epoch_is_unresolved():
    assert provenance.resolve("2020-01-01") == {"epoch": None, "easy_otp_commit": None}


def test_feed_capability_from_city_defects_registry():
    assert has_window_signal("lodz") is True
    assert has_window_signal("gdansk") is False  # city_defects.yaml: no_stop_sequence


def _tiny_tidy_row(**overrides) -> dict:
    row = {c: "" for c in TIDY_COLUMNS}
    row.update({
        "city": "testcity", "service_date": "2026-09-24", "day_type": "weekday", "recording_date": "2026-09-24",
        "trip_id": "t1", "route_id": "r1", "route_short_name": "1", "direction_id": "0",
        "stop_sequence": 1, "stop_id": "B", "from_stop_id": "A",
        "sched_arr": "2026-09-24 06:00:00+02:00", "obs_time": "2026-09-24 06:00:10+02:00",
        "obs_local": "2026-09-24 06:00:10+02:00", "delay_s": 10.0,
        "seg_time_s": 60.0, "seg_dist_m": 500.0, "seg_status": "ok",
        "is_first_stop": False, "headway_s": 300.0, "sched_headway_s": 300.0,
        "headway_spans_outage": False, "headway_skips_vehicles": 0,
    })
    row.update(overrides)
    return row


def test_build_l0_filters_and_flags_area(tmp_path):
    rows = [
        _tiny_tidy_row(),  # bus, in area, ok
        _tiny_tidy_row(trip_id="t2", stop_id="C", from_stop_id="B", seg_status="stationary"),  # rejected
        _tiny_tidy_row(trip_id="t3", route_id="r2", stop_id="Z", from_stop_id="A"),  # bus, outside area
    ]
    tidy = tmp_path / "tidy.csv.gz"
    pd.DataFrame(rows)[TIDY_COLUMNS].to_csv(tidy, index=False, compression="gzip")

    mode_of = {"r1": "bus", "r2": "bus"}
    inside = {"A", "B"}  # Z is outside
    l0, report = obs.build_l0(tidy, mode_of, inside)

    assert report["rows_tidy"] == 3
    assert report["rows_ok"] == 2  # the "stationary" row is dropped; the outside-area one is kept and just flagged
    assert set(l0.seg_id) == {"A>B", "A>Z"}
    by_seg = l0.set_index("seg_id")
    assert bool(by_seg.loc["A>B", "in_area"]) is True
    assert bool(by_seg.loc["A>Z", "in_area"]) is False
    assert (l0["mode"] == "bus").all()
    assert l0.band.iloc[0] == "shoulder"  # 06:00 local is outside every named band


def test_build_l0_sched_pass_time_s_matches_reference(tmp_path):
    rows = [
        _tiny_tidy_row(stop_sequence=1, sched_arr="2026-09-24 06:00:00+02:00", is_first_stop=True),
        _tiny_tidy_row(stop_sequence=2, stop_id="C", from_stop_id="B", sched_arr="2026-09-24 06:02:00+02:00"),
    ]
    tidy = tmp_path / "tidy.csv.gz"
    pd.DataFrame(rows)[TIDY_COLUMNS].to_csv(tidy, index=False, compression="gzip")
    l0, _ = obs.build_l0(tidy, {"r1": "bus"}, {"A", "B", "C"})
    assert l0.sched_pass_time_s.iloc[-1] == pytest.approx(120.0)


def test_static_store_dedup_is_idempotent(tmp_path, monkeypatch):
    import zipfile

    monkeypatch.setattr(static_store, "STATIC_STORE", tmp_path / "static")
    zpath = tmp_path / "gtfs.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("routes.txt", "route_id,route_short_name,route_type\nr1,1,3\n")
        z.writestr("stops.txt", "stop_id,stop_lat,stop_lon\nA,52.0,19.0\n")
        z.writestr("trips.txt", "trip_id,route_id,service_id,shape_id\nt1,r1,s1,sh1\n")

    sha1 = static_store.store(zpath)
    sha2 = static_store.store(zpath)  # second call must be a no-op, not an error
    assert sha1 == sha2
    assert (static_store.STATIC_STORE / sha1 / "routes.parquet").exists()
    assert not (static_store.STATIC_STORE / sha1 / "shapes.parquet").exists()  # optional table, absent from the zip
