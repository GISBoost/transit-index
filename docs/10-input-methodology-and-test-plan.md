# 10 · Metodologia wejścia i plan testów przed wdrożeniem (2026-09-26)

Odpowiada na dwa pytania autora: (1) czy wynik składać z kilku tabel tidy z kilku dni, czy z surowych pozycji z kilku dni, (2) czy mamy zaplanowane testy wrażliwości i jakie jeszcze są potrzebne. Źródła: kod `easy-OTP/tools/family_a_reconstruction` i `tools/transit_charts` (odczyt, stan `main` z 2026-09-04, epoka `t1`), `easy-GTFS-RT` (workflow, `HOW-IT-WORKS.pl.md`), `docs/03`, `docs/07`, `docs/09`. **Co zweryfikowałem, a co nie, jest zaznaczone przy każdym punkcie.**

## 1. Z czego jest zbudowane tidy

Łańcuch w workflow `family_a_build_and_notify_from_phone.yml` (per miasto, per dzień):

```
record (telefon, co 60 s, ok. 06:00-22:00)  ->  surowe snapshoty VehiclePositions
match   (family_a.cli match)                 ->  matched.csv: pozycja rzutowana na polilinię kształtu z GTFS
                                                 (distance_along_shape_m), okno FA-12 wokół przystanku raportowanego przez pojazd
collect_stop_crossings (segment_stats.py)    ->  jedno przejście = jeden przystanek rozkładowy kursu, czas przez interpolację liniową
tidy.build (transit_charts/tidy.py)          ->  34 kolumny, opóźnienie, odstępy (headway), data serwisowa, etykieta seg_status
```

Cztery fakty, które rozstrzygają pytanie o metodologię:

1. **Tidy to obserwacje bezpośrednie, nie agregat.** `collect_stop_crossings` zwraca "jeden wiersz na przystanek rozkładowy każdego kursu, bez pooling, percentyla i kotwiczenia" (docstring i `family_a/README.md`, sekcja "What this feed measures"). P50/P85 z `build` to **osobny produkt** (rozkład "zrealizowany"), który tłumi opóźnienie do 13-45% wartości obserwowanej; my go **nie używamy**. Wszystkie nasze agregaty (mediana, `ΣL/ΣT`, EWT, bootstrap) liczymy sami z wierszy tidy.
2. **Każdy wiersz zależy tylko od jednego przebiegu kursu** (pozycje jednego pojazdu w jednym dniu + statyka tego dnia). W `matcher.py` nie znalazłem żadnej statystyki liczonej na całym zbiorze (mediana, percentyl, moda). Wyjątki poziomu zbioru w `extract`/`tidy`: `quality.drop_stale_observations` (moda daty nagrania), `find_outages` (przerwy całego feedu) oraz `_attach_headway` (klucz `route, direction, stop, stop_sequence` bez daty serwisowej).
3. **Statyka jest jedna na przebieg** (`--static`). README `family_a` mówi wprost, że przy republikacji statyki z nową generacją `trip_id` łączenie dni "nie zgłasza błędu, po cichu odrzuca każdą obserwację jako `unknown_shape`".
4. **Część parametrów jest zapieczona w tidy** (patrz tabela niżej) i nie da się ich zmienić bez surowych pozycji.

### Co da się zmienić po fakcie, a co nie

| parametr | wartość | gdzie działa | zmiana z samego tidy? |
|---|---|---|---|
| próg prędkości minimalnej (FA-18, `stationary`) | 2 km/h | etykieta `seg_status`; `seg_time_s`, `seg_dist_m` są zapisane także dla odrzuconych | **tak** (przeliczam z `seg_speed_kmh`) |
| próg prędkości maksymalnej (FA-13, `implausible`) | 100 km/h (200 dla kolei), 7200 s | jw. | **tak** |
| progi punktualności, odstępów, pasma, dzień tygodnia, obszar, tryb | `config/metrics.yaml` | nasz kod | **tak** |
| maksymalna przerwa między pingami (FA-14) | 300 s | brak `obs_time` (NaT) w tidy | **nie** (tylko z surowych) |
| tolerancja wsteczna kotwiczenia przystanków (FA-11) | 50 m | `shape_dist_m` | **nie** |
| okno dopasowania FA-12, odległość od trasy (`too_far_from_route`) | zależy od feedu | `matched.csv` | **nie** |
| pominięcie pierwszej pary przystanków (FA-20) | zawsze | `seg_status = first_pair`, brak `seg_time_s` | **nie** |
| gęstość próbkowania | 60 s (efektywnie zależna też od tempa odświeżania feedu operatora) | wszystko | **nie** |

Niepotwierdzone progi: kod `family_a` sam zaznacza przy `DEFAULT_MAX_BRACKET_GAP_S` i `DEFAULT_BACKWARD_TOLERANCE_M` "NOT YET CONFIRMED", a "threshold-sensitivity sweep" dla 300 s był zapowiedziany, ale nie znalazłem jego wyniku w dokumentach. To luka, którą zamyka T2.

## 2. Tidy z kilku dni czy surowe pozycje z kilku dni

| wariant | opis | ocena |
|---|---|---|
| **A. Tabele tidy z pojedynczych dni, sklejone** (obecny plan) | każdy dzień zbudowany ze statyką **tego** dnia; my łączymy wiersze i agregujemy | **rekomendowany** jako wejście produkcyjne |
| B. Surowe pozycje z kilku dni, jedna statyka, jeden przebieg | jedno `match`/`extract` na wielu dniach | **odrzucony**: `trip_id` niestabilny w 7 z 16 miast kandydujących (Łódź, Poznań, Gdańsk, Kraków, Turyn, Warszawa, Rzym; mieszany Praga, Wilno; `docs/02` §8a), więc dni z innej generacji statyki znikają po cichu; do tego zbiorowe kroki z pkt 2 wyżej (odstęp między ostatnim kursem dnia i pierwszym następnego jest chroniony tylko pośrednio, przez wykrywanie przerw) |
| C. Surowe pozycje, przebudowa **dzień po dniu** ze statyką tego dnia | to samo co A, ale z możliwością zmiany parametrów | to jest wariant A z dostępem do parametrów zapieczonych; potrzebny do testów i do przebudowy historii po zmianie metody (ADR-0004) |

**Wniosek: A i C dają te same wiersze, gdy kod i parametry są te same, a B tylko ryzykuje.** Łączenie dni w naszym kodzie to zwykłe sklejenie i agregacja po `service_date` (wiersze różnych dni nie mają wspólnej zależności), więc nie ma czego "składać z surowych" dla samej statystyki. Surowe pozycje są potrzebne w trzech sytuacjach:

1. **testy wrażliwości parametrów zapieczonych** (T2, T3),
2. **przebudowa historii po zmianie semantyki** (epoki, T1 i T21),
3. **test odtwarzalności** (T1), który sprawdza, czy archiwum miesięczne w ogóle nadaje się do przebudowy.

Ograniczenia, których nie zweryfikowałem: (a) zawartość archiwów `raw-snapshots-*` (nie otwierałem żadnego), (b) czy statyka dołączona do release'u jest dokładnie tą, której użył `match` (workflow ją archiwizuje w tym celu, ale nie testowałem), (c) archiwum września pojawi się dopiero na początku października, więc testy T1-T3 idą na lipcu i sierpniu (test metody, nie okna pilotażu).

## 3. Co mamy zaplanowane, a czego brakuje

**Jest (w `docs/03` §9, wymagane przez M2 w `docs/07`):** W1 `ΣL/ΣT` vs mediana ważona; bez 1% najwolniejszych; pasma odniesienia W3; tylko wt-czw; bez pierwszej i ostatniej godziny pasma; bootstrap po dniach; progi W10 120/180/300 s; agregacja i próg linii częstych W11; warianty W12; korelacje rang między wymiarami. Reguła decyzyjna: korelacja rang < 0,9 => publikuj oba warianty albo przejdź na odporny (ADR). Policzone są tylko dwa wyniki wstępne (na 1 dniu i 5 miastach): W1 (tramwaje ρ = 0,7) i wrażliwość pasm W3 (Łódź).

**Nie ma (luki):**

| luka | dlaczego ma znaczenie |
|---|---|
| parametry zapieczone w tidy (FA-14, FA-11, FA-12, pierwsza para, próbkowanie) | wszystkie liczby stoją na nich, a autor `family_a` sam oznaczył je jako niepotwierdzone |
| zbieżność wyniku od liczby dni | progi `city_gate` (40 i 20 dni) nie mają uzasadnienia empirycznym testem; raport dashboardu mówi o stabilizacji P50/P85 po ok. 14 dniach na poziomie odcinka, nie rankingu miast |
| wiarygodność podziałowa (split-half) odcinków i klas mapy | nie wiemy, czy ten sam odcinek dostaje tę samą klasę koloru w dwóch niezależnych połówkach danych; to jest sedno mapy |
| wpływ progów bramki (`day_gate`, `segment_min`, `city_gate`) na ranking | wszystkie są **propozycjami**; nie wiemy, czy bramka nie wybiera dni "dobrych" |
| systematyczny wpływ braków obserwacji (`crossing_rate` 0,71-0,89) i różnic technicznych feedów na porównanie miast | miasta różnią się źródłem odległości (`shape_dist_traveled` tylko Praga), sygnałem pozycji (Gdańsk bez okna), próbkowaniem |
| protokół porównywalności po zmianie metody | zmiana z 2026-07-30 obniżyła średnie opóźnienie o 34% (Rzym -83%, Bukareszt -79%); dla W10 to skala, której nie wolno przeoczyć |
| odtwarzalność raw -> tidy | nie wiemy, czy archiwum pozwala odtworzyć opublikowane tidy |
| weryfikacja zewnętrzna | nie mamy żadnej wartości niezależnej od tej rekonstrukcji |

## 4. Plan testów

Priorytet: **P0** = blokuje wynik pokazywany na stronie (M3/M5), **P1** = przed publikacją rankingu, **P2** = wzmacnia, nie blokuje. "Kiedy" odnosi się do kamieni milowych z `docs/07`. Progi decyzyjne są zapisane **przed** zobaczeniem wyników (rozdz. 5).

### A. Wejście (czy tidy mierzy to, co myślimy)

| ID | pytanie | metoda | dane | reguła decyzyjna | pr. | kiedy |
|---|---|---|---|---|---|---|
| T1 | czy z archiwum miesięcznym da się odtworzyć opublikowane tidy? | przebuduj 1 miasto-dzień (Łódź, sierpień, dzień po 2026-08-09) kodem z epoki `t1` w osobnym procesie ze statyką z release'u; porównaj wiersz po wierszu z opublikowanym tidy; przebieg dwukrotny (determinizm) | `raw-snapshots-2026-08` + release | identyczne (poza kolejnością) => archiwum wiarygodne; różnice => opisz przyczynę (kod, statyka, dane), a T2/T3 traktuj jako przybliżone | P0 | przed M2 |
| T2 | jak wynik zależy od parametrów zapieczonych w tidy? | z surowych: `max_bracket_gap` 120/300/600 s; tolerancja wsteczna 0/50/100 m; okno FA-12 włączone/wyłączone; pierwsza para włączona/pominięta; raport zmiany W1, W3, W10, W11, `crossing_rate`, udziału `ok` oraz **rang miast** (Spearman) | 6 miast o różnych feedach (Łódź, Praga, Gdańsk, Wilno lub Sofia, Bukareszt, Warszawa) x 3 dni | ρ rang miast >= 0,9 dla każdego parametru => parametr nie zmienia rankingu (zapisz wielkość efektu bezwzględnego); ρ < 0,9 => ADR: parametr zamrożony z uzasadnieniem i oznaczone ograniczenie w metodyce | P0 | M2 |
| T3 | ile zmienia próbkowanie 60 s (i tempo odświeżania feedu)? | z surowych: decymacja co 2. i co 3. snapshot (120 s, 180 s); dla każdego miasta rozkład odstępów między kolejnymi pozycjami pojazdu (mediana, P90) | jw. | jak T2; dodatkowo tabela "efektywne próbkowanie per miasto"; jeśli różni się >2x między miastami, ranking oznacz w metodyce jako wrażliwy na próbkowanie | P1 | M2 |
| T4 | czy progi 2 i 100 km/h (etykiety) zmieniają wynik? | z tidy: próg dolny 0/1/2/3/5 km/h (w tym obserwacje `stationary`), górny 60/80/100 km/h; W1 i ranking | tidy, 15 miast, wiele dni | ρ >= 0,9 | P1 | M2 |
| T5 | czy różnice techniczne feedów tłumaczą różnice między miastami? | korelacja rang: W1 (i W10, W11) miasta vs `crossing_rate`, udział `gap`, `first_pair`-speed, dostępność sygnału pozycji i zaufanej `shape_dist_traveled` | tidy + `reports/m0/` | \|ρ\| >= 0,5 => flaga przy mieście i zapis w metodyce; nie usuwamy miasta bez decyzji autora | P1 | M2 |
| T6 | czy braki obserwacji (pojazdy znikające z feedu) obciążają wynik? | wewnątrz miasta: dzienne W1 vs dzienne `crossing_rate`; kursy z wysokim i niskim `trip_coverage`; nachylenie z przedziałem | tidy, wiele dni | nachylenie istotne i kierunkowo spójne w >= 60% miast => zapisz kierunek błędu ("optymistyczne/pesymistyczne") i uwzględnij w bramce | P1 | M2 |

### B. Agregacja i stabilność (czy wynik zależy od doboru i liczby dni)

| ID | pytanie | metoda | reguła decyzyjna | pr. | kiedy |
|---|---|---|---|---|---|
| T7 | ile dni trzeba, żeby ranking był stabilny? | dla N = 3, 5, 10, 15, 20, 30, 40 losuj N dni ważnych (>= 200 losowań), ρ i Kendall tau rangi miast względem pełnego zbioru, szerokość przedziału W1 | najmniejsze N z ρ >= 0,9 w 90% losowań => uzasadnia `city_gate` (dziś 40 i 20); jeśli 20 wystarcza, obniż próg, jeśli 40 nie wystarcza, podnieś | P0 | M2 (dane do ok. 25 dni), powtórz przy >= 40 dniach ważnych (ok. początek listopada) |
| T8 | czy odcinek dostaje tę samą klasę w niezależnych połówkach danych? | podziel dni losowo lub wg parzystości tygodni na dwie połowy; dla odcinków `ok` w obu: korelacja prędkości, zgodność klas (Cohen kappa, udział zgodnych, udział przesunięć > 1 klasy) | kappa >= 0,7 i przesunięcia > 1 klasy < 5% => progi `segment_min` (10, 5) i 5 klas wystarczają; inaczej podnieś progi albo zmniejsz liczbę klas | P0 | M2 |
| T9 | wpływ dnia tygodnia i kalendarza | tylko wt-czw; bez poniedziałków i piątków; ze świętami i feriami vs bez (po uzupełnieniu ferii w `config/calendars/`) | ρ >= 0,9 | P1 | M2/M3 |
| T10 | czy bramka dnia wybiera "dobre" dni? | ranking dla: wszystkich dni z danymi, dni po bramce, bramki ostrzejszej i łagodniejszej (progi +-0,05, +-0,10); liczba dni, które zmieniają status; różnica W1 dni odrzuconych vs przyjętych w tym samym mieście | ρ >= 0,9 i brak istotnej różnicy W1 dni odrzuconych i przyjętych; inaczej odrzucone dni pokazuj obok | P0 | M3 |
| T11 | progi odcinka i miasta | `segment_min` (n_obs 5/10/20; n_days 3/5/8), `city_gate`; wpływ na pokrycie sieci i W1 (czy odcinki odrzucone są systematycznie wolne lub szybkie) | odcinki odrzucone nie mogą przesuwać W1 o więcej niż 0,3 km/h albo zostają oznaczone | P1 | M2/M3 |
| T12 | czy bootstrap po dniach daje uczciwe przedziały? | symulacja: pokrycie przedziału 90% na podziale danych; wariant blokowy po tygodniach; liczba par miast nierozróżnialnych | pokrycie 85-95%; jeśli bootstrap dzienny zaniża, użyj blokowego | P1 | M3 |

### C. Definicje metryk

| ID | pytanie | metoda | reguła | pr. | kiedy |
|---|---|---|---|---|---|
| T13 | W1: `ΣL/ΣT` vs mediana ważona długością; bez 1% najwolniejszych; bez brzegów pasma | jak w `docs/03` §9, ale na wszystkich miastach, wielu dniach i po filtrze obszaru | reguła z `docs/03` §9 (ρ < 0,9 => publikuj oba lub odporny + ADR); tramwaje osobno | P0 | M2 |
| T14 | W3: pasma odniesienia, minimalne `n` | `midday`, `evening`, oba; próg 5/10/20 obserwacji | kolejność AM < PM i bus > tram utrzymana | P1 | M2 |
| T15 | W10: progi (120/180/300 s), wyłączenie pierwszego przystanku, definicja opóźnienia | jak w §9 + porównanie z **niezależnym źródłem** tam, gdzie feed publikuje `TripUpdates` (w handoffie wymienione: Kraków, Lublana, Nikozja; **czy telefon je nagrywa, nie wiem**) | ρ >= 0,9; zgodność z TripUpdates raportowana jako błąd bezwzględny (nie kryterium zaliczenia, bo to inne źródło z własnymi błędami) | P0 | M2 |
| T16 | W11: agregacja (`ΣΣ` vs mediana), próg linii częstych 480/600/720 s, obsługa `headway_skips_vehicles`, minimalna liczba odstępów w komórce | jak w §9; osobno EWT z i bez odstępów przechodzących przez brakujący kurs | ρ >= 0,9; jeśli EWT rośnie liniowo z udziałem odstępów z pominiętym kursem, metryka mierzy braki w danych, nie regularność => zmień definicję | P0 | M2 |
| T17 | W12: mediana po przystankach vs udział przystanków >= próg; źródło (tidy vs `stop_times`) | jak w §9 | ρ >= 0,9 albo wybór wariantu w ADR | P1 | M2 |
| T18 | klasy prędkości `[15,20,25,30]` po filtrze obszaru | rozkład długości sieci w klasach na pełnych danych; alternatywy: kwantylowe; zamrożenie | żadna klasa > 35% ani < 8% długości sieci w większości miast; krawędzie zamrażane | P1 | M2 |
| T19 | filtr obszaru: wpływ wyboru poligonu na **ranking** | M0 policzył wpływ na wartości; policz ρ rang dla GISCO vs OSM vs wariant węższy | ρ >= 0,9; inaczej ADR-0002 uzupełnij | P1 | M2 |
| T20 | czy wymiary niosą różną informację? | korelacje rang W1, W3, W10, W11, W12 | ρ > 0,9 => wymiar zbędny albo nazwany inaczej | P1 | M2 |

### D. Wersje, statyka, odtwarzalność

| ID | pytanie | metoda | reguła | pr. | kiedy |
|---|---|---|---|---|---|
| T21 | jak sprawdzać zmianę metody (ADR-0004)? | **protokół:** każda zmiana semantyki `family_a`/`transit_charts` => nowa epoka w `config/tidy_epochs.yaml` i obowiązkowy A/B: przebudowa >= 3 miast x 3 dni starym i nowym kodem z tych samych surowych; raport zmiany W1, W3, W10, W11 i rang | zmiana rang ρ < 0,9 albo zmiana wartości > 3% => epoki nieporównywalne (nie łączymy) | P0 | protokół w M1, wykonanie przy każdej zmianie |
| T22 | czy dni z niską `crossing_rate` to dni ze zmianą statyki? | zestaw skrótów statyk z M0 (`reports/m0/`) vs dzień z bramką odrzuconą | potwierdza hipotezę (Poznań 2.09: 0,47) => dodaj "zmiana statyki" jako powód odrzucenia dnia w raporcie | P2 | M1/M3 |
| T23 | poprawność kodu | testy wzorcowe (`golden_values.json`), idempotencja, schematy, zgodność z `metrics_reference.py` | zgodnie z kryteriami M1-M3 | P0 | M1-M3 |

### E. Ważność zewnętrzna

| ID | pytanie | metoda | reguła | pr. | kiedy |
|---|---|---|---|---|---|
| T24 | czy rząd wielkości W1 zgadza się z danymi niezależnymi? | porównanie z publikowaną przez operatorów prędkością komunikacyjną lub eksploatacyjną, gdzie jest dostępna (raporty roczne; **źródeł jeszcze nie zebrałem i nie wiem, czy są**) | oczekiwana zgodność kolejności i rzędu wielkości, nie równości; różnice opisz | P1 | przed publikacją |
| T25 | kontrola ręczna | 20 losowych odcinków i 10 najwolniejszych (W8) na mapie/OSM; jedna linia vs wykres D14 (osobny proces); wartości absurdalne (> 60 km/h w mieście) | brak nierozwiązanych anomalii | P0 | M2 (wykres D14), M4 (mapa) |

## 5. Zasady prowadzenia testów

1. **Reguły decyzyjne zapisane przed wynikami** (kolumna "reguła"); zmiana reguły po zobaczeniu wyników wymaga wpisu z uzasadnieniem w `docs/progress.md`.
2. **Testy uruchamiam dwa razy:** w M2 na danych dostępnych wtedy (do ok. 25 dni ważnych), potem powtórnie przy >= 40 dniach ważnych (T7, T10, T12); wynik pierwszej rundy nie zamyka tematu.
3. **Wynik każdego testu wchodzi do `docs/sensitivity-report.md`** (wymóg M2) z: wartością, `n`, liczbą dni, miastami; decyzje do `docs/adr/`.
4. **Surowe pozycje uruchamiam tylko w osobnym procesie** i tylko do weryfikacji (kod `family_a` jest GPL-3.0, `CLAUDE.md`); kopia repo w katalogu tymczasowym, bez modyfikacji `easy-OTP`.
5. Testy nie zmieniają danych ani konfiguracji produkcyjnej; wyniki mają numer commita naszego repo i epokę tidy.

## 6. Zależności i ryzyka planu

- **Surowe pozycje (T1-T3):** archiwa lipca (14 plików, 1,1 GB) i sierpnia (31 plików, 7,1 GB) istnieją (`docs/02` §1). Testy robią się na kilku miastach; szacunek pobrania to rząd 1-2 GB (do potwierdzenia po zobaczeniu rozmiarów per miasto). **Nie wiem, czy zawartość archiwów wystarcza do przebudowy**: to pierwszy krok T1 (i powód, dla którego T1 stoi przed T2/T3).
- **Wrzesień:** archiwum dopiero na początku października, więc T2/T3 nie obejmą okna pilotażu, tylko metodę. To wystarcza do decyzji o parametrach.
- **Liczba dni:** T7 w pełnej postaci wymaga >= 40 dni ważnych (ok. początku listopada przy obecnym tempie, `docs/progress.md`).
- **Ferie szkolne** w `config/calendars/` są jeszcze nieuzupełnione (T9).
- **Zależność od decyzji autora:** T24 i T15 (porównania zewnętrzne) potrzebują źródeł; jeśli ich nie ma, zostają uczciwie zapisane jako brak walidacji zewnętrznej w metodyce strony.

## 7. Status wykonania (2026-09-27, rundy 1 i 2 przed M1)

Wyniki i interpretacja: `docs/sensitivity-report.md`. Tabele: `reports/tests/`. Narzędzia testowe (tymczasowe, poprzednik M1/M2): `scripts/t_l0.py`, `t_metrics.py`, `t_pool.py`, `t26_pooling.py`, `t_sens.py`, `t17_service.py`, `t2_param_sweep.py`, `t2_summary.py`, `t1_compare_tidy.py`. Kod `easy-OTP` uruchamiany tylko jako osobne procesy przez CLI (commit `bccb17b`, identyczny z HEAD w narzędziach rekonstrukcji).

| test | status | uwaga |
|---|---|---|
| T1 odtwarzalność raw -> tidy | **wykonany** | 9 dni-miast: Łódź x2, Wilno, Poznań x3, Bukareszt, Gdańsk, Praga; te same wiersze, <= 9 z 32-784 tys. różni się o 1 µs |
| T2 parametry zapieczone | **wykonany** | Łódź, Poznań (2 dni), Wilno, Bukareszt, Gdańsk (11 wariantów), Praga (6 wariantów); sierpień |
| T3 próbkowanie | **wykonany** | decymacja 120 s i 180 s (bez Pragi) |
| T4 progi 2 i 100 km/h | wykonany | z samego tidy |
| T5, T6 cechy techniczne i braki | wykonane | 15 miast, 10-15 dni |
| T7 zbieżność po liczbie dni | **runda 1-2** | do 15 dni ważnych; **powtórzyć przy >= 40 dniach** |
| T8 zgodność klas odcinków (połówki) | wykonany | |
| T9 dzień tygodnia | wykonany | |
| T10 bramka dnia | wykonany | powtórzyć z pełną bramką w M3 |
| T11 progi odcinka | wykonany | progi miasta (`city_gate`) po pomiarze pokrycia sieci w M2 |
| T12 bootstrap | wykonany | |
| T13 W1 warianty | wykonany | |
| T14 W3 pasma i min. `n` | wykonany (w T15) | inne okna szczytów nie testowane |
| T15 W10, W3 warianty | wykonany | bez porównania z TripUpdates (feedy `family A` to tylko VehiclePositions; `family B` tylko ŁKA) |
| T16 W11 warianty | wykonany | |
| T17 W12 źródło i agregacja | **wykonany** (runda 2) | jeden dzień, statyka; normalizacja `stop_id` i kilka dni w M2 |
| T18 klasy prędkości | wykonany | |
| T19 filtr obszaru | wykonany | obszar vs brak; GISCO vs OSM z M0 (1 dzień) |
| T20 korelacje wymiarów | wykonany | |
| T21 protokół zmiany metody | **opisany**; wykonanie przy zmianie semantyki | `t2_param_sweep.py --variants base` z `OTP_SRC` wskazującym stary i nowy commit |
| T22 zmiana statyki a dni z małą liczbą kursów | wykonany | hipoteza słabo potwierdzona |
| T23 poprawność kodu | częściowo | `tests/test_pool_harness.py`; testy M1-M3 przy implementacji |
| T24 porównanie z operatorami | **odpada** | autor: dane operatorów raczej niedostępne |
| T25 kontrola ręczna | częściowo | automatyczne kontrole skrajnych wartości; wykres D14 i przegląd odcinków w M2/M4 |
| T26 sklejanie dni (z prośby autora) | **wykonany** | pojedyncze dni vs tygodnie vs wszystkie dni, dni anomalne, weekendy |

## 8. Uruchamianie w chmurze (GitHub Actions): ocena 2026-09-27

Nic nie zostało uruchomione ani założone (repo GitHub nie istnieje, decyzja autora). Ocena z kodu i istniejących workflowów.

**Czy się da: tak.** Te same polecenia (`family_a.cli match`, `transit_charts.cli extract`) działają codziennie w workflowie `easy-GTFS-RT` na `ubuntu-latest` (macierz po mieście, `timeout-minutes: 60`, Python 3.11, cache pip). `easy-GTFS-RT` i `easy-OTP` są publiczne, więc pliki release'ów i kod pobiera się bez tokenów.

**Co trzeba zmienić:**
1. Repo `GISBoost/transit-index` (prywatne: `docs/08` ma uwagi prawne i wizerunkowe, których nie wolno commitować do publicznego repo bez przeglądu) i push historii; potrzebna zgoda autora.
2. Workflow z macierzą (miasto x dzień lub miasto x wariant): `actions/checkout` dla tego repo, drugi `checkout` `GISBoost/easy-OTP` w commicie `bccb17b` (jak robi to `easy-GTFS-RT`), `setup-python` 3.11, `pip install pandas pyarrow geopandas shapely pyyaml numpy gtfs-realtime-bindings tzdata`; zmienne `OTP_SRC` i `OTP_PY` z workflow zamiast lokalnych ścieżek; job końcowy scala wyniki (`t2_sweep.jsonl`, tabele).
3. Skrypty: `py` -> `python`; ścieżki są względne i przenośne; nie ma zależności od Windowsa (rename katalogu z `PermissionError` już obsłużony).
4. **Dane wyjściowe:** tabele L0 to 2,8 GB (16 miast x 26 dni); artefakty workflowów na darmowym planie mają mały limit, więc L0 trzeba zapisywać jako assety release'u (do 2 GB na plik, po jednym na miasto), w cache (10 GB) albo liczyć od nowa w każdym jobie.
5. Uprawnienia: `contents: write` (upload do release'ów); żadnych osobistych tokenów.

**Ile to daje:** równoległość (do 20 jobów naraz na darmowym planie): budowa L0 z ok. 2-3 h do kilkunastu minut; sweep T2/T3 z ok. 4 h lokalnie do ok. godziny (najdłuższe miasto). Koszt w minutach runnera: jeden pełny sweep ok. 6 godzin, jedna budowa L0 ok. 4 godziny, czyli ok. 600 min; **prywatne repo ma na darmowym planie 2 000 min/mies.** (do zweryfikowania w ustawieniach rozliczeń; API nie zwróciło planu konta), a runner prywatny ma 2 vCPU i 7 GB RAM (Praga i Warszawa mogą się zbliżać do limitu pamięci, do zmierzenia). Repo publiczne: bez limitu minut, 4 vCPU i 16 GB, ale wtedy `docs/08` i wszystko inne jest publiczne. Te liczby o limitach i runnerach pochodzą z mojej wiedzy ogólnej, nie z weryfikacji w dokumentacji GitHub.

**Ocena:** na resztę tych testów nie było warto (lokalnie zostawało 15 minut). Opłaca się dla: M1 (ingest 16 miast x wszystkie dni, potem codzienny przyrost ok. 16 minut), powtórki T7/T10/T12 przy >= 40 dniach, T21 przy każdej zmianie metody, przebudowy historii z archiwów miesięcznych. Praca nad workflow i debugowanie: ok. pół dnia (szacunek). Wymaga decyzji: repo prywatne z limitem minut czy publiczne.
