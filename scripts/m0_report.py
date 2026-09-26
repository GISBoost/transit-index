#!/usr/bin/env python3
"""Build docs/data-inventory.generated.md from reports/m0/*.jsonl|csv (M0).

    py scripts/m0_report.py

Reads config/metrics.yaml (day_gate), config/cities.yaml and config/calendars/*.yaml. No numbers are
hard-coded here except the report layout.
"""
import json
from pathlib import Path

import datetime as dt

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "reports" / "m0"
OUT = ROOT / "docs" / "data-inventory.generated.md"
FULL_FROM = "2026-09-07"  # first day with a full-day recording (see section 2)
PILOT_TO = "2026-12-18"   # end of the pilot window (docs/05)


def jl(path: Path) -> pd.DataFrame:
    return pd.DataFrame([json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()])


def md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_brak danych_\n"
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(rows) + "\n"


def main() -> None:
    cfg = yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]
    gate = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))["day_gate"]
    heads = jl(REP / "heads.jsonl")
    heads = heads[heads.city.map(lambda c: cfg[c]["tier"] != "out_of_scope")]
    stats = jl(REP / "stats.jsonl") if (REP / "stats.jsonl").exists() else pd.DataFrame()
    first, last = heads.date.min(), heads.date.max()

    hol = {}
    for c in cfg:
        f = ROOT / "config" / "calendars" / f"{c}.yaml"
        if f.exists():
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
            hol[c] = {h["date"] for h in doc["public_holidays"]}

    out = [f"# Inwentarz danych na oknie {first} … {last} (wygenerowane)\n",
           "Wygenerowane przez `scripts/m0_inventory.py` i `scripts/m0_report.py`. Nie edytuj ręcznie. Surowe wyniki: `reports/m0/`.\n",
           "Metoda: (1) `heads`: dla każdej pary miasto-dzień zapytanie zakresowe o rozmiar tidy i statyki (bez pobierania) oraz odcisk zawartości statyki (SHA-256 z listy nazw, CRC32 i rozmiarów członków zip odczytanej z katalogu centralnego; tani zamiennik, **nie** SHA-256 pliku wymagany do deduplikacji w M1); (2) `stats`: dla miast `candidate` i dni roboczych pobranie tidy strumieniowo, statystyki, skasowanie pliku. "
           "Definicja dnia ważnego: `config/metrics.yaml` → `day_gate` "
           f"(`crossing_rate ≥ {gate['min_crossing_rate']}`, udział `ok ≥ {gate['min_ok_share']}`, wiarygodność `service_date ≥ {gate['min_plausible_service_date']}`, "
           f"pokrycie godzin każdego pasma ≥ {gate['min_band_recorded_share']}, gdzie godzina jest pokryta, jeśli ma ≥ 1% wierszy `ok`; to przybliżenie), bez świąt państwowych z `config/calendars/`.\n"]

    # ---- coverage (all cities)
    h = heads.copy()
    h["has_tidy"] = h.tidy_bytes.notna()
    h["wd"] = h.weekday < 5
    rows = []
    for c, g in h.groupby("city"):
        wd = g[g.wd]
        fp = g.dropna(subset=["static_fp"]).sort_values("date")
        rows.append({"miasto": c, "poziom": cfg[c]["tier"], "dni z tidy": int(g.has_tidy.sum()),
                     "dni robocze z tidy": int(wd.has_tidy.sum()), "dni robocze bez tidy": ", ".join(wd[~wd.has_tidy].date.str[5:]) or "-",
                     "tidy GB": round(g.tidy_bytes.sum() / 1e9, 2),
                     "statyka: liczba różnych wersji": int(fp.static_fp.nunique()),
                     "statyka: zmiany w dniach": ", ".join(fp[fp.static_fp != fp.static_fp.shift()].date.str[5:].iloc[1:]) or "-"})
    out += ["## 1. Pokrycie: obecność plików (wszystkie miasta w zakresie)\n", md(pd.DataFrame(rows).sort_values(["poziom", "miasto"]))]
    out.append(f"Łącznie plików tidy w oknie: {int(h.has_tidy.sum())}, {round(h.tidy_bytes.sum()/1e9, 1)} GB.\n")

    # ---- quality (candidates)
    if not stats.empty:
        s = stats[stats.status == "ok"].copy()
        band_min = s.band_hour_coverage.map(lambda d: min(d.values()) if isinstance(d, dict) and d else None)
        s["band_min"] = band_min
        s["holiday"] = [d in hol.get(c, set()) for c, d in zip(s.city, s.date)]
        s["gate_ok"] = ((s.crossing_rate >= gate["min_crossing_rate"]) & (s.ok_share >= gate["min_ok_share"])
                        & (s.service_date_plausible_share.fillna(1) >= gate["min_plausible_service_date"])
                        & (s.band_min.fillna(0) >= gate["min_band_recorded_share"]) & s.schema_ok)
        s["valid"] = s.gate_ok & ~s.holiday
        rows = []
        for c, g in s.groupby("city"):
            rows.append({"miasto": c, "dni robocze z danymi": len(g), "schemat 34 kol. OK": f"{int(g.schema_ok.sum())}/{len(g)}",
                         "dni święta": int(g.holiday.sum()), "dni ważne": int(g.valid.sum()),
                         "crossing min/med/max": f"{g.crossing_rate.min():.2f}/{g.crossing_rate.median():.2f}/{g.crossing_rate.max():.2f}",
                         "udział ok min/med/max": f"{g.ok_share.min():.2f}/{g.ok_share.median():.2f}/{g.ok_share.max():.2f}",
                         "dni ważne od 09-07": int(g[g.date >= FULL_FROM].valid.sum()),
                         "min. pokrycie pasma": round(g.band_min.min(), 2) if g.band_min.notna().any() else None,
                         "wiersze/dzień (med.)": int(g.rows.median())})
        out += ["## 2. Jakość dni (miasta kandydujące, dni robocze)\n", md(pd.DataFrame(rows)),
                "Dni niewazne (powód):\n"]
        bad = s[~s.valid][["city", "date", "crossing_rate", "ok_share", "band_min", "holiday", "schema_ok"]]
        out.append(md(bad.rename(columns={"city": "miasto", "date": "dzień", "band_min": "min. pokrycie pasma", "holiday": "święto", "schema_ok": "schemat OK"})))

        rows = []
        for c, g in s.groupby("city"):
            rows.append({"miasto": c,
                         "delay_s dostępne (W10) med.": g.delay_available_share.median(),
                         "headway_s dostępne (W11) med.": g.headway_available_share.median(),
                         "sched_headway dostępne med.": g.sched_headway_available_share.median(),
                         "udział wierszy linii częstych": g.frequent_row_share.median(),
                         "trip_coverage śr.": g.trip_coverage_mean.median()})
        d3 = pd.DataFrame(rows).round(3)
        out += ["## 3. Gotowość danych pod wymiary W10–W12 (mediany po dniach)\n",
                "Odsetek wierszy z wartością w kolumnach potrzebnych do punktualności (`delay_s`; liczone tylko dla wierszy z obserwacją, więc zawsze ok. 1,0 i mało informacyjne), regularności (`headway_s` wśród wierszy z obserwacją; `sched_headway_s` wśród wszystkich wierszy) oraz udział wierszy linii częstych (`sched_headway_s < frequent_headway_s`). **Mianownik udziału linii częstych to wiersze z `sched_headway_s`** (67–89% wszystkich), nie wszystkie wiersze. To wskaźnik wykonalności, nie wartość metryk.\n",
                md(d3)]

        # matrix city x weekday
        days = [d for d in pd.bdate_range(first, last).strftime("%Y-%m-%d")]
        rows = []
        for c in sorted(s.city.unique()):
            g = s[s.city == c].set_index("date")
            row = {"miasto": c}
            for d in days:
                if d in g.index:
                    r = g.loc[d]
                    row[d[5:]] = "H" if r.holiday else ("✓" if r.valid else "g")
                else:
                    row[d[5:]] = "–"
            rows.append(row)
        out += ["## 4. Macierz miasto × dzień roboczy (kandydaci)\n",
                "`✓` dzień ważny, `g` odrzucony przez bramkę dnia, `H` święto państwowe, `–` brak tidy. Dla wszystkich dni: `reports/m0/stats.jsonl` (crossing, udział `ok`, pokrycie pasm, rozmiary, SHA-256 tidy).\n",
                md(pd.DataFrame(rows))]

        # projection against the city gate
        cg = yaml.safe_load((ROOT / "config" / "metrics.yaml").read_text(encoding="utf-8"))["city_gate"]
        defects = yaml.safe_load((ROOT / "config" / "city_defects.yaml").read_text(encoding="utf-8"))["defects"]
        excluded_by_defect = {d["city"] for d in defects if d["action"].startswith("exclude")}
        rows = []
        for c in sorted(s.city.unique()):
            g = s[(s.city == c) & (s.date >= FULL_FROM)]
            all_wd = [d for d in pd.bdate_range(FULL_FROM, last).strftime("%Y-%m-%d") if d not in hol.get(c, set())]
            share = g.valid.sum() / len(all_wd)  # missing releases count as invalid days
            future = [d for d in pd.bdate_range(FULL_FROM, PILOT_TO).strftime("%Y-%m-%d") if d not in hol.get(c, set())]
            proj = round(share * len(future))
            status = ("ranked" if proj >= cg["ranked"]["min_valid_days"] else "limited" if proj >= cg["limited"]["min_valid_days"] else "excluded")
            if c in excluded_by_defect:
                status = "excluded (rejestr wad)"
            rows.append({"miasto": c, "dni ważne od 09-07": int(g.valid.sum()), "dni robocze bez świąt": len(all_wd),
                         "udział dni ważnych": round(share, 2), f"prognoza dni ważnych do {PILOT_TO[5:]}": proj,
                         "status wg bramki (bez pokrycia sieci)": status})
        out += ["## 5. Prognoza kwalifikacji miast do pilotażu\n",
                f"Założenie: udział dni ważnych od {FULL_FROM} utrzyma się do końca okna ({PILOT_TO}). Progi z `config/metrics.yaml` → `city_gate` (`ranked` ≥ {cg['ranked']['min_valid_days']} dni ważnych, `limited` ≥ {cg['limited']['min_valid_days']}). **Do dziś żaden kandydat nie ma jeszcze {cg['limited']['min_valid_days']} dni ważnych** (okno ma 15 dni roboczych od {FULL_FROM}), więc to prognoza, nie kwalifikacja. Nie uwzględnia pokrycia sieci (`min_network_coverage`, liczone w M2) ani licencji (`docs/licenses.md`).\n",
                md(pd.DataFrame(rows))]

    # ---- polygons
    pc = REP / "polygons_compare.csv"
    if pc.exists():
        out += ["## 6. Poligony miast: GISCO vs OSM (D12)\n",
                "GISCO = Urban Audit 2024, `URAU_RG_100K_2024_4326_CITIES`; OSM = relacja administracyjna z Nominatim. IoU liczone w EPSG:3035.\n",
                md(pd.read_csv(pc))]
    ae = REP / "area_effect.csv"
    if ae.exists():
        out += ["## 7. Wpływ poligonu na wyniki (2026-09-24, bus + tram)\n",
                "`obs_share` = udział obserwacji `ok` z obu przystankami w poligonie; prędkości `ΣL/ΣT` [km/h].\n", md(pd.read_csv(ae))]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print("written", OUT, len("\n".join(out)), "chars")


if __name__ == "__main__":
    main()
