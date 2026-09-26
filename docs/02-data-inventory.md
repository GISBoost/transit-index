# 02 · Inwentarz danych i ograniczenia

Stan na **2026-09-26**. Źródła: lista tagów `GISBoost/easy-GTFS-RT` (`git ls-remote --tags`), kod `tools/transit_charts` i `tools/family_a_reconstruction` z `GISBoost/easy-OTP`, oraz **zawartość release'ów pobrana i sprawdzona** (tidy + statyka z 2026-09-24 dla 15 miast, Łódź z 9 dni; szczegóły w `09-validation-on-real-data.md`). Publiczne adresy plików działają bez API GitHub.

## 1. Co jest publikowane

Dla każdego miasta i dnia release z tagiem `<miasto>-realized-<data>-phone` zawiera (według README i HOW-IT-WORKS):

| Załącznik | Zawartość | Uwagi dla indeksu |
|---|---|---|
| `<miasto>_tidy_<data>.csv.gz` | tabela całego feedu, jeden wiersz na rozkładowy przystanek każdego kursu | **główne wejście**; od 2026-08-03, tylko w przód |
| `<miasto>_static_gtfs_<data>.zip` | dokładnie ta statyka, której użyto | źródło geometrii (`shapes.txt`), trybu (`routes.txt`), współrzędnych przystanków |
| `<miasto>_realized_<data>_p50.zip`, `_p85.zip` | zrealizowany rozkład | **nie używać** do indeksu (patrz sekcja 4) |
| `<miasto>_diff_<data>_p50_summary.csv`, `_chart.png` | podsumowanie różnic | nie używać |

Adres pliku: `https://github.com/GISBoost/easy-GTFS-RT/releases/download/<tag>/<asset>`; pobieranie skryptem `reference/fetch_release_assets.py` (brak pliku = 404, zapisywany jako `missing` w manifeście pobrania).

Surowe pozycje (`positions-raw-*`) są kasowane po zbudowaniu; `matched.csv` nigdy nie jest wgrywany. Konsekwencja: **tidy jest jedyną trwałą postacią obserwacji**. Zabezpiecz ją (kopia w release'ach nowego repo).

## 2. Pokrycie (tagi realized `-phone`, snapshot 2026-09-25)

29 unikalnych nazw, z czego 28 jest w `config/cities.json`; `amsterdam` ma 1 dzień (test). Łącznie 1630 par miasto-dzień, z czego 1385 od 2026-08-03 (kiedy zaczęły się załączniki tidy). Kolumna "od 08-03" to górne ograniczenie liczby dostępnych tidy.

| miasto | dni (tag) | od 08-03 | pierwszy | ostatni |
|---|---|---|---|---|
| szczecin | 73 | 54 | 2026-07-15 | 2026-09-25 |
| lodz | 72 | 51 | 2026-07-13 | 2026-09-25 |
| vilnius | 72 | 53 | 2026-07-15 | 2026-09-25 |
| lisbon | 71 | 53 | 2026-07-15 | 2026-09-25 |
| prague | 71 | 52 | 2026-07-15 | 2026-09-25 |
| sofia | 71 | 52 | 2026-07-15 | 2026-09-25 |
| rome | 70 | 52 | 2026-07-15 | 2026-09-25 |
| boston | 68 | 51 | 2026-07-16 | 2026-09-25 |
| brisbane | 67 | 50 | 2026-07-17 | 2026-09-25 |
| bucharest | 65 | 46 | 2026-07-15 | 2026-09-25 |
| gdansk | 65 | 51 | 2026-07-20 | 2026-09-25 |
| poznan | 65 | 49 | 2026-07-15 | 2026-09-25 |
| turin | 60 | 44 | 2026-07-15 | 2026-09-25 |
| kielce | 54 | 53 | 2026-08-02 | 2026-09-25 |
| przemysl | 54 | 53 | 2026-08-02 | 2026-09-25 |
| radom | 54 | 53 | 2026-08-02 | 2026-09-25 |
| rybnik | 54 | 53 | 2026-08-02 | 2026-09-25 |
| rzeszow | 54 | 53 | 2026-08-02 | 2026-09-25 |
| suwalki | 54 | 53 | 2026-08-02 | 2026-09-25 |
| warszawa | 54 | 53 | 2026-08-02 | 2026-09-25 |
| elblag | 53 | 52 | 2026-08-02 | 2026-09-25 |
| lublin | 53 | 52 | 2026-08-02 | 2026-09-25 |
| krakow | 52 | 51 | 2026-08-02 | 2026-09-25 |
| gzm | 48 | 47 | 2026-08-02 | 2026-09-25 |
| nicosia | 41 | 41 | 2026-08-15 | 2026-09-25 |
| ljubljana | 40 | 40 | 2026-08-15 | 2026-09-25 |
| zagreb | 37 | 37 | 2026-08-15 | 2026-09-25 |
| lka | 37 | 36 | 2026-08-02 | 2026-09-08 |

Uwagi:
- `lka` (Łódzka Kolej Aglomeracyjna) to kolej; nagrania pozycji dotyczyły wcześniej złej sieci (autobusów zastępczych) i zostały wycofane, a realized dla ŁKA powstaje z TripUpdates (17 tagów `-tripupdates`). **Poza indeksem.**
- `gzm` to metropolia (wiele miast), nie miasto. Etykieta "GZM (metropolia)" i osobna decyzja, czy w rankingu.
- Istnieją też tagi `raw-*` dla miast bez realized (np. Helsinki 30, Ryga 21). Helsinki nie publikuje `trip_id`.
- Liczby niespójne w dokumentacji: README easy-GTFS-RT mówi o 13 nagrywanych miastach, strona główna GISBoost o 27, `cities.json` ma 28 wpisów. **M0: ustalić, które miasta mają ciągłe, użyteczne dane.**

## 3. Tabela tidy (kontrakt wejściowy)

Kolumny (`transit_charts.tidy.TIDY_COLUMNS`, 34 kolumny):

```
city, service_date, day_type, recording_date,
trip_id, route_id, route_short_name, route_group, direction_id, trip_headsign,
stop_sequence, stop_id, stop_name, shape_dist_m,
sched_arr, sched_dep, obs_time, obs_local, delay_s,
seg_time_s, sched_seg_time_s, seg_dist_m, seg_speed_kmh, seg_status,
is_first_stop, from_stop_id, from_stop_name,
headway_s, sched_headway_s, headway_spans_outage, headway_skips_vehicles,
trip_coverage, service_date_offset_days, service_date_plausible
```

Semantyka (z kodu, **potwierdzona na danych**: 15 plików ma dokładnie te 34 kolumny w tej kolejności; `seg_dist_m` i `seg_time_s` zgadzają się z różnicami `shape_dist_m` i `obs_time` do ~1e-11):
- Wiersz = rozkładowy przystanek kursu. Odcinek to para (`from_stop_id` → `stop_id`), kończąca się w tym wierszu.
- `seg_time_s` = czas przejazdu przez przystanek końcowy minus czas przejazdu przez początkowy, oba **interpolowane z pozycji GPS** (przejazd-do-przejazdu, więc **zawiera postój na przystanku początkowym**). `seg_dist_m` = odległość wzdłuż kształtu trasy. `seg_speed_kmh` = dystans/czas·3,6. To jest prędkość **komunikacyjna** (potwierdzone w kodzie: 100 km/h jako limit dla prędkości komunikacyjnej, decyzja Michała).
- `sched_seg_time_s` = przyjazd minus **odjazd** z poprzedniego przystanku (bez postoju). To inna konwencja niż `seg_time_s`, ale w praktyce różnica jest zerowa: rozkładowy postój (`sched_pass_time_s − sched_seg_time_s`) wynosi 0,0–0,7 s dla autobusów i tramwajów we wszystkich 15 miastach. Do porównania z rozkładem używaj `sched_pass_time_s` (`reference/metrics_reference.py`).
- `seg_status`: `ok`, `first_pair` (FA-20, pierwsza para pominięta), `stationary` (FA-18, < 2 km/h), `implausible` (FA-13: czas ≤ 0, > 2 h lub prędkość > 100 km/h, dla kolei 200 km/h), `gap` (brak przejazdu przez przystanek), `missing_stop_location`, `no_previous_stop`. **Etykiety są niestosowane**; wykresy i indeks muszą filtrować `seg_status == "ok"`.
- `obs_local` jest w **czasie lokalnym miasta** (potwierdzone: offsety +01:00 do +03:00), więc pasma godzinowe liczy się bezpośrednio z tej kolumny. Przejazd interpolowany liniowo między pingami; pary pingów odległe o > 300 s są odrzucane (FA-14); próbkowanie co 60 s.

**Czego brak w tidy** (trzeba dołożyć ze statyki **tego samego dnia**: statyka z innego dnia mapuje trasy tylko w 98,65% wierszy): geometria odcinka, tryb (`route_type` z `routes.txt`), współrzędne przystanków, `vehicle_id`.

### Rozmiary (2026-09-24, 15 miast)

- tidy: 4,7–80 MB na miasto-dzień (Łódź 19, Warszawa 72, Praga 80), razem **433 MB dziennie**;
- statyka: 3,7–108 MB na miasto, razem 416 MB dziennie, ale zmienia się rzadko: **deduplikuj po SHA-256**;
- wąska tabela obserwacji L0 (tylko `ok`, zstd): Łódź 1,2 MB, ok. 16× mniej niż tidy (`04` §5).

## 4. Czego nie używać

Feedy realized P50/P85: kotwiczone na rozkładowym pierwszym odjeździe, kubełki 2-godzinne, wszystkie kursy ze statyki (także nieobserwowane), P85 to górne ograniczenie sumy percentyli, nie percentyl podróży. Dla indeksu bezużyteczne (opis w `transit_charts/README.md` §13).

## 5. Znane defekty (uwzględnić w rejestrze `config/city_defects.yaml`)

| Miasto | Defekt | Skutek |
|---|---|---|
| Turyn | feed często bez `trip_id` (47–100% wpisów); **brak release'u 24.09** (są 20–23 i 25.09) | dni prawie puste i luki; **wykluczyć** lub bramka |
| Bukareszt | najsłabsze pokrycie w próbce: `crossing_rate` 0,71, udział `ok` 0,64 | prawdopodobnie `limited` (`03` §6) |
| Praga, Zagrzeb, Nikozja | wysokie prędkości autobusów (28,1 / 24,1 / 27,2) | linie podmiejskie; obowiązkowy filtr obszaru W0 (`03` §2) |
| Helsinki | brak `trip_id` w ogóle | nieużyteczne |
| Gdańsk | brak `current_stop_sequence` i `stop_id` w pozycjach | brak okna dopasowania, słabsze dopasowanie; ma `speed` na 100% encji |
| Łódź | wcześniej 97 `shape_id` bez geometrii; **24.09 wszystkie kursy mają geometrię**; przenumerowanie `trip_id` co 1–3 dni | wymagana statyka **tego samego dnia**; sprawdzaj odsetek kursów bez `shape_id` w każdym dniu |
| Poznań | statyka następnego okresu publikowana z wyprzedzeniem | ok. 1 dzień na 3 zdegradowany (wykrywać przez odsetek nieznanych `trip_id`) |
| Bukareszt (dodatkowo) | linie metra wykluczone z dopasowania; więcej szumu GPS | metro poza indeksem tak czy inaczej |
| Praga | kolej regionalna (route_type 2) | poza indeksem (tryby drogowe) |
| Boston | buildy sprzed 2026-07-28 tylko 25/126 linii | nie dotyczy tidy (od 08-03) |
| Wilno, Sofia | brak `current_stop_sequence` (tylko `stop_id`) | słabsze okno dopasowania |
| Wszystkie | pierwsza para przystanków chłonie postój na pętli (mediana 2,5–12 km/h vs 16–27 w środku kursu) | FA-20 ją odrzuca domyślnie; Łódź prawie bez artefaktu |

## 6. Wersje metody (nie mieszać)

- 2026-07-14: nagrywanie przeniesione na telefon (Termux).
- 2026-07-29/30: reguły FA-17→FA-20 (pierwsza para), FA-18 (< 2 km/h), FA-19.
- 2026-08-03: załącznik tidy w release'ach.
- 2026-08-09: poprawki D1–D3 i F12 dotyczą `build` (realized), nie tidy.
- **Workflow easy-GTFS-RT wykonuje checkout `easy-OTP`** – jeśli `main`, to metoda zmienia się po cichu. **M0: ustalić, jaki ref jest używany, i przypiąć tag** (`easy_otp_ref` w manifeście edycji).

## 7. Okno nagrywania i strefy czasowe (rozstrzygnięte)

Nagrywanie trwa ok. 06:00–22:00 **w czasie lokalnym miasta**, a `obs_local` jest lokalne. Wszystkie 10 sprawdzonych miast (9 zagranicznych) ma obserwacje w godzinach lokalnych 6–21, więc problemu stref czasu nie ma. Pasma: `am_peak` 7–8, `midday` 10–13, `pm_peak` 15–17, `evening` 19–21; godziny 6, 9, 14, 18 tylko w wartości całodziennej. **Bramka pasm:** miasto ma pasmo, jeśli nagranie pokrywa ≥ 90% godzin pasma.

## 8. Lista kontrolna M0 (stan po weryfikacji)

Zrobione (`09`): schemat 34 kolumn (15 plików), semantyka odcinków, strefy czasu, stabilność klucza odcinka w Łodzi (98,3–99,4%), rozmiary, luki (Turyn), rozkład prędkości i kalibracja klas.

Do zrobienia w M0 na pełnym oknie:
1. Inwentarz wszystkich par miasto-dzień z załącznikiem tidy i statyką (skrypt `fetch_release_assets.py` daje 404 jako `missing`); luki dzienne.
2. Stabilność schematu w całym okresie od 2026-08-03 (wersjonowanie?).
3. Stabilność `stop_id` między dniami dla pozostałych miast (nie tylko Łodzi).
4. Ref `easy-OTP` używany przez workflow; daty zmian metody.
5. Pokrycie pasm per miasto na wszystkich dniach.
6. Odsetek `seg_status == "ok"` per miasto i dzień; kandydaci na `excluded`.
7. Dostępność `QualityReport` (crossing rate, przerwy) poza tidy.
8. Poligony obszarów miast (`config/areas/`, D12) i audyt licencji.
