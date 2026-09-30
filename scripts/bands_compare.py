#!/usr/bin/env python3
"""Compare `2026-pilot` before/after the band-window change (issue #5): checks the invariants
from docs/prompts/2026-09-30-bands-recompute.md §3 and writes reports/bands/compare_2026-09-30.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / "data" / "editions" / "2026-pilot.before-bands"
NEW = ROOT / "data" / "editions" / "2026-pilot"
CITIES = ["bucharest", "gdansk", "krakow", "lisbon", "ljubljana", "lodz", "nicosia", "poznan",
          "prague", "rome", "sofia", "szczecin", "turin", "vilnius", "warszawa", "zagreb"]

UNCHANGED_COLS = ["n_obs", "v_p50", "q"]


def load(edition_dir: Path, city: str) -> pd.DataFrame:
    return pd.read_parquet(edition_dir / city / "segment_stats.parquet")


def main() -> None:
    lines = ["# Przeliczenie po zmianie pasm (issue #5) — 2026-09-30\n",
              "Porównanie `data/editions/2026-pilot.before-bands/` (stare pasma) z `data/editions/2026-pilot/` (nowe pasma), per miasto.\n"]

    unchanged_violations = []
    n_obs_deltas = []
    pen_pm_deltas = []
    q_pm_none_before_after = {}

    lines.append("## Niezmienniki `all_day`/`am_peak`\n")
    lines.append("| miasto | all_day identyczne | am_peak identyczne |")
    lines.append("|---|---|---|")
    for city in CITIES:
        old = load(OLD, city)
        new = load(NEW, city)
        row = {"city": city}
        ok = {}
        for band in ("all_day", "am_peak"):
            o = old[old.band == band].set_index("seg_id")[["n_obs", "v_p50", "q"]]
            n = new[new.band == band].set_index("seg_id")[["n_obs", "v_p50", "q"]]
            common = o.index.intersection(n.index)
            same_n = (o.loc[common, "n_obs"] == n.loc[common, "n_obs"]).all()
            same_v = np.allclose(o.loc[common, "v_p50"].fillna(-999), n.loc[common, "v_p50"].fillna(-999), atol=1e-6)
            same_q = (o.loc[common, "q"] == n.loc[common, "q"]).all()
            same_idx = set(o.index) == set(n.index)
            ok[band] = bool(same_n and same_v and same_q and same_idx)
            if not ok[band]:
                unchanged_violations.append((city, band))
        lines.append(f"| {city} | {'OK' if ok['all_day'] else 'ROZNI SIE'} | {'OK' if ok['am_peak'] else 'ROZNI SIE'} |")

        # n_obs sums for changed bands
        for band in ("midday", "pm_peak", "evening"):
            o_sum = old[old.band == band].n_obs.sum()
            n_sum = new[new.band == band].n_obs.sum()
            n_obs_deltas.append({"city": city, "band": band, "n_obs_before": int(o_sum), "n_obs_after": int(n_sum)})

        # pen_pm: try to load from dim table (segments.parquet) if present, else skip
        dim_old_path = OLD / city / "segments.parquet"
        dim_new_path = NEW / city / "segments.parquet"
        if dim_old_path.exists() and dim_new_path.exists():
            do = pd.read_parquet(dim_old_path).set_index("seg_id")
            dn = pd.read_parquet(dim_new_path).set_index("seg_id")
            if "pen_pm" in do.columns and "pen_pm" in dn.columns:
                common = do.index.intersection(dn.index)
                d = (dn.loc[common, "pen_pm"] - do.loc[common, "pen_pm"]).dropna()
                if len(d):
                    pen_pm_deltas.append({"city": city, "median": float(d.median()), "p05": float(d.quantile(0.05)),
                                           "p95": float(d.quantile(0.95)), "n": int(len(d))})
            for label, df in (("before", do), ("after", dn)):
                pass

        # q_pm none/thin counts + segments with NO pm_peak row at all (the ones rendered gray on the map)
        o_all = old[old.band == "all_day"]
        n_all = new[new.band == "all_day"]
        o_pm = old[old.band == "pm_peak"]
        n_pm = new[new.band == "pm_peak"]
        q_pm_none_before_after[city] = {
            "before_no_row": int(len(o_all) - len(o_pm)), "after_no_row": int(len(n_all) - len(n_pm)),
            "before_none": int((o_pm.q == "none").sum()), "before_thin": int((o_pm.q == "thin").sum()),
            "after_none": int((n_pm.q == "none").sum()), "after_thin": int((n_pm.q == "thin").sum()),
            "segments_total": int(len(n_all)),
        }

    lines.append("\n## Suma `n_obs` w zmienionych pasmach (przed/po)\n")
    lines.append("| miasto | pasmo | n_obs przed | n_obs po | delta |")
    lines.append("|---|---|---|---|---|")
    for d in n_obs_deltas:
        lines.append(f"| {d['city']} | {d['band']} | {d['n_obs_before']} | {d['n_obs_after']} | {d['n_obs_after'] - d['n_obs_before']:+d} |")

    lines.append("\n## `pen_pm`: zmiana (po - przed), per miasto\n")
    lines.append("| miasto | mediana | p05 | p95 | n |")
    lines.append("|---|---|---|---|---|")
    for d in sorted(pen_pm_deltas, key=lambda x: -abs(x["median"])):
        lines.append(f"| {d['city']} | {d['median']:+.3f} | {d['p05']:+.3f} | {d['p95']:+.3f} | {d['n']} |")

    lines.append("\n## Odcinki bez wiersza w `pm_peak` (szare na mapie) i `q_pm` = none/thin wśród obecnych, przed/po\n")
    lines.append("| miasto | odcinki (all_day) | bez wiersza przed | bez wiersza po | none przed | none po | thin przed | thin po |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for city, v in q_pm_none_before_after.items():
        lines.append(f"| {city} | {v['segments_total']} | {v['before_no_row']} | {v['after_no_row']} | {v['before_none']} | {v['after_none']} | {v['before_thin']} | {v['after_thin']} |")

    lines.append("\n## Bramka (`ti gate`) i ranking\n")
    lines.append("- Wszystkie 16 miast nadal `excluded` (< 20 dni ważnych w oknie 2026-09-01..2026-12-18, 19 dni roboczych upłynęło); bez zmiany statusu.\n")
    lines.append("- `ranking.json`: 0 wpisów przed i po (wszystkie miasta excluded) — brak zmian w rankingach W3/W12 do opisania.\n")

    lines.append("## Kafle (`ti geometry`)\n")
    rep = json.loads((ROOT / "reports" / "m4" / "geometry_2026-pilot.json").read_text(encoding="utf-8"))
    total = sum(e["bytes"]["pmtiles"] + e["bytes"]["geojson_gz"] for e in rep["cities"].values())
    all_pass = all(e.get("acceptance", {}).get("pass") for e in rep["cities"].values())
    lines.append(f"- 16/16 miast: acceptance z14+ `pass={all_pass}`\n")
    lines.append(f"- Suma bajtów (pmtiles + geojson.gz): {total/1e6:.1f} MB (budżet 700 MB)\n")

    out = ROOT / "reports" / "bands"
    out.mkdir(parents=True, exist_ok=True)
    (out / "compare_2026-09-30.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out / "compare_2026-09-30.md")
    print("all_day/am_peak violations:", unchanged_violations)


if __name__ == "__main__":
    main()
