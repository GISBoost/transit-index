#!/usr/bin/env python3
"""Sonda danych: liczy wskaźniki kontrolne dla jednego miasta z jednego lub wielu dni tidy.

    python reference/probe_release_data.py --city lodz \
        --tidy data/raw/lodz_tidy_2026-09-24.csv.gz --static data/raw/lodz_static_gtfs_2026-09-24.zip \
        [--area-radius-km 8 12 20] [--out wynik.json]

Do czego służy:
- weryfikuje schemat (34 kolumny tidy), statusy odcinków, pokrycie godzin w czasie lokalnym,
- liczy prędkość komunikacyjna wg trybu (ΣL/ΣT i mediana ważona), prędkość względem rozkładu,
  prędkości w pasmach, punktualność wg progów C11,
- przy >= 5 dniach: pokrycie komórek (jakość ok/thin), kara szczytu (W3),
- opcjonalnie: wpływ obszaru (odcinki, których oba przystanki leżą w promieniu od środka sieci;
  grube przybliżenie granicy miasta, produkcyjnie użyj wielokąta, docs/03 §2).
Wynik porównuj z reference/golden_values.json (skróty SHA-256 wejść w polu inputs).
Używa metrics_reference.py, więc jest jednocześnie testem, że funkcje referencyjne działają na
prawdziwych danych.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics_reference as mr  # noqa: E402

TIDY_COLUMNS = [
    "city", "service_date", "day_type", "recording_date",
    "trip_id", "route_id", "route_short_name", "route_group", "direction_id", "trip_headsign",
    "stop_sequence", "stop_id", "stop_name", "shape_dist_m",
    "sched_arr", "sched_dep", "obs_time", "obs_local", "delay_s",
    "seg_time_s", "sched_seg_time_s", "seg_dist_m", "seg_speed_kmh", "seg_status",
    "is_first_stop", "from_stop_id", "from_stop_name",
    "headway_s", "sched_headway_s", "headway_spans_outage", "headway_skips_vehicles",
    "trip_coverage", "service_date_offset_days", "service_date_plausible",
]
USECOLS = [
    "trip_id", "route_id", "recording_date", "stop_sequence", "sched_arr", "obs_time", "obs_local",
    "delay_s", "is_first_stop", "from_stop_id", "stop_id", "seg_dist_m", "seg_time_s", "seg_status",
]
DTYPES = {"trip_id": str, "route_id": str, "stop_id": str, "from_stop_id": str}
PUNCTUALITY_EDGES_S = (-60, 180, 600)  # progi C11 z transit_charts: za wcześnie / o czasie / spóźniony / bardzo


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def r(x, nd=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), nd)


def speeds(g: pd.DataFrame) -> dict:
    if len(g) < 500:
        return {"n_obs": int(len(g))}
    v = mr.commercial_speed_kmh(g)
    return {"n_obs": int(len(g)), "v_sum_ratio_kmh": r(v), "v_median_weighted_kmh": r(mr.length_weighted_median_speed_kmh(g)),
            "minutes_per_10km": r(mr.minutes_per_10km(v), 1)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", required=True)
    ap.add_argument("--tidy", nargs="+", type=Path, required=True)
    ap.add_argument("--static", type=Path, required=True, help="statyka z tego samego dnia (ostatniego z --tidy)")
    ap.add_argument("--area-radius-km", nargs="*", type=float, default=[])
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    out: dict = {"city": a.city, "inputs": {p.name: sha256(p) for p in a.tidy}}
    out["inputs"][a.static.name] = sha256(a.static)

    frames, per_file = [], []
    for p in a.tidy:
        header = pd.read_csv(p, nrows=0).columns.tolist()
        d = pd.read_csv(p, low_memory=False, usecols=USECOLS, dtype=DTYPES)
        d["file_date"] = re.search(r"(\d{4}-\d{2}-\d{2})", p.name).group(1)
        st = d.seg_status.value_counts(normalize=True)
        per_file.append({"date": d.file_date.iloc[0], "rows": int(len(d)), "schema_ok": header == TIDY_COLUMNS,
                         "trips": int(d.trip_id.nunique()), "crossing_rate": r(d.obs_time.notna().mean(), 3),
                         "seg_status_share": {k: r(v, 3) for k, v in st.items()}})
        frames.append(d)
    out["per_file"] = per_file
    df = pd.concat(frames, ignore_index=True)
    n_days = df.file_date.nunique()
    out["n_days"] = int(n_days)

    z = zipfile.ZipFile(a.static)
    routes = pd.read_csv(z.open("routes.txt"), dtype=str)
    mode_of = dict(zip(routes.route_id, routes.route_type.map(mr.mode_from_route_type)))
    df["mode"] = df.route_id.map(mode_of).fillna("unmapped")
    out["route_types_in_static"] = routes.route_type.value_counts().to_dict()
    out["row_share_by_mode"] = {k: r(v, 3) for k, v in df["mode"].value_counts(normalize=True).items()}
    df["sched_pass_s"] = mr.sched_pass_time_s(df)

    ok = mr.usable(df)
    hours = mr.hour_from_obs_local(ok.obs_local)
    share = hours.value_counts(normalize=True).sort_index()
    out["local_hours_with_>=1pct_of_ok"] = [int(h) for h in share[share >= 0.01].index]
    ok = ok.assign(hour=hours)
    ok = ok[ok["mode"].isin(["bus", "tram"])].copy()
    ok["band"] = [mr.band_of_hour(int(h)) for h in ok.hour]
    ok["seg_id"] = ok.from_stop_id + ">" + ok.stop_id
    out["street"] = speeds(ok)
    out["bus"] = speeds(ok[ok["mode"] == "bus"])
    out["tram"] = speeds(ok[ok["mode"] == "tram"])
    out["median_seg_dist_m"] = r(ok.seg_dist_m.median(), 0)
    out["share_seg_over_1000m"] = r((ok.seg_dist_m > 1000).mean(), 3)

    with_sched = ok[ok.sched_pass_s > 0]
    vs = with_sched.seg_dist_m.sum() / with_sched.sched_pass_s.sum() * 3.6
    vm = with_sched.seg_dist_m.sum() / with_sched.seg_time_s.sum() * 3.6
    out["v_sched_kmh"] = r(vs)
    out["speed_vs_sched_pct"] = r((vm / vs - 1) * 100, 1)
    out["speed_by_band_kmh"] = {b: r(mr.commercial_speed_kmh(g)) for b, g in ok.groupby("band")}
    out["speed_by_day_kmh"] = {d: r(mr.commercial_speed_kmh(g)) for d, g in ok.groupby("file_date")}

    obs = df[df.obs_time.notna() & ~df.is_first_stop.astype(bool) & df.delay_s.notna()]
    labels = ["early", "on_time", "late", "very_late"]
    cls = pd.cut(obs.delay_s, [-1e12, *PUNCTUALITY_EDGES_S, 1e12], right=False, labels=labels)
    out["punctuality_share"] = {k: r(v, 3) for k, v in cls.value_counts(normalize=True).reindex(labels).items()}

    if n_days >= 5:
        total_len = ok.groupby("seg_id").seg_dist_m.median().sum()
        cover = {}
        for band, sub in [("all_day", ok)] + [(b, ok[ok.band == b]) for b in mr.BANDS]:
            agg = sub.groupby("seg_id").agg(n=("seg_time_s", "size"), days=("file_date", "nunique"), L=("seg_dist_m", "median"))
            q = [mr.segment_quality(int(n), int(d)) for n, d in zip(agg.n, agg.days)]
            agg["q"] = q
            cover[band] = {k: r(agg.loc[agg.q == k, "L"].sum() / total_len, 3) for k in ("ok", "thin")}
        out["segment_length_share_by_quality"] = cover
        pen = {}
        for name, g in (("street", ok), ("bus", ok[ok["mode"] == "bus"]), ("tram", ok[ok["mode"] == "tram"])):
            for band in ("am_peak", "pm_peak"):
                pct, n_obs, n_seg = mr.peak_penalty_pct(g, band)
                pen[f"{name}_{band}"] = {"penalty_pct": r(pct, 1), "n_obs": n_obs, "n_segments": n_seg}
        out["peak_penalty_vs_midday_evening"] = pen

    if a.area_radius_km:
        stops = pd.read_csv(z.open("stops.txt"), dtype={"stop_id": str}, usecols=["stop_id", "stop_lat", "stop_lon"]).dropna()
        used = stops[stops.stop_id.isin(set(ok.stop_id))]
        lat0, lon0 = used.stop_lat.median(), used.stop_lon.median()
        p = np.pi / 180
        lat, lon = stops.stop_lat.to_numpy(), stops.stop_lon.to_numpy()
        h = np.sin((lat - lat0) * p / 2) ** 2 + np.cos(lat0 * p) * np.cos(lat * p) * np.sin((lon - lon0) * p / 2) ** 2
        radius = pd.Series(2 * 6371.0088 * np.arcsin(np.sqrt(h)), index=stops.stop_id.to_numpy())
        r1, r2 = ok.from_stop_id.map(radius), ok.stop_id.map(radius)
        out["area_effect"] = {}
        for rad in a.area_radius_km:
            g = ok[(r1 <= rad) & (r2 <= rad)]
            out["area_effect"][f"R<={rad:g}km"] = {"share_of_obs": r(len(g) / len(ok), 3), "bus": speeds(g[g["mode"] == "bus"]),
                                                    "tram": speeds(g[g["mode"] == "tram"]), "street": speeds(g)}

    text = json.dumps(out, indent=2, ensure_ascii=False)
    if a.out:
        a.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
