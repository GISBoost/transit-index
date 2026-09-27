"""T1 helper: row-level diff between a published tidy table and one rebuilt from the raw archive."""
import sys
import numpy as np
import pandas as pd

pub, reb = (pd.read_csv(p, dtype={"trip_id": str, "stop_id": str, "route_id": str, "from_stop_id": str}, low_memory=False)
            for p in sys.argv[1:3])
print("rows published / rebuilt:", len(pub), len(reb), "| columns equal:", list(pub.columns) == list(reb.columns))
key = ["trip_id", "stop_sequence"]
for f in (pub, reb):
    f["_k"] = f.groupby(key).cumcount()
m = pub.merge(reb, on=key + ["_k"], how="outer", suffixes=("_p", "_r"), indicator=True)
print(m["_merge"].value_counts().to_dict())
both = m[m["_merge"] == "both"]
worst = []
for c in pub.columns:
    if c in key or c == "_k":
        continue
    a, b = both[c + "_p"], both[c + "_r"]
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b) and a.dtype != bool and b.dtype != bool:
        d = (a - b).abs()
        neq = ~((a == b) | (a.isna() & b.isna()) | (d < 1e-6))
    else:
        neq = ~((a == b) | (a.isna() & b.isna()))
    if neq.any():
        worst.append((c, int(neq.sum()), f"{neq.mean():.4%}"))
print("columns with differences (col, n_rows, share):")
for w in worst:
    print("  ", w)
if not worst:
    print("   none: identical")
