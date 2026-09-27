# Raport czułości i walidacji przed M1 (rundy 1 i 2)

Stan: 2026-09-27. Plan i reguły decyzyjne (zapisane przed wynikami): `docs/10-input-methodology-and-test-plan.md`. Tabele źródłowe: `reports/tests/` (kopia rundy 1 w `reports/tests/round1_backup/`). Runda 1 (26.09): dane 2026-09-07…25. Runda 2 (27.09): dane 2026-09-01…26 dla wszystkich 16 miast kandydujących, bramka dnia z kryterium pokrycia pasm oraz dokończone testy T2/T3 i T17. Wyniki obu rund różnią się o <= 0,02 w rho, więc wnioski rundy 1 się utrzymały. Wyniki są **wstępne**: obejmują trzy tygodnie jednego miesiąca i nic nie mówią o sezonowości. Progi z tego raportu to **rekomendacje do decyzji autora**; w `config/` nic nie zmieniono.

## 1. Dane i metoda

- **Wejście:** opublikowane tabele tidy z `easy-GTFS-RT` (statyka tego samego dnia), 16 miast kandydujących, dni 2026-09-01…26, zapisane jako wąska tabela obserwacji (tryb ze statyki, obszar z `config/areas/`, godzina lokalna) w `data/l0/` (gitignore, 2,8 GB). Luki jak w M0 (17.09 w 8 miastach; Turyn, Zagrzeb, Poznań 3.09, Bukareszt 1.09).
- **Dzień ważny:** dzień roboczy bez święta, który przechodzi `day_gate`: `crossing_rate` >= 0,60, udział `ok` >= 0,55, pokrycie pasm >= 0,90 **oraz** kryterium liczby kursów w tidy >= 0,70 mediany miasta (`anomaly_min_trip_ratio`, planowane w M3; tu zastosowane, bo bez niego pojedyncze dni są zniekształcone, pkt 3.2). Ważne dni robocze: Łódź, Lizbona, Wilno 15; Praga, Szczecin, Warszawa, Lublana 14; Gdańsk, Rzym, Sofia 13; Bukareszt, Kraków, Nikozja, Zagrzeb 12; Poznań 10. **Turyn ma po bramce mniej niż 10 dni i wypadł z rundy.**
- **Metryki (prototypy zgodne z `docs/03`):** W1 `ΣL/ΣT` (bus+tram w obszarze), W3 kara szczytu AM i PM (odniesienie `midday`+`evening`), W10 odsetek przyjazdów "o czasie" (-60…180 s, bez pierwszego przystanku), W11 EWT w minutach (linie z odstępem < 600 s, winsoryzacja 0,99), W12 mediana rozkładowych odjazdów na godzinę (T17).
- **Sklejanie dni:** sumowanie statystyk dziennych (W1, W3 po odcinkach i pasmach, W10 z histogramu opóźnień, W11 z par odstępów); to samo co liczenie z wierszy wszystkich dni (`tests/test_pool_harness.py` i sprawdzone na danych).
- **Skróty z `family_a`:** **FA-12 (okno)**: gdy feed podaje w pozycji pojazdu `current_stop_sequence` albo `stop_id` (u >= 60% pojazdów danego dnia), dopasowanie pozycji GPS do trasy szuka tylko na odcinku między sąsiednimi przystankami (od przystanku poprzedniego do następnego), a nie na całej trasie; usuwa niejednoznaczność pętli i nakładających się przebiegów, a gdy okno nic nie znajdzie, wraca do szukania na całej trasie. **FA-20**: pierwsza para przystanków kursu jest pomijana, bo zawiera postój na pętli. **FA-14**: przejście z przerwą między pingami dłuższą niż 300 s jest odrzucane (interpolacja mierzyłaby rzadkość nagrywania). Pełny opis: `easy-GTFS-RT/HOW-IT-WORKS.pl.md`.
- **Surowe pozycje:** archiwa `raw-snapshots-2026-08`; kod `family_a` i `transit_charts` (commit `bccb17b`) uruchamiany wyłącznie jako osobne procesy.

## 2. Podsumowanie

| test | wynik | reguła | ocena | skutek |
|---|---|---|---|---|
| T1 odtwarzalność raw -> tidy | 9 dni-miast (Łódź x2, Wilno, Poznań x3, Bukareszt, Gdańsk, Praga): te same wiersze; 3 dni identyczne co do wartości, w pozostałych <= 9 z 32-784 tys. wierszy różni się o 1 µs w czasie | identyczne | **PASS** | archiwa miesięczne nadają się do przebudowy historii |
| T26 pojedynczy dzień vs tydzień vs wszystkie dni | pkt 3.2 | | **dni anomalne istnieją**; kryterium kursów je usuwa | kryterium kursów obowiązkowe (R1) |
| T7 zbieżność rankingu | W1, W10, W11: rho >= 0,95 już dla 1-3 dni; W3 PM 0,94-0,95 od 5 dni; **W3 AM nie przekracza 0,83** | rho >= 0,9 | W1, W10, W11 **PASS**; W3 PM na granicy; W3 AM **FAIL** | R2, R4 |
| T2, T3 parametry zapieczone i próbkowanie | pkt 3.1: FA-20 kluczowe, próg 300 s i okno FA-12 ważne w wybranych miastach, reszta bez wpływu; powtórzenie na drugim dniu daje ten sam obraz | efekt względem różnicy sąsiadów | patrz 3.1 | R7 |
| T4 progi 2 i 100 km/h | rho >= 0,968; bez progu 2 km/h W1 zmienia się do 1,3 km/h | >= 0,9 | PASS | ranking odporny |
| T5 cechy techniczne feedów | wszystkie \|rho\| < 0,5 (największe: `crossing_rate` vs W1 0,47) | \|rho\| < 0,5 | PASS | zapisać pokrycie i udział `ok` przy mieście |
| T6 braki obserwacji w mieście | W1 rośnie z `crossing_rate` w 14 z 15 miast (0,02-0,29 km/h na +0,01), \|r\| >= 0,5 w 40% miast | kierunek spójny | **efekt jest, mały** | ok. 0,3 km/h przy różnicy 0,1 w `crossing_rate`; **dni z mniejszym pokryciem są wolniejsze**, nie szybsze |
| T8 zgodność klas odcinków (połówki) | całodzienne: zgodność 92% (kappa 0,89); PM: 87-88% (kappa 0,82-0,83); skok o >= 2 klasy <= 1% | kappa >= 0,7 i skoki < 5% | **PASS** | klasy na mapie stabilne; progi `segment_min` zachowawcze |
| T9 dzień tygodnia | wt-czw vs wszystkie dni robocze: rho >= 0,986; piątek zmienia W3 AM o -4,1 pp | >= 0,9 | PASS | W3 AM zależy od dnia tygodnia |
| T10 bramka dnia | zmiany progów `crossing` i `ok` nie zmieniają rankingu, ale **przy 0,7 (crossing) lub 0,65 (`ok`) Bukareszt wypada** (< 5 dni); brak kryterium kursów: rho 0,993, W1 do 0,19 km/h | >= 0,9 | PASS; Bukareszt kruchy | R5 |
| T11 progi odcinka | `ok` (n >= 10, 5 dni) zachowuje 97,6% długości i 100% obserwacji; przesunięcie W1 <= 0,03 km/h | brak przesunięcia > 0,3 | **PASS** | progi bez uprzedzenia |
| T12 bootstrap po dniach | SE bootstrapu / SE empiryczny 0,91-0,98; nierozróżnialne pary miast: W1 11%, W10 5%, W11 11%, W3 PM 22%, W3 AM 34% | 0,8-1,2 | **PASS** | przedziały realistyczne, lekko za wąskie (2-9%) |
| T13 W1: `ΣL/ΣT` vs mediana ważona | rho 0,979 (razem, autobusy), 0,982 (tramwaje); bez 1% najwolniejszych 0,979-1,0 | >= 0,9 | **PASS** | jednodniowe rho = 0,7 dla tramwajów nie utrzymało się |
| T15 W10 i W3 warianty | W10: rho 0,911-0,986; W3 PM: 0,954-1,0; W3 AM: 0,896-0,996 | >= 0,9 | PASS (W3 AM z odniesieniem samym `evening`: 0,896) | poziom W10 zależy od progu (48-79%), kolejność nie |
| T16 W11 warianty | rho 0,943-1,0; korelacja EWT z udziałem pominiętych kursów: mediana -0,08 | >= 0,9 | PASS | EWT nie mierzy głównie braków |
| T17 W12 źródło i agregacja | z tidy vs ze statyki: rho 0,92, ale tidy zawiera mediana 0,94 rozkładu (Turyn 0,36); mediana vs średnia rho 0,83, vs udział przystanków >= 4/h 0,87, >= 6/h 0,93 | >= 0,9 | źródło: **statyka**; agregacja **wpływa na ranking** | R10 |
| T18 klasy prędkości | 13 z 15 miast bez klasy > 35% i < 8%; Bukareszt i Lizbona mają 75-81% długości w dwóch najniższych klasach | większość miast | PASS | wspólna skala; miasta wolne będą "czerwone" |
| T19 filtr obszaru | rho 0,961, 6,7% par zmienia kolejność; mediana -0,75 km/h, maks. -6,2 (Nikozja), -5,0 (Praga); GISCO vs OSM (M0, 1 dzień): rho 0,957, różnią się głównie Nikozja (5,8 km/h) | >= 0,9 | PASS | filtr zmienia poziomy silniej niż kolejność |
| T20 korelacje wymiarów | W10 vs W11: rho = -0,92; W1 vs reszta \|rho\| <= 0,51 | rho < 0,9 | **W10 i W11 prawie redundantne** | R3 |
| T22 zmiana statyki a dni z małą liczbą kursów | 9 z 11 dni z małą liczbą kursów miało zmienioną statykę, ale statyka zmienia się w 70% dni | | **hipoteza słabo potwierdzona** | przyczyna nieznana (R6) |
| T25 wartości skrajne | segmenty z n >= 10: < 1% > 50 km/h, < 1% < 5 km/h; p99 31-49 km/h | brak absurdów | PASS | |

## 3. Szczegóły

### 3.1 Parametry zapieczone w tidy (T2, T3)

Zrobione: Łódź (12 i 18.08), Poznań (14 i 17.08), Wilno, Bukareszt, Gdańsk (po jednym dniu, 11 wariantów) i Praga 12.08 (6 wariantów bez ponownego dopasowania). Dni sierpniowe (wakacje). Kolejność miast nie jest tu testowana (jeden dzień, różne dni w różnych miastach); efekt każdego parametru wyrażam jako **ułamek typowej różnicy między sąsiednimi miastami w rankingu** (W1: 0,148 km/h; W10: 2,0 pp; W3 PM: 0,75 pp; W11: 0,032 min), bo tylko zmiana tej wielkości może przestawić dwa miasta. Tabele: `reports/tests/t2_effects.csv`.

| parametr (wariant) | zmiana W1 [km/h] (% ; w różnicach sąsiadów) | W10 / W11 (w różnicach sąsiadów) | wniosek |
|---|---|---|---|
| **pierwsza para przystanków zachowana** (`kfs`, kontrola pozytywna: FA-20 wyłączone) | Łódź -0,01; Gdańsk -0,38 (-2,1%; 2,6); Wilno -0,39 (-2,0%; 2,6); Bukareszt -0,15 (-1,0%; 1,0); Poznań -0,85 (-4,3%; 5,8; 17.08: 5,3); **Praga -1,83 (-8,6%; 12,4)** | bez zmian | **test jest czuły**: bez FA-20 ranking W1 by się przestawił; FA-20 niezbędne, w Pradze najbardziej |
| maks. przerwa między pingami 120 s zamiast 300 s (`g120`) | Łódź +0,06/+0,08 (0,4-0,5); Poznań -0,04 (0,3-0,4); Wilno, Gdańsk ~0; **Bukareszt +0,15 (+1,0%; 1,0); Praga +0,31 (+1,4%; 2,1)** | W10 <= 0,23; W11 <= 0,57 | **próg 300 s ma znaczenie tam, gdzie pingi są rzadsze** (Bukareszt, Praga): krótszy próg odrzuca wolne obserwacje (Praga -28 tys.) i podnosi W1 |
| maks. przerwa 600 s (`g600`) | <= 0,04 (<= 0,40) | <= 0,11 / <= 0,24 | bez wpływu |
| tolerancja kotwiczenia 0 m i 100 m (`bt0`, `bt100`) | <= 0,01 (<= 0,02) | <= 0,08 / <= 0,06 | **bez wpływu** (wszystkie miasta) |
| okno FA-12 wyłączone (`win_off`) | Łódź, Bukareszt ~0; Wilno -0,07 (0,5); Poznań -0,10/-0,16 (0,7-1,1); Gdańsk 0 (nie ma sygnału okna) | Łódź, Wilno, Bukareszt: W10 <= 0,2, W11 <= 0,44; **Poznań: W10 -2,8 pp (0,8-1,4), W11 +0,275 min (8,4-8,6)** | wpływ na W1 mały, na W10 i W11 **zależy od miasta**, duży w Poznaniu, powtarza się w obu dniach. Gdańsk idzie ścieżką bez okna z definicji; nie da się tego skorygować, można tylko oznaczyć |
| odległość od trasy 50 m i 200 m (`perp50`, `perp200`) | <= 0,03 (<= 0,43) | W10 <= 0,07; **Poznań: W11 do 2,3** | mały wpływ, W11 w Poznaniu wrażliwe |
| próbkowanie 120 s i 180 s (`dec2`, `dec3`; co 2. i 3. snapshot) | Łódź, Wilno, Bukareszt, Gdańsk: <= 0,08 km/h; **Poznań -0,09/-0,23 (-1,1%; do 1,5)** | W10 <= 0,25; W11 do 1,5 (Poznań, Łódź 18.08 do 1,0) | `crossing_rate` spada o 0,02-0,065; **W1 jest odporny na 2-3 razy rzadsze próbkowanie poza Poznaniem**; W11 wrażliwy |

**Wnioski:** (1) jedynym parametrem, który w każdym mieście przestawia W1, jest FA-20 (włączony); (2) próg 300 s (Bukareszt, Praga) i okno FA-12 (Poznań) mają znaczenie w konkretnych miastach, więc nie ma jednego "bezpiecznego" ustawienia, a rekomendacja R7 (flaga `feed_capability`) zostaje; (3) tolerancja kotwiczenia i odległość od trasy nie wpływają na W1, W10 i W3; (4) przy rzadszym próbkowaniu W1 i W10 się nie załamują, W11 jest wrażliwy; (5) drugie dni (Poznań, Łódź) dają ten sam obraz co pierwsze, więc wynik jest powtarzalny.

**Ile obserwacji kosztuje próg 300 s** (dodatkowy wariant `ginf`: bez limitu przerwy między pingami; `reports/tests/t3_bracket_gap_loss.csv`). Próg odrzuca tylko pojedyncze przejścia przez przystanek (kurs zostaje w tidy, bo wiersze wszystkich przystanków kursu są zapisane), więc **liczba kursów w tidy się nie zmienia**. Utrata przejść względem braku limitu:

| miasto (sierpień) | `crossing_rate` z limitem 300 s | bez limitu | odrzucone przejścia | odrzucone obserwacje `ok` | W1 bez limitu |
|---|---|---|---|---|---|
| Bukareszt | 0,742 | 0,765 | **3,0%** (2,3 pp) | 3,2% | -0,20 km/h |
| Wilno | 0,828 | 0,843 | 1,8% | 1,9% | -0,17 |
| Łódź | 0,871 | 0,882 | 1,2% | 1,3% | -0,05 |
| Praga | 0,874 | 0,886 | 1,3% | 0,3% | -0,04 |
| Poznań | 0,877 | 0,882 | 0,6% | 0,5% | -0,01 |
| Gdańsk | 0,879 | 0,883 | 0,5% | 0,3% | -0,10 |

Odrzucone przejścia są **wolniejsze od reszty** (bez limitu W1 spada o 0,01-0,20 km/h), więc limit lekko zawyża prędkość: w skali różnicy sąsiadów (0,15 km/h) istotnie w Bukareszcie i Wilnie, w mniejszym stopniu w Gdańsku (0,10). Próg **nie jest zmienialny z opublikowanego tidy** (brakujące przejścia mają puste `obs_time`), ale jest zmienialny po fakcie z pozycji: wymaga ponownego `match` i `extract` z archiwum miesięcznego (T1 potwierdził, że to działa; koszt to kilka minut na miasto-dzień).

### 3.2 Sklejanie dni (T26) i zbieżność (T7)

**Pytanie autora:** czy jedna anomalia w jednym dniu zniekształca wynik, a sklejenie 5-7 dni daje wartość "typowego" dnia.

**Tak, anomalie w pojedynczych dniach są rzeczywiste i nie łapie ich obecna bramka dnia.**

| miasto, dzień | W1 tego dnia | mediana miasta | kursów w tidy | typowo |
|---|---|---|---|---|
| Poznań 10.09 | 27,3 km/h | 19,5 | 1 507 | 9 400 |
| Poznań 11.09 | 27,6 | 19,5 | 1 537 | 9 400 |
| Poznań 21.09 | 25,4 | 19,5 | 1 926 | 9 400 |
| Rzym 18.09 | 20,7 | 16,9 | 5 950 | 27 300 |

Wszystkie przeszły `day_gate` z `config/metrics.yaml` (`crossing_rate` 0,87-0,89, udział `ok` 0,81-0,83). Powód: tidy zawiera **tylko kursy z co najmniej jednym dopasowaniem**; gdy statyka nie pasuje do części kursów (inna generacja `trip_id`), zostaje szybki, nielosowy podzbiór (Poznań 10.09: same autobusy), a `crossing_rate` liczony wśród tych kursów wygląda zdrowo. Kryterium liczby kursów względem mediany miasta (>= 0,70, planowane w M3) łapie wszystkie te dni. Dni z małą liczbą kursów (pełne dni robocze): Poznań 5 z 15, Kraków 3 z 15 (53-62% mediany), Sofia 2, Rzym 1. Potwierdzenie pośrednie: w T17 statyka Poznania z 24.09 nie zawiera żadnej usługi na ten dzień (0 aktywnych `service_id`), a 24.09 był w Poznaniu dniem z 58% kursów.

Skutek dla pojedynczego dnia (błąd względem wszystkich pozostałych dni tego samego miasta), mediana / p90 / maksimum:

| wymiar | bramka podstawowa, 1 dzień | z kryterium kursów, 1 dzień | z kryterium kursów, tydzień (5 dni sklejonych) |
|---|---|---|---|
| W1 | 0,82% / 2,6% / **41%** (Poznań) | 0,77% / 2,0% / 7,7% | 0,48% / 2,3% / 3,1% |
| W10 | 2,5% / 7,7% / 27% | 2,3% / 7,6% / 27% (Lublana) | 1,8% / 8,3% / 13,5% |
| W11 | 11% / 27% / 84% | 11% / 27% / 54% | 6,3% / 20% / 31% |
| W3 PM | 12,7% / 34% / 192%* | 12,2% / 32% / 192%* | 7,8% / 21% / 29% |
| W3 AM | 27% / 116% / 1 349%* | 26% / 115% / 1 349%* | 12,6% / 97% / 801%* |

\* błąd względny wybucha, gdy wartość miasta jest bliska zera; w punktach procentowych rozrzut W3 to 2-3 pp.

Wnioski:
1. **Sklejanie pomaga najbardziej tam, gdzie wskaźnik jest szumowy** (W11, W3): tydzień zmniejsza medianę błędu o 27-52% względem pojedynczego dnia. Dla W1 i W10 (średnie z wielu tysięcy obserwacji) pojedynczy zdrowy dzień jest już blisko typowego (mediana błędu < 1% i 2,5%); główny zysk to ograniczenie **rzadkich dużych błędów** (maksimum W1 z 7,7% do 3,1%, W11 z 54% do 31%).
2. **Wartość sklejona ΣL/ΣT jest ważona liczbą obserwacji**, więc dzień z małą liczbą kursów waży mało: wszystkie dni anomalne razem przesuwają W1 miasta o <= 0,19 km/h nawet bez kryterium kursów. To chroni wynik zbiorczy, ale **nie** widok pojedynczego dnia ani tygodnia (tydzień Poznania 7-11.09 z dwoma dniami anomalnymi ma błąd W1 1,8%, W10 1,2%, W11 -16%, czyli nadal widoczny).
3. **Sklejona vs mediana z dni:** ta sama kolejność (rho 0,99-1,0 dla W1, W10, W11; 0,93-0,96 dla W3), różnica typowo 0,01-0,02 odchylenia między miastami. "Typowego dnia" można więc czytać z wartości sklejonej.
4. **Nie sklejać z weekendami.** Dodanie sobót i niedziel do dni roboczych zmienia mediany miast: W1 +0,44 km/h (+2,3%), W10 +2,0 pp, W3 PM -2,5 pp, W3 AM -2,4 pp (kara szczytu w weekend prawie znika). Filtr dnia roboczego jest wymagany (`docs/03` §2.2).
5. **Piątek** obniża poranną karę szczytu (W3 AM -4,1 pp względem średniej dni roboczych), poniedziałek podnosi (+1,0 pp): jeśli W3 AM wejdzie do rankingu, dni tygodnia trzeba ważyć albo rozdzielić.

**Zbieżność rankingu (T7):** rho Spearmana między rankingiem z K losowych dni a rankingiem z pozostałych dni (300 losowań, 15 miast, kryterium kursów włączone):

| K dni | W1 | W10 | W11 | W3 PM | W3 AM |
|---|---|---|---|---|---|
| 1 | 0,975 | 0,975 | 0,954 | 0,871 | 0,655 |
| 3 | 0,979 | 0,989 | 0,979 | 0,929 | 0,793 |
| 5 | 0,982 | 0,993 | 0,982 | 0,943 | 0,825 |
| 7 | 0,982 | 0,993 | 0,982 | 0,946 | 0,814 |

W1, W10, W11 przekraczają 0,9 już dla jednego dnia (90-100% losowań); W3 PM od 5 dni (93% losowań); **W3 AM nie zbliża się do 0,9 nawet dla 7 dni**: to nie brak dni, tylko mała rozpiętość wartości między miastami względem szumu dziennego (5,8 pp między miastami, 3,3 pp w obrębie miasta). Kalendarzowy tydzień vs reszta: rho W1 0,97, W10 0,98, W11 0,94, W3 PM 0,93, W3 AM 0,78.

**Uwaga do `city_gate`:** ranking W1, W10, W11 jest stabilny już po kilku dniach, więc **próg 40 dni nie wynika ze stabilności rankingu**, tylko z reprezentatywności (sezon, szkoły) i pokrycia sieci, których ta runda nie mierzy (R4).

### 3.3 W12: źródło i agregacja (T17)

Jeden dzień roboczy na miasto (24.09; Turyn i Poznań 23.09, bo statyka Poznania z 24.09 nie ma usług na ten dzień). Odjazdy w paśmie 10-14 z `stop_times` aktywnych usług (kalendarz, wyjątki, `frequencies.txt` w Warszawie), bus+tram, przystanki w obszarze miasta, bez ostatniego przystanku kursu.

- **Źródło:** tidy zawiera tylko kursy z co najmniej jednym dopasowaniem i odtwarza 77-105% rozkładu (mediana 0,94), w Turynie **36%** (feed bez `trip_id`). Mediana W12 z tidy vs ze statyki: rho 0,92, ale wartości się różnią (Turyn 3,25 vs 5,0). **Źródłem W12 powinna być statyka tego samego dnia.**
- **Agregacja:** mediana po przystankach vs średnia rho 0,83, vs udział przystanków z >= 4 odj./h 0,87, vs udział >= 6 odj./h 0,93 (wszystkie ze statyki). Wybór wpływa na ranking; mediany są skwantyzowane (2,0-9,0 co 0,25), co daje remisy.
- **Zależność od stop_id:** liczba przystanków na miasto różni się 10-krotnie (Lublana 694, Nikozja 982, Warszawa 4 183, Rzym 7 913), a mediana po przystankach zależy od tego, czy `stop_id` to słupek czy zespół; w teście nie normalizowałem (M2).
- Wartości: Bukareszt 9,0; Warszawa 7,0; Lizbona 6,5; Poznań 6,0; Sofia 5,25; Rzym 5,0; Turyn 5,0; ... Nikozja 2,0 odj./h (mediana po przystankach). Tabela: `reports/tests/sens/t17_service_by_city.csv`.

### 3.4 Pozostałe testy (skrót liczb)

- **T4:** bez progu 2 km/h rho 0,975 (mediana zmiany W1 0,15 km/h, maks. 1,3); próg 5 km/h: 0,968 i 0,34; sufit 60 km/h: 0,989.
- **T5:** rho między cechami feedu a wartościami miast (n = 15): `crossing_rate` vs W1 0,47; udział `ok` vs W3 AM -0,41, vs W10 0,43; liczba kursów dziennie vs W3 PM -0,34.
- **T8:** przy ok. 7 dniach w połowie: zgodność klas (całodzienna) 0,92 mediana, minimum 0,85-0,87; PM 0,87 (minimum 0,79-0,83). Próg `n` na połowę 5, 10 i 20 zmienia zgodność o 0,003-0,01: próg `ok: n_obs 10` nie jest wąskim gardłem.
- **T10:** kryterium kursów 0,5, 0,7, 0,85 lub brak: zmiana W1 miast <= 0,19 km/h, rho >= 0,993 dla wartości sklejonych z ok. 14 dni.
- **T13:** `ΣL/ΣT` jest o ok. 2,4 km/h wyższe od mediany ważonej długością (inna statystyka, ta sama kolejność).
- **T15:** W10: okno (0, 180) rho 0,911; (-120, 180) 0,946; (-60, 300) 0,961; (-30, 180) 0,986; (-60, 120) 0,982. W3 PM z odniesieniem samym `midday` 0,957, samym `evening` 0,954.
- **T16:** W11: linie częste < 480 s rho 0,943, < 720 s 0,968; bez winsoryzacji 0,993; winsoryzacja 0,95 0,989; bez odstępów z pominiętym kursem 1,0 (takich odstępów jest 0-1,6%, bo tidy nie zawiera kursów bez ani jednego dopasowania).
- **T18:** udział długości sieci w klasach (mediana miast): 18% / 25% / 23% / 15% / 20%; Zagrzeb 34% w klasie >= 30 km/h; Bukareszt i Lizbona 48% w klasie < 15 km/h.
- **T20:** macierz rang (15 miast): W1 z W10 0,51, z W11 -0,49; W10 z W11 -0,92; W3 AM z W3 PM 0,53.
- **T22:** dni z małą liczbą kursów: Poznań 5, Kraków 3, Sofia 2, Rzym 1; statyka zmienia się względem dnia poprzedniego w 9 z 15 miast w co najmniej 12 z 13-15 dni (Bukareszt, Zagrzeb, Szczecin prawie nigdy).

## 4. Wnioski i rekomendacje (do decyzji autora)

| # | rekomendacja | podstawa | decyzja |
|---|---|---|---|
| R1 | **Kryterium liczby kursów (>= 0,70 mediany dnia roboczego miasta) jest częścią bramki dnia.** Chodzi o liczbę kursów (unikalnych `trip_id`, bus+tram) w tidy danego dnia, np. 1,5 tys. wobec typowych 9,4 tys. w Poznaniu, a **nie o prędkość**: zmienność prędkości dzień do dnia zostaje w danych i jest wartościowym sygnałem (TTV dzień do dnia, u zdrowych dni W1 ma odchylenie 0,2 km/h, tj. CV 0,9%). Dni odrzucone nie znikają: w manifeście lista dni wyłączonych z powodem i ich wartości pokazane osobno | T26: bez niego błąd jednodniowego W1 do 41%, z nim do 7,7% | wpisać w M3 (`docs/03` §6/§7) |
| R2 | Kara szczytu rankingowa: AM czy PM czy łączony? Poranna nie ma stabilnego rankingu (rho 0,83 przy 7 dniach, 34% par nierozróżnialnych, zależy od dnia tygodnia). **Decyzja autora (2026-09-27): pokazać oba pasma osobno, nie łączyć.** AM = ryzyko spóźnienia (praca/szkoła), PM = wydłużenie powrotu — różne znaczenie, nie tylko różna stabilność; niestabilność AM to sygnał TTV dzień-do-dzień, pokazywany ze statusem, nie ukrywany | T7, T9, T12 | M2 (implementacja) |
| R3 | **W10 i W11 niosą prawie tę samą informację o rankingu** (rho -0,92, 15 miast). Zostawić oba do M2, na stronie nie przedstawiać jako niezależnych dowodów; w M2 sprawdzić W11 na poziomie linii, a przy dalszym rho > 0,9 rozważyć rezygnację z jednego | T20 | **decyzja autora po M2** |
| R4 | `city_gate.ranked.min_valid_days: 40` jest zachowawczy względem stabilności rankingu, więc jego uzasadnieniem musi być reprezentatywność i pokrycie sieci; T7 powtórzyć przy >= 40 dniach ważnych. Do tego czasu bez zmian | T7 | informacja |
| R5 | **Bukareszt jest na granicy bramki dnia** (crossing 0,62-0,69): próg 0,7 lub `ok` 0,65 wykluczyłby go prawie całkiem. Zostawić 0,60/0,55; zaakceptować status `limited`, jeśli pogorszy się dalej | T10, M0 | informacja |
| R6 | **Poznań i Kraków tracą 20-33% dni roboczych** przez niedopasowanie statyki do RT. **Mechanizm doprecyzowany 2026-09-27** (analiza `easy-GTFS-RT`, tylko odczyt, autor: "sprawdź jak to wygląda"): workflow pobiera statykę "na żywo" w chwili builda (koniec dnia), nie statykę datowaną na dzień nagrania; gdy operator republikuje kolejny okres przed jego `start_date`, build łapie okres, który się jeszcze nie zaczął. Potwierdzone wprost: statyka użyta do builda Poznania 24.09 (czwartek) miała `calendar.txt` ważny dopiero od 25.09 — zero usług na 24.09. Nie jest to specyficzne dla piątku/soboty (autor tak podejrzewał), tylko dla dnia, w którym operator akurat republikuje. Dodatkowo: `match`/`build` drukują pełny rozkład odrzuceń (FA-15: `unknown_shape`, `too_far_from_route`, `no_trip_id`), ale workflow tego nie zapisuje (brak artefaktu, brak alertu) i sprawdza tylko `matched == 0` — degradacja częściowa jak w Poznaniu przechodzi niezauważona | T22, T26, T17 | **pytanie do autora**, opcjonalne |
| R7 | Flaga `feed_capability` przy mieście: okno FA-12 (Poznań: W11 zmienia się o 8 różnic sąsiadów, gdy okna nie ma; Gdańsk go nie ma) i rzadkie pingi (próg 300 s: Bukareszt, Praga) | T2 | **zaimplementowane w M1** (2026-09-27): `feed_capability_window_signal` w `reports/m1/ingest_report.jsonl`, z rejestru `city_defects.yaml` (nie mierzalne z tidy — własność feedu, nie dnia) |
| R8 | **Zawsze filtrować dzień roboczy**; nie mieszać weekendów | T26 | już w spec |
| R9 | Filtr obszaru zostaje wymogiem: zmienia poziomy do 6 km/h (Nikozja, Praga) i kolejność 7% par miast | T19 | już w spec |
| R10 | **W12 ze statyki tego samego dnia**, nie z tidy (**potwierdzone przez autora**); agregacja (mediana / udział przystanków >= 4 odj./h) do wyboru w M2, bo zmienia ranking (rho 0,83-0,93); uwaga na granulację `stop_id`. Autor skłania się ku medianie, ale niepewny; rozważyć pokazanie na mapie (kolor odcinka/przystanku) zamiast surowej tabeli | T17 | M2, agregacja + forma prezentacji |

## 5. Ograniczenia

- **Krótkie okno:** 12-15 dni roboczych jednego miesiąca, bez ferii i jesieni; nie wolno wnioskować o sezonowości ani o progu 40 dni.
- **Podziały dni nie są niezależne czasowo** (te same tygodnie); losowe podzbiory mogą zawyżać zgodność względem dni odległych w czasie.
- **Brak porównania zewnętrznego:** operatorzy nie udostępniają prędkości, a `TripUpdates` dla `family A` nie istnieją (poza ŁKA, poza zakresem). Wszystkie liczby to rekonstrukcje jednej metody; testy pokazują stabilność i odporność, nie zgodność z rzeczywistością.
- **T2/T3 na sierpniu** (wakacje, rzadsza oferta), 6-7 miast, 1-2 dni każde; ranking miast pod wpływem parametrów nie był liczony, tylko efekt względem różnicy sąsiadów. Tolerancja kotwiczenia i wariant `dec` nie dla Pragi.
- **Nie testowano:** pokrycia sieci (`city_gate`), alternatywnych okien szczytów, T21 w praktyce (protokół zmiany metody), W12 w kilku dniach i po normalizacji `stop_id`.
- Turyn wypadł z rundy (za mało dni po bramce; feed często bez `trip_id`).

## 6. Jak powtórzyć

```
py scripts/t_l0.py build --from 2026-09-01 --to 2026-09-26 --workers 2      # tidy -> data/l0 (ok. 2-3 h lokalnie)
py scripts/t26_pooling.py --gate trips                                     # T26, T7
py scripts/t_sens.py all                                                   # T4-T22, T25
py scripts/t17_service.py                                                  # T17
# T1-T3: OTP_SRC=<git archive bccb17b>, OTP_PY=<venv>; py scripts/t2_param_sweep.py --city lodz --date 2026-08-12; py scripts/t2_summary.py
```
