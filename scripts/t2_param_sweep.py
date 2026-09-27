"""T2/T3 (docs/10): sensitivity of city metrics to parameters baked into the tidy table, from raw snapshots.

Rebuilds one city-day from the monthly raw archive with variants of the reconstruction parameters and
records the dimension metrics of each variant. easy-OTP code (GPL-3.0) is run ONLY as separate processes
through its CLI (`family_a.cli match`, `transit_charts.cli extract`); nothing from it is imported here.

    set OTP_SRC=<dir with tools/family_a_reconstruction and tools/transit_charts (git archive bccb17b)>
    set OTP_PY=<python of a venv with numpy, pandas, gtfs-realtime-bindings, tzdata>
    py scripts/t2_param_sweep.py --city lodz --date 2026-08-12 [--variants base g120 ...]

Output: appends to reports/tests/t2_sweep.jsonl. Work files go to data/t2/ (gitignored).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import t_l0  # noqa: E402
import t_metrics as tm  # noqa: E402

RAW = ROOT / "data" / "raw_snap"
WORK = ROOT / "data" / "t2"
OUT = ROOT / "reports" / "tests" / "t2_sweep.jsonl"
OTP_SRC, OTP_PY = Path(os.environ["OTP_SRC"]), os.environ["OTP_PY"]
FA, TC = OTP_SRC / "tools" / "family_a_reconstruction", OTP_SRC / "tools" / "transit_charts"
EXCLUDE = {"bucharest": ["968", "969", "970", "971", "999"]}  # easy-GTFS-RT config/cities.json (Metrorex)

# variant -> (match extra args | None = reuse base match, extract extra args, decimation step)
VARIANTS = {
    "base": ([], [], 1),
    "g120": (None, ["--max-bracket-gap-seconds", "120"], 1),
    "g600": (None, ["--max-bracket-gap-seconds", "600"], 1),
    "ginf": (None, ["--max-bracket-gap-seconds", "1000000"], 1),  # no limit on the bracketing gap
    "kfs": (None, ["--keep-first-segment"], 1),          # first stop pair kept (FA-20 off)
    "bt0": (None, ["@bt0"], 1),                            # backward tolerance 0 m (function patch)
    "bt100": (None, ["@bt100"], 1),                        # backward tolerance 100 m
    "win_off": (["--position-signal-coverage-threshold", "1.01"], [], 1),  # FA-12 window disabled
    "perp50": (["--max-perpendicular-dist-m", "50"], [], 1),
    "perp200": (["--max-perpendicular-dist-m", "200"], [], 1),
    "dec2": ([], [], 2),                                   # every 2nd snapshot (~120 s sampling)
    "dec3": ([], [], 3),
}

BT_CODE = """
import functools, sys
sys.path.insert(0, r'{fa}')
import transit_charts.extract as ex
ex.collect_stop_crossings = functools.partial(ex.collect_stop_crossings, backward_tolerance_m={bt})
from transit_charts.cli import main
sys.exit(main(sys.argv[1:]))
"""


def sh(cmd, cwd, log):
    with open(log, "a", encoding="utf-8") as f:
        r = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode:
        raise RuntimeError(f"failed ({r.returncode}): {' '.join(map(str, cmd))} -> see {log}")


def prepare(city: str, date: str) -> tuple[Path, Path]:
    w = WORK / f"{city}_{date}"
    w.mkdir(parents=True, exist_ok=True)
    pos = w / "pos"
    shutil.rmtree(w / "_x", ignore_errors=True)
    if not pos.exists():
        with tarfile.open(RAW / f"{city}_snapshots_{date[:7]}.tar.xz") as t:
            members = [m for m in t.getmembers() if f"_{date}_" in m.name.split("/")[0]]
            dirs = {}
            for m in members:
                if m.isfile():
                    dirs.setdefault(m.name.split("/")[0], []).append(m)
            main_dir = max(dirs, key=lambda k: len(dirs[k]))  # the full-day session
            t.extractall(w / "_x", members=[m for m in members if m.name.split("/")[0] == main_dir])
        for attempt in range(8):  # Windows: freshly extracted files may be locked by a scanner for a moment
            try:
                shutil.copytree(w / "_x" / main_dir, pos)
                break
            except OSError:
                shutil.rmtree(pos, ignore_errors=True)
                time.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(f"could not stage {main_dir}")
        shutil.rmtree(w / "_x", ignore_errors=True)
    static = w / "static.zip"
    if not static.exists():
        urllib.request.urlretrieve(t_l0.fx.url_for(city, date, "static"), static)
    return w, static


def decimate(pos: Path, step: int, dest: Path) -> Path:
    if not dest.exists():
        dest.mkdir()
        for i, f in enumerate(sorted(pos.glob("snapshot_*.pb"))):
            if i % step == 0:
                shutil.copy(f, dest / f.name)
    return dest


def summarise(city, date, variant, tidy: Path, static: Path, secs) -> dict:
    mode_of, inside = t_l0.static_maps(static, city)
    d = tm.prep(t_l0.tidy_to_l0(tidy, city, mode_of, inside))
    row = {"city": city, "date": date, "variant": variant, "seconds": round(secs)}
    row.update(tm.city_metrics(d))
    row["rows"] = int(len(d))
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--variants", nargs="*", default=list(VARIANTS))
    a = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    w, static = prepare(a.city, a.date)
    log = w / "run.log"
    excl = [x for r in EXCLUDE.get(a.city, []) for x in ("--exclude-route-id", r)]
    matched: dict[str, Path] = {}

    def do_match(name, extra, step):
        if name in matched:
            return matched[name]
        pos = w / "pos" if step == 1 else decimate(w / "pos", step, w / f"pos_dec{step}")
        out = w / f"matched_{name}.csv"
        if not out.exists():
            sh([OTP_PY, "-m", "family_a.cli", "match", "--positions-dir", str(pos), "--static", str(static), "--out", str(out), *excl, *extra], FA, log)
        matched[name] = out
        return out

    for v in a.variants:
        m_extra, x_extra, step = VARIANTS[v]
        t0 = time.time()
        mname = "base" if m_extra is None else v if (m_extra or step > 1) else "base"
        m = do_match(mname, m_extra or [], step)
        tidy = w / f"tidy_{v}.csv.gz"
        cmd_tail = ["extract", "--matched", str(m), "--static", str(static), "--city", a.city, "--out", str(tidy)]
        if x_extra and x_extra[0].startswith("@bt"):
            bt = x_extra[0][3:]
            code = BT_CODE.format(fa=FA, bt=float(bt))
            sh([OTP_PY, "-c", code, *cmd_tail], TC, log)
        else:
            sh([OTP_PY, "-m", "transit_charts.cli", *cmd_tail, *x_extra], TC, log)
        if v == "base":  # T1 for this city-day: rebuilt tidy vs the published one
            pub = w / "published_tidy.csv.gz"
            if not pub.exists():
                urllib.request.urlretrieve(t_l0.fx.url_for(a.city, a.date, "tidy"), pub)
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "t1_compare_tidy.py"), str(pub), str(tidy)], capture_output=True, text=True)
            with open(OUT.with_name("t1_compare.txt"), "a", encoding="utf-8") as f:
                f.write("\n".join([f"== {a.city} {a.date}", r.stdout + r.stderr, ""]))
        row = summarise(a.city, a.date, v, tidy, static, time.time() - t0)
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
