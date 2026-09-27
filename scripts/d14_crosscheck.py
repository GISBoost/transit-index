"""M2 acceptance criterion (docs/07): cross-check one line against transit_charts' D14 chart
("segment speed by segment and hour"), as a separate process on the GPL tool - no import, just a
subprocess-equivalent call into easy-OTP's own package, reading the same tidy CSV `ti` reads.

Downloads one city-day's tidy+static (kept under data/raw/, gitignored), runs
`transit_charts.cli chart D14` for one route, and compares its n-weighted mean speed with `ti`'s
own ΣL/ΣT for the same route and days, straight from L0. Writes the comparison to
reports/m2/d14_crosscheck.json so the finding survives after data/raw/ is cleaned up again
(milestone-reviewer M2 found the first run of this check undocumented - the files had been
deleted after computing the numbers by hand instead of saving them here).

    py scripts/d14_crosscheck.py --city lodz --route 5 --dates 2026-09-23 2026-09-24
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EASY_OTP_CHARTS = ROOT.parent / "easy-OTP" / "tools" / "transit_charts"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "reference"))

import pandas as pd  # noqa: E402

import fetch_release_assets as fx  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default="lodz")
    ap.add_argument("--route", default="5")
    ap.add_argument("--dates", nargs="+", default=["2026-09-23", "2026-09-24"])
    a = ap.parse_args()

    raw = ROOT / "data" / "raw" / "d14_check"
    raw.mkdir(parents=True, exist_ok=True)
    tidy_paths = []
    for date in a.dates:
        p = raw / f"{a.city}_tidy_{date}.csv.gz"
        if fx.fetch(fx.url_for(a.city, date, "tidy"), p) == "missing":
            print(f"skip {date}: no tidy release")
            continue
        tidy_paths.append((date, p))
    if not tidy_paths:
        raise SystemExit("no tidy data available for the requested dates")

    out_prefix = raw / f"d14_{a.city}_route{a.route}"
    cmd = [sys.executable, "-m", "transit_charts.cli", "chart", "D14",
           "--out-prefix", str(out_prefix), "--route", a.route]
    for _, p in tidy_paths:
        cmd += ["--table", str(p)]
    subprocess.run(cmd, cwd=EASY_OTP_CHARTS, check=True)  # separate process, GPL tool, no import (CLAUDE.md)

    d14 = pd.read_csv(out_prefix.with_suffix(".csv"))
    d14_v_weighted = float((d14.speed_kmh * d14.n).sum() / d14.n.sum())

    ti_speeds = {}
    for date, _ in tidy_paths:
        l0 = pd.read_parquet(ROOT / "data" / "obs" / a.city / f"{date}.parquet")
        r = l0[(l0.route_short_name == a.route) & (l0["mode"].isin(("bus", "tram")))]
        ti_speeds[date] = float(r.seg_dist_m.sum() / r.seg_time_s.sum() * 3.6) if len(r) else None

    result = {
        "city": a.city, "route": a.route, "dates": [d for d, _ in tidy_paths],
        "d14_chart": {
            "n_weighted_mean_speed_kmh": round(d14_v_weighted, 2),
            "n_total": int(d14.n.sum()),
            "speed_range_kmh": [round(float(d14.speed_kmh.min()), 2), round(float(d14.speed_kmh.max()), 2)],
            "source": "easy-OTP/tools/transit_charts, chart D14 (segment speed by segment and hour), subprocess, no import (GPL)",
        },
        "ti_l0_sum_ratio_speed_kmh": {d: (round(v, 2) if v is not None else None) for d, v in ti_speeds.items()},
        "note": "Different aggregation on purpose: D14 grids by stop_sequence x time bucket with a "
                "min_n floor and reports a per-bucket median-ish speed; ti's number is Sigma L / Sigma T "
                "(docs/03 W1). Agreement in order of magnitude, no absurd values (>60 km/h) - that is "
                "the cross-check this criterion asks for, not an exact match of two different statistics.",
    }
    out = ROOT / "reports" / "m2" / "d14_crosscheck.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_out = ROOT / "reports" / "m2" / "d14_crosscheck_numbers.csv"
    shutil.copy(out_prefix.with_suffix(".csv"), csv_out)  # D14's own "numbers plotted" - durable evidence
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nwrote {out}\nwrote {csv_out}")


if __name__ == "__main__":
    main()
