"""Referencyjna implementacja definicji z docs/03-metrics-spec.md.

To jest wykonywalna specyfikacja, nie kod produkcyjny: ma rozstrzygać wątpliwości
("co dokładnie znaczy kara szczytu?") i służyć jako punkt odniesienia dla testów w M2.
Uruchom: python reference/metrics_reference.py   (samotest na danych syntetycznych)

Kolumny wejściowe zgodne z tabelą tidy (transit_charts.tidy.TIDY_COLUMNS):
    trip_id, recording_date, stop_sequence, sched_arr, seg_dist_m, seg_time_s, seg_status,
    obs_local, service_date
oraz kolumny dokładane przez pipeline (docs/04):
    seg_id  - klucz odcinka fizycznego "from_stop_id>to_stop_id"
    mode    - "bus" | "tram" | "other" (z routes.txt statyki TEGO SAMEGO dnia)
    band    - pasmo doby (patrz BANDS)
Wartości wzorcowe policzone tymi funkcjami na prawdziwych danych: reference/golden_values.json.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Pasma czasu lokalnego (godzina końca odcinka). Godziny 6, 9, 14, 18 należą tylko do all_day.
BANDS = {
    "am_peak": (7, 8),
    "midday": (10, 11, 12, 13),
    "pm_peak": (15, 16, 17),
    "evening": (19, 20, 21),
}
DEFAULT_SPEED_EDGES_KMH = (15, 20, 25, 30)  # PROPOZYCJA: 5 klas = tokeny --speed-1..5 z design/, kalibracja na kwintylach (docs/03 §5)


def band_of_hour(hour: int) -> str:
    for name, hours in BANDS.items():
        if hour in hours:
            return name
    return "shoulder"


def hour_from_obs_local(obs_local: pd.Series) -> pd.Series:
    """Godzina lokalna z ISO-8601 z offsetem strefy (np. '2026-09-24 06:00:03+02:00').

    Kolumna obs_local jest już w czasie lokalnym miasta (zweryfikowane dla 10 miast), więc
    wystarczy wyciąć godzinę; nie konwertuj strefy ponownie.
    """
    return pd.to_numeric(obs_local.str.slice(11, 13), errors="coerce").astype("Int64")


def mode_from_route_type(route_type) -> str:
    """route_type GTFS (podstawowy i rozszerzony) -> tryb indeksu. Metro i kolej są poza indeksem."""
    t = int(route_type)
    if t == 0 or 900 <= t <= 999:
        return "tram"
    if t == 3 or 700 <= t <= 799 or t == 11 or 800 <= t <= 899:
        return "bus"  # trolejbusy doliczane do autobusów (z etykietą na stronie)
    return "other"


def minutes_per_10km(speed_kmh: float) -> float:
    """Czas przejazdu 10 km przy danej prędkości (analog TomTom: średni czas na 10 km)."""
    return 600.0 / speed_kmh


def usable(df: pd.DataFrame) -> pd.DataFrame:
    """Tylko odcinki, które przeszły filtry family_a (FA-13/14/18/20).

    seg_status == "ok" jest obowiązkowe: bez tego postój na pętli renderuje się jako
    korek o prędkości 1,5 km/h (patrz tidy.usable_segments).
    """
    return df[(df.seg_status == "ok") & (df.seg_time_s > 0) & (df.seg_dist_m > 0)]


def commercial_speed_kmh(df: pd.DataFrame) -> float:
    """Prędkość komunikacyjna = suma dystansów / suma czasów (ważona dystansem).

    To samo, co odległość / czas całej podróży pasażera, z postojami. Czas odcinka jest
    liczony przejazd-przez-przystanek do przejazdu-przez-przystanek, więc zawiera postój
    na przystanku początkowym.
    """
    u = usable(df)
    return float(u.seg_dist_m.sum() / u.seg_time_s.sum() * 3.6)


def weighted_median(values: pd.Series, weights: pd.Series) -> float:
    order = np.argsort(values.to_numpy())
    v = values.to_numpy()[order]
    w = weights.to_numpy()[order]
    cum = np.cumsum(w)
    return float(v[np.searchsorted(cum, cum[-1] / 2.0)])


def length_weighted_median_speed_kmh(df: pd.DataFrame) -> float:
    """Wariant odporny (test czułości dla commercial_speed_kmh)."""
    u = usable(df)
    speed = u.seg_dist_m / u.seg_time_s * 3.6
    return weighted_median(speed, u.seg_dist_m)


def sched_pass_time_s(df: pd.DataFrame) -> pd.Series:
    """Rozkładowy czas przejazd-do-przejazdu: sched_arr wiersza minus sched_arr poprzedniego
    przystanku tego samego kursu. Jednorodny z seg_time_s (który zawiera postój).

    Nie używaj sched_seg_time_s (przyjazd minus ODJAZD poprzedniego): w feedach polskich
    miast różnica wynosi ok. 0 s, ale w feedach z postojami w rozkładzie zaniża rozkład.
    """
    d = df.sort_values(["trip_id", "recording_date", "stop_sequence"], kind="stable")
    arr = pd.to_datetime(d.sched_arr, utc=True, errors="coerce")
    prev = arr.groupby([d.trip_id, d.recording_date], sort=False).shift()
    return (arr - prev).dt.total_seconds().reindex(df.index)


def speed_class(speed_kmh: float, edges=DEFAULT_SPEED_EDGES_KMH) -> int:
    """Numer klasy 0..len(edges) dla prędkości (klasa i ↔ token --speed-{i+1}) (lewostronnie domknięte przedziały)."""
    return int(np.searchsorted(np.asarray(edges, dtype=float), speed_kmh, side="right"))


def segment_quality(n_obs: int, n_days: int, ok_obs: int = 10, ok_days: int = 5, thin_obs: int = 3) -> str:
    """Status komórki odcinek x pasmo: 'ok', 'thin' (rysuj szrafem) albo 'none' (szary)."""
    if n_obs >= ok_obs and n_days >= ok_days:
        return "ok"
    if n_obs >= thin_obs:
        return "thin"
    return "none"


def peak_penalty_pct(
    df: pd.DataFrame,
    band: str,
    ref_bands=("midday", "evening"),
    min_n: int = 10,
) -> tuple[float, int, int]:
    """KARA SZCZYTU (W3): o ile dłużej trwa przejazd tych samych odcinków w paśmie `band`
    niż w pasmach odniesienia. Porównanie sparowane po odcinkach, bez arbitralnego kwantyla.

    Dla odcinka s: v_ref(s) = ΣL / ΣT w pasmach odniesienia. Kara = ΣT_band / Σ(L / v_ref) - 1.
    Odcinek liczy się tylko, gdy ma >= min_n obserwacji w paśmie i w odniesieniu.
    Zwraca (kara w %, liczba obserwacji, liczba odcinków).
    """
    u = usable(df)
    ref = u[u.band.isin(ref_bands)].groupby("seg_id").agg(Lr=("seg_dist_m", "sum"), Tr=("seg_time_s", "sum"), nr=("seg_time_s", "size"))
    ref = ref[ref.nr >= min_n]
    ref["vref"] = ref.Lr / ref.Tr  # m/s
    p = u[u.band == band].merge(ref[["vref"]], left_on="seg_id", right_index=True)
    n_band = p.groupby("seg_id").seg_time_s.transform("size")
    p = p[n_band >= min_n]
    if p.empty:
        return float("nan"), 0, 0
    expected = (p.seg_dist_m / p.vref).sum()
    return float((p.seg_time_s.sum() / expected - 1.0) * 100.0), int(len(p)), int(p.seg_id.nunique())


# --- Wariant eksperymentalny (NIE do rankingu): spowolnienie względem P85 ---------------------

def free_flow_kmh(
    df: pd.DataFrame,
    q: float = 0.85,
    min_obs: int = 30,
    min_days: int = 5,
    min_bands: int = 3,
) -> pd.Series:
    """Prędkość 'swobodna' odcinka = kwantyl q rozkładu prędkości ze wszystkich pasm.

    UWAGA: wynik spowolnienia względem tej prędkości zależy od q niemal liniowo (Łódź, 9 dni:
    q=0,5 -> 5%; 0,7 -> 21%; 0,85 -> 37%; 0,95 -> 57%), więc wartość bezwzględna nie ma
    interpretacji. Zostaje jako wariant eksperymentalny; rankingowa jest kara szczytu.
    """
    u = usable(df).copy()
    u["speed_kmh"] = u.seg_dist_m / u.seg_time_s * 3.6
    g = u.groupby("seg_id")
    ff = g.speed_kmh.quantile(q)
    ok = (g.size() >= min_obs) & (g.service_date.nunique() >= min_days) & (g.band.nunique() >= min_bands)
    return ff.where(ok)


def slowdown_pct(df: pd.DataFrame, ff: pd.Series) -> float:
    """Spowolnienie = suma rzeczywistych czasów / suma czasów przy prędkości swobodnej - 1."""
    u = usable(df)
    ff_obs = u.seg_id.map(ff)
    u = u[ff_obs.notna()]
    ff_obs = ff_obs[ff_obs.notna()]
    t_ff = u.seg_dist_m / (ff_obs / 3.6)
    return float((u.seg_time_s.sum() / t_ff.sum() - 1.0) * 100.0)


def _self_test() -> None:
    # 1. prędkość komunikacyjna: 1000 m w 180 s = 20 km/h
    df = pd.DataFrame(
        {"seg_dist_m": [500.0, 500.0], "seg_time_s": [60.0, 120.0], "seg_status": ["ok", "ok"]}
    )
    assert abs(commercial_speed_kmh(df) - 20.0) < 1e-9
    assert abs(minutes_per_10km(20.0) - 30.0) < 1e-9

    # 2. odcinek z etykietą "stationary" nie wchodzi do statystyk
    df2 = pd.concat(
        [df, pd.DataFrame({"seg_dist_m": [500.0], "seg_time_s": [3000.0], "seg_status": ["stationary"]})],
        ignore_index=True,
    )
    assert abs(commercial_speed_kmh(df2) - 20.0) < 1e-9

    # 3. mediana ważona
    assert weighted_median(pd.Series([10, 20, 30]), pd.Series([1, 1, 2])) == 20.0

    # 4. tryby: typy podstawowe i rozszerzone (Gdańsk używa 700 i 900), metro i kolej poza indeksem
    assert [mode_from_route_type(t) for t in (0, 900, 3, 700, 11, 800, "3")] == ["tram", "tram", "bus", "bus", "bus", "bus", "bus"]
    assert [mode_from_route_type(t) for t in (1, 400, 2, 100, 5)] == ["other"] * 5

    # 5. pasma i godzina lokalna z obs_local
    assert [band_of_hour(h) for h in (6, 7, 9, 10, 14, 15, 18, 19, 21)] == [
        "shoulder", "am_peak", "shoulder", "midday", "shoulder", "pm_peak", "shoulder", "evening", "evening"]
    assert int(hour_from_obs_local(pd.Series(["2026-09-24 06:00:03.358099+02:00"]))[0]) == 6

    # 6. klasy prędkości (5 klas) (krawędzie lewostronnie domknięte)
    assert [speed_class(v) for v in (9.9, 14.9, 15.0, 19.9, 20.0, 29.9, 30.0, 55.0)] == [0, 0, 1, 1, 2, 3, 4, 4]

    # 7. status komórki
    assert segment_quality(12, 6) == "ok"
    assert segment_quality(20, 3) == "thin"
    assert segment_quality(5, 2) == "thin"
    assert segment_quality(2, 1) == "none"

    # 8. rozkładowy czas przejazd-do-przejazdu (różni się od sched_seg_time_s, gdy jest postój)
    sched = pd.DataFrame({
        "trip_id": ["t"] * 3, "recording_date": ["2026-09-24"] * 3, "stop_sequence": [1, 2, 3],
        "sched_arr": ["2026-09-24 10:00:00+00:00", "2026-09-24 10:02:00+00:00", "2026-09-24 10:05:30+00:00"],
    })
    assert sched_pass_time_s(sched).tolist()[1:] == [120.0, 210.0]

    # 9. kara szczytu: odcinek A: odniesienie 20 km/h (10 przejazdów), szczyt 10 km/h (10 przejazdów) -> +100%
    rows = []
    for band, v in (("midday", 20.0), ("evening", 20.0), ("pm_peak", 10.0)):
        for _ in range(10 if band != "evening" else 5):
            rows.append({"seg_id": "A", "band": band, "seg_dist_m": 500.0, "seg_time_s": 500.0 / (v / 3.6), "seg_status": "ok"})
    d = pd.DataFrame(rows)
    pct, n, segs = peak_penalty_pct(d, "pm_peak")
    assert abs(pct - 100.0) < 1e-6 and n == 10 and segs == 1, (pct, n, segs)
    # brak odniesienia (za mało obserwacji) -> odcinek pominięty
    assert np.isnan(peak_penalty_pct(d, "pm_peak", ref_bands=("am_peak",))[0])

    # 10. wariant eksperymentalny: 30 przejazdów po 20 km/h i 10 po 10 km/h -> +25% względem P85
    speeds = [20.0] * 30 + [10.0] * 10
    rows = []
    for i, v in enumerate(speeds):
        rows.append({"seg_id": "S1", "seg_dist_m": 500.0, "seg_time_s": 500.0 / (v / 3.6), "seg_status": "ok",
                     "service_date": f"2026-10-{1 + i % 6:02d}", "band": ["am_peak", "midday", "pm_peak"][i % 3]})
    d = pd.DataFrame(rows)
    ff = free_flow_kmh(d)
    assert abs(ff["S1"] - 20.0) < 1e-9, ff
    assert abs(slowdown_pct(d, ff) - 25.0) < 1e-6
    assert free_flow_kmh(d.head(10)).isna().all()  # za mała próba

    print("metrics_reference: wszystkie testy przeszły")


if __name__ == "__main__":
    _self_test()
