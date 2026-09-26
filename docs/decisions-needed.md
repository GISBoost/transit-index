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

**Pytania, na które potrzebuję odpowiedzi przed startem M1:**
1. **Repo `GISBoost/transit-index` na GitHubie nie istnieje** (lokalne repo nie ma remote'a). Potrzebne do archiwum L0 w release'ach (`docs/04` §6) i później do Pages. Czy mogę je utworzyć jako **prywatne** i wypchnąć historię? (L0 zawiera identyfikatory operatorów, więc prywatne do czasu publikacji.) Jeśli wolisz odłożyć: M1 zapisuje L0 lokalnie, a upload zrobimy później.
2. Czy zakres M1 (punkt 1 powyżej: 16 miast, wszystkie dni od 1.09) jest OK?
