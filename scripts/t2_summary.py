"""Summarise reports/tests/t2_sweep.jsonl: effect of each reconstruction parameter on the city metrics.

Effect sizes are compared with the typical gap between NEIGHBOURING cities in the pooled ranking (t26 daily table),
because only an effect of that size can reorder two cities."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
rows = pd.DataFrame([json.loads(l) for l in open(ROOT / "reports/tests/t2_sweep.jsonl", encoding="utf-8")])
rows = rows.rename(columns={"w3_am": "w3_am", "w3_pm": "w3_pm"})
MET = ["w1", "w3_pm", "w10", "w11", "crossing_rate", "n_ok"]
daily = pd.read_csv(ROOT / "reports/tests/t26_trips/daily.csv")
pooled = daily.groupby("city")[["w1", "w3_pm", "w10", "w11"]].mean()
gap = {m: float(np.median(np.diff(np.sort(pooled[m].to_numpy())))) for m in pooled}
sd = {m: float(pooled[m].std()) for m in pooled}
print("typical gap between neighbouring cities:", {k: round(v, 3) for k, v in gap.items()}, "\nbetween-city SD:", {k: round(v, 3) for k, v in sd.items()})
out = []
for (city, date), g in rows.groupby(["city", "date"]):
    base = g[g.variant == "base"].iloc[0]
    for _, r in g.iterrows():
        if r.variant == "base":
            continue
        e = {"city": city, "date": date, "variant": r.variant}
        for m in MET:
            e[f"d_{m}"] = r[m] - base[m]
        e["d_w1_pct"] = (r.w1 / base.w1 - 1) * 100
        e["w1_over_gap"] = abs(r.w1 - base.w1) / gap["w1"]
        e["w10_over_gap"] = abs(r.w10 - base.w10) / gap["w10"]
        e["w3pm_over_gap"] = abs(r.w3_pm - base.w3_pm) / gap["w3_pm"]
        e["w11_over_gap"] = abs(r.w11 - base.w11) / gap["w11"]
        out.append(e)
df = pd.DataFrame(out)
df.to_csv(ROOT / "reports/tests/t2_effects.csv", index=False)
pd.set_option("display.width", 250)
print(df[["city", "date", "variant", "d_w1", "d_w1_pct", "d_w3_pm", "d_w10", "d_w11", "d_crossing_rate", "d_n_ok", "w1_over_gap", "w10_over_gap", "w3pm_over_gap", "w11_over_gap"]].round(3).to_string(index=False))
