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

Dzienne surowe pozycje (`positions-raw-*`) są kasowane po zbudowaniu dnia, ale **co miesiąc są archiwizowane jako kopia zapasowa** (potwierdzone przez właściciela 2026-09-26): telefon (`easy-OTP/scripts/termux/archive_monthly.sh`, codziennie, nadrabianie przez pierwsze 5 dni miesiąca) pakuje je per miasto do jednego archiwum `<miasto>_snapshots_<RRRR-MM>.tar.xz` (zwarty xz, ok. 10% rozmiaru) i wysyła do release'u **`raw-snapshots-<RRRR-MM>`** w `GISBoost/easy-GTFS-RT`. Istnieją `raw-snapshots-2026-07` (14 plików, 1,1 GB; część jako `.7z`, ręczna archiwizacja zaległości) i `raw-snapshots-2026-08` (31 plików, 7,1 GB); archiwum za wrzesień pojawi się na początku października. Użytkownicy widzą je w `gtfs-dashboard` (workflow `refresh-manifest.yml` rozpoznaje tagi `raw-snapshots-*`). `matched.csv` nie jest wgrywany. **Konsekwencja:** tidy jest trwałą, ale pochodną postacią obserwacji, a **historię można przebudować** nowszym kodem `family_a` z archiwów (nie sprawdzałem zawartości archiwów ani wykonalności przebudowy; to kosztowne: ok. 7 GB na miesiąc). Nasza kopia tidy/L0 w release'ach nowego repo jest dodatkowym zabezpieczeniem, nie jedynym.

## 2. Pokrycie (tagi realized `-phone`, snapshot 2026-09-25)

29 unikalnych nazw tagów; w `config/cities.json` jest teraz 27 miast (`lka` usunięto 2026-09-09, ma tylko stare tagi); `amsterdam` ma 1 dzień (test). Łącznie 1630 par miasto-dzień, z czego 1385 od 2026-08-03 (kiedy zaczęły się załączniki tidy). Kolumna "od 08-03" to górne ograniczenie liczby dostępnych tidy.

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
- Liczby niespójne w dokumentacji: README easy-GTFS-RT mówi o 13 nagrywanych miastach, strona główna GISBoost o 27, `cities.json` ma 27 wpisów (stan 2026-09-26). M0 ustalił, które miasta mają ciągłe dane: `docs/data-inventory.generated.md`.

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
- statyka: 3,7–108 MB na miasto, razem 416 MB dziennie. **M0 (okno 2026-09-01…25) pokazał, że zmienia się rzadko tylko w części miast** (odcisk z CRC32 członków zip: Zagrzeb i Elbląg 1 wersja w 25 dniach, Szczecin 3, Lublin i Radom 2, Rzeszów 4, Bukareszt 3), a w innych prawie codziennie (Praga, Warszawa, Wilno, Lublana, Nikozja, Sofia, Gdańsk, Rzym, Lizbona, GZM, Przemyśl, Rybnik, Suwałki: 20–25 wersji w 25 dniach). **Deduplikuj po SHA-256**, ale nie licz na duże oszczędności;
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
- **Workflow easy-GTFS-RT wykonuje checkout `easy-OTP` bez `ref`** (`family_a_build_and_notify_from_phone.yml`, krok "Checkout easy-OTP"), czyli z domyślnej gałęzi `main`: metoda zmienia się po cichu. **Ustalone w M0 (2026-09-26):** ostatni commit zmieniający `tools/family_a_reconstruction` i `tools/transit_charts` to `bccb17bb0066a358fde547dbe215fd50517838b2` (2026-09-04, `perf`, bez zmiany semantyki); ostatnia zmiana semantyki tidy to 2026-08-09 (`88a2e1e`, `86929f6`). Dla okna od 2026-09-01 semantyka jest więc jednolita. **Decyzja właściciela (2026-09-26, ADR-0004): bez pinu.** Metoda może się zmieniać (poprawki, ulepszenia); dla każdego dnia zapisujemy czas budowy tidy (`Last-Modified` załącznika) i commit `easy-OTP` z tej chwili, a `config/tidy_epochs.yaml` wskazuje zmiany semantyki. Dane as is.

## 7. Okno nagrywania i strefy czasowe (rozstrzygnięte)

Nagrywanie trwa ok. 06:00–22:00 **w czasie lokalnym miasta**, a `obs_local` jest lokalne. Wszystkie 10 sprawdzonych miast (9 zagranicznych) ma obserwacje w godzinach lokalnych 6–21, więc problemu stref czasu nie ma. Pasma: `am_peak` 7–8, `midday` 10–13, `pm_peak` 15–17, `evening` 19–21; godziny 6, 9, 14, 18 tylko w wartości całodziennej. **Bramka pasm:** miasto ma pasmo, jeśli nagranie pokrywa ≥ 90% godzin pasma.

## 8a. Diagnostyka Family A w `gtfs-dashboard` (przeczytana 2026-09-26)

Portal `gtfs-dashboard` (lokalny klon, stan z 2026-09-13; nie czytałem żywej strony) ma zakładkę **Diagnostyka** z dwoma raportami inżynierskimi o jakości i rzetelności rekonstrukcji (źródło: `easy-OTP/docs/reviews/family-a_*.md`). Autor zaznacza, że to diagnostyka założeń pipeline'u, nie stwierdzenie, że opublikowane feedy są błędne.

**Raport 1: "Ile nagrywania GTFS-RT wystarczy?"** (9 miast, okna 1–20 dni). Estymata P50/P85 segmentu stabilizuje się po ok. **14 dniach** (mediana zmiany na kroku 14→20 dni: 0,0 s w 4 zdrowych miastach; praktyczne minimum 3 dni). Główne ustalenie: w ok. połowie z 9 miast (4/9) wieloetapowe użycie **jednego pliku statycznego na całe okno** po cichu gubi dane, bo trip_id lub kalendarz w statyce już się zmieniły; objawem są rosnące odrzucenia dopasowania (telemetria FA-15), nie rozrzut.

**Raport 2: przegląd 25 miast/przewoźników (stabilność trip_id, calendar.txt).** 9/25 miast ma niestabilny `trip_id` (jeden statyk nie jest bezpieczny nawet na < 2 tygodnie), 11/25 nie ma `calendar.txt` (tylko `calendar_dates.txt`), Brisbane ma niestabilny `route_id`. `stop_id` jest stabilny (Jaccard ≥ 0,94 wszędzie). Dla naszych kandydatów (Jaccard między 3 migawkami statyki z początku sierpnia; małe rozstawy próbek dają niską pewność):

| miasto | profil | trip_id | route_id | stop_id | okno calendar (dni) |
|---|---|---|---|---|---|
| Łódź | trip_id niestabilny | 0,00 | 0,976 | 0,987 | 1–3 |
| Poznań | trip_id niestabilny | 0,04 | 0,938 | 0,977 | 1–11 |
| Gdańsk | trip_id niestabilny | 0,12 | 0,961 | 0,981 | 1–9 |
| Kraków | trip_id niestabilny | 0,14 | 0,979 | 0,988 | 3–7 |
| Turyn | trip_id niestabilny | 0,22 (do 0,05 po 13–25 dniach) | 0,938 | 0,978 | 12 |
| Warszawa | trip_id niestabilny | 0,33 | 0,992 | 0,994 | 3–4 |
| Rzym | trip_id niestabilny | 0,41 | 0,972 | 0,993 | 12–13 |
| Praga | mieszany | 0,67 | 0,966 | 0,968 | 25 |
| Wilno | mieszany | 0,67 | 1,000 | 0,986 | 25 |
| Szczecin, Sofia, Lizbona, Bukareszt | stabilny | 0,81–1,00 | ok. 1,0 | ok. 1,0 | 90–200 |
| Zagrzeb, Lublana, Nikozja | poza przeglądem | | | | |

**Co to znaczy dla Transit Index:**
1. **Nasz sposób użycia jest mniej narażony.** Bierzemy tidy budowane **osobno dla każdego dnia** ze statyką tego dnia, więc niestabilność `trip_id` między dniami nie łączy nam różnych namespace'ów. Klucz odcinka opiera się na `stop_id` (`from>to`), który jest stabilny (Jaccard 0,94–1,00), co zgadza się z F9 (Łódź 98,3–99,4%). W M1 sprawdzamy stabilność `stop_id` między dniami dla wszystkich kandydatów.
2. **Rezydualne ryzyko w obrębie dnia.** Statyka do dopasowania jest pobierana przy budowie (po dniu), więc republikacja lub statyka publikowana z wyprzedzeniem (Poznań) obniża `crossing_rate` tego dnia. Tak najpewniej należy tłumaczyć pojedyncze dni z niskim `crossing_rate` (np. Poznań 2026-09-02: 0,47). Bramka dnia je odrzuca; w `config/city_defects.yaml` miasta niestabilne są oznaczone.
3. **Dodatkowy sygnał jakości do rozważenia:** odsetek odrzuceń dopasowania FA-15 (nie jest w tidy; nie sprawdzałem, czy jest dostępny per dzień w release'ach). Progi FA-15 (`max_reject_share 0.25`) były podstawą naszej bramki (`docs/03` §6).
4. **Uzasadnienie progów odcinka:** stabilizacja po ok. 14 dniach i praktyczne minimum 3 dni są zgodne z `segment_min.ok` (≥ 5 dni, ≥ 10 obserwacji). Pilotaż (kilkadziesiąt dni ważnych) jest daleko ponad punktem nasycenia; komórki pasmowe są cieńsze, co sprawdza test czułości w M2.
5. **Niemonotoniczne wzorce** (GZM, Suwałki, Kielce; wg raportu możliwa cykliczna renumeracja) dotyczą miast poza rankingiem pilotażu (`watch`).

## 8. Lista kontrolna M0 (stan po weryfikacji)

Zrobione (`09`): schemat 34 kolumn (15 plików), semantyka odcinków, strefy czasu, stabilność klucza odcinka w Łodzi (98,3–99,4%), rozmiary, luki (Turyn), rozkład prędkości i kalibracja klas.

Zadania M0 na pełnym oknie (stan 2026-09-26, wyniki: `docs/data-inventory.generated.md`, `docs/progress.md`):
1. ~~Inwentarz par miasto-dzień z tidy i statyką; luki dzienne.~~ **Zrobione** (25 miast w zakresie, 601 plików tidy, 10,2 GB). Luka wspólna 2026-09-17: brak release'u w 11 z 25 miast.
2. ~~Stabilność schematu.~~ **Zrobione dla okna 09-01…25:** 34 kolumny w każdym z 287 plików kandydatów. Okres od 2026-08-03 nie sprawdzany.
3. Stabilność `stop_id` między dniami dla pozostałych miast: **przeniesione do M1** (wymaga statyk).
4. ~~Ref `easy-OTP`; daty zmian metody.~~ **Zrobione**, patrz wyżej.
5. ~~Pokrycie pasm per miasto na wszystkich dniach.~~ **Zrobione.** 1–4.09 nagranie częściowe; pełne dni od 2026-09-07.
6. ~~Odsetek `ok` per miasto i dzień; kandydaci na `excluded`.~~ **Zrobione.** Turyn: 7 z 15 dni ważnych od 09-07; Bukareszt na granicy.
7. `QualityReport` poza tidy: **nie sprawdzano** (nie jest publikowany; poza zakresem).
8. ~~Poligony (`config/areas/`, D12) i audyt licencji.~~ **Zrobione roboczo:** poligony GISCO i OSM porównane, GISCO w `config/areas/` jako propozycja; audyt licencji w `docs/licenses.md` (wstępny, GTFS-RT nieaudytowane).
