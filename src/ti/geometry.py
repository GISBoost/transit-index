"""Physical-segment geometry (docs/04 §4): shape polyline cut between projected stops.

Pipeline per city: `extract` reduces each unique static (SHA-256 of the zip, same key as the ingest
log) to what geometry needs (stops, route modes, trip patterns = shape + stop sequence, used
shapes, calendars); `build` weights every pattern by the trips that ran on each ingested weekday
(same-day static, CLAUDE.md) and keeps, for each L1 `seg_id`, the geometry of the most frequent
pattern. No easy-OTP / family_a code is used: the projection is our own (`project_stops`).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from .config import geometry_cfg
from .paths import DATA, ROOT, mr

GEOM = DATA / "geom"
SEP = "\x1f"  # joins stop_ids inside a pattern key (stop_ids may contain any printable char)


# ---- geometry primitives --------------------------------------------------------------------

def haversine_m(lat1, lon1, lat2, lon2) -> np.ndarray:
    r = geometry_cfg()["earth_radius_m"]
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def cumulative_m(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Cumulative haversine distance along a polyline, starting at 0 (docs/04 §4 pt 2)."""
    if len(lat) < 2:
        return np.zeros(len(lat))
    return np.concatenate([[0.0], np.cumsum(haversine_m(lat[:-1], lon[:-1], lat[1:], lon[1:]))])


def _local_xy(lat, lon, lat0, lon0) -> np.ndarray:
    r = geometry_cfg()["earth_radius_m"]
    k = np.pi / 180.0
    return np.column_stack([(np.asarray(lon) - lon0) * k * r * np.cos(lat0 * k), (np.asarray(lat) - lat0) * k * r])


def project_stops(shape_lat, shape_lon, stop_lat, stop_lon) -> tuple[np.ndarray, np.ndarray]:
    """Position (m along the shape, haversine-cumulative) and snap distance (m) of each stop.

    Each stop has a few candidate projections (shape segments within `candidate_slack_m` of the
    nearest one); a Viterbi pass picks the combination with the smallest total snap distance under
    the constraint that positions never go backwards (`monotone_tolerance_m`), so a stop near a
    loop or a return leg is not grabbed by the wrong pass of the line."""
    cfg = geometry_cfg()["projection"]
    shape_lat, shape_lon = np.asarray(shape_lat, float), np.asarray(shape_lon, float)
    stop_lat, stop_lon = np.asarray(stop_lat, float), np.asarray(stop_lon, float)
    cum = cumulative_m(shape_lat, shape_lon)
    lat0, lon0 = float(shape_lat.mean()), float(shape_lon.mean())
    pts, sxy = _local_xy(shape_lat, shape_lon, lat0, lon0), _local_xy(stop_lat, stop_lon, lat0, lon0)
    a, b = pts[:-1], pts[1:]
    ab = b - a
    seg2 = (ab ** 2).sum(1)
    seg2[seg2 == 0] = np.inf  # zero-length segments never win
    seg_len = np.diff(cum)
    m = len(sxy)
    cands: list[tuple[np.ndarray, np.ndarray]] = []  # per stop: (positions, distances)
    for i in range(m):
        ap = sxy[i] - a
        t = np.clip((ap * ab).sum(1) / seg2, 0.0, 1.0)
        d = np.linalg.norm(ap - t[:, None] * ab, axis=1)
        pos = cum[:-1] + t * seg_len
        best = d.min()
        idx = np.flatnonzero(d <= best + cfg["candidate_slack_m"])
        idx = idx[np.argsort(d[idx])][: cfg["max_candidates_per_stop"]]
        cands.append((pos[idx], d[idx]))
    tol = cfg["monotone_tolerance_m"]
    cost = [c[1].copy() for c in cands]
    back: list[np.ndarray] = [np.zeros(len(c[0]), dtype=int) for c in cands]
    eff = [c[0].copy() for c in cands]  # effective positions (clamped when no feasible predecessor)
    for i in range(1, m):
        pp, pc = eff[i - 1], cost[i - 1]
        for j, (pos, d) in enumerate(zip(cands[i][0], cands[i][1])):
            ok = pp <= pos + tol
            if ok.any():
                k = int(np.flatnonzero(ok)[np.argmin(pc[ok])])
            else:
                k = int(np.argmin(pc))
                eff[i][j] = pp[k]
            cost[i][j] = d + pc[k]
            back[i][j] = k
    j = int(np.argmin(cost[-1]))
    pos_out, snap_out = np.zeros(m), np.zeros(m)
    for i in range(m - 1, -1, -1):
        pos_out[i], snap_out[i] = eff[i][j], cands[i][1][j]
        j = int(back[i][j])
    return pos_out, snap_out


def cut_polyline(lat, lon, cum, p0: float, p1: float) -> np.ndarray:
    """(lon, lat) points of the polyline between cumulative positions p0 < p1 (endpoints interpolated)."""
    inner = (cum > p0) & (cum < p1)
    xs = np.concatenate([[p0], cum[inner], [p1]])
    return np.column_stack([np.interp(xs, cum, lon), np.interp(xs, cum, lat)])


def simplify(coords: np.ndarray, tol_m: float) -> np.ndarray:
    """Douglas-Peucker in a local metric plane; endpoints always kept."""
    if len(coords) <= 2 or tol_m <= 0:
        return coords
    from shapely.geometry import LineString

    lat0, lon0 = float(coords[:, 1].mean()), float(coords[:, 0].mean())
    xy = _local_xy(coords[:, 1], coords[:, 0], lat0, lon0)
    keep = np.array(LineString(xy).simplify(tol_m, preserve_topology=False).coords)
    if len(keep) == len(xy):
        return coords
    # map simplified vertices back to original indices (they are a subset, in order)
    idx, j = [], 0
    for q in keep:
        while not np.allclose(xy[j], q):
            j += 1
        idx.append(j)
    return coords[idx]


def length_m(coords: np.ndarray) -> float:
    return float(cumulative_m(coords[:, 1], coords[:, 0])[-1]) if len(coords) > 1 else 0.0


# ---- static extract -------------------------------------------------------------------------

def _read(z: zipfile.ZipFile, name: str, cols: list[str]) -> pd.DataFrame | None:
    if name not in z.namelist():
        return None
    return pd.read_csv(z.open(name), dtype=str, usecols=lambda c: c in cols, keep_default_na=False)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def extract(zip_path: Path, dest: Path) -> dict:
    """Reduce one static GTFS zip to geometry inputs under `dest` (idempotent per sha)."""
    z = zipfile.ZipFile(zip_path)
    stops = _read(z, "stops.txt", ["stop_id", "stop_name", "stop_lat", "stop_lon"])
    routes = _read(z, "routes.txt", ["route_id", "route_short_name", "route_type"])
    trips = _read(z, "trips.txt", ["trip_id", "route_id", "service_id", "shape_id"])
    st = pd.read_csv(z.open("stop_times.txt"), dtype=str, usecols=["trip_id", "stop_id", "stop_sequence"], keep_default_na=False)
    st["seq"] = pd.to_numeric(st.stop_sequence, errors="coerce")
    st = st.dropna(subset=["seq"]).sort_values(["trip_id", "seq"], kind="stable")
    seq = st.groupby("trip_id", sort=False).stop_id.agg(SEP.join).rename("stops").reset_index()
    t = trips.merge(seq, on="trip_id", how="inner")
    if "shape_id" not in t:
        t["shape_id"] = ""
    routes["mode"] = routes.route_type.map(lambda x: mr.mode_from_route_type(x) if x.strip().lstrip("-").isdigit() else "other")
    t = t.merge(routes[["route_id", "route_short_name", "mode"]], on="route_id", how="left")
    pat = (t.groupby(["shape_id", "stops", "service_id", "route_id", "route_short_name", "mode"], dropna=False)
           .size().rename("n_trips").reset_index())
    used = set(pat.shape_id) - {""}
    shapes = _read(z, "shapes.txt", ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"])
    dest.mkdir(parents=True, exist_ok=True)
    n_shapes = 0
    if shapes is not None and used:
        shapes = shapes[shapes.shape_id.isin(used)].copy()
        shapes["seq"] = pd.to_numeric(shapes.shape_pt_sequence, errors="coerce")
        shapes["lat"] = pd.to_numeric(shapes.shape_pt_lat, errors="coerce")
        shapes["lon"] = pd.to_numeric(shapes.shape_pt_lon, errors="coerce")
        shapes = shapes.dropna(subset=["seq", "lat", "lon"]).sort_values(["shape_id", "seq"], kind="stable")
        g = shapes.groupby("shape_id", sort=False)
        sh = pd.DataFrame({"shape_id": list(g.groups), "lat": [x.lat.to_numpy(np.float64) for _, x in g],
                           "lon": [x.lon.to_numpy(np.float64) for _, x in g]})
        sh.to_parquet(dest / "shapes.parquet", index=False)
        n_shapes = len(sh)
    stops["lat"] = pd.to_numeric(stops.stop_lat, errors="coerce")
    stops["lon"] = pd.to_numeric(stops.stop_lon, errors="coerce")
    stops[["stop_id", "stop_name", "lat", "lon"]].to_parquet(dest / "stops.parquet", index=False)
    pat.to_parquet(dest / "patterns.parquet", index=False)
    for name, cols in (("calendar", ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"]),
                       ("calendar_dates", ["service_id", "date", "exception_type"])):
        df = _read(z, f"{name}.txt", cols)
        if df is not None:
            df.to_parquet(dest / f"{name}.parquet", index=False)
    return {"patterns": len(pat), "shapes": n_shapes, "stops": len(stops), "trips": int(pat.n_trips.sum())}


def active_services(dest: Path, date: str) -> set[str]:
    d = dt.date.fromisoformat(date)
    ymd, wd = d.strftime("%Y%m%d"), d.strftime("%A").lower()
    out: set[str] = set()
    cal, cd = dest / "calendar.parquet", dest / "calendar_dates.parquet"
    if cal.exists():
        c = pd.read_parquet(cal)
        c = c[(c.start_date <= ymd) & (c.end_date >= ymd) & (c[wd] == "1")]
        out |= set(c.service_id)
    if cd.exists():
        x = pd.read_parquet(cd)
        x = x[x.date == ymd]
        out |= set(x.loc[x.exception_type == "1", "service_id"])
        out -= set(x.loc[x.exception_type == "2", "service_id"])
    return out


# ---- per-city build -------------------------------------------------------------------------

def _pairs(stops: list[str], needed: set[str]):
    for i in range(len(stops) - 1):
        sid = f"{stops[i]}>{stops[i + 1]}"
        if stops[i] != stops[i + 1] and sid in needed:
            yield i, sid


def pattern_pairs(shape: tuple | None, stop_ids: list[str], stop_xy: dict, needed: set[str]) -> dict[str, tuple[str, np.ndarray]]:
    """seg_id -> (quality, (lon, lat) coords) for the needed consecutive-stop pairs of one pattern."""
    cfg = geometry_cfg()
    snap_max = cfg["projection"]["max_snap_m"]
    pairs = list(_pairs(stop_ids, needed))
    if not pairs:
        return {}
    pos = snap = None
    if shape is not None and len(shape[0]) >= 2 and all(s in stop_xy for s in stop_ids):
        slat = np.array([stop_xy[s][0] for s in stop_ids])
        slon = np.array([stop_xy[s][1] for s in stop_ids])
        pos, snap = project_stops(shape[0], shape[1], slat, slon)
        cum = cumulative_m(shape[0], shape[1])
    out = {}
    for i, sid in pairs:
        a, b = stop_ids[i], stop_ids[i + 1]
        if a not in stop_xy or b not in stop_xy:
            continue
        if pos is not None and snap[i] <= snap_max and snap[i + 1] <= snap_max and pos[i + 1] > pos[i]:
            out[sid] = ("shape", cut_polyline(shape[0], shape[1], cum, pos[i], pos[i + 1]))
        else:
            out[sid] = ("straight", np.array([[stop_xy[a][1], stop_xy[a][0]], [stop_xy[b][1], stop_xy[b][0]]]))
    return out


def _geom_key(coords: np.ndarray) -> str:
    return hashlib.blake2b(np.round(coords, 6).tobytes(), digest_size=8).hexdigest()


def build_city(city: str, needed: set[str], day_sha: dict[str, str]) -> dict:
    """Most frequent geometry per `needed` seg_id over `day_sha` ({date: static sha}), plus a report.

    Returns {"geom": {seg_id: (quality, coords)}, "names": {stop_id: name}, "report": {...}}.
    Weight of a pattern on a day = number of trips of the services active that day."""
    cfg = geometry_cfg()
    weight: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))  # seg -> key -> weight
    cand: dict[tuple[str, str], tuple[str, np.ndarray]] = {}
    names: dict[str, str] = {}
    stop_xy_all: dict[str, tuple[float, float]] = {}
    cache: dict[str, dict] = {}
    by_sha: dict[str, list[str]] = defaultdict(list)
    for date, sha in day_sha.items():
        by_sha[sha].append(date)
    for sha, dates in by_sha.items():
        d = GEOM / sha
        if not (d / "patterns.parquet").exists():
            continue
        stops = pd.read_parquet(d / "stops.parquet")
        stops = stops.dropna(subset=["lat", "lon"])
        stop_xy = dict(zip(stops.stop_id, zip(stops.lat, stops.lon)))
        names.update(zip(stops.stop_id, stops.stop_name))
        stop_xy_all.update(stop_xy)
        pat = pd.read_parquet(d / "patterns.parquet")
        shapes = {}
        if (d / "shapes.parquet").exists():
            sh = pd.read_parquet(d / "shapes.parquet")
            shapes = {k: (a, b) for k, a, b in zip(sh.shape_id, sh.lat, sh.lon)}
        # pattern weights over the dates this static covers
        w = defaultdict(float)
        for date in dates:
            act = active_services(d, date)
            sub = pat[pat.service_id.isin(act)]
            for (shape_id, stops_key), n in sub.groupby(["shape_id", "stops"]).n_trips.sum().items():
                w[(shape_id, stops_key)] += float(n)
        for (shape_id, stops_key), wt in w.items():
            ids = stops_key.split(SEP)
            if not any(True for _ in _pairs(ids, needed)):
                continue
            ck = hashlib.blake2b(f"{sha}|{shape_id}|{stops_key}".encode(), digest_size=8).hexdigest()
            res = cache.get(ck)
            if res is None:
                res = cache[ck] = pattern_pairs(shapes.get(shape_id), ids, stop_xy, needed)
            for sid, (q, coords) in res.items():
                key = q + ":" + _geom_key(coords)
                weight[sid][key] += wt
                cand.setdefault((sid, key), (q, coords))
    geom, dominance = {}, []
    for sid, ws in weight.items():
        key = max(ws, key=lambda k: (ws[k], k.startswith("shape")))
        q, coords = cand[(sid, key)]
        geom[sid] = (q, simplify(coords, cfg["simplify_tolerance_m"]))
        dominance.append(ws[key] / sum(ws.values()))
    # fallback: seg in L1 but never in a weighted pattern -> straight if both stops are known
    fallback = 0
    for sid in needed - set(geom):
        a, _, b = sid.partition(">")
        if a in stop_xy_all and b in stop_xy_all:
            geom[sid] = ("straight", np.array([[stop_xy_all[a][1], stop_xy_all[a][0]], [stop_xy_all[b][1], stop_xy_all[b][0]]]))
            fallback += 1
    return {"geom": geom, "names": names,
            "report": {"patterns_cached": len(cache), "fallback_straight_no_pattern": fallback,
                       "dominant_share_median": float(np.median(dominance)) if dominance else None,
                       "dominant_share_p10": float(np.quantile(dominance, 0.10)) if dominance else None}}


# ---- orchestration --------------------------------------------------------------------------

def day_static_map(city: str, start: str | None = None, end: str | None = None) -> dict[str, str]:
    """{date: static sha256} for the weekdays the ingest log (M1) holds a static for."""
    import datetime as _dt

    from .gate import load_ingest

    out = {}
    for (c, date), rec in load_ingest().items():
        if c != city or not rec.get("static_sha256"):
            continue
        if _dt.date.fromisoformat(date).weekday() >= 5 or (start and date < start) or (end and date > end):
            continue
        out[date] = rec["static_sha256"]
    return dict(sorted(out.items()))


def resolve_unlogged(city: str, start: str | None = None, end: str | None = None, log=print) -> dict[str, str]:
    """{date: sha} for weekdays the ingest log marks `ok`/`cached` but never recorded a static SHA-256
    for (M1's cached re-runs did not log it): the static is downloaded once, hashed, reduced and cached.
    A date whose static is missing (404) is left out (its segments then rely on other days)."""
    import json as _json

    from .paths import REPORTS, fx

    logged = day_static_map(city, start, end)
    dates = set()
    for line in (REPORTS / "ingest_report.jsonl").read_text(encoding="utf-8").splitlines():
        r = _json.loads(line) if line.strip() else {}
        if r.get("city") == city and r.get("status") in ("ok", "cached") and r["date"] not in logged \
                and dt.date.fromisoformat(r["date"]).weekday() < 5 and not (start and r["date"] < start) and not (end and r["date"] > end):
            dates.add(r["date"])
    cache_path = GEOM / "date_sha.json"
    cache = _json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    tmp = DATA / "raw_geom"
    tmp.mkdir(parents=True, exist_ok=True)
    out = {}
    for date in sorted(dates):
        key = f"{city}/{date}"
        if key not in cache:
            zp = tmp / f"{city}_{date}.zip"
            if fx.fetch(fx.url_for(city, date, "static"), zp) == "missing":
                cache[key] = None
            else:
                sha = sha256_of(zp)
                dest = GEOM / sha
                if not (dest / "patterns.parquet").exists():
                    tmp_dest = dest.with_name(dest.name + ".tmp")
                    extract(zp, tmp_dest)
                    tmp_dest.replace(dest)
                zp.unlink(missing_ok=True)
                cache[key] = sha
                log(f"  {city} {date} resolved {sha[:10]}")
            GEOM.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(_json.dumps(cache, indent=1), encoding="utf-8")
        if cache[key]:
            out[date] = cache[key]
    return out


def ensure_extracts(city: str, day_sha: dict[str, str], tmp: Path | None = None, log=print) -> dict[str, str]:
    """Download + reduce every unique static not yet under data/geom/. The zip is deleted after the
    reduction (disk). A download whose SHA-256 differs from the logged one is skipped and reported.
    Returns {sha: status} with status in `cached` / `ok` / `missing` / `sha_mismatch`."""
    from .paths import fx

    tmp = tmp or (DATA / "raw_geom")
    tmp.mkdir(parents=True, exist_ok=True)
    first: dict[str, str] = {}
    for date, sha in day_sha.items():
        first.setdefault(sha, date)
    status = {}
    for sha, date in first.items():
        dest = GEOM / sha
        if (dest / "patterns.parquet").exists():
            status[sha] = "cached"
            continue
        zp = tmp / f"{city}_{date}.zip"
        res = fx.fetch(fx.url_for(city, date, "static"), zp)
        if res == "missing":
            status[sha] = "missing"
            continue
        if sha256_of(zp) != sha:
            status[sha] = "sha_mismatch"
            zp.unlink(missing_ok=True)
            continue
        tmp_dest = dest.with_name(dest.name + ".tmp")
        info = extract(zp, tmp_dest)
        tmp_dest.replace(dest)
        zp.unlink(missing_ok=True)
        status[sha] = "ok"
        log(f"  {city} {date} {sha[:10]} {info}")
    return status


def report_path(edition: str) -> Path:
    return ROOT / "reports" / "m4" / f"geometry_{edition}.json"
