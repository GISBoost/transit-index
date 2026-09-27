"""List recording directories (day, n snapshots) inside a monthly raw-snapshots tar.xz."""
import collections, sys, tarfile

for path in sys.argv[1:]:
    c = collections.Counter()
    with tarfile.open(path) as t:
        for m in t:
            if m.isfile():
                c[m.name.split("/")[0]] += 1
    print(path.split("/")[-1])
    full = {k.split("_")[-2]: n for k, n in c.items() if n >= 900}
    print("  full days (>=900 snapshots):", sorted(full))
