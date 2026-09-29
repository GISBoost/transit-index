"""M4: segment geometry, features vs schema, tiles. Synthetic data only (no network, no statics);
the real-data checks skip when data/ or the M4 report is absent."""
import gzip
import io
import json
import shutil
import zipfile
from pathlib import Path

import jsonschema
import numpy as np
import pandas as pd
import pytest

from ti import geometry as G
from ti import tiles as T
from ti.config import geometry_cfg

ROOT = Path(__file__).resolve().parent.parent
FEATURE_SCHEMA = json.loads((ROOT / "schemas" / "segment_feature.schema.json").read_text(encoding="utf-8"))

# a shape that goes east ~1.1 km, north ~1.1 km, then back west along the same road (a return leg)
LAT0, LON0, D = 52.0, 20.0, 0.01
SHAPE_LAT = np.array([LAT0, LAT0, LAT0 + D, LAT0 + D])
SHAPE_LON = np.array([LON0, LON0 + D, LON0 + D, LON0])


def test_haversine_cumulative_is_monotone_and_close_to_local_metres():
    cum = G.cumulative_m(SHAPE_LAT, SHAPE_LON)
    assert cum[0] == 0 and np.all(np.diff(cum) > 0)
    assert cum[1] == pytest.approx(0.01 * 111_195 * np.cos(np.radians(52.0)), rel=2e-3)


def test_project_stops_positions_increase_along_shape():
    lat = np.array([LAT0, LAT0, LAT0 + 0.5 * D, LAT0 + D])
    lon = np.array([LON0 + 0.2 * D, LON0 + 0.9 * D, LON0 + D, LON0 + 0.5 * D])
    pos, snap = G.project_stops(SHAPE_LAT, SHAPE_LON, lat, lon)
    assert np.all(np.diff(pos) >= 0) and snap.max() < 1.0


def test_project_stops_return_leg_is_not_grabbed_by_the_outbound_pass():
    # out-and-back on the same road: the third stop is at the same place as a point of the outbound
    # leg, but stop order (it comes after the far end) forces its position onto the return leg
    slat = np.array([LAT0, LAT0, LAT0])
    slon = np.array([LON0, LON0 + D, LON0])
    lat = np.array([LAT0, LAT0, LAT0])
    lon = np.array([LON0 + 0.3 * D, LON0 + D, LON0 + 0.5 * D])
    pos, snap = G.project_stops(slat, slon, lat, lon)
    total = G.cumulative_m(slat, slon)[-1]
    assert np.all(np.diff(pos) > 0) and snap.max() < 1.0
    assert pos[2] == pytest.approx(total - 0.5 * total / 2, rel=1e-3)  # halfway back: 0.5D from the start of the return leg
    assert pos[2] > pos[1]


def test_cut_polyline_between_positions_has_the_right_length():
    cum = G.cumulative_m(SHAPE_LAT, SHAPE_LON)
    p0, p1 = cum[1] * 0.3, cum[2] + 100.0
    c = G.cut_polyline(SHAPE_LAT, SHAPE_LON, cum, p0, p1)
    assert G.length_m(c) == pytest.approx(p1 - p0, rel=1e-3)
    assert c[0][0] == pytest.approx(LON0 + 0.3 * D, abs=1e-6)


def test_simplify_keeps_endpoints_and_drops_collinear_points():
    x = np.linspace(20.0, 20.01, 50)
    c = np.column_stack([x, np.full(50, 52.0)])
    s = G.simplify(c, geometry_cfg()["simplify_tolerance_m"])
    assert len(s) == 2 and (s[0] == c[0]).all() and (s[-1] == c[-1]).all()


def test_pattern_pairs_shape_vs_straight_fallback():
    stop_xy = {"A": (LAT0, LON0), "B": (LAT0, LON0 + D), "C": (LAT0 + D, LON0 + D), "FAR": (LAT0 + 0.1, LON0 + 0.1)}
    needed = {"A>B", "B>C", "C>FAR"}
    res = G.pattern_pairs((SHAPE_LAT, SHAPE_LON), ["A", "B", "C", "FAR"], stop_xy, needed)
    assert res["A>B"][0] == "shape" and res["B>C"][0] == "shape"
    assert res["C>FAR"][0] == "straight" and len(res["C>FAR"][1]) == 2  # stop far from the shape (> max_snap_m)
    none_shape = G.pattern_pairs(None, ["A", "B"], stop_xy, {"A>B"})
    assert none_shape["A>B"][0] == "straight"


def _gtfs_zip(path: Path, shape: bool = True) -> None:
    files = {
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nA,Alfa,52.0,20.0\nB,Beta,52.0,20.01\nC,Gamma,52.01,20.01\n",
        "routes.txt": "route_id,route_short_name,route_type\nR1,1,3\nR2,2,0\n",
        "trips.txt": "route_id,service_id,trip_id,shape_id\n" + "\n".join(
            [f"R1,WD,t{i},{'S1' if shape else ''}" for i in range(3)] + ["R1,WD,u1,S2", "R2,SAT,x1,S1"]),
        "stop_times.txt": "trip_id,stop_id,stop_sequence\n" + "\n".join(
            f"{t},{s},{n}" for t in ("t0", "t1", "t2", "u1", "x1") for n, s in enumerate("ABC", 1)),
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                        "WD,1,1,1,1,1,0,0,20260101,20261231\nSAT,0,0,0,0,0,1,0,20260101,20261231\n",
        "calendar_dates.txt": "service_id,date,exception_type\nWD,20260902,2\n",
    }
    if shape:
        pts = "".join(f"S1,{la},{lo},{i}\n" for i, (la, lo) in enumerate([(52.0, 20.0), (52.0, 20.01), (52.01, 20.01)]))
        # S2: a detour shape used by one trip only (less frequent)
        pts += "".join(f"S2,{la},{lo},{i}\n" for i, (la, lo) in enumerate([(52.0, 20.0), (52.004, 20.005), (52.0, 20.01), (52.01, 20.01)]))
        files["shapes.txt"] = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n" + pts
    with zipfile.ZipFile(path, "w") as z:
        for n, c in files.items():
            z.writestr(n, c)


@pytest.fixture
def geom_store(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "GEOM", tmp_path / "geom")
    return tmp_path


def test_extract_and_build_picks_the_most_frequent_pattern_of_the_day(geom_store):
    z = geom_store / "s.zip"
    _gtfs_zip(z)
    info = G.extract(z, G.GEOM / "sha1")
    assert info["stops"] == 3 and info["trips"] == 5
    # 2026-09-01 (Tue): WD active -> S1 (3 trips) beats S2 (1 trip); SAT trip x1 inactive
    out = G.build_city("x", {"A>B", "B>C", "A>Z"}, {"2026-09-01": "sha1"})
    q, coords = out["geom"]["A>B"]
    assert q == "shape" and len(coords) == 2  # straight leg of S1, not the S2 detour
    assert out["names"]["A"] == "Alfa"
    assert out["geom"].get("A>Z") is None  # unknown stop: nothing invented


def test_calendar_dates_removal_changes_the_active_services(geom_store):
    z = geom_store / "s.zip"
    _gtfs_zip(z)
    G.extract(z, G.GEOM / "sha1")
    assert G.active_services(G.GEOM / "sha1", "2026-09-01") == {"WD"}
    assert G.active_services(G.GEOM / "sha1", "2026-09-02") == set()  # exception_type 2
    assert G.active_services(G.GEOM / "sha1", "2026-09-05") == {"SAT"}


def test_no_shapes_gives_straight_geometry(geom_store):
    z = geom_store / "s.zip"
    _gtfs_zip(z, shape=False)
    G.extract(z, G.GEOM / "sha1")
    out = G.build_city("x", {"A>B", "B>C"}, {"2026-09-01": "sha1"})
    assert {q for q, _ in out["geom"].values()} == {"straight"}


def _l1():
    rows = []
    for sid, ln in (("A>B", 1113.0), ("B>C", 1112.0)):
        for band in ("all_day", "am_peak", "midday", "pm_peak", "evening"):
            rows.append({"seg_id": sid, "band": band, "n_obs": 50, "n_days": 12, "n_trips": 40, "v_p20": 12.0, "v_p50": 18.04,
                         "v_p80": 24.0, "v_sched_p50": 20.0, "sum_dist_m": 1.0, "sum_time_s": 1.0, "length_m": ln,
                         "day_type": "WEEKDAY", "q": "ok" if band != "am_peak" else "thin"})
    stats = pd.DataFrame(rows)
    stats.loc[(stats.seg_id == "B>C") & (stats.band == "evening"), ["v_p50", "q"]] = [np.nan, "none"]
    dim = pd.DataFrame({"seg_id": ["A>B", "B>C"], "from_stop_id": ["A", "B"], "stop_id": ["B", "C"],
                        "modes": [["bus"], ["bus"]], "routes": [["1", "2"], ["1"]], "n_obs_total": [250, 250],
                        "primary_mode": ["bus", "bus"], "pen_am": [1.0, 2.0], "pen_pm": [3.14159, np.nan]})
    return stats, dim


def test_features_match_the_schema_exactly_and_use_null_for_missing(geom_store):
    geom = {"A>B": ("shape", np.array([[20.0, 52.0], [20.01, 52.0]])), "B>C": ("straight", np.array([[20.01, 52.0], [20.01, 52.01]]))}
    feats, cnt = T.build_features(*_l1(), geom, {"A": "Alfa", "B": "Beta"})
    assert cnt["segments_no_geometry"] == 0 and cnt["stop_names_missing"] == 1  # C has no name -> stop_id used, counted
    for f in feats:
        jsonschema.validate(f, FEATURE_SCHEMA)
    ab, bc = (f["properties"] for f in feats)
    assert ab["v_pm"] == 18.0 and ab["q_am"] == "thin" and ab["pen_pm"] == 3.1
    assert bc["v_eve"] is None and bc["q_eve"] == "none" and bc["pen_pm"] is None and bc["to_name"] == "C"
    assert set(ab) <= set(FEATURE_SCHEMA["properties"]["properties"]["properties"])


def test_segment_without_geometry_is_counted_not_invented(geom_store):
    feats, cnt = T.build_features(*_l1(), {"A>B": ("shape", np.array([[20.0, 52.0], [20.01, 52.0]]))}, {"A": "a", "B": "b", "C": "c"})
    assert len(feats) == 1 and cnt["segments_no_geometry"] == 1
    assert cnt["no_geometry_long"] == 1 and cnt["no_geometry_long_examples"] == ["B>C"]  # >= 200 m and lost: must be visible


@pytest.mark.skipif(not shutil.which("tippecanoe"), reason="tippecanoe not installed")
def test_tiles_keep_every_segment_at_z14_and_above(geom_store, monkeypatch):
    geom = {"A>B": ("shape", np.array([[20.0, 52.0], [20.01, 52.0]])), "B>C": ("straight", np.array([[20.01, 52.0], [20.01, 52.01]]))}
    feats, _ = T.build_features(*_l1(), geom, {"A": "Alfa", "B": "Beta", "C": "Gamma"})
    monkeypatch.setattr(T, "DATA", geom_store / "data")
    d = geom_store / "data" / "editions" / "e" / "x"
    T.write_geojson_gz(feats, d / "segments.geojson.gz")
    T.tippecanoe(d / "segments.geojson.gz", geom_store / "data" / "editions" / "e" / "tiles" / "x.pmtiles")
    acc = T.acceptance(d / "segments.geojson.gz", geom_store / "data" / "editions" / "e" / "tiles" / "x.pmtiles")
    assert acc["n_long"] == 2 and acc["pass"], acc
    assert T.tiles_present(geom_store / "data" / "editions" / "e" / "tiles" / "x.pmtiles", 14) == {"A>B", "B>C"}


def test_real_report_meets_acceptance_where_present():
    rp = ROOT / "reports" / "m4" / "geometry_2026-pilot.json"
    if not rp.exists():
        pytest.skip("no M4 report")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    assert rep["cities"], "empty report"
    for city, c in rep["cities"].items():
        assert c["acceptance"]["pass"], (city, c["acceptance"])
        assert c["segments_no_geometry"] == 0 or c["segments_in_tiles"] > 0


def test_committed_pilot_geojson_validates_against_the_feature_schema():
    files = sorted((ROOT / "site-test" / "geojson" / "2026-pilot").glob("*.geojson.gz"))
    if not files:
        pytest.skip("no committed pilot GeoJSON")
    for f in files:
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            feats = json.load(fh)["features"]
        assert feats, f.name
        ids = [x["properties"]["seg_id"] for x in feats]
        assert len(ids) == len(set(ids)), f"{f.name}: duplicate seg_id"
        validator = jsonschema.Draft202012Validator(FEATURE_SCHEMA)
        for x in feats:
            validator.validate(x)
            assert not x["properties"].get("placeholder")
