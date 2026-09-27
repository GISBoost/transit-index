# ADR-0006: Ostateczne definicje W10, W11, W12 i zamrożenie klas prędkości

Status: przyjęta 2026-09-27 (właściciel: GISBoost). Dotyczy R2, R3, R10 (`docs/decisions-needed.md` §2a), `docs/03` §4 i §9.

## Kontekst

`docs/03` §4 zostawiało kilka parametrów jako propozycję do potwierdzenia w M2: próg "o czasie" W10 (transit_charts C11: -60/+180/+600 s), próg linii częstych i agregacja W11 (600 s, suma zbiorcza Σh²/2Σh), źródło i agregacja W12 (R10: statyka tego samego dnia, ale mediana po przystankach vs udział ≥ progu nierozstrzygnięte), oraz krawędzie klas prędkości `[15, 20, 25, 30]` (§5, "[PROPOZYCJA]"). Wszystko liczone wcześniej na próbce 1-dniowej/5-15-miastowej. M2 uruchomił `scripts/m2_sensitivity.py` na pełnym oknie: 16 miast kandydujących, 14-19 dni roboczych (bez świąt) na miasto, po filtrze obszaru W0 (`reports/m2/sensitivity_by_city.csv`).

## Decyzje

### W10 (punktualność)

Test progu "o czasie" (T15): ranking dla `late_s` = 120 i 300 s wobec bazowego 180 s: ρ = 0,953 i 0,950. **Oba ≥ 0,9 → ranking nie zależy od dokładnego progu.** Zostają progi `transit_charts` C11 bez zmian: wcześnie `< -60 s`, o czasie `-60…+180 s`, spóźniony `+180…+600 s`, bardzo spóźniony `> +600 s`; bez pierwszego przystanku kursu.

### W11 (regularność, EWT)

Test progu linii częstych (T16): `frequent_headway_s` = 480 i 720 s wobec bazowego 600 s: ρ = 0,965 i 0,979. Test agregacji: suma zbiorcza (Σh²/2Σh) vs mediana po komórkach (przystanek×linia×kierunek×pasmo): ρ = 0,971. **Wszystkie ≥ 0,9.** Zostają: próg 600 s, agregacja zbiorcza (ta sama statystyka co `ΣL/ΣT` dla W1 — spójność metodyczna), `min_headways_per_cell: null` (żaden dolny próg nie był potrzebny, żeby osiągnąć tę odporność).

### W12 (oferta rozkładowa)

Źródło: statyka tego samego dnia (R10, bez zmian; tidy zaniża ofertę nawet o 64%, `docs/09` F-wcześniejsze). C1 (2026-09-27): `static_store.py` doekstrahował `stop_times`/`calendar`/`calendar_dates`/`frequencies` do wszystkich 273 już zdeduplikowanych statyk (`scripts/backfill_static_tables.py`), bez ponownego liczenia L0.

Agregacja (T17): mediana po przystankach (liczona dzień po dniu, potem mediana po dniach — nie pula wszystkich dni naraz, bo to myliłoby "więcej dni" z "więcej przystanków na godzinę") vs udział przystanków ≥ 4 odj./h i ≥ 6 odj./h, 16 miast (`reports/m2/sensitivity_by_city.csv`):

| wariant | ρ (Spearman) |
|---|---|
| autobus: mediana vs udział ≥ 4 odj./h | **0,965** |
| autobus: mediana vs udział ≥ 6 odj./h | **0,939** |
| tramwaj: mediana vs udział ≥ 4 odj./h | **−0,155** |

Dla **autobusów** oba warianty ≥ 0,9 → agregacja nie zmienia rankingu, mediana po przystankach zostaje (zgodnie z wcześniejszą skłonnością autora). Dla **tramwajów** korelacja jest praktycznie zerowa (nawet ujemna) — wybór agregacji **odwraca** ranking tramwajowy. To nie jest mały efekt do zignorowania: sieci tramwajowe są mniejsze i gęstsze niż autobusowe (mediana wrażliwa na kilka nietypowych przystanków), więc mediana i udział ≥ progu mierzą tu wyraźnie różne rzeczy.

**Decyzja:** mediana po przystankach zostaje jedyną publikowaną agregacją W12 (spójność między trybami, prostota), ale **ranking W12 dla tramwajów dostaje status "niepewny co do metody"** — nie jest to status jakości danych (jak `thin`/`none`), tylko jawna adnotacja przy tym wymiarze/trybie, że inny rozsądny wybór agregacji dałby inny ranking. Nie ukrywamy tego ani nie podmieniamy metody bez decyzji: zgodnie z regułą `docs/03` §9 (ρ < 0,9 ⇒ opublikuj oba warianty albo zapisz decyzję z uzasadnieniem) — tu decyzja to "jeden wariant, ale z ostrzeżeniem", bo alternatywa (dwie równoległe liczby na każdej karcie miasta) kłóci się z propozycją R10 pokazania oferty na mapie, nie w tabeli liczb. Ostateczna forma prezentacji (kolor odcinka/przystanku) i dokładny tekst ostrzeżenia: M5, z designem.

### Klasy prędkości (T18)

Udział długości sieci (bus+tram, mediana prędkości odcinka, po filtrze obszaru) w pięciu klasach `[<15, 15-20, 20-25, 25-30, >=30]` na wszystkich 16 miastach pełnego okna:

| miasto | <15 | 15-20 | 20-25 | 25-30 | >=30 |
|---|---|---|---|---|---|
| bucharest | **37,1** | 38,0 | 16,0 | **4,4** | **4,5** |
| gdansk | 14,0 | 26,9 | 23,8 | 12,7 | 22,7 |
| krakow | 9,7 | 23,2 | 29,0 | 19,6 | 18,4 |
| lisbon | **40,5** | 30,6 | 15,5 | **7,7** | 5,7 |
| ljubljana | 12,0 | 23,9 | 22,3 | 16,5 | 25,4 |
| lodz | 18,4 | 24,2 | 23,4 | 18,9 | 15,1 |
| nicosia | **6,6** | 13,7 | 25,5 | 19,1 | 35,0 |
| poznan | 12,9 | 21,4 | 26,2 | 16,2 | 23,4 |
| prague | **6,9** | 19,1 | 28,8 | 18,9 | 26,2 |
| rome | 18,5 | 20,8 | 18,4 | 14,7 | 27,7 |
| sofia | 21,3 | 31,2 | 17,7 | 12,8 | 17,0 |
| szczecin | 15,6 | 22,4 | 21,6 | 16,4 | 24,0 |
| turin | **36,9** | 33,7 | 14,6 | **7,6** | **7,2** |
| vilnius | 12,8 | 20,4 | 20,5 | 17,6 | 28,7 |
| warszawa | 16,6 | 27,1 | 26,2 | 15,8 | 14,3 |
| zagreb | 9,7 | 13,9 | 20,6 | 18,2 | **37,6** |

(pogrubione: poza pasmem 8-35%, `reports/m2/sensitivity_by_city.csv` ma same kwintyle — powyższa tabela liczona osobnym przebiegiem `speed_class()` na medianie prędkości odcinka ważonej długością).

**To NIE jest czysty "confirm"** — 4 z 16 miast (bucharest, lisbon, turin, zagreb) przekraczają próg 35% w jednej klasie, kilka spada poniżej 8%. Trzy z czterech (bucharest, turin, zagreb) mają już zarejestrowaną wadę feedu w `config/city_defects.yaml` (`weak_coverage`, `no_trip_id`/`trip_id_unstable`, `suburban_lines`), która wiarygodnie tłumaczy przekrzywiony rozkład prędkości niezależnie od wyboru krawędzi klas. **Lizbona nie ma zarejestrowanej wady** — jej 40,5% w najwolniejszej klasie może być realną cechą sieci (wąskie uliczki starego miasta, wolne zabytkowe tramwaje), nie błędem danych; wymaga ręcznego sprawdzenia (T25) przed M3, nie jest powodem zmiany krawędzi teraz.

**Decyzja:** krawędzie `[15, 20, 25, 30]` **zostają bez zmian** dla v1 — działają rozsądnie dla większości miast bez znanych wad (11-12 z 16), a rekalibracja pod miasta o skrajnie innym profilu prędkości (dużo linii podmiejskich vs wolne historyczne centrum) i tak nie da jednego uniwersalnego zestawu bez utraty porównywalności między miastami, co jest sensem współdzielonych, zamrożonych krawędzi. Oznaczenie "[PROPOZYCJA]" usunięte z `config/metrics.yaml`, ale komentarz opisuje realny wynik (z zastrzeżeniami), nie fałszywe "wszystko się zgadza".

### W10 × W11 (R3, korelacja wymiarów)

Na poziomie miasta ρ = -0,929 (T20), niemal identyczne z próbką sprzed M1 (-0,92) — pozornie ponad próg 0,9 z reguły decyzyjnej `docs/03` §9 ("wymiar zbędny"). R3 wymagał sprawdzenia **na poziomie linii** przed decyzją o łączeniu. Wynik (651 par miasto-linia, próg ≥ 500 obserwacji na linię, ≥ 200 obserwacji punktualności, ≥ 100 odstępów): ρ spada do **-0,789** (pula wszystkich linii), a per miasto rozrzut jest szeroki: od -0,923 (Kraków) do +0,376 (Zagrzeb), większość miast wyraźnie poniżej 0,9 co do wartości bezwzględnej (`reports/m2/w10_w11_by_line.csv`).

**Wniosek:** silna korelacja na poziomie miasta to w znacznej mierze zbieżność między miastami (miasto dobre w jednym wymiarze bywa dobre w drugim), a nie dowód, że W10 i W11 mierzą to samo w obrębie miasta. **W10 i W11 zostają dwoma osobnymi wymiarami w v1.** Wzorzec miejski (ujemna korelacja) jest wartą wzmianki obserwacją na stronie metodyki, nie powodem do łączenia.

## Konsekwencje

`config/metrics.yaml`: krawędzie klas prędkości zamrożone (komentarz zaktualizowany), progi W10/W11/W12 potwierdzone komentarzami odsyłającymi tu. `docs/03` §1, §4, §9 i `docs/08` D2/"Czego nie zweryfikowano" zaktualizowane. `docs/decisions-needed.md` R2/R3/R10 zamknięte. Kod produkcyjny (`ti/metrics.py`, `ti/sched.py`, `reference/metrics_reference.py`: `punctuality_shares`, `ewt_minutes`, `ewt_minutes_median_of_cells`, `service_offer_per_hour`, `service_offer_share_above`) już implementuje te definicje od tego kamienia.
