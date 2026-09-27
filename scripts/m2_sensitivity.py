"""M2 sensitivity report (docs/07 M2, docs/03 §9, docs/10 T13/T15-T18/T20): runs the variants on
the full ingested window and all candidate cities, not the 1-day/5-city sample used pre-M1.

    py scripts/m2_sensitivity.py [--from 2026-09-01] [--to 2026-12-18]

Writes reports/m2/sensitivity_by_city.csv and prints the rank-correlation summary that goes into
docs/sensitivity-report.md.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "reference"))

import ti.aggregate as aggregate  # noqa: E402
import ti.metrics as metrics  # noqa: E402
import ti.sched as sched  # noqa: E402
import ti.static_store as static_store  # noqa: E402
from ti.config import candidate_cities  # noqa: E402
from ti.paths import DATA, mr  # noqa: E402

OUT = ROOT / "reports" / "m2"


def rho(a: pd.Series, b: pd.Series) -> float:
    df = pd.concat([a, b], axis=1).dropna()
    if len(df) < 3:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(spearmanr(df.iloc[:, 0], df.iloc[:, 1]).statistic)


def per_city_row(city: str, from_date: str, to_date: str) -> dict:
    l0 = aggregate.reference_day_l0(city, from_date, to_date)
    row = {"city": city, "n_days": int(l0.service_date.nunique()) if len(l0) else 0, "n_obs": int(len(l0))}
    street = l0[l0["mode"].isin(("bus", "tram"))]
    if street.empty:
        return row

    # T13: W1 headline (Sigma L / Sigma T) vs the robust variant (length-weighted median of segment speeds)
    row["w1_sum_ratio_kmh"] = mr.commercial_speed_kmh(street)
    row["w1_weighted_median_kmh"] = mr.length_weighted_median_speed_kmh(street)
    for mode in ("bus", "tram"):
        s = l0[l0["mode"] == mode]
        if len(s):
            row[f"w1_{mode}_sum_ratio_kmh"] = mr.commercial_speed_kmh(s)
            row[f"w1_{mode}_weighted_median_kmh"] = mr.length_weighted_median_speed_kmh(s)

    # T18: speed-class distribution (per-segment median speed, docs/03 §5)
    seg_speed = street.assign(v=street.seg_dist_m / street.seg_time_s * 3.6).groupby("seg_id", observed=True).v.median()
    row["v_q20"], row["v_q40"], row["v_q60"], row["v_q80"] = [float(seg_speed.quantile(q)) for q in (0.2, 0.4, 0.6, 0.8)]

    # W3 peak penalty (R2: AM and PM kept separate)
    pk = metrics.CFG["peak_penalty"]
    for band, key in (("am_peak", "w3_am"), ("pm_peak", "w3_pm")):
        pct, n, _ = mr.peak_penalty_pct(street, band, tuple(pk["ref_bands"]), pk["min_obs_per_segment"])
        row[key] = pct if pct == pct else None

    # T15: W10 punctuality at threshold variants 120/180/300s (docs/03 §9 default: 180s)
    for late_s in (120, 180, 300):
        row[f"w10_on_time_late{late_s}"] = mr.punctuality_shares(street, (-60, late_s), 600)["on_time"]

    # T16: W11 EWT, pooled-sum vs median-of-cells, at headway thresholds 480/600/720s
    reg = metrics.CFG["regularity"]
    for freq_s in (480, 600, 720):
        ewt, n = mr.ewt_minutes(street, freq_s)
        row[f"w11_pooled_{freq_s}"] = ewt if ewt == ewt else None
        if freq_s == reg["frequent_headway_s"]:
            row["w11_median_of_cells"] = mr.ewt_minutes_median_of_cells(street, freq_s)
            row["w11_n_headways"] = n

    # T17: W12 aggregation variant (median-per-stop-per-day, then median across days, vs the
    # share-of-stops->=4/h robust variant), source = same-day static (R10; C1 backfilled it).
    svc = metrics.CFG["service"]
    band_hours = tuple(metrics.CFG["bands"][svc["band"]])
    dates = sorted(l0.service_date.astype(str).unique())
    inside_by_sha: dict = {}
    # Known shas only (metrics._ingest_log()) - skip the "cached"-status days from M1's double-run
    # incident that never logged a sha. metrics.static_sha_for()'s network fallback for those is
    # fine for occasional production use but multiplies badly here (up to ~9 extra fetches per
    # city x up to 3 retries x 120s timeout each) - a diagnostic script doesn't need that tail.
    known = {d: r["static_sha256"] for (c, d), r in metrics._ingest_log().items() if c == city and r.get("static_sha256")}
    for mode in ("bus", "tram"):
        medians, shares4, shares6 = [], [], []
        n_days = 0
        for date in dates:
            sha = known.get(date)
            if sha is None or not metrics._has_stop_times(sha):
                continue
            dep = sched.departures(sha, date)
            if sha not in inside_by_sha:
                _, inside = static_store.load(sha, city)
                inside_by_sha[sha] = inside
            dep = dep[dep.stop_id.isin(inside_by_sha[sha]) & (dep["mode"] == mode)]
            v, _ = mr.service_offer_per_hour(dep, band_hours, svc["min_stop_departures"])
            s4 = mr.service_offer_share_above(dep, band_hours, 4.0, svc["min_stop_departures"])
            s6 = mr.service_offer_share_above(dep, band_hours, 6.0, svc["min_stop_departures"])
            if v == v:
                medians.append(v)
                n_days += 1
            if s4 == s4:
                shares4.append(s4)
            if s6 == s6:
                shares6.append(s6)
        row[f"w12_{mode}_median"] = float(pd.Series(medians).median()) if medians else None
        row[f"w12_{mode}_share_ge4"] = float(pd.Series(shares4).median()) if shares4 else None
        row[f"w12_{mode}_share_ge6"] = float(pd.Series(shares6).median()) if shares6 else None
        row[f"w12_{mode}_n_days"] = n_days

    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default="2026-09-01")
    ap.add_argument("--to", dest="end", default="2026-12-18")
    a = ap.parse_args()

    rows = []
    for c in candidate_cities():
        print(f"... {c}", flush=True)
        rows.append(per_city_row(c, a.start, a.end))
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "sensitivity_by_city.csv", index=False)
    print(df.round(3).to_string(index=False))

    print("\n--- rank correlations (M2, full ingested window) ---")
    pairs = [
        ("T13 all: sum-ratio vs weighted-median", "w1_sum_ratio_kmh", "w1_weighted_median_kmh"),
        ("T13 bus: sum-ratio vs weighted-median", "w1_bus_sum_ratio_kmh", "w1_bus_weighted_median_kmh"),
        ("T13 tram: sum-ratio vs weighted-median", "w1_tram_sum_ratio_kmh", "w1_tram_weighted_median_kmh"),
        ("T15 W10: late=120 vs late=180", "w10_on_time_late120", "w10_on_time_late180"),
        ("T15 W10: late=300 vs late=180", "w10_on_time_late300", "w10_on_time_late180"),
        ("T16 W11: freq=480 vs freq=600", "w11_pooled_480", "w11_pooled_600"),
        ("T16 W11: freq=720 vs freq=600", "w11_pooled_720", "w11_pooled_600"),
        ("T16 W11: pooled vs median-of-cells (600s)", "w11_pooled_600", "w11_median_of_cells"),
        ("T20 dims: W1(all) vs W3(pm)", "w1_sum_ratio_kmh", "w3_pm"),
        ("T20 dims: W1(all) vs W10(180s)", "w1_sum_ratio_kmh", "w10_on_time_late180"),
        ("T20 dims: W1(all) vs W11(pooled 600s)", "w1_sum_ratio_kmh", "w11_pooled_600"),
        ("T20 dims: W10(180s) vs W11(pooled 600s)", "w10_on_time_late180", "w11_pooled_600"),
        ("T17 W12 bus: median vs share>=4/h", "w12_bus_median", "w12_bus_share_ge4"),
        ("T17 W12 bus: median vs share>=6/h", "w12_bus_median", "w12_bus_share_ge6"),
        ("T17 W12 tram: median vs share>=4/h", "w12_tram_median", "w12_tram_share_ge4"),
        ("T20 dims: W1(all) vs W12(bus median)", "w1_sum_ratio_kmh", "w12_bus_median"),
    ]
    for label, a_col, b_col in pairs:
        if a_col in df and b_col in df:
            print(f"{label:45s} rho = {rho(df[a_col], df[b_col]):.3f}")

    edges = metrics.CFG["speed_classes_kmh"]
    print(f"\n--- T18 speed classes: share of network length in each class (edges {edges}) ---")
    for _, r in df.iterrows():
        if pd.isna(r.get("v_q20")):
            continue
        print(f"{r.city:12s} quintiles: {r.v_q20:5.1f} / {r.v_q40:5.1f} / {r.v_q60:5.1f} / {r.v_q80:5.1f}   edges: {edges}")


if __name__ == "__main__":
    main()
