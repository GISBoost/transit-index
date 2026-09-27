# Decyzje i pytania (stan 2026-09-26, po M0)

Właściciel wszystkich repo: GISBoost (Michał Kaczorowski). Zmiany w innych repo (`easy-OTP`, `easy-GTFS-RT`, `easy-R5` itd.) robię tylko po zapytaniu, każdorazowo.

## 1. Rozstrzygnięte

| # | decyzja | zapis |
|---|---|---|
| D1 | zakres: kilkanaście miast europejskich | `docs/08` |
| D5 | stack: Astro + MapLibre + PMTiles, build tylko w GitHub Actions; wyjątek od reguły "bez build stepu" zapisany w `easy/CLAUDE.md` | `docs/adr/0001-astro-build-step.md` |
| D11 | jakość = pięć osobnych wymiarów, wskaźnik złożony w v2 | `docs/03` §1 |
| ADR-0004 | **bez pinu `easy-OTP`**: metoda może się zmieniać; oznaczamy pochodzenie każdego dnia (czas budowy tidy + commit `easy-OTP` z tej chwili + epoka semantyczna), dane serwujemy as is; żadnych zmian w `easy-OTP` ani `easy-GTFS-RT` | `docs/adr/0004-no-easy-otp-pin.md`, `config/tidy_epochs.yaml` |
| — | surowe pozycje: **co miesiąc archiwizowane jako kopia zapasowa** w `easy-GTFS-RT` (release `raw-snapshots-<RRRR-MM>`), dostępne przez `gtfs-dashboard`; historię można przebudować | `docs/02` §1 |
| D12 | poligony miast (W0): GISCO Urban Audit 2024 domyślnie; gdy źródła się różnią, **preferuj mniejszy obszar** (rdzeń miejski); Sofia i Lizbona z OSM; Nikozja i Gdańsk z GISCO | `docs/adr/0002-city-area-polygons.md`, `config/areas/sources.yaml` |
| licencje, D7 | **projekt niekomercyjny; wyniki na CC BY 4.0; wszystkie miasta publikowane z poprawną atrybucją źródeł**; Turyn pod bramką jakości; audyt GTFS-RT wykonany | `docs/adr/0003-licensing-stance.md`, `docs/licenses.md` |

## 2. Otwarte, ale nie blokują M1

| # | pytanie | rekomendacja | kiedy |
|---|---|---|---|
| — | pliki geometrii z kształtami OSM (Warszawa): ODbL, share-alike | oznaczyć te pliki atrybucją OSM i licencją ODbL dla bazy geometrii (wyniki nadal CC BY 4.0) | przed publikacją |
| — | strona `/dane/` z atrybucją per miasto (operator/portal, link, data pobrania, informacja o przetworzeniu) i pole `license` + `attributions` w manifeście edycji | zaplanowane w M3 (manifest) i M5 (strona) | M3, M5 |
| — | adresy RT z telefonu | na telefonie: `grep -h VEHICLE_POSITIONS_URL ~/easy-gtfs-rt-termux/cities/*.env` (zakryj klucze API); domyka `docs/licenses.md` §2b | przed publikacją |
| — | (opcjonalnie) SHA commita `easy-OTP` w treści release'u w workflow `easy-GTFS-RT` (jedna linia; zapytam przed zmianą) | zastąpiłoby wnioskowanie z czasu budowy | opcjonalnie |
| — | alert o brakującym release'ie (luka 2026-09-17: 8 miast bez tagu, 3 z tagiem bez tidy; przyczyna nieustalona) | tani alert w `easy-GTFS-RT` (Twoje repo, zapytam przed zmianą) | opcjonalnie |
| D4 | nazwa i adres (`Transit Index`, `gisboost.github.io/transit-index/`) | zatwierdzić i sprawdzić kolizje nazwy | przed M5 |
| D13, D14 | copy landingu do modelu jakości; nazwy wymiarów w UI | Claude Design | przed M5 |
| D3, D8, D9 | okno pilotażu, GZM, rytm publikacji | bez zmian względem `docs/08` | później |
| — | ferie szkolne w `config/calendars/` | uzupełnić ręcznie z oficjalnych kalendarzy | przed M3 |

## 2a. Decyzje z testów wrażliwości, runda 1 (2026-09-26, `docs/sensitivity-report.md` §4)

| # | pytanie / propozycja | rekomendacja | kiedy |
|---|---|---|---|
| R1 | kryterium liczby kursów (>= 0,70 mediany miasta) jako obowiązkowa część bramki dnia | tak: bez niego błąd jednodniowego W1 do 41% (Poznań), z nim do 7,7%; wpis w M3 | M3 |
| R2 | ranking kary szczytu: tylko PM czy wskaźnik łączny AM+PM? Poranna kara nie ma stabilnego rankingu (rho 0,83 przy 7 dniach; 34% par miast nierozróżnialnych) | **Rozstrzygnięte (2026-09-27, autor):** pokazywać **oba pasma osobno**, nie łączyć w jeden wskaźnik. Ranga: AM = ryzyko spóźnienia (praca/szkoła, da się spóźnić), PM = wydłużenie powrotu (dom/zakupy/siłownia, nie da się "spóźnić" wracając) — różne znaczenie użytkowe, nie tylko różna stabilność statystyczna. Niestabilność AM (rho 0,83) nie jest wadą do ukrycia: to sygnał zmienności dzień-do-dzień (TTV), pokazywany ze statusem/niepewnością, nie wycofywany z widoku. Copy/UI: M5. | M2 (implementacja), zapis w `docs/03` przy wdrożeniu W3 |
| R3 | W10 (punktualność) i W11 (regularność): rho rang -0,92 na 15 miastach, prawie ta sama informacja | **Rozstrzygnięte (2026-09-27, autor):** zostawić oba do M2, sprawdzić W11 na poziomie linii; jeśli nadal > 0,9, rozważyć jeden wymiar wtedy, nie teraz | po M2 |
| R4 | próg `city_gate.ranked` 40 dni: statystycznie wystarcza kilka dni, więc uzasadnieniem jest reprezentatywność i pokrycie sieci | bez zmian do powtórzenia T7 przy >= 40 dniach | listopad |
| R5 | Bukareszt na granicy bramki dnia (crossing 0,62-0,69) | zostawić 0,60/0,55, ewentualnie `limited` | informacja |
| R6 | Poznań i Kraków tracą 20-33% dni roboczych (statyka nie pasuje do RT). **Mechanizm doprecyzowany 2026-09-27** (analiza `easy-GTFS-RT`, tylko odczyt): workflow pobiera "świeżą" statykę operatora w chwili builda (tuż po zakończeniu nagrywania danego dnia), a nie statykę datowaną na ten dzień; gdy operator republikuje kolejny okres rozkładu wcześniej niż jego `start_date`, build tego dnia łapie okres, który jeszcze się nie zaczął. Potwierdzone wprost na Poznaniu 24.09 (czwartek): statyka użyta do builda miała `calendar.txt` ważny wyłącznie 25.09–18.10 (zero usług na 24.09) — to nie jest specyficzne dla piątku/soboty, tylko dla dnia, w którym operator akurat republikuje. **Dodatkowo potwierdzone:** `match`/`build` drukują szczegółowy rozkład odrzuceń (`unknown_shape`, `too_far_from_route`, `no_trip_id`, udział FA-15), ale workflow niczego z tego nie zapisuje (brak `upload-artifact`, brak webhooka) i sprawdza tylko, czy `matched == 0` — degradacja częściowa (jak w Poznaniu) nie jest nigdzie wykrywana ani później analizowana. | zapytać przed zmianą (Twoje repo); możliwy kierunek: (a) sprawdzać `calendar.txt`/`calendar_dates.txt` przed matchem, czy `DATE` ma aktywne usługi, i ostrzegać jeśli nie; (b) zapisywać `match_output.log`/`build_output.log` jako artefakt workflow | **pytanie do autora**, opcjonalne |
| R10 | W12 ze statyki tego samego dnia (tidy zaniża ofertę, Turyn 36%); agregacja (mediana / udział przystanków >= 4 odj./h) zmienia ranking (rho 0,83-0,93) | **Częściowo rozstrzygnięte (2026-09-27, autor):** źródło = statyka (bez zmian). Agregacja: skłania się ku medianie po przystankach, ale niepewny; propozycja pokazania na mapie (kolor odcinka/przystanku) zamiast surowej tabeli — do zaprojektowania z designem w M2/M5, ostateczny wybór wtedy | M2, agregacja + forma prezentacji |
| R7 | flaga `feed_capability` przy mieście (okno FA-12: sygnał pozycji w feedzie) | **Zaimplementowane w M1 (2026-09-27, autor: "policzyć i zapisać teraz"):** pole `feed_capability_window_signal` w `reports/m1/ingest_report.jsonl` per miasto-dzień, wyprowadzone z rejestru `city_defects.yaml` (`no_stop_sequence`). Uwaga: to własność feedu (stała, nie dzienna) — nie da się jej policzyć z samego tidy, wymagałaby surowych pozycji; źródłem prawdy nadal jest `city_defects.yaml`, `ti ingest` tylko go publikuje w raporcie | zrobione (M1) |

## 3. Przed M1: co warto wiedzieć

**Ustalenia z M0, które M1 dziedziczy (`docs/progress.md`, `docs/data-inventory.generated.md`):**
1. Pełne dni nagrania zaczynają się od **2026-09-07**; 1–4.09 są częściowe (bramka dnia je odetnie). Luka 17.09 w 11 miastach. Turyn: 7 z 15 dni ważnych od 7.09.
2. Schemat tidy jest stabilny (34 kolumny). Semantyka tidy jest jednolita od 2026-08-09 (ostatni commit narzędzi `bccb17b`, 2026-09-04).
3. **Statyki zmieniają się prawie codziennie** w większości miast, więc każdy dzień wymaga statyki z tego samego dnia, a deduplikacja po SHA-256 da małe oszczędności.
4. Poligony są w `config/areas/` (sposób wyboru: ADR-0002); wpływ na wyniki: 0–6 km/h i do 30% obserwacji.
5. Poznań ma po filtrze nadal wysoką prędkość autobusów (26,6 km/h); to sprawa dla M2, nie M1.

**Założenia robocze M1 (wchodzą do planu, chyba że powiesz inaczej):**
1. **Zakres:** 16 miast `candidate` (z Turynem), dni od 2026-09-01 do dziś, **wszystkie dni** (także weekendy; agregacja później wybiera typ dnia). Miasta `watch` nie wchodzą.
2. **Pobieranie:** strumieniowo po dniu. Tidy kasowane po zbudowaniu L0 (opcja `--keep-raw`). Statyki: liczę SHA-256 pliku, do `data/static/<sha256>/` zapisuję tylko potrzebne tabele (`routes`, `stops`, `trips`, `shapes`) jako Parquet, zip kasuję. Szacunek: ok. 20 GB transferu, poniżej 5 GB na dysku (wolne 44 GB).
3. **Kod:** pakiet `src/ti/`, CLI `ti` (argparse, bez nowych zależności), testy pytest; test wzorcowy Łodzi (1 dzień: 168 507 wierszy i 17,58 km/h; 9 dni: 17,59 km/h).
4. **L0:** kolumny z `docs/04` §2, w tym `delay_s`, `headway_s` i pokrewne (W10, W11); flaga `in_area` z poligonu; `share_of_obs_in_area` w raporcie miasto-dzień. Dodatkowo wąska tabela rozkładowa z wierszy tidy (`sched_dep` wszystkich kursów) pod W12; ostateczna definicja W12 w M2.
5. **Idempotencja i luki:** ponowny przebieg nie zmienia wyników (skróty zawartości); 404 to luka dnia, nie błąd; raport odrzuceń per miasto-dzień.
6. **Sprawdzę w M1** stabilność `stop_id` między dniami dla wszystkich miast kandydujących (w M0 tylko Łódź).
7. **Pochodzenie:** dla każdego dnia zapisuję czas budowy tidy i commit `easy-OTP` z tej chwili (ADR-0004).
8. Nic nie commituję bez Twojej prośby i niczego nie publikuję.

**Pytania przed startem M1:**
1. ~~Repo `GISBoost/transit-index` na GitHubie.~~ **Rozstrzygnięte (2026-09-26): repo nie jest zakładane, leży lokalnie.** M1 zapisuje L0 lokalnie (upload do release'ów później).
2. ~~Zakres M1.~~ **Rozstrzygnięte (2026-09-27): wszystkie miasta kandydujące (16, z Turynem) i wszystkie dni od 2026-09-01** (także weekendy; agregacja wybiera typ dnia). Turyn wchodzi do M1 jako `candidate`; jego status ustali bramka (po bramce z kryterium kursów ma < 10 dni roboczych).
3. ~~GitHub Actions.~~ **Rozstrzygnięte (2026-09-27): lokalnie na M1.** Ocena w `docs/10` §8 zostaje jako materiał na później (M4/M5, gdzie Actions jest tak czy inaczej wymagany dla builda strony — decyzja o repo prywatne/publiczne raz, przy tamtej okazji, zamiast dwa razy).
4. R1-R10: **R1, R2, R3, R6 (mechanizm), R7, część R10 rozstrzygnięte 2026-09-27** (sekcja 2a); R4, R5, R8, R9 informacyjne bez zmian; R6 (wdrożenie alertu w `easy-GTFS-RT`) i reszta R10 (agregacja W12, prezentacja) czekają na dalszą decyzję.
5. **M1 zakończony 2026-09-27:** pakiet `src/ti/` (`ti ingest`, `ti obs`, `ti stability`), test wzorcowy Łodzi przechodzi na prawdziwych danych (168 507 wierszy, 17,58 km/h, epoka `t1`). Ingest 16 miast x 2026-09-01..27 zakończony lokalnie: 370/432 dni-miast zbudowane, 28 z cache, 34 luki jawne, 0 błędów, 0 uszkodzonych plików (`reports/m1/ingest_report.jsonl`, `data/obs/` 2,5 GB, `data/static/` 1,8 GB — poza gitem). Szczegóły i incydent (chwilowy brak pamięci przez zdublowany proces w tle): `docs/progress.md`.
