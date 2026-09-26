"""Generate PLACEHOLDER data into public/data/ ("dane zastepcze").

Real structure, invented values: nothing here is measured. Deterministic (seeded) so reruns give
identical files. Replace public/data/* with real files of the same shape (see src/lib/schema.ts,
README.md "Podmiana danych"); the UI does not change.

Run: py tools/gen_placeholder_data.py
"""
import json
import math
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "public" / "data"
PEAK = [7, 8, 9, 15, 16, 17]

# slug, name, name_en, region, region_en, [lon, lat], zoom, quality, radius km, hourly nulls, kpi, rank
CITIES = [
    ("warszawa", "Warszawa", "Warsaw", "mazowieckie", "Masovian", [21.012, 52.230], 11.2, "ranked", 8.0, 4, (19.4, 21.2), 1),
    ("rzeszow", "Rzeszów", "Rzeszów", "podkarpackie", "Subcarpathian", [22.000, 50.041], 12.0, "ranked", 4.5, 4, (18.1, 19.4), 2),
    ("lodz", "Łódź", "Łódź", "łódzkie", "Łódź", [19.456, 51.759], 11.6, "ranked", 6.0, 4, (17.8, 19.6), 3),
    ("kielce", "Kielce", "Kielce", "świętokrzyskie", "Świętokrzyskie", [20.628, 50.866], 12.0, "limited", 4.0, 7, (15.2, 16.9), 4),
    ("miasto-e", "Miasto E", "City E", "XX", "XX", [18.600, 53.010], 12.0, "out", 3.5, 24, (None, None), None),
]

LOC = {'warszawa': 'w Warszawie', 'rzeszow': 'w Rzeszowie', 'lodz': 'w Łodzi', 'kielce': 'w Kielcach', 'miasto-e': 'w Mieście E'}

# ranking placeholders: kmh per city (warszawa, rzeszow, lodz, kielce, miasto-e)
RANK = {
    "tram": {"day": (19.4, 18.1, 17.8, 15.2, None), "peak": (17.2, 17.5, 15.9, 13.6, None), "off": (21.0, 19.2, 19.7, 16.4, None)},
    "bus": {"day": (17.6, 16.8, 16.1, 14.4, None), "peak": (14.9, 15.7, 13.8, 12.3, None), "off": (19.6, 17.7, 18.1, 15.8, None)},
}


def r1(v):
    return None if v is None else round(v, 1)


def dip(h):
    """Daily speed factor: slower in the two peaks."""
    return 1 - 0.14 * math.exp(-((h - 8) ** 2) / 5) - 0.16 * math.exp(-((h - 16.5) ** 2) / 6)


def hourly(rng, base, plan, nulls):
    """plan: flat-ish with peak dips; meas: below plan; hours 0..nulls-1 are null (sample too small)."""
    p = [r1(plan * (1 - 0.5 * (1 - dip(h)))) for h in range(24)]
    m = [None if h < nulls else r1(base * dip(h) / 0.93 + rng.uniform(-0.25, 0.25)) for h in range(24)]
    return p, m


def offset(center, dx_km, dy_km):
    lon, lat = center
    return [round(lon + dx_km / (111.32 * math.cos(math.radians(lat))), 5), round(lat + dy_km / 110.57, 5)]


def segments(rng, city):
    slug, center, quality, R = city[0], city[5], city[7], city[8]
    feats, sid, stop_n = [], 0, 0
    lines = 8
    nodata_share = 0.07 if quality != "out" else 0.6

    def stop():
        nonlocal stop_n
        stop_n += 1
        return f"Przystanek {chr(65 + (stop_n - 1) % 26)}{(stop_n - 1) // 26 + 1 if stop_n > 26 else ''}"

    def make(a, b, r_frac, mode, route, names):
        nonlocal sid
        sid += 1
        nodata = rng.random() < nodata_share
        if nodata:
            arr15, arr50, arr85 = [None] * 24, [None] * 24, [None] * 24
        else:
            v = 8 + r_frac * 22 + rng.uniform(-4.5, 4.5)
            arr50, arr15, arr85 = [], [], []
            for h in range(24):
                if h < 4 and rng.random() < 0.85 or (h >= 22 and rng.random() < 0.4) or rng.random() < 0.02:
                    arr15.append(None); arr50.append(None); arr85.append(None)
                    continue
                m = max(3.0, v * dip(h) / 0.93)
                arr50.append(r1(m)); arr15.append(r1(m * 0.8)); arr85.append(r1(m * 1.18))
        plan = None if nodata else r1(max(x for x in arr50 if x is not None) * 1.06)
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [a, b]},
            "properties": {
                "id": f"{slug}-{sid:03d}", "route": route, "mode": mode,
                "stop_from": names[0], "stop_to": names[1], "plan_kmh": plan,
                "kmh_p15": arr15, "kmh_p50": arr50, "kmh_p85": arr85, "n": None,
            },
        })

    for i in range(lines):
        ang = i / lines * 2 * math.pi + rng.uniform(-0.15, 0.15)
        mode = "tram" if i % 2 == 0 else "bus"
        route = "11" if i == 0 else None
        prev, prev_name, k = center, stop(), 7 + rng.randint(0, 2)
        for j in range(1, k + 1):
            rr = R * j / k
            an = ang + rng.uniform(-0.05, 0.05)
            p = offset(center, math.cos(an) * rr * 1.25, math.sin(an) * rr * 0.9)
            nm = stop()
            make(prev, p, j / k, mode, route, (prev_name, nm))
            prev, prev_name = p, nm
    for ring in range(2):
        rad = R * (0.35 + 0.3 * ring)
        pts = [offset(center, math.cos(t / 20 * 2 * math.pi) * rad * 1.25, math.sin(t / 20 * 2 * math.pi) * rad * 0.9) for t in range(21)]
        names = [stop() for _ in pts]
        for t in range(20):
            if t % 5 != 4 or ring:
                make(pts[t], pts[t + 1], 0.35 + 0.3 * ring, "bus", None, (names[t], names[t + 1]))
    return {"type": "FeatureCollection", "features": feats}


def main():
    rng = random.Random(2026)
    (OUT / "segments").mkdir(parents=True, exist_ok=True)
    cities = []
    for c in CITIES:
        slug, name, name_en, region, region_en, center, zoom, quality, R, nulls, kpi, rank = c
        measured, plan = kpi
        p, m = hourly(rng, measured or 15.0, plan or 17.0, nulls)
        if quality == "out":
            p, m = [None] * 24, [None] * 24
        lines = [
            {"route": "11", "measured": r1((measured or 15) - 1.5), "plan": r1((plan or 17) - 0.4), "n": None},
            {"route": None, "measured": r1((measured or 15) + 1.2), "plan": r1((plan or 17) + 1.4), "n": None},
            {"route": None, "measured": r1((measured or 15) - 3.1), "plan": r1((plan or 17) - 2.0), "n": None},
            {"route": None, "measured": r1((measured or 15) + 3.3), "plan": r1((plan or 17) + 2.9), "n": None},
            {"route": None, "measured": None, "plan": r1((plan or 17) - 0.9), "n": None},
        ] if quality != "out" else []
        cities.append({
            "slug": slug, "name": name, "name_en": name_en, "name_loc": LOC[slug], "region": region, "region_en": region_en,
            "center": center, "zoom": zoom, "quality": quality, "coverage": None,
            "kpi": {"measured": measured, "plan": plan, "n": None, "rank": rank},
            "hourly": {"plan": p, "meas": m}, "lines": lines,
        })
        (OUT / "segments" / f"{slug}.geojson").write_text(
            json.dumps(segments(rng, c), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    ranking = {
        mode: {per: [{"slug": c[0], "kmh": v} for c, v in zip(CITIES, vals)] for per, vals in pers.items()}
        for mode, pers in RANK.items()
    }
    manifest = {
        "placeholder": True, "edition": "XXXX-XX", "generated": None, "peak_hours": PEAK,
        "thresholds": {"sample_min": None, "coverage_min": None},
        "files": [
            {"id": "segments", "name": "predkosci_odcinkow_XXXX-XX.csv", "format": "CSV", "encoding": "UTF-8", "license": None, "size_mb": None, "url": None},
            {"id": "ranking", "name": "ranking_miast_XXXX-XX.csv", "format": "CSV", "encoding": "UTF-8", "license": None, "size_mb": None, "url": None},
            {"id": "geojson", "name": "odcinki_XXXX-XX.geojson", "format": "GeoJSON", "encoding": "UTF-8", "license": None, "size_mb": None, "url": None},
        ],
        "editions": [{"edition": "XXXX-XX", "current": True, "published": None}],
    }
    for name, obj in (("cities", cities), ("ranking", ranking), ("manifest", manifest)):
        (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("public/data: cities, ranking, manifest,", len(CITIES), "segment files")


main()
