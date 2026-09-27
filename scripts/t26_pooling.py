"""T26 + T7 (docs/10): what does pooling several days buy? And how many days does a city ranking need?

For every candidate city with enough valid weekdays (day gate on crossing_rate / ok_share, no public holidays):
  A. day-to-day dispersion of each dimension vs the spread between cities (signal-to-noise of ONE day),
  B. ranking reliability: K randomly chosen days per city vs the pooled remainder (independent halves),
     plus consecutive calendar weeks (5 weekdays pooled) and every single calendar day,
  C. influence of anomalous days: error of a single day vs the calendar week containing it,
  D. pooled value vs median of daily values,
  E. weekend contamination: 5 weekdays + 2 weekend days vs 5 weekdays.

    py scripts/t26_pooling.py            # writes reports/tests/t26_*.csv and prints a summary
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import t_pool as tp  # noqa: E402

OUT = ROOT / "reports" / "tests"
RNG = np.random.default_rng(20260926)
KS = (1, 2, 3, 5, 7)
DRAWS = 300
MIN_DAYS = 10  # need K + 5 remaining days for the largest K
MET = tp.METRICS
HIGHER_BETTER = {"w1": True, "w3_am": False, "w3_pm": False, "w10": True, "w11": False}


def spearman(a, b):
    m = ~(np.isnan(a) | np.isnan(b))
    if m.sum() < 4:
        return np.nan
    return float(pd.Series(a[m]).rank().corr(pd.Series(b[m]).rank()))


def pair_flips(a, b):
    """Share of city pairs whose order differs between two value vectors."""
    m = ~(np.isnan(a) | np.isnan(b))
    a, b = a[m], b[m]
    i, j = np.triu_indices(len(a), 1)
    return float((np.sign(a[i] - a[j]) != np.sign(b[i] - b[j])).mean())


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", choices=["basic", "trips"], default="trips",
                    help="basic = crossing_rate/ok_share only; trips = also trips >= anomaly_min_trip_ratio x median")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    global OUT
    OUT = ROOT / "reports" / "tests" / f"t26_{a.tag or a.gate}"
    OUT.mkdir(parents=True, exist_ok=True)
    stores, dense, days = {}, {}, {}
    for c in sorted(p.name for p in tp.tm.L0.iterdir() if p.is_dir() and not p.name.startswith("_")):
        s = tp.build_store(c)
        d = tp.valid_weekdays(c, s, trip_gate=(a.gate == "trips"))
        if len(d) >= MIN_DAYS:
            stores[c], days[c], dense[c] = s, d, tp.Dense(s, d)
    cities = list(dense)
    print(f"cities used ({len(cities)}): {cities}; valid weekdays: { {c: len(days[c]) for c in cities} }")

    # daily values ------------------------------------------------------------------------------------------
    daily = pd.DataFrame([{"city": c, "date": days[c][i], **dense[c].all([i])} for c in cities for i in range(len(days[c]))])
    daily.to_csv(OUT / "daily.csv", index=False)

    # A. dispersion ------------------------------------------------------------------------------------------
    rows = []
    for m in MET:
        piv = daily.pivot(index="date", columns="city", values=m)
        sd_within = piv.std()
        pooled_all = pd.Series({c: dense[c].all(range(len(days[c])))[m] for c in cities})
        between = pooled_all.std()
        rows.append({"metric": m, "between_city_sd": between, "mean_within_city_sd": sd_within.mean(),
                     "median_within_city_sd": sd_within.median(), "ratio_between_to_within": between / sd_within.mean(),
                     "cv_within_pct_median": float((sd_within / pooled_all.abs()).median() * 100),
                     "worst_city_cv_pct": float((sd_within / pooled_all.abs()).max() * 100)})
    disp = pd.DataFrame(rows)
    disp.to_csv(OUT / "dispersion.csv", index=False)
    per_city = daily.groupby("city")[MET].agg(["mean", "std", "min", "max"]).round(3)
    per_city.to_csv(OUT / "per_city_daily_stats.csv")

    # B. ranking reliability --------------------------------------------------------------------------------
    rel = []
    for K in KS:
        rho = {m: [] for m in MET}
        flips = {m: [] for m in MET}
        for _ in range(DRAWS):
            sub, rest = {}, {}
            for c in cities:
                n = len(days[c])
                pick = RNG.choice(n, K, replace=False)
                sub[c] = dense[c].all(pick)
                rest[c] = dense[c].all(np.setdiff1d(np.arange(n), pick))
            for m in MET:
                a = np.array([sub[c][m] for c in cities])
                b = np.array([rest[c][m] for c in cities])
                rho[m].append(spearman(a, b))
                flips[m].append(pair_flips(a, b))
        for m in MET:
            r = np.array(rho[m])
            rel.append({"K_days": K, "metric": m, "rho_median": np.nanmedian(r), "rho_p5": np.nanpercentile(r, 5),
                        "share_draws_rho_ge_0.9": float(np.nanmean(r >= 0.9)), "pair_flips_median": np.nanmedian(flips[m])})
    rel = pd.DataFrame(rel)
    rel.to_csv(OUT / "rank_reliability_random_days.csv", index=False)

    # B2. consecutive calendar weeks and single calendar days vs the rest ---------------------------------------
    all_dates = sorted(set(d for c in cities for d in days[c]))
    week_of = {d: (pd.Timestamp(d) - pd.Timestamp(d).weekday() * pd.Timedelta(days=1)).strftime("%Y-%m-%d") for d in all_dates}
    weeks = sorted(set(week_of.values()))
    cal = []

    def vec(cs_idx, m):
        return np.array([dense[c].all(cs_idx[c])[m] if len(cs_idx[c]) else np.nan for c in cities])

    for kind, groups in (("week", [[d for d in all_dates if week_of[d] == w] for w in weeks]), ("day", [[d] for d in all_dates])):
        for g in groups:
            sub_idx = {c: [i for i, d in enumerate(days[c]) if d in g] for c in cities}
            rest_idx = {c: [i for i, d in enumerate(days[c]) if d not in g] for c in cities}
            if min(len(v) for v in sub_idx.values()) == 0:
                continue
            for m in MET:
                a, b = vec(sub_idx, m), vec(rest_idx, m)
                cal.append({"kind": kind, "start": g[0], "n_days": len(g), "metric": m, "rho": spearman(a, b), "pair_flips": pair_flips(a, b)})
    cal = pd.DataFrame(cal)
    cal.to_csv(OUT / "rank_reliability_calendar.csv", index=False)
    cal_sum = cal.groupby(["kind", "metric"]).agg(rho_median=("rho", "median"), rho_min=("rho", "min"),
                                                  flips_median=("pair_flips", "median"), flips_max=("pair_flips", "max"), n=("rho", "size")).reset_index()
    cal_sum.to_csv(OUT / "rank_reliability_calendar_summary.csv", index=False)

    # C. single day vs calendar week: error against the rest -------------------------------------------------
    err = []
    for c in cities:
        for m in MET:
            ref_all = dense[c].all(range(len(days[c])))[m]
            for kind, groups in (("day", [[d] for d in days[c]]), ("week", [[d for d in days[c] if week_of[d] == w] for w in weeks])):
                for g in groups:
                    if len(g) < (1 if kind == "day" else 3):
                        continue
                    si = [i for i, d in enumerate(days[c]) if d in g]
                    ri = [i for i, d in enumerate(days[c]) if d not in g]
                    x, r = dense[c].all(si)[m], dense[c].all(ri)[m]
                    err.append({"city": c, "metric": m, "kind": kind, "start": g[0], "err": x - r, "rel_err_pct": (x - r) / abs(r) * 100 if r else np.nan})
    err = pd.DataFrame(err)
    err.to_csv(OUT / "error_vs_rest.csv", index=False)
    between = disp.set_index("metric").between_city_sd
    err["abs_err_in_between_sd"] = err.apply(lambda r: abs(r.err) / between[r.metric], axis=1)
    e_sum = err.groupby(["metric", "kind"]).agg(median_abs_rel_pct=("rel_err_pct", lambda s: s.abs().median()),
                                                p90_abs_rel_pct=("rel_err_pct", lambda s: s.abs().quantile(0.9)),
                                                max_abs_rel_pct=("rel_err_pct", lambda s: s.abs().max()),
                                                median_in_between_sd=("abs_err_in_between_sd", "median"),
                                                p90_in_between_sd=("abs_err_in_between_sd", lambda s: s.quantile(0.9))).reset_index()
    e_sum.to_csv(OUT / "error_summary.csv", index=False)

    # anomalous days: robust z of the daily value within city
    an = []
    for m in MET:
        piv = daily.pivot(index="date", columns="city", values=m)
        med = piv.median()
        mad = (piv - med).abs().median() * 1.4826
        z = (piv - med) / mad.replace(0, np.nan)
        for c in piv.columns:
            for d in piv.index[z[c].abs() > 3.5]:
                an.append({"metric": m, "city": c, "date": d, "value": piv.loc[d, c], "city_median": med[c], "robust_z": z.loc[d, c]})
    an = pd.DataFrame(an)
    an.to_csv(OUT / "anomalous_days.csv", index=False)

    # D. pooled vs median of days ---------------------------------------------------------------------------
    pm = []
    for m in MET:
        pooled_v = np.array([dense[c].all(range(len(days[c])))[m] for c in cities])
        med_v = np.array([daily[daily.city == c][m].median() for c in cities])
        pm.append({"metric": m, "rho_pooled_vs_median_of_days": spearman(pooled_v, med_v), "pair_flips": pair_flips(pooled_v, med_v),
                   "median_abs_diff": float(np.nanmedian(np.abs(pooled_v - med_v))), "median_abs_diff_in_between_sd": float(np.nanmedian(np.abs(pooled_v - med_v)) / between[m])})
    pd.DataFrame(pm).to_csv(OUT / "pooled_vs_median.csv", index=False)

    # E. weekend contamination -----------------------------------------------------------------------------
    wk = []
    for c in cities:
        s = stores[c]
        hol = tp.holidays(c)
        weekdays = days[c]
        weekend = [d for d in sorted(s) if pd.Timestamp(d).weekday() >= 5 and d not in hol]
        if not weekend:
            continue
        # one week of 5 weekdays vs the same week with its Sat+Sun added
        allw = sorted(s)
        dd = tp.Dense(s, sorted(set(weekdays) | set(weekend)))
        idx = {d: i for i, d in enumerate(dd.days)}
        wd = [idx[d] for d in weekdays]
        for m in MET:
            base = dd.all(wd)[m]
            mixed = dd.all(wd + [idx[d] for d in weekend])[m]
            wk.append({"city": c, "metric": m, "weekday_pooled": base, "weekdays_plus_weekend": mixed, "diff": mixed - base,
                       "rel_pct": (mixed - base) / abs(base) * 100 if base else np.nan})
    wk = pd.DataFrame(wk)
    wk.to_csv(OUT / "weekend_contamination.csv", index=False)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print("\n== A. dispersion (between-city SD vs within-city day-to-day SD)\n", disp.round(3).to_string(index=False))
    print("\n== B. ranking reliability: K random days vs pooled remainder (%d draws)\n" % DRAWS, rel.round(3).to_string(index=False))
    print("\n== B2. calendar weeks / single days vs rest\n", cal_sum.round(3).to_string(index=False))
    print("\n== C. error of 1 day / 1 week vs the rest\n", e_sum.round(3).to_string(index=False))
    print("\n== anomalous days (|robust z|>3.5):", len(an), "\n", an.groupby("metric").size().to_string())
    print("\n== D. pooled vs median of days\n", pd.DataFrame(pm).round(3).to_string(index=False))
    print("\n== E. weekend contamination (median over cities)\n", wk.groupby("metric")[["diff", "rel_pct"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
