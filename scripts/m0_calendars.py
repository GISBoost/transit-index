#!/usr/bin/env python3
"""Generate config/calendars/<city>.yaml: explicit list of public holidays in the pilot window.

    py scripts/m0_calendars.py --from 2026-09-01 --to 2026-12-18

School breaks are NOT known to the `holidays` library: `school_breaks` stays empty and must be filled
by hand from official calendars (docs/05 §1a). Regional holidays (e.g. Italian patron saints) are not
covered by the country-level list.
"""
import argparse
import datetime as dt
from pathlib import Path

import holidays
import yaml

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end", required=True)
    a = ap.parse_args()
    start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    cities = yaml.safe_load((ROOT / "config" / "cities.yaml").read_text(encoding="utf-8"))["cities"]
    out_dir = ROOT / "config" / "calendars"
    out_dir.mkdir(parents=True, exist_ok=True)
    weekdays = sum(1 for i in range((end - start).days + 1) if (start + dt.timedelta(i)).weekday() < 5)
    for city, cfg in cities.items():
        if cfg["tier"] == "out_of_scope":
            continue
        hol = holidays.country_holidays(cfg["country"], years=range(start.year, end.year + 1))
        in_window = [(d, n) for d, n in sorted(hol.items()) if start <= d <= end]
        weekday_hol = [(d, n) for d, n in in_window if d.weekday() < 5]
        doc = {
            "city": city,
            "country": cfg["country"],
            "window": {"from": a.start, "to": a.end},
            "source": f"python-holidays {holidays.__version__}, country-level (no regional holidays)",
            "public_holidays": [{"date": d.isoformat(), "name": n, "weekday": d.strftime("%a")} for d, n in in_window],
            "school_breaks": [],  # TODO by hand from the official school calendar
            "weekdays_in_window": weekdays,
            "weekdays_minus_public_holidays": weekdays - len(weekday_hol),
        }
        (out_dir / f"{city}.yaml").write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"{city:10s} {cfg['country']}  weekday holidays: {[d.isoformat() for d, _ in weekday_hol]}")


if __name__ == "__main__":
    main()
