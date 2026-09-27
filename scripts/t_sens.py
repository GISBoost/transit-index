"""Sensitivity tests on the pre-M1 harness (docs/10): T4 T5 T6 T8 T9 T10 T11 T12 T13 T15 T16 T18 T19 T20 T22.

Works on the per-day cells of t_pool.py (valid weekdays, day gate incl. the trip-ratio criterion) and, where a test
needs rows, on the L0-lite parquet files. Every test writes a CSV to reports/tests/sens/ and prints a summary.

    py scripts/t_sens.py all            # or one of: t4 t5 t6 t8 t9 t10 t11 t12 t13 t15 t16 t18 t19 t20 t22
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import t_metrics as tm  # noqa: E402
import t_pool as tp  # noqa: E402

CFG = tm.CFG
OUT = ROOT / "reports" / "tests" / "sens"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20260926)
MIN_DAYS = 10
MET = tp.METRICS
pd.set_option("display.width", 230)
pd.set_option("display.max_columns", 40)
EDGES = CFG["speed_classes_kmh"]


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    return float(pd.Series(a[m]).rank().corr(pd.Series(b[m]).rank())) if m.sum() >= 4 else np.nan


def flips(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    a, b = a[m], b[m]
    i, j = np.triu_indices(len(a), 1)
    return float((np.sign(a[i] - a[j]) != np.sign(b[i] - b[j])).mean())


class Ctx:
    """Stores, valid days and dense pools for all cities with >= MIN_DAYS valid weekdays (trip gate on)."""

    def __init__(self, gate_kwargs=None):
        self.store, self.days, self.dense = {}, {}, {}
        for c in sorted(p.name for p in tm.L0.iterdir() if p.is_dir() and not p.name.startswith("_")):
            s = tp.build_store(c)
            d = tp.valid_weekdays(c, s, **(gate_kwargs or {}))
            if len(d) >= MIN_DAYS:
                self.store[c], self.days[c] = s, d
                self.dense[c] = tp.Dense(s, d)
        self.cities = list(self.dense)

    def vec(self, fn) -> np.ndarray:
        return np.array([fn(c) for c in self.cities], float)

    def all_idx(self, c):
        return list(range(len(self.days[c])))


def report(name, df, note=""):
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\n== {name} {note}\n{df.round(3).to_string(index=False)}")


# --------------------------------------------------------------------------------------------------------------
def t4(ctx):
    """Speed floor/ceiling: W1 with the 2 km/h / 100 km/h labels re-applied at other values (from rows)."""
    variants = {"floor0": (0, 100), "floor1": (1, 100), "floor2 (base)": (2, 100), "floor3": (3, 100), "floor5": (5, 100),
                "ceil60": (2, 60), "ceil80": (2, 80)}
    res = {v: {} for v in variants}
    for c in ctx.cities:
        parts = []
        for d in ctx.days[c]:
            x = pd.read_parquet(tm.L0 / c / f"{d}.parquet", columns=["mode", "seg_status", "seg_dist_m", "seg_time_s", "seg_in_area"])
            x = x[x["mode"].isin(["bus", "tram"]) & x.seg_in_area & x.seg_status.isin(["ok", "stationary", "implausible"]) & (x.seg_time_s > 0) & (x.seg_dist_m > 0)]
            parts.append(x[["seg_dist_m", "seg_time_s"]].astype("float64"))
        x = pd.concat(parts)
        sp = x.seg_dist_m / x.seg_time_s * 3.6
        for v, (lo, hi) in variants.items():
            k = (sp >= lo) & (sp <= hi)
            res[v][c] = x.seg_dist_m[k].sum() / x.seg_time_s[k].sum() * 3.6
    df = pd.DataFrame(res)
    base = df["floor2 (base)"]
    rows = [{"variant": v, "rho_vs_base": spearman(df[v], base), "pair_flips": flips(df[v], base),
             "median_abs_diff_kmh": float((df[v] - base).abs().median()), "max_abs_diff_kmh": float((df[v] - base).abs().max())} for v in variants]
    report("t4_speed_thresholds", pd.DataFrame(rows), "(W1, all valid weekdays, bus+tram in area)")


def t5_t6(ctx):
    """T5: technical covariates vs city values; T6: within-city daily W1 vs crossing rate."""
    rows = []
    for c in ctx.cities:
        s, d = ctx.store[c], ctx.days[c]
        pooled = ctx.dense[c].all(ctx.all_idx(c))
        gap = float(np.mean([1 - s[x]["n_obs"] / s[x]["n_rows"] for x in d]))
        rows.append({"city": c, "crossing_rate": 1 - gap, "ok_share": float(np.mean([s[x]["n_ok_all"] / s[x]["n_rows"] for x in d])),
                     "trips_per_day": float(np.mean([s[x]["n_trips"] for x in d])), **pooled})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "t5_city_covariates.csv", index=False)
    cor = []
    for cov in ("crossing_rate", "ok_share", "trips_per_day"):
        for m in MET:
            cor.append({"covariate": cov, "metric": m, "spearman": spearman(df[cov], df[m])})
    report("t5_covariate_correlations", pd.DataFrame(cor), f"(n={len(df)} cities; |rho|>=0.5 => flag)")
    slopes = []
    for c in ctx.cities:
        s, d = ctx.store[c], ctx.days[c]
        x = np.array([s[y]["n_obs"] / s[y]["n_rows"] for y in d])
        for m in ("w1", "w10"):
            y = np.array([ctx.dense[c].all([i])[m] for i in range(len(d))])
            b = np.polyfit(x - x.mean(), y, 1)[0] if x.std() > 0 else np.nan
            r = np.corrcoef(x, y)[0, 1] if x.std() > 0 else np.nan
            slopes.append({"city": c, "metric": m, "crossing_sd": x.std(), "slope_per_0.01_crossing": b * 0.01, "corr": r})
    sl = pd.DataFrame(slopes)
    report("t6_within_city_slopes", sl, "(daily metric vs daily crossing_rate)")
    print("\nT6 share of cities with corr>0 (W1):", float((sl[sl.metric == "w1"]["corr"] > 0).mean()), " |corr|>=0.5:", float((sl[sl.metric == "w1"]["corr"].abs() >= 0.5).mean()))


def t8(ctx):
    """Split-half reliability of segment speeds and speed classes (all-day and pm_peak)."""
    rows = []
    for c in ctx.cities:
        D = ctx.dense[c]
        n_days = len(D.days)
        for band in ("all_day", "pm_peak"):
            mask = np.ones(D.band.shape, bool) if band == "all_day" else (D.band == band)
            seg = D.seg_idx
            m = seg.max() + 1
            for min_n in (5, 10, 20):
                agree, kap_a, kap_b, shift2, nseg, corr = [], [], [], [], [], []
                for _ in range(60):
                    perm = RNG.permutation(n_days)
                    A, B = perm[: n_days // 2], perm[n_days // 2: 2 * (n_days // 2)]
                    def sp(idx):
                        n = np.bincount(seg, weights=D.n[idx].sum(0) * mask, minlength=m)
                        L = np.bincount(seg, weights=D.L[idx].sum(0) * mask, minlength=m)
                        T = np.bincount(seg, weights=D.T[idx].sum(0) * mask, minlength=m)
                        return n, np.where(T > 0, L / np.where(T > 0, T, 1) * 3.6, np.nan)
                    na, sa = sp(A)
                    nb, sb = sp(B)
                    ok = (na >= min_n) & (nb >= min_n) & ~np.isnan(sa) & ~np.isnan(sb)
                    if ok.sum() < 30:
                        continue
                    ca, cb = np.searchsorted(EDGES, sa[ok], side="right"), np.searchsorted(EDGES, sb[ok], side="right")
                    agree.append((ca == cb).mean())
                    shift2.append((np.abs(ca - cb) >= 2).mean())
                    pe = sum(((ca == k).mean() * (cb == k).mean()) for k in range(len(EDGES) + 1))
                    kap_a.append(((ca == cb).mean() - pe) / (1 - pe) if pe < 1 else np.nan)
                    corr.append(np.corrcoef(sa[ok], sb[ok])[0, 1])
                    nseg.append(int(ok.sum()))
                if agree:
                    rows.append({"city": c, "band": band, "min_n_per_half": min_n, "segments": int(np.median(nseg)), "class_agreement": np.mean(agree),
                                 "kappa": np.nanmean(kap_a), "shift_ge2_classes": np.mean(shift2), "speed_corr": np.nanmean(corr)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "t8_split_half_by_city.csv", index=False)
    s = df.groupby(["band", "min_n_per_half"]).agg(cities=("city", "size"), segments_median=("segments", "median"), agreement_median=("class_agreement", "median"),
                                                  agreement_min=("class_agreement", "min"), kappa_median=("kappa", "median"), kappa_min=("kappa", "min"),
                                                  shift_ge2_median=("shift_ge2_classes", "median"), shift_ge2_max=("shift_ge2_classes", "max")).reset_index()
    report("t8_split_half_summary", s, "(halves of ~7 valid weekdays; per-half n = observations in the segment)")


def t9(ctx):
    """Day-of-week: Tue-Thu only, without Mon/Fri, and single weekdays, vs all valid weekdays."""
    ref = {m: ctx.vec(lambda c, m=m: ctx.dense[c].all(ctx.all_idx(c))[m]) for m in MET}
    sets = {"tue_thu": (1, 2, 3), "no_mon_fri": (1, 2, 3), "mon": (0,), "fri": (4,)}
    rows = []
    for name, dows in (("tue_thu", (1, 2, 3)), ("mon", (0,)), ("fri", (4,))):
        vals = {m: [] for m in MET}
        for c in ctx.cities:
            idx = [i for i, d in enumerate(ctx.days[c]) if pd.Timestamp(d).weekday() in dows]
            r = ctx.dense[c].all(idx)
            for m in MET:
                vals[m].append(r[m])
        for m in MET:
            v = np.array(vals[m])
            rows.append({"subset": name, "metric": m, "rho_vs_all_weekdays": spearman(v, ref[m]), "pair_flips": flips(v, ref[m]),
                         "median_shift": float(np.nanmedian(v - ref[m])), "median_abs_shift": float(np.nanmedian(np.abs(v - ref[m])))})
    report("t9_day_of_week", pd.DataFrame(rows))


def t10(ctx):
    """Day-gate thresholds: how many days flip status, and does the ranking change?"""
    ref_days = ctx.days
    ref = {m: ctx.vec(lambda c, m=m: ctx.dense[c].all(ctx.all_idx(c))[m]) for m in MET}
    grid = [("crossing", 0.5), ("crossing", 0.7), ("ok_share", 0.45), ("ok_share", 0.65), ("trip_ratio", 0.5), ("trip_ratio", 0.85), ("no_trip_gate", 0)]
    rows = []
    for name, val in grid:
        vals, lost, kept, dropped = {m: [] for m in MET}, 0, 0, []
        for c in ctx.cities:
            s = ctx.store[c]
            allw = [d for d in sorted(s) if pd.Timestamp(d).weekday() < 5 and d not in tp.holidays(c)]
            g = dict(CFG["day_gate"])
            if name == "crossing":
                g["min_crossing_rate"] = val
            if name == "ok_share":
                g["min_ok_share"] = val
            days = [d for d in allw if s[d]["n_obs"] / s[d]["n_rows"] >= g["min_crossing_rate"] and s[d]["n_ok_all"] / s[d]["n_rows"] >= g["min_ok_share"]]
            if name != "no_trip_gate" and days:
                r = val if name == "trip_ratio" else g["anomaly_min_trip_ratio"]
                med = np.median([s[d]["n_trips"] for d in days])
                days = [d for d in days if s[d]["n_trips"] >= r * med]
            lost += len(set(ref_days[c]) ^ set(days))
            kept += len(days)
            if len(days) >= 5:
                D = tp.Dense(s, days)
                r_ = D.all(range(len(days)))
            else:
                r_ = {m: np.nan for m in MET}
                dropped.append(c)
            for m in MET:
                vals[m].append(r_[m])
        for m in MET:
            v = np.array(vals[m])
            rows.append({"variant": f"{name}={val}", "metric": m, "days_changed_vs_base": lost, "cities_left_with_lt5_days": ",".join(dropped) or "-", "rho_vs_base": spearman(v, ref[m]), "pair_flips": flips(v, ref[m]),
                         "max_abs_diff": float(np.nanmax(np.abs(v - ref[m])))})
    report("t10_gate_thresholds", pd.DataFrame(rows))


def t11(ctx):
    """Segment thresholds: coverage of the network and bias of W1 when only 'ok' segments are kept."""
    rows = []
    for c in ctx.cities:
        D = ctx.dense[c]
        seg, m = D.seg_idx, D.seg_idx.max() + 1
        n_all = D.n.sum(0)
        L_all, T_all = D.L.sum(0), D.T.sum(0)
        nseg = np.bincount(seg, weights=n_all, minlength=m)
        Lseg = np.bincount(seg, weights=L_all, minlength=m)
        Tseg = np.bincount(seg, weights=T_all, minlength=m)
        days_present = np.zeros(m)
        for i in range(len(D.days)):
            days_present += (np.bincount(seg, weights=D.n[i], minlength=m) > 0)
        length = np.where(nseg > 0, Lseg / np.where(nseg > 0, nseg, 1), 0)  # mean segment length
        w1_all = Lseg.sum() / Tseg.sum() * 3.6
        for n_obs, n_days in ((5, 3), (10, 5), (20, 5), (10, 8), (30, 8)):
            k = (nseg >= n_obs) & (days_present >= n_days)
            rows.append({"city": c, "n_obs": n_obs, "n_days": n_days, "share_segments": float(k.mean()), "share_length": float(length[k].sum() / length.sum()),
                         "share_observations": float(nseg[k].sum() / nseg.sum()), "w1_ok_only": float(Lseg[k].sum() / Tseg[k].sum() * 3.6), "w1_all": float(w1_all)})
    df = pd.DataFrame(rows)
    df["w1_shift"] = df.w1_ok_only - df.w1_all
    df.to_csv(OUT / "t11_segment_thresholds_by_city.csv", index=False)
    s = df.groupby(["n_obs", "n_days"]).agg(length_share_median=("share_length", "median"), length_share_min=("share_length", "min"),
                                            obs_share_median=("share_observations", "median"), w1_shift_median=("w1_shift", "median"),
                                            w1_shift_max_abs=("w1_shift", lambda x: x.abs().max())).reset_index()
    report("t11_segment_thresholds", s, "(all-day; length share = share of network length, ok segments / all seen)")


def t12(ctx):
    """Bootstrap over days: is the bootstrap SE realistic, and how many city pairs are indistinguishable?

    Realism check: for K = n//2 days, compare (a) the SD of the pooled value across independent K-day samples
    (random K-subsets, divided by sqrt((n-K)/(n-1)) to undo the finite-population effect) with (b) the SD of a
    bootstrap over the days of ONE such subset (averaged over subsets). Ratio ~1 => the bootstrap SE is realistic."""
    rows, ci = [], {m: {} for m in MET}
    for c in ctx.cities:
        D, n = ctx.dense[c], len(ctx.days[c])
        for m in MET:
            boot = np.array([D.all(RNG.integers(0, n, n))[m] for _ in range(200)])
            ci[m][c] = (np.nanpercentile(boot, 5), np.nanpercentile(boot, 95))
    for m in MET:
        ratios = []
        for c in ctx.cities:
            D, n = ctx.dense[c], len(ctx.days[c])
            K = n // 2
            subs = [RNG.choice(n, K, replace=False) for _ in range(150)]
            emp = np.nanstd([D.all(s_)[m] for s_ in subs]) / np.sqrt((n - K) / (n - 1))
            bs = np.mean([np.nanstd([D.all(s_[RNG.integers(0, K, K)])[m] for _ in range(80)]) for s_ in subs[:20]])
            ratios.append(bs / emp if emp > 0 else np.nan)
        keys = list(ctx.cities)
        lo = np.array([ci[m][c][0] for c in keys])
        hi = np.array([ci[m][c][1] for c in keys])
        pairs = [(i, j) for i in range(len(keys)) for j in range(i + 1, len(keys))]
        overlap = sum(1 for i, j in pairs if not (hi[i] < lo[j] or hi[j] < lo[i]))
        rows.append({"metric": m, "median_ci90_halfwidth": float(np.nanmedian((hi - lo) / 2)), "median_boot_over_empirical_se": float(np.nanmedian(ratios)),
                     "p10_ratio": float(np.nanpercentile(ratios, 10)), "p90_ratio": float(np.nanpercentile(ratios, 90)),
                     "city_pairs": len(pairs), "pairs_indistinguishable": overlap, "share_indistinguishable": overlap / len(pairs)})
    report("t12_bootstrap", pd.DataFrame(rows), "(ratio ~1 => bootstrap SE realistic; CI = 90% over all valid weekdays)")


def t25(ctx):
    """Automatic sanity checks on segment values (all-day, segments with n>=10 and >=5 days)."""
    rows = []
    for c in ctx.cities:
        D = ctx.dense[c]
        seg, m = D.seg_idx, D.seg_idx.max() + 1
        n = np.bincount(seg, weights=D.n.sum(0), minlength=m)
        L = np.bincount(seg, weights=D.L.sum(0), minlength=m)
        T = np.bincount(seg, weights=D.T.sum(0), minlength=m)
        dp = np.zeros(m)
        for i in range(len(D.days)):
            dp += np.bincount(seg, weights=D.n[i], minlength=m) > 0
        k = (n >= 10) & (dp >= 5)
        sp = L[k] / T[k] * 3.6
        ln = L[k] / n[k]
        rows.append({"city": c, "segments": int(k.sum()), "speed_p1": np.percentile(sp, 1), "speed_p99": np.percentile(sp, 99), "share_gt50": float((sp > 50).mean()),
                     "share_lt5": float((sp < 5).mean()), "share_len_lt150m": float((ln < 150).mean()), "median_len_m": float(np.median(ln))})
    report("t25_sanity", pd.DataFrame(rows), "(segments with n>=10, >=5 days, in area)")


def t13(ctx):
    """W1 variants: sum(L)/sum(T) vs length-weighted median vs W1 without the slowest 1% (by speed), per mode."""
    rows = []
    for c in ctx.cities:
        parts = []
        for d in ctx.days[c]:
            x = pd.read_parquet(tm.L0 / c / f"{d}.parquet", columns=["mode", "seg_status", "seg_dist_m", "seg_time_s", "seg_in_area", "hour"])
            x = x[x["mode"].isin(["bus", "tram"]) & x.seg_in_area & (x.seg_status == "ok") & (x.seg_time_s > 0) & (x.seg_dist_m > 0)]
            parts.append(x[["mode", "seg_dist_m", "seg_time_s", "hour"]])
        x = pd.concat(parts)
        x["speed"] = x.seg_dist_m / x.seg_time_s * 3.6
        for label, g in (("all", x), ("bus", x[x["mode"] == "bus"]), ("tram", x[x["mode"] == "tram"]), ("trimmed_hours_7_20", x[(x.hour >= 7) & (x.hour <= 20)])):
            if len(g) < 5000:
                continue
            o = np.argsort(g.speed.to_numpy())
            v, w = g.speed.to_numpy()[o], g.seg_dist_m.to_numpy()[o]
            cum = np.cumsum(w)
            wmed = float(v[np.searchsorted(cum, cum[-1] / 2)])
            q01 = g.speed.quantile(0.01)
            gg = g[g.speed >= q01]
            rows.append({"city": c, "subset": label, "w1_sumL_over_sumT": g.seg_dist_m.sum() / g.seg_time_s.sum() * 3.6, "w1_weighted_median": wmed,
                         "w1_without_slowest_1pct": gg.seg_dist_m.sum() / gg.seg_time_s.sum() * 3.6, "n": len(g)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "t13_w1_variants_by_city.csv", index=False)
    s = []
    for sub, g in df.groupby("subset"):
        s.append({"subset": sub, "cities": len(g), "rho_sumLT_vs_weighted_median": spearman(g.w1_sumL_over_sumT, g.w1_weighted_median),
                  "flips_vs_median": flips(g.w1_sumL_over_sumT, g.w1_weighted_median), "rho_vs_without_slowest_1pct": spearman(g.w1_sumL_over_sumT, g.w1_without_slowest_1pct),
                  "median_diff_kmh_to_median": float((g.w1_weighted_median - g.w1_sumL_over_sumT).median())})
    report("t13_w1_variants", pd.DataFrame(s), "(rho < 0.9 => publish both / robust variant, docs/03 §9)")


def t15(ctx):
    """W10 thresholds; W3 reference bands / min n; from cells."""
    ref10 = ctx.vec(lambda c: ctx.dense[c].w10(ctx.all_idx(c)))
    rows = []
    for name, ot in (("(-60,120)", (-60, 120)), ("(-60,180) base", (-60, 180)), ("(-60,300)", (-60, 300)), ("(-120,180)", (-120, 180)), ("(-30,180)", (-30, 180)), ("(0,180)", (0, 180))):
        v = ctx.vec(lambda c, ot=ot: ctx.dense[c].w10(ctx.all_idx(c), ot))
        rows.append({"metric": "w10", "variant": name, "rho_vs_base": spearman(v, ref10), "pair_flips": flips(v, ref10), "median_value": float(np.nanmedian(v))})
    for band in ("am_peak", "pm_peak"):
        ref = ctx.vec(lambda c, b=band: ctx.dense[c].w3(ctx.all_idx(c), b))
        for name, kw in (("ref midday only", {"ref_bands": ["midday"]}), ("ref evening only", {"ref_bands": ["evening"]}), ("min_n 5", {"min_n": 5}), ("min_n 20", {"min_n": 20}), ("min_n 40", {"min_n": 40})):
            v = ctx.vec(lambda c, b=band, kw=kw: ctx.dense[c].w3(ctx.all_idx(c), b, **kw))
            rows.append({"metric": f"w3_{band}", "variant": name, "rho_vs_base": spearman(v, ref), "pair_flips": flips(v, ref), "median_value": float(np.nanmedian(v))})
    report("t15_w10_w3_variants", pd.DataFrame(rows))


def t16(ctx):
    """W11: frequent-line threshold, winsorisation, skipped vehicles; and does EWT track the share of skipped vehicles?"""
    def w11(c, **kw):
        return tp.w11_from(ctx.store[c], ctx.days[c], **kw)
    ref = ctx.vec(lambda c: w11(c))
    rows = []
    for name, kw in (("frequent 480", {"frequent_s": 480}), ("frequent 720", {"frequent_s": 720}), ("no winsor", {"winsor": None}), ("winsor 0.95", {"winsor": 0.95}), ("drop skips", {"drop_skips": True})):
        v = ctx.vec(lambda c, kw=kw: w11(c, **kw))
        rows.append({"variant": name, "rho_vs_base": spearman(v, ref), "pair_flips": flips(v, ref), "median_value": float(np.nanmedian(v)), "n_nan": int(np.isnan(v).sum())})
    report("t16_w11_variants", pd.DataFrame(rows), f"(base median EWT {np.nanmedian(ref):.3f} min)")
    cor = []
    for c in ctx.cities:
        e, sk = [], []
        for d in ctx.days[c]:
            a = ctx.store[c][d]["hw"]
            a = a[a[:, 1] < CFG["regularity"]["frequent_headway_s"]]
            if len(a) < 100:
                continue
            e.append(tp.w11_from(ctx.store[c], [d]))
            sk.append((a[:, 2] > 0).mean())
        if len(e) >= 8:
            cor.append({"city": c, "days": len(e), "corr_ewt_vs_skip_share": np.corrcoef(e, sk)[0, 1], "mean_skip_share": float(np.mean(sk))})
    cd = pd.DataFrame(cor)
    report("t16_ewt_vs_skipped_vehicles", cd, "(corr>0.5 => EWT partly measures missing vehicles)")
    print("median corr:", float(cd.corr_ewt_vs_skip_share.median()), " share corr>0.5:", float((cd.corr_ewt_vs_skip_share > 0.5).mean()))


def t18(ctx):
    """Distribution of network length over the 5 speed classes per city (segments passing 'ok': n>=10, days>=5)."""
    rows = []
    for c in ctx.cities:
        D = ctx.dense[c]
        seg, m = D.seg_idx, D.seg_idx.max() + 1
        n = np.bincount(seg, weights=D.n.sum(0), minlength=m)
        L = np.bincount(seg, weights=D.L.sum(0), minlength=m)
        T = np.bincount(seg, weights=D.T.sum(0), minlength=m)
        dp = np.zeros(m)
        for i in range(len(D.days)):
            dp += np.bincount(seg, weights=D.n[i], minlength=m) > 0
        k = (n >= CFG["segment_min"]["ok"]["n_obs"]) & (dp >= CFG["segment_min"]["ok"]["n_days"])
        sp = np.where(T > 0, L / np.where(T > 0, T, 1) * 3.6, np.nan)
        length = L / np.where(n > 0, n, 1)
        cls = np.searchsorted(EDGES, sp[k], side="right")
        tot = length[k].sum()
        row = {"city": c, "segments": int(k.sum())}
        for i in range(len(EDGES) + 1):
            row[f"class{i + 1}"] = float(length[k][cls == i].sum() / tot)
        rows.append(row)
    df = pd.DataFrame(rows)
    cl = [f"class{i + 1}" for i in range(len(EDGES) + 1)]
    df["max_class"], df["min_class"] = df[cl].max(axis=1), df[cl].min(axis=1)
    report("t18_speed_classes", df, "(share of network length; rule: no class >35% or <8% in most cities)")
    print("cities with a class >35%:", int((df.max_class > 0.35).sum()), " with a class <8%:", int((df.min_class < 0.08).sum()), "of", len(df))


def t19(ctx):
    """Effect of the area filter (W0) on the ranking: W1 with vs without the polygon."""
    rows = []
    for c in ctx.cities:
        L1 = T1 = L0 = T0 = 0.0
        for d in ctx.days[c]:
            x = pd.read_parquet(tm.L0 / c / f"{d}.parquet", columns=["mode", "seg_status", "seg_dist_m", "seg_time_s", "seg_in_area"])
            x = x[x["mode"].isin(["bus", "tram"]) & (x.seg_status == "ok") & (x.seg_time_s > 0) & (x.seg_dist_m > 0)]
            L0 += x.seg_dist_m.sum(); T0 += x.seg_time_s.sum()
            y = x[x.seg_in_area]
            L1 += y.seg_dist_m.sum(); T1 += y.seg_time_s.sum()
        rows.append({"city": c, "w1_no_area": L0 / T0 * 3.6, "w1_area": L1 / T1 * 3.6})
    df = pd.DataFrame(rows)
    df["shift"] = df.w1_area - df.w1_no_area
    df.to_csv(OUT / "t19_area_effect_by_city.csv", index=False)
    print(df.round(2).to_string(index=False))
    report("t19_area_effect", pd.DataFrame([{"rho_area_vs_no_area": spearman(df.w1_area, df.w1_no_area), "pair_flips": flips(df.w1_area, df.w1_no_area),
                                            "median_shift_kmh": float(df["shift"].median()), "max_abs_shift_kmh": float(df["shift"].abs().max())}]))


def t20(ctx):
    """Rank correlations between dimensions (pooled over valid weekdays)."""
    df = pd.DataFrame({m: ctx.vec(lambda c, m=m: ctx.dense[c].all(ctx.all_idx(c))[m]) for m in MET}, index=ctx.cities)
    df.to_csv(OUT / "t20_city_values.csv")
    cor = df.rank().corr()
    cor.to_csv(OUT / "t20_dimension_rank_correlations.csv")
    print("\n== t20 pooled values\n", df.round(2).to_string(), "\n\n== rank correlations between dimensions\n", cor.round(2).to_string())


def t22(ctx):
    """Are low-trip days days after a change of the static feed? Uses reports/m0/heads.jsonl fingerprints."""
    heads = pd.DataFrame([json.loads(l) for l in open(ROOT / "reports" / "m0" / "heads.jsonl", encoding="utf-8")])
    fp = [c for c in heads.columns if "fp" in c or "fingerprint" in c]
    print("heads columns with fingerprint:", fp)
    if not fp:
        print("no fingerprint column, skipped")
        return
    fc = fp[0]
    rows = []
    for c in ctx.cities:
        h = heads[(heads.city == c) & heads[fc].notna()].sort_values("date")[["date", fc]]
        h["changed"] = h[fc] != h[fc].shift()
        chg = dict(zip(h.date, h.changed))
        s = ctx.store[c]
        allw = [d for d in sorted(s) if pd.Timestamp(d).weekday() < 5 and tp.band_coverage(s[d]) >= CFG["day_gate"]["min_band_recorded_share"]]
        med = np.median([s[d]["n_trips"] for d in allw])
        for d in allw:
            rows.append({"city": c, "date": d, "trip_ratio": s[d]["n_trips"] / med, "low": s[d]["n_trips"] < CFG["day_gate"]["anomaly_min_trip_ratio"] * med, "static_changed": chg.get(d)})
    df = pd.DataFrame(rows).dropna(subset=["static_changed"])
    df.to_csv(OUT / "t22_low_trip_days_vs_static_change.csv", index=False)
    tab = pd.crosstab(df.static_changed, df.low)
    print("\n== t22 (rows: static changed vs previous day, cols: low-trip day)\n", tab)
    by_city = df.groupby("city").agg(days=("low", "size"), low_days=("low", "sum"), changed=("static_changed", "sum")).reset_index()
    report("t22_by_city", by_city)


TESTS = {"t4": t4, "t5": t5_t6, "t6": t5_t6, "t8": t8, "t9": t9, "t10": t10, "t11": t11, "t12": t12, "t13": t13, "t15": t15, "t16": t16, "t18": t18, "t19": t19, "t20": t20, "t22": t22, "t25": t25}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    ctx = Ctx()
    print(f"cities ({len(ctx.cities)}): {ctx.cities}; valid weekdays: { {c: len(ctx.days[c]) for c in ctx.cities} }")
    names = list(dict.fromkeys(TESTS)) if which == ["all"] else which
    done = set()
    for n in names:
        f = TESTS[n]
        if f in done:
            continue
        done.add(f)
        f(ctx)
