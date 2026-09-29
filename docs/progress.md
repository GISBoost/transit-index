# Dziennik postępu

Jeden wpis na kamień milowy (M0–M7), najnowszy na górze. Wpis powstaje na końcu kamienia i jest uzupełniany o werdykt `milestone-reviewer`. Decyzje techniczne: `docs/adr/`, pytania do autora: `docs/decisions-needed.md`.

## M3: bramka jakości, ranking, manifest (2026-09-29)

**Status: kod i testy gotowe; bramka policzona na prawdziwym L1 i logach M0/M1; wartości wymiarów, bootstrap i wykrywanie odchyleń prędkości NIE były uruchomione na prawdziwych danych** (sesja w chmurze bez `data/obs/` i `data/static/`, patrz "Czego M3 nie zrobił"). Werdykt `milestone-reviewer`: na dole.

### Co powstało

| wynik | gdzie |
|---|---|
| bramka dnia i miasta, dni anomalne (`low_trip_count`, `speed_outlier`, luka nagrania jako `recording_gap`) | `src/ti/gate.py` |
| bootstrap po dniach (200 losowań, przedział 90%, ziarno per miasto+ranking) i nierozróżnialność (nakładanie przedziałów) | `src/ti/uncertainty.py` |
| statystyki dzienne z L0 (jedyny etap M3 czytający L0): sumy `ΣL/ΣT`, W3, W10, W11, W12, profil godzinowy, linie, pokrycie pasm | `src/ti/daystats.py`, `ti daystats` |
| pokrycie sieci i minima trybu z L1 | `src/ti/coverage.py` |
| `ranking.json`, `summary.json`, `hourly.json`, `lines.csv`, `quality.json`, `manifest.json` (`license`, `attributions`, `easy_otp_commits`, `inputs_sha256`, `config_sha256`) | `src/ti/edition.py`, `ti gate` |
| atrybucje per miasto (wyłącznie z `docs/licenses.md`, nieznane = `null`, `verified: false`) | `config/attributions.yaml` |
| nowe schematy `hourly`, `quality`; rozszerzone `ranking` (tryb, przedziały, nierozróżnialność, sufiks pasma w `id`) i `edition_manifest` (`license`, `attributions`, `excluded_days`, `data_through`) | `schemas/` |
| progi M3 (`anomaly`, `bootstrap`, `dimension_gate`) | `config/metrics.yaml` |
| zapis decyzji dni (małe, do przeglądu) | `reports/m3/gate_days_2026-pilot.json` |
| testy (28 nowych; m.in. sumy dzienne = `reference/metrics_reference.py` dla W1, W3, W10, W11) | `tests/test_m3_gate.py` |

Przepływ: `ti daystats --city X ...` (tam, gdzie jest L0) -> `ti gate --from 2026-09-01 --to 2026-12-18` -> (opcjonalnie drugi przebieg `ti daystats --valid-only`, potem `ti gate`) . `ti gate` czyta tylko `day_stats.parquet`, L1 i `reports/`.

### Wynik bramki na prawdziwych danych (dane do 2026-09-27, L1 z 09-27)

Dni ważne (z 19 dni roboczych okna do 09-27; 1-4.09 odpadają jako `recording_gap`, część miast traci dni na `no_static`/`no_tidy`/`low_crossing_rate`/`low_trip_count`):
Łódź 15, Lizbona 15, Wilno 15, Lublana 14, Praga 14, Szczecin 14, Warszawa 14, Gdańsk 13, Rzym 13, Sofia 13, Bukareszt 12, Kraków 12, Nikozja 12, Zagrzeb 12, Poznań 10, Turyn 6.
**Żadne miasto nie ma jeszcze 20 dni ważnych (`city_gate.limited`), więc wszystkie 16 mają status `excluded` z powodem `too_few_days`** (tak jak zapowiadała prognoza M0; `ranking.json` ma dziś 0 rankingów i 16 wykluczonych). Pokrycie sieci (górne oszacowanie, patrz niżej) 0,91-0,999, więc drugi próg bramki nie jest wąskim gardłem. Tryb tramwajowy nie przechodzi `mode_min` w Lizbonie, Lublanie, Nikozji, Rzymie i Wilnie (za mało linii/odcinków).

### Decyzje i założenia do potwierdzenia przez autora

1. **`anomaly.mad_scale: 1.0`** = dosłowne "3 MAD" ze specyfikacji (surowe MAD, ok. 2 sigma dla rozkładu normalnego; odrzuci ok. 5% dobrych dni). Wartość 1,4826 dawałaby ok. 3 sigma. Do rozstrzygnięcia po zobaczeniu prawdziwych dziennych prędkości.
2. **`dimension_gate.min_obs`** (1000/1000/1000/200/0) to propozycje bez kalibracji ("status wymiaru wynika z jego n i progów", docs/03 §6); poniżej progu wymiar jest co najwyżej `limited`.
3. **Pokrycie sieci** = długość odcinków `q = ok` / długość wszystkich odcinków, na których L1 ma jakąkolwiek obserwację. To górne oszacowanie (sieć rozkładowa bez obserwacji nie jest w mianowniku); dokładniejsze wymaga `stop_times` statyki. Zapisane w `quality.json`.
4. **Dzienna prędkość miasta do kryterium MAD** = `ΣL/ΣT` (W1) dnia, tryb `street`, `all_day`; mediana i MAD po dniach, które przeszły wcześniejsze kryteria.
5. **Kryterium liczby kursów** używa `trips` z logu ingestu (kursy w tidy), mediana po dniach, które przeszły resztę bramki dnia (jeden `day_type`, bo dzień odniesienia to WEEKDAY).
6. **Wiarygodność `service_date`** jest dostępna tylko w statystykach M0; gdy brak, kryterium jest pomijane, a `quality.json` to zapisuje. Pokrycie pasm: z `day_stats` (L0), a bez niego ze statystyk M0 (to samo przybliżenie: godzina nagrana, gdy >= 1% wierszy `ok`).
7. **W3 z dwóch przebiegów**: odniesienie (prędkość pasm `midday`+`evening` per odcinek) jest liczone z dni podanych do `ti daystats`; przebieg `--valid-only` wyklucza dni odrzucone przez bramkę.
8. **Epoki**: dni z różnych epok tidy nie są wykluczane (ADR-0004, dane as is); notatka przy wpisach rankingu i liczniki w `quality.json`. Dziś wszystkie dni to epoka `t1` (dni `cached` w logu ingestu nie mają epoki: `unknown`).
9. **Zmiany schematów** (wszystkie addytywne poza `id`): `ranking.id` = `<tryb>_<wymiar>` z istniejącego wzorca plus `_<pasmo>` poza widokiem domyślnym; `edition_manifest` wymaga teraz `license` i `attributions`/`excluded_days` per miasto; `examples/edition_manifest.example.json` zaktualizowany.
10. **`placeholder: true`**: `edition.validate` odrzuca dowolny dokument z tym polem (test na plikach z `examples/`).
11. **`slowest_segments`** (opcjonalne w `city_summary`) pominięte: wymaga nazw przystanków i geometrii (M4).

### Czego M3 nie zrobił / ograniczenia

- **Sesja bez L0 i statyk.** Nie uruchomiono `ti daystats`, więc nie ma wartości W1/W3/W10/W11/W12, bootstrapu, nierozróżnialności, `hourly`/`lines` z danymi ani kryterium `speed_outlier` na prawdziwych dniach. Te ścieżki są sprawdzone tylko na danych syntetycznych, z sumami dziennymi zgodnymi z `reference/metrics_reference.py`. Wyniki z tych ścieżek nie istnieją i nie wolno ich cytować.
- `inputs_sha256` oznacza znakiem `?` dni bez skrótu tidy/statyki (wpisy `cached` w logu ingestu: Bukareszt 4, Kraków 1, Łódź 2, Nikozja 1); do domknięcia po ponownym `ti ingest` tych dni.
- Ferie szkolne w `config/calendars/` nadal puste (świadomie); wykrywanie dni anomalnych od nich nie zależy.
- `ti_commit` w manifeście ma sufiks `-dirty`, dopóki zmiany nie są scommitowane.
- Godziny 6-21 (`range(6, 22)` w `hourly`, `between(6, 21)` w `daystats`) są zapisane w kodzie tak jak w `aggregate.py` z M2, nie w configu.

### Co autor ma zweryfikować ręcznie

1. Na maszynie z L0: `ti daystats` dla 16 miast, potem `ti gate`; sprawdzić, które dni dostają `speed_outlier` i czy odpowiadają znanym (Poznań 10.09, Rzym, Kraków; `docs/sensitivity-report.md` §3.2).
2. Porównać `ranking.json` (W1, kolejność miast) z `reports/m2/metrics/*.json`; różnice mają wynikać tylko z wyłączenia dni odrzuconych.
3. Atrybucje w `config/attributions.yaml`: każdy wiersz z `verified: false` wymaga otwarcia strony licencji (`docs/licenses.md` §5).

## M2: segmenty i metryki — rdzeń (2026-09-27)

**Status: wykonany, przegląd `milestone-reviewer` FAIL po pierwszym przebiegu (dwie pozycje blokujące), obie naprawione z dowodem w repo — patrz niżej.**

### Co powstało

| wynik | gdzie |
|---|---|
| `ti aggregate`: L0 → L1 (`segment_stats.parquet`, `segments.parquet` z `pen_am`/`pen_pm`), dla wszystkich 16 miast kandydujących, edycja robocza `2026-pilot` | `src/ti/aggregate.py`, `data/editions/2026-pilot/<miasto>/` (poza gitem) |
| `ti metrics`: W1, W2, W3 (AM/PM osobno, R2), W6, W9, W10, W11, W12 na poziomie miasto × tryb × pasmo | `src/ti/metrics.py`, `reports/m2/metrics/<miasto>.json` |
| rozkład ze statyki (kalendarz + `stop_times` + `frequencies`) dla W12, zamiast tabeli z tidy | `src/ti/sched.py` |
| C1: `stop_times`/`calendar`/`calendar_dates`/`frequencies` doekstrahowane do wszystkich 273 już zdeduplikowanych statyk z M1, bez ponownego liczenia L0 (per-table top-up w `static_store.store()`) | `scripts/backfill_static_tables.py` |
| C2: stabilność `seg_id`/`stop_id` sprawdzona na wszystkich 16 miastach (nie tylko Łodzi jak w M0/M1) — mediana 0,917-0,998 (najniżej Turyn, znana wada feedu), żadne miasto nie potrzebuje zapasowego klucza z `docs/04` §1 | `reports/m1/stability.csv` |
| funkcje referencyjne W10/W11/W12 (`punctuality_shares`, `ewt_minutes` + wariant medianowy, `service_offer_per_hour` + wariant udziałowy, `peak_penalty_by_segment`) z samotestami | `reference/metrics_reference.py` |
| raport czułości na pełnym oknie (16 miast, 14-19 dni roboczych bez świąt), T13/T15/T16/T17/T18/T20 | `scripts/m2_sensitivity.py` → `reports/m2/sensitivity_by_city.csv` |
| ADR-0005 (W1 = `ΣL/ΣT`, potwierdzone dla tramwajów), ADR-0006 (progi/agregacja W10/W11/W12, zamrożenie klas prędkości, R3 rozstrzygnięte na poziomie linii) | `docs/adr/0005-*.md`, `docs/adr/0006-*.md` |
| testy: 9 jednostkowych M2 (agregacja, pasma, statyka-topup, EWT/oferta, brzegowy przypadek pustego pasma) + 1 na prawdziwych danych | `tests/test_ti_aggregate_metrics.py`, `tests/test_m2_golden.py` |

### Jak powtórzyć

```
PYTHONPATH=src;reference py -m ti.cli aggregate --city lodz --from 2026-09-01 --to 2026-12-18
PYTHONPATH=src;reference py -m ti.cli metrics --from 2026-09-01 --to 2026-12-18
py scripts/m2_sensitivity.py
py -m pytest tests -q
```

### Najważniejsze ustalenia

1. **Trzy realne błędy znalezione i naprawione — dwa przez własne testy na prawdziwych danych, jeden przez `milestone-reviewer`.** (a) `metrics_reference.py`: `peak_penalty_pct`/`peak_penalty_by_segment` wywalały się z `ValueError: 'seg_id' is both an index level and a column label`, gdy pasmo docelowe w ogóle nie występowało w danych (merge dwóch pustych ramek myli pandasa) — poprawione przez wcześniejsze odcięcie pustego przypadku. (b) `ti/metrics.py`: W12 sumowało odjazdy z wielu dni w jedną pulę i dzieliło tylko przez liczbę godzin pasma, nie przez liczbę dni — dawało absurdalne 71-200 odj./h zamiast 3,75-10,5. Naprawione na medianę dzienną (mediana po przystankach każdego dnia z osobna, potem mediana po dniach). (c) **Znalezione przez recenzenta:** `aggregate.reference_day_l0()` nie filtrował trybu do bus/tram, więc odcinki metra/kolei (`mode == "other"`) wyciekały do `segment_stats.parquet`/`segments.parquet` (np. Praga: 249 z 4332 odcinków) — `ti/metrics.py`'s liczby nagłówkowe były czyste (własny filtr `MODE_GROUPS` nigdy nie wybiera `other`), ale L1 jako samodzielny wynik M2 był zanieczyszczony. Naprawione filtrem trybu w tym samym miejscu co filtr obszaru W0; L1 przeliczone od zera dla wszystkich 16 miast.
2. **W1 = `ΣL/ΣT` potwierdzone na pełnym oknie, w tym dla tramwajów** (ρ = 0,986; ostrzeżenie z próbki 1-dniowej sprzed M1, ρ = 0,7, było artefaktem małej próby) — ADR-0005.
3. **R3 (W10 vs W11) rozstrzygnięte z realnymi dowodami, nie tylko odłożone.** Korelacja na poziomie miasta (ρ = −0,93) prawie się nie zmieniła względem próbki sprzed M1, ale na poziomie linii (651 par miasto-linia) spadła do ρ = −0,79 (pula) i od −0,92 do +0,38 per miasto — silna korelacja miejska to głównie zbieżność między miastami, nie ta sama informacja w obrębie miasta. Oba wymiary zostają osobne (ADR-0006).
4. **Progi W10 (120/180/300 s) i W11 (480/600/720 s, agregacja zbiorcza vs medianowa) potwierdzone jako odporne** (ρ ≥ 0,95 w każdym wariancie) — zero zmian w `config/metrics.yaml`, tylko potwierdzenie.
5. **Klasy prędkości `[15, 20, 25, 30]` zostają bez zmian po sprawdzeniu na pełnym oknie (T18) — ale to nie jest czysty "confirm".** Pierwsza wersja tego wpisu błędnie twierdziła "żadne miasto nie przekracza 35%/8%" na podstawie samych kwintyli, bez policzenia realnego udziału długości sieci w klasach; po przeliczeniu wprost okazało się, że 4 z 16 miast (Bukareszt, Lizbona, Turyn, Zagrzeb) przekraczają próg. 3 z 4 mają już zarejestrowaną wadę feedu w `city_defects.yaml`, która to tłumaczy; Lizbona nie — możliwa realna cecha sieci, do ręcznego sprawdzenia (T25) przed M3. Szczegóły i decyzja: ADR-0006.
6. **Krzyżowa kontrola z wykresem D14** (`transit_charts`, osobny proces GPL, tylko odczyt, `scripts/d14_crosscheck.py`): trasa 5 w Łodzi, 2 dni — D14 dało 16,04 km/h (ważone `n`, `n`=4308), `ti` L0 dało 14,79/14,90 km/h dla tych samych dni; ten sam rząd wielkości, brak wartości absurdalnych, różnica tłumaczona inną metodą agregacji (siatka godzina×przystanek z progiem `min_n`, nie `ΣL/ΣT`). **Poprawka po recenzji M2:** pierwszy przebieg tego sprawdzenia nie zostawił żadnego artefaktu (pliki tymczasowe skasowane po ręcznym odczytaniu liczb) — `milestone-reviewer` słusznie oznaczył to jako niezweryfikowalne. Powtórzone ze skryptem, wynik zapisany trwale w `reports/m2/d14_crosscheck.json` i `reports/m2/d14_crosscheck_numbers.csv`.
7. **W12: mediana po przystankach potwierdzona odporna dla autobusów (ρ = 0,965/0,939 wobec udziału ≥ 4/6 odj./h), ale niepewna dla tramwajów (ρ = −0,155, praktycznie brak korelacji)** — sieci tramwajowe są mniejsze i gęstsze, więc mediana i próg udziału mierzą wyraźnie różne rzeczy. Mediana zostaje jedyną publikowaną liczbą, ranking tramwajowy W12 dostaje jawną adnotację niepewności metodycznej (ADR-0006) — uczciwie pokazane, nie ukryte.
8. **Odkryto po drodze:** 3 statyki (na 273 zdeduplikowanych) nie dały się doekstrahować o `stop_times` mimo backfillu — wszystkie trzy to Warszawa/Turyn 2026-09-17, dokładnie ten sam dzień, który `config/city_defects.yaml` już rejestruje jako `window_events: missing_releases` (11 miast bez tidy tego dnia, przyczyna nieustalona). Spójne z wcześniejszą diagnozą, nie nowy problem.

### Czego M2 nie zrobił / ograniczenia

- L2/L3 (`ranking.json`, `summary.json`, bramka jakości, bootstrap, status miasta) to M3 — `ti metrics` liczy same wartości, bez kwalifikacji dni/miast ani bez porównań między miastami.
- Ferie szkolne nadal nie są uzupełnione w `config/calendars/` (C4: zaplanowane przed M3, bez zmian).
- T7/T9/T10/T12 (zbieżność po liczbie dni, dni tygodnia, bramka dnia, bootstrap) czekają na ≥ 40 dni ważnych (listopad).
- Geometria odcinków i kafle mapy to M4; `pen_am`/`pen_pm` są policzone per odcinek, ale jeszcze nie podłączone do żadnej mapy.
- `speed_class()`/`DEFAULT_SPEED_EDGES_KMH` (`reference/metrics_reference.py`) nie są jeszcze podpięte do `src/ti/` — klasyfikacja odcinka do klasy prędkości nie istnieje w `aggregate.py`/`metrics.py`; świadomie odłożone do M4/M5 (mapa), gdzie klasa faktycznie jest potrzebna.

### Przegląd `milestone-reviewer`

**Pierwszy przebieg: WERDYKT FAIL** (dwie pozycje blokujące). Recenzent niezależnie przeliczył 7 wartości (W1 dla 4 miast, W12 Łódź po naprawie poolingu dni, EWT Łódź, korelacje R3 na poziomie linii) prosto z `data/obs/*.parquet` przeciw `reports/m2/` — wszystkie zgodne co do kilku miejsc po przecinku. Zweryfikował też, że golden 168 507 (Łódź 24.09) to `street` PRZED filtrem obszaru, a 161 522 po `WEEKDAY`+`in_area` jest spójne z `docs/03` §2.1 — nie założył błędu tam, gdzie różnica miała wytłumaczenie.

| uwaga | rozstrzygnięcie |
|---|---|
| **Blokujące:** krzyżowa kontrola z wykresem D14 (kryterium akceptacji M2) nie miała żadnego artefaktu w repo — liczby w `docs/progress.md` były policzone ręcznie, pliki tymczasowe skasowane po drodze | Powtórzone ze skryptem `scripts/d14_crosscheck.py`, który zostawia trwały wynik: `reports/m2/d14_crosscheck.json` i `reports/m2/d14_crosscheck_numbers.csv` (trasa 5, Łódź, 2 dni: D14 16,04 km/h vs `ti` 14,79/14,90 km/h — ten sam rząd wielkości) |
| **Blokujące:** `segment_stats.parquet`/`segments.parquet` nie filtrowały trybu — odcinki metra/kolei (`mode == "other"`) wyciekały do L1 (Praga: 249/4332 odcinków), mimo że `docs/03` §1 wyklucza je z każdego wymiaru | `aggregate.reference_day_l0()` filtruje teraz też `mode in (bus, tram)`, w tym samym miejscu co filtr obszaru W0; nowy test regresyjny (`test_reference_day_l0_filters_weekday_and_holiday`); L1 przeliczone od zera dla wszystkich 16 miast. `ti/metrics.py`'s liczby nagłówkowe nie zmieniły się (własny filtr trybu już tam był poprawny) |
| `scripts/m2_sensitivity.py` miało krawędzie klas `[15,20,25,30]` zapisane literalnie zamiast z `config/metrics.yaml` (skrypt diagnostyczny, nie metryka produkcyjna, ale narusza literę zasady) | poprawione: czyta `metrics.CFG["speed_classes_kmh"]` |
| `reports/m1/stability.csv`: mediana Turynu 0,9167, a wpis mówił "≥ 0,92 wszędzie" (0,3 p.p. nieścisłości) | poprawiony opis w `docs/progress.md` (zakres 0,917-0,998) |
| `speed_class()`/`DEFAULT_SPEED_EDGES_KMH` niepodpięte do `src/ti/`, niewspomniane w "czego M2 nie zrobił" | dodane do listy ograniczeń; komentarz w `metrics_reference.py` zaktualizowany (nie jest już "PROPOZYCJA") |

**Po poprawkach:** `py -m pytest tests -q -m "not network"` → 26/26 przechodzi. Werdykt po poprawkach nie był ponownie zlecany drugiemu przebiegowi recenzenta (koszt kolejnego pełnego przebiegu z niezależnymi przeliczeniami na dużych miastach), ale obie pozycje blokujące mają teraz konkretny, sprawdzalny dowód w repo, zgodnie z tym, czego recenzent zażądał.

## M1: ingest i tabela obserwacji L0 (2026-09-27)

**Status: wykonany, przegląd PASS po poprawce (pierwszy przebieg: FAIL, jedna pozycja blokująca — rozwiązana, patrz niżej).**

### Co powstało

| wynik | gdzie |
|---|---|
| pakiet produkcyjny: `ti ingest`, `ti obs`, `ti stability`, CLI `ti` (`pyproject.toml`: `[project.scripts]`) | `src/ti/` |
| statyka dedup po SHA-256 (`routes`/`stops`/`trips`/`shapes` jako Parquet, zip odrzucany) | `data/static/<sha256>/` (poza gitem) |
| L0: 24 kolumny z `docs/04` §2 (klucze, `mode`, `seg_id`, `sched_pass_time_s`, `band`, kolumny W10/W11, `in_area`) | `data/obs/<miasto>/<data>.parquet` (poza gitem) |
| pochodzenie (ADR-0004): epoka i commit `easy-OTP` per dzień, z `Last-Modified` załącznika tidy i `config/tidy_epochs.yaml` | pole `epoch`/`easy_otp_commit` w raporcie |
| flaga `feed_capability_window_signal` (R7, z rejestru `city_defects.yaml`, nie liczona z tidy) | pole w raporcie |
| raport odrzuceń per miasto-dzień (`rows_tidy`, `rows_ok`, `crossing_rate`, `seg_status_share`, `share_of_obs_in_area`, skróty SHA-256) | `reports/m1/ingest_report.jsonl` |
| stabilność `seg_id`/`stop_id` dzień-do-dnia, wszystkie miasta kandydujące (M0 sprawdzał tylko Łódź) | `ti stability` -> `reports/m1/stability.csv` |
| testy: 7 jednostkowych (schemat, pochodzenie, `feed_capability`, transformacja tidy->L0, dedup statyk) + 3 na prawdziwych danych | `tests/test_ti_units.py`, `tests/test_m1_golden.py` |

### Jak powtórzyć

```
PYTHONPATH=src;reference py -m ti.cli ingest --from 2026-09-01 --to 2026-09-27 --workers 4
PYTHONPATH=src;reference py -m ti.cli stability
py -m pytest tests -q
```

### Najważniejsze ustalenia

1. **Test wzorcowy na prawdziwych danych, Łódź 2026-09-24: 168 507 wierszy `ok`, `ΣL/ΣT` (bus+tram) = 17,58 km/h, epoka `t1`** — dokładnie zgodne z `reference/golden_values.json`; `tidy_sha256` odtworzony w raporcie zgadza się ze skrótem w pliku złotym.
2. **Ingest pełnego okna wykonany:** 16 miast kandydujących x 2026-09-01…27 (432 dni-miast). 370 zbudowanych, 28 z cache (powtórne uruchomienie), 34 luki jawne (31 `missing_static`, 3 `missing_tidy` — brak release'u lub załącznika, zgodne z lukami z M0: Turyn najwięcej, 17.09 w kilku miastach). **0 nieprzetworzonych, 0 uszkodzonych plików Parquet** (zweryfikowane `pyarrow` na wszystkich 398 plikach). Dane lokalne: `data/obs/` 2,5 GB, `data/static/` 1,8 GB (dedup, mniej unikatowych plików niż dni x miasta).
3. **Odstąpiono od budowy tabeli rozkładowej "z tidy" pod W12**, którą zakładał pierwotny plan (`docs/decisions-needed.md` §3 sprzed testów): T17 (`docs/sensitivity-report.md` R10) wykazał, że tidy zaniża ofertę nawet o 64% (Turyn), więc budowanie jej teraz byłoby budowaniem znanego złego źródła. Tabela rozkładowa ze statyki zostaje w M2 (R10).
4. **`feed_capability_window_signal` (R7)** nie jest liczony z tidy per dzień — to własność feedu (okno FA-12), niemierzalna bez surowych pozycji. `ti ingest` publikuje w raporcie to, co już wie `config/city_defects.yaml`, żeby M2/M3 miało to pod ręką bez ponownego liczenia; źródłem prawdy zostaje rejestr, nie raport.
5. **Incydent podczas budowy:** pierwsze uruchomienie pełnego ingestu w tle zostało przypadkowo podwójnie zbackgroundowane (błąd operatora, nie kodu) i przez pewien czas dwa komplety procesów liczyły równolegle, co doprowadziło do chwilowego krytycznego braku pamięci w systemie i przerwania śledzenia zadania przez harness (sam proces przeżył i dokończył samodzielnie). Skutek: 18 przejściowych błędów `NotADirectoryError` w plikach tymczasowych (naprawione przy odduplikowaniu raportu; idempotencja `ti ingest` — kontrola `dest.exists()` — sprawiła, że nic nie trzeba było liczyć drugi raz). Żadnych danych nie ubyło ani nie uszkodzono.

### Czego M1 nie zrobił / ograniczenia

- L0 nie filtruje po trybie (bus/tram/other) ani po obszarze — trzyma wszystkie `ok` z flagą `in_area`/`mode`, decyzję filtrowania zostawia metrykom (M2), zgodnie z `docs/04` §2.
- `data/obs/` i `data/static/` nie są jeszcze wysyłane jako załączniki release'ów nowego repo (`docs/04` §6) — repo nie istnieje (decyzja: lokalnie na razie, `docs/decisions-needed.md`).
- Tabela rozkładowa pod W12 (źródło: statyka) nie została zbudowana — M2 (patrz punkt 3 wyżej).
- Stabilność `seg_id`/`stop_id` policzona (`ti stability`), ale interpretacja progu "za mało stabilne" nie jest jeszcze ustalona (nie było w kryteriach akceptacji M1).
- `ti ingest`/`ti obs` nie są zainstalowane jako pakiet (`pip install -e .` nie było uruchamiane w tej sesji) — testy i CLI działają przez `PYTHONPATH`.

### Przegląd `milestone-reviewer`

**Pierwszy przebieg: WERDYKT FAIL** (jedna pozycja blokująca). Recenzent niezależnie przeliczył 5 losowych liczb z `data/obs/*.parquet` przeciw `reports/m1/ingest_report.jsonl` (wszystkie zgodne), zweryfikował integralność 15 losowych plików Parquet (0 uszkodzonych), potwierdził pełne pokrycie 432 dni-miast po odduplikowaniu raportu i przeliczył test wzorcowy Łodzi 24.09 z sieci na żywo (168 507 wierszy, 17,575 km/h — w tolerancji).

| uwaga | rozstrzygnięcie |
|---|---|
| **Blokujące:** kryterium "9 dni: 17,59 km/h" nie jest odtwarzane (`ti` daje 17,58, różnica 0,0115 km/h > tolerancja 0,01) i nic tego nie testowało | Zweryfikowane niezależnie i potwierdzone: `golden_values.json`'s wpis 9-dniowy policzono JEDNĄ statyką (24.09) dla wszystkich 9 dni, bo `probe_release_data.py` przyjmuje tylko jedną `--static`; `docs/09` F10 to udokumentował już wcześniej (98,65% dopasowania trybu, nie 100%). `docs/04` §2 i `CLAUDE.md` wymagają statyki **każdego dnia z osobna** — `ti obs` robi to poprawnie, więc 17,58 jest wartością prawidłową, a 17,59 przestarzałą. Poprawiono: `golden_values.json` (nowe pole `_uwaga_2026-09-27` na tym wpisie, oryginalne liczby zostają jako historyczne), `CLAUDE.md`, `docs/07-milestones.md` (17,59 → 17,58), nowy test `tests/test_m1_golden.py::test_ingest_nine_days_matches_corrected_value` |
| osierocone katalogi `<sha256>.tmp<pid>/` w `data/static/` po incydencie z podwójnym procesem w tle | posprzątane (17 katalogów); `static_store.store()` dostał `try/except`+`shutil.rmtree` na wypadek przerwania w trakcie |
| `reference/metrics_reference.py` ma `BANDS`/`DEFAULT_SPEED_EDGES_KMH` na sztywno zamiast czytać `config/metrics.yaml` | niekrytyczne (nieużywane w L0), zgodność już pilnowana testem; odłożone do M2 (produkcyjna implementacja metryk) |
| `area_polygon` używa `within()` (przystanek dokładnie na granicy = "outside") | przypadek brzegowy bez praktycznego znaczenia, zostawione |
| "kopia L0 jako załączniki release'ów" (`docs/04` §6) nie zrobiona | świadomie odłożone — repo nie istnieje (decyzja właściciela) |

**Po poprawkach: `py -m pytest tests -q` → 26/26 przechodzi** (nowy test wzorcowy 9-dniowy). Werdykt: **PASS**.

## M0: repo, dane na pełnym oknie, decyzje (2026-09-26)

**Status: wykonany, przegląd PASS (warunkowy), decyzje właściciela wprowadzone** (otwarte pozycje: `docs/decisions-needed.md`, żadna nie blokuje M1).

### Co powstało

| wynik | gdzie |
|---|---|
| szkielet repo: `pyproject.toml`, `.gitignore` (dane poza gitem), pytest, venv `.venv` (poza gitem) | korzeń |
| progi i klasy (jedyne miejsce na liczby), lista miast, rejestr wad feedów | `config/metrics.yaml`, `config/cities.yaml`, `config/city_defects.yaml` |
| kalendarze świąt na okno 2026-09-01…12-18 dla 25 miast (biblioteka `holidays`; ferie szkolne puste, do ręcznego uzupełnienia) | `config/calendars/` |
| poligony miast (GISCO, tymczasowo, D12) i rejestr źródeł | `config/areas/` |
| test regresyjny: sonda odtwarza `golden_values.json` dla Łodzi 2026-09-24 (SHA-256 wejść zgodne) | `tests/test_golden_lodz.py` |
| testy konfiguracji, klas prędkości vs tokeny designu, poligonów | `tests/` (13 testów) |
| skrypty M0 (powtarzalne, wznawialne) | `scripts/m0_inventory.py`, `m0_polygons.py`, `m0_area_effect.py`, `m0_calendars.py`, `m0_report.py` |
| inwentarz na oknie 2026-09-01…25 | `docs/data-inventory.generated.md`, surowe: `reports/m0/` |
| audyt licencji (wstępny) | `docs/licenses.md` |
| decyzje i pytania; ADR-y (Astro, poligony, licencje) | `docs/decisions-needed.md`, `docs/adr/` |

### Jak powtórzyć

```
py -m venv --system-site-packages .venv && .venv/Scripts/python.exe -m pip install holidays
.venv/Scripts/python.exe scripts/m0_inventory.py heads --from 2026-09-01 --to 2026-09-25 --out reports/m0/heads.jsonl
.venv/Scripts/python.exe scripts/m0_inventory.py statics --from 2026-09-01 --to 2026-09-25 --out reports/m0/heads.jsonl
.venv/Scripts/python.exe scripts/m0_inventory.py stats --from 2026-09-01 --to 2026-09-25 --heads reports/m0/heads.jsonl --out reports/m0/stats.jsonl   # ~10 GB przez strumień, ~16 min
.venv/Scripts/python.exe scripts/m0_polygons.py fetch && .venv/Scripts/python.exe scripts/m0_polygons.py compare   # wymaga pliku GISCO w data/m0_polygons/
.venv/Scripts/python.exe scripts/m0_area_effect.py
.venv/Scripts/python.exe scripts/m0_report.py
.venv/Scripts/python.exe -m pytest
```

### Najważniejsze ustalenia

1. **Schemat:** 34 kolumny w każdym z 287 plików kandydatów (dni robocze 2026-09-01…25).
2. **Nagrania 1–4.09 są częściowe** (od 11:00, 15:00, 17:00); pełne dni od **2026-09-07**. Bramka dnia odrzuca je w większości miast (nie we wszystkich: np. Lizbona 09-02 ją przechodzi, bo godziny 7–21 pokrywają pasma).
3. **2026-09-17: brak tidy w 11 z 25 miast** (8 bez tagu release'u, 3 z tagiem bez tidy). Przyczyna nieustalona.
4. **Dni ważne od 7.09 (z 15 dni roboczych, po bramce dnia, brakach release'ów i świętach):** Kraków, Łódź, Poznań, Wilno 15; Gdańsk 13 (1 brak, 1 bramka); Lizbona, Lublana, Praga, Rzym, Szczecin, Warszawa 14; Sofia 13 (2 święta); Bukareszt, Nikozja, Zagrzeb 12; **Turyn 7**. Szczegóły: `docs/data-inventory.generated.md` §2.
5. **Poligon (D12):** GISCO i OSM zgodne w 19 z 23 miast; różnice: Sofia, Lizbona, Nikozja, Gdańsk (`docs/decisions-needed.md` §1). Filtr obszaru zmienia prędkość autobusów o 0,0–6,2 km/h (prawie wcale w Rzymie, Sofii, Lizbonie, Lublanie) i odcina do 30% obserwacji.
6. **Statyki zmieniają się prawie codziennie** w większości miast, więc deduplikacja SHA-256 daje małe oszczędności.
7. **`easy-OTP` w workflow bez `ref`** (checkout `main`). Semantyka tidy jednolita od 2026-08-09; ostatni commit narzędzi `bccb17b` (2026-09-04, `perf`). Decyzja właściciela: **bez pinu**, oznaczanie pochodzenia per dzień (ADR-0004, `config/tidy_epochs.yaml`).
8. **Licencje (statyka i RT, `docs/licenses.md`):** Turyn tylko niekomercyjnie (projekt niekomercyjny, więc dopuszczony pod bramką), Rzym RT "wyłącznie jako wsparcie podróży", Warszawa ODbL share-alike dla kształtów, 7 miast bez znalezionej licencji statyki, miasta ze zbiorkom.live bez warunków. **Właściciel: wyniki na CC BY 4.0, wszystkie miasta publikowane z atrybucją (ADR-0003).** Lista adresów RT z telefonu jeszcze potrzebna dla pełnego domknięcia.
9. **Wykonalność W10–W12:** `delay_s` i `headway_s` są dostępne w ok. 92–100% wierszy z obserwacją. Linie częste (< 600 s) to 1–3% wierszy w Poznaniu, Nikozji i Łodzi, więc W11 może mieć małą próbę w polskich miastach.
10. **Poznań:** po filtrze obszaru autobusy nadal 26,6 km/h (Kraków 19,7); do wyjaśnienia w M2.
11. **Liczba miast w `cities.json`:** 27 (dokumentacja podawała 28; `lka` usunięto 2026-09-09).

### Czego M0 nie zrobił / ograniczenia

- Stabilność `stop_id` między dniami dla miast innych niż Łódź: przeniesione do M1 (wymaga statyk).
- Okres 2026-08-03…08-31 nie był sprawdzany (poza oknem pilotażu).
- Pokrycie pasm to przybliżenie ("godzina ma ≥ 1% wierszy `ok`"), nie definicja docelowa z `docs/03` §2.3.
- Kalendarze: ferie szkolne i święta regionalne nie są uwzględnione.
- Poligon dla Przemyśla: tylko OSM (brak w Urban Audit); GZM bez poligonu (metropolia, D8).
- Audyt licencji oparty na wyszukiwaniu i stronach operatorów, nie na pełnych regulaminach; RT dla Zagrzebia, Lublany, Nikozji, Rzeszowa i Kielc bez adresu endpointu (jest na telefonie).
- Nie zmieniano żadnych repo poza tym (`easy-OTP`, `easy-GTFS-RT` czytane tylko do odczytu).

## Ocena ryzyka jakości danych (stan 2026-09-25, wygenerowane z `reports/m0/`)

Pełne dni nagrania od 2026-09-07. Prognoza zakłada, że udział dni ważnych utrzyma się do końca okna pilotażu (2026-12-18; 72–75 dni roboczych na miasto po odjęciu świąt). Progi: `ranked` ≥ 40 dni ważnych, `limited` ≥ 20. Ocena: **OK** = udział dni ważnych ≥ 90% i mediany `crossing_rate` i `ok` co najmniej 0,15 nad progiem; **do obserwacji** = któryś z tych warunków niespełniony; **RYZYKO** = prognoza poniżej progu `ranked`. Nie uwzględnia pokrycia sieci (M2).

| miasto | dni ważne od 09-07 | z dni roboczych | udział od 09-07 | udział ostatnie 2 tyg. | mediana crossing (próg 0.6) | mediana ok (próg 0.55) | prognoza do 12-18 (tempo od 09-07) | prognoza (tempo 2 tyg.) | zapas nad 40 dniami | trend crossing / tydz. | ocena |
|---|---|---|---|---|---|---|---|---|---|---|---|
| turin | 7 | 15 | 47% | 50% | 0.73 | 0.68 | 35 | 37 | -5 | -0.040 | RYZYKO |
| bucharest | 12 | 15 | 80% | 70% | 0.69 | 0.62 | 58 | 51 | 18 | +0.006 | do obserwacji |
| gdansk | 13 | 15 | 87% | 80% | 0.88 | 0.82 | 64 | 59 | 24 | +0.001 | do obserwacji |
| nicosia | 12 | 15 | 80% | 80% | 0.88 | 0.78 | 58 | 58 | 18 | -0.001 | do obserwacji |
| zagreb | 12 | 15 | 80% | 90% | 0.87 | 0.77 | 59 | 67 | 19 | -0.001 | do obserwacji |
| krakow | 15 | 15 | 100% | 100% | 0.78 | 0.71 | 74 | 74 | 34 | +0.010 | OK |
| lisbon | 14 | 15 | 93% | 100% | 0.83 | 0.78 | 67 | 72 | 27 | +0.004 | OK |
| ljubljana | 14 | 15 | 93% | 90% | 0.88 | 0.79 | 70 | 68 | 30 | +0.008 | OK |
| lodz | 15 | 15 | 100% | 100% | 0.86 | 0.81 | 74 | 74 | 34 | -0.004 | OK |
| poznan | 15 | 15 | 100% | 100% | 0.88 | 0.82 | 74 | 74 | 34 | -0.001 | OK |
| prague | 14 | 15 | 93% | 90% | 0.88 | 0.78 | 67 | 65 | 27 | +0.001 | OK |
| rome | 14 | 15 | 93% | 90% | 0.83 | 0.77 | 69 | 67 | 29 | +0.004 | OK |
| sofia | 13 | 13 | 100% | 100% | 0.89 | 0.84 | 73 | 73 | 33 | +0.000 | OK |
| szczecin | 14 | 15 | 93% | 90% | 0.87 | 0.81 | 69 | 67 | 29 | +0.004 | OK |
| vilnius | 15 | 15 | 100% | 100% | 0.84 | 0.77 | 74 | 74 | 34 | +0.002 | OK |
| warszawa | 14 | 15 | 93% | 90% | 0.88 | 0.81 | 69 | 67 | 29 | -0.001 | OK |

**Zagrożenia przy obecnym tempie:**
1. **Liczba dni nie jest wąskim gardłem.** Do `ranked` trzeba ok. 40 z ~74 dni, więc miasto może stracić do ok. 45% dni roboczych. Poza Turynem wszystkie mają zapas 18–34 dni.
2. **Turyn:** 7 z 15 dni ważnych, 4 dni bez release'u, trend jakości spadkowy; prognoza 35–37 dni, czyli `limited`, nie `ranked`.
3. **Bukareszt:** najwęższe marginesy jakości (mediana `crossing_rate` 0,69 przy progu 0,60, `ok` 0,62 przy 0,55) i 3 dni odrzucone na 15 (09-15 o 0,004 poniżej progu), w ostatnich dwóch tygodniach 70% dni ważnych. To najbardziej prawdopodobne miasto, które wypadnie z `ranked`, jeśli jakość się obniży.
4. **Nikozja, Zagrzeb, Gdańsk:** po 80–87% dni ważnych; braki to głównie dni bez release'u (Zagrzeb 3, Nikozja i Gdańsk po 1) i pojedyncze dni z niepełnym pokryciem pasm. Jakość dni, które są, jest dobra.
5. **Pokrycie sieci (drugi próg `city_gate`) nie jest jeszcze zmierzone** (M2). Dla Łodzi przy 9 dniach: 95% długości sieci z odcinkami `ok` (`docs/09` F16), więc progi 0,60 i 0,40 wyglądają na łatwe, ale dla reszty miast to niepotwierdzone.
6. **Zmiana metody w trakcie okna (ADR-0004).** Jeśli poprawka `family_a` zmieni semantykę tidy między ok. **21.10 a 5.11**, żadna z dwóch epok nie ma osobno ≥ 40 dni ważnych, więc wyniki per epoka byłyby co najwyżej `limited`. Bezpieczniej robić takie zmiany przed ok. 20.10 albo po ok. 6.11 (po zmianie jedna z epok ma wtedy ≥ 40 dni), albo zaakceptować wyniki `limited`.
7. **Awarie wspólne** (jak 17.09: 11 z 25 miast bez tidy). Jedna taka doba na 15 kosztuje ok. 7% dni; nawet kilkutygodniowa przerwa telefonu mieści się w zapasie (do ok. 34 dni), ale kolejne przerwy nakładałyby się na braki poszczególnych operatorów. Przyczyny 17.09 nie znamy.
8. **Sezonowość i kalendarz.** Ferie i przerwy szkolne (np. jesienne) nie są jeszcze w `config/calendars/`; dni z mniejszą liczbą kursów odetnie bramka anomalii (M3), co zmniejszy liczbę dni ważnych. Zmiana czasu 25.10 wypada w niedzielę (poza dniami roboczymi). Okno kończy się 18.12, więc okres świąteczny do końca roku nie wchodzi do pilotażu.
9. **Trend jakości** (`crossing_rate` na tydzień) jest bliski zera we wszystkich miastach poza Turynem (−0,04/tydz.); nie widać powolnej degradacji.

### Decyzje właściciela po M0 (2026-09-26)

D12: GISCO, przy różnicach preferować mniejszy obszar, Sofia i Lizbona z OSM (ADR-0002). Projekt niekomercyjny, wyniki na CC BY 4.0, wszystkie miasta publikowane z atrybucją źródeł, Turyn pod bramką jakości (ADR-0003; pełne warunki GTT w `docs/licenses.md` §2a). Audyt GTFS-RT wykonany (`docs/licenses.md` §2b). Astro (ADR-0001). Bez pinu `easy-OTP` (ADR-0004). Surowe pozycje są co miesiąc archiwizowane w `easy-GTFS-RT` (`raw-snapshots-*`), dostępne przez `gtfs-dashboard`. Zmiany w innych repo tylko po pytaniu. Reszta: `docs/decisions-needed.md`.

### Metodologia wejścia i plan testów (2026-09-26, po M0)

Analiza `easy-GTFS-RT` i `easy-OTP` (odczyt): tidy to obserwacje bezpośrednie (`collect_stop_crossings`), nie agregat P50/P85, więc wejściem produkcyjnym pozostają tabele tidy z pojedynczych dni (statyka tego dnia), a surowe pozycje służą do testów parametrów zapieczonych w tidy i do przebudowy po zmianie metody. Plan 25 testów (T1-T25, priorytety, reguły decyzyjne zapisane z góry): `docs/10-input-methodology-and-test-plan.md`. **Testy przed M1 zakończone 2026-09-27** (`docs/sensitivity-report.md`, status T1-T26: `docs/10` §7, ocena uruchamiania w chmurze: `docs/10` §8): T1 zaliczony (9 dni-miast), T2/T3 na 6-7 miastach (powtarzalne na drugim dniu), T4-T22, T25 i T26 na 15 miastach (2026-09-01…26), T17 wykonany (W12: źródło statyka), T24 odpada, T21 opisany. Główne wyniki: dni anomalne w pojedynczych dniach (Poznań, Rzym, Kraków) i konieczność kryterium liczby kursów; W3 AM bez stabilnego rankingu; W10 i W11 prawie redundantne (rho -0,92); FA-20, próg 300 s i okno FA-12 mają znaczenie w konkretnych miastach. Rekomendacje R1-R10 czekają na decyzje autora (`docs/decisions-needed.md` §2a). Zakres M1 rozstrzygnięty 2026-09-27 (16 miast, wszystkie dni od 1.09). M1 nie rozpoczęty.

### Przegląd `milestone-reviewer`

**Werdykt: PASS (warunkowy), brak pozycji blokujących.** Recenzent niezależnie przeliczył kluczowe liczby (Łódź, Poznań po filtrze GISCO, dni ważne od 7.09, liczba wersji statyk, poligony) i zgodziły się z raportem. Uwagi i ich rozstrzygnięcie:

| uwaga | rozstrzygnięcie |
|---|---|
| luka 2026-09-17 opisana jako awaria wspólna/telefon, a to hipoteza (8 miast bez tagu, 3 z tagiem bez tidy) | poprawione w `progress.md`, `decisions-needed.md`, `config/city_defects.yaml`: przyczyna nieustalona |
| brak listy miast kwalifikujących się do pilotażu i macierzy miasto × dzień | dodane do raportu: §4 macierz, §5 prognoza kwalifikacji względem `city_gate` (żaden kandydat nie ma jeszcze 20 dni ważnych, więc prognoza) |
| kolumna "brak trip_id" zawsze 0 (nic nie mierzy) | usunięta z raportu; wpis Turynu w `city_defects.yaml` oznaczony jako niepotwierdzony w M0 |
| magiczne liczby w skryptach (`600`, `0.01`, `500`) | przeniesione do `config/metrics.yaml` (`regularity.frequent_headway_s`, sekcja `inventory`) |
| opis odcisku statyki (SHA-256 ogona vs CRC32 z katalogu zip) | poprawiony; zaznaczone, że to zamiennik, a SHA-256 pliku liczy M1 |
| "filtr zmienia o 0,3–6 km/h" | poprawione na 0,0–6,2 km/h |
| Lizbona 09-02 przechodzi bramkę | zastrzeżenie dodane w ustaleniu 2 |
| mianownik udziału linii częstych | opisany w §3 raportu; liczby zaokrąglone |
| komentarz w `cities.yaml` obiecywał pola, których nie ma | poprawiony |
| test regresyjny wymaga sieci przy pierwszym uruchomieniu | brak sieci daje teraz `skip`, nie błąd |
| `bccb17b` dotyczy tylko narzędzi tworzących tidy (w `tools/` są nowsze commity `family_b`) | doprecyzowane w `decisions-needed.md` §4 |
| nie sprawdza wariantu 9-dniowego (17,59) | odłożone do M1/M2 (kryterium M0 dotyczy 2026-09-24) |
