# 03 · Metryki, obszar, pasma i bramka jakości

Definicje są wykonywalne w `reference/metrics_reference.py` (samotest: `python reference/metrics_reference.py`) i sprawdzone na prawdziwych danych (`docs/09`, `reference/golden_values.json`). Wszystkie progi trafiają do `config/metrics.yaml`, nie do kodu. Progi oznaczone **[PROPOZYCJA]** mają uzasadnienie w danych, ale wymagają potwierdzenia na pełnym oknie edycji.

## 1. Zasady

1. Jednostką obserwacji jest **przejazd kursu przez odcinek** (wiersz tidy z `seg_status == "ok"`).
2. Każda liczba pokazywana użytkownikowi ma liczbę obserwacji `n` i status jakości. Komórka z małą próbą jest oznaczona, nigdy pusta.
3. Mediany i percentyle są normą w `transit_charts`. Wyjątek: prędkość komunikacyjna, która z definicji jest sumą dystansów przez sumę czasów, z obowiązkowym testem czułości (sekcja 9).
4. Indeks mierzy **jakość funkcjonowania** transportu publicznego, nie samą prędkość (misja z `design/readme.md`: "how well public transport actually works"). Jest **wielowymiarowy, bez wskaźnika złożonego w v1** (D11, rozstrzygnięte). Każdy wymiar ma własny ranking, `n` i status jakości. Wskaźnik złożony to cel v2 i wymaga testu wag (sekcja 4.4).
5. Nie porównuj liczb z TomTom Traffic Index: TomTom mierzy samochody względem swobodnego przepływu, my transport publiczny z postojami.

### Model jakości: pięć wymiarów

| wymiar | pytanie | metryka (ID) | kierunek | status |
|---|---|---|---|---|
| Prędkość | jak szybko jedzie | prędkość komunikacyjna W1 (+ czas 10 km W2) | więcej = lepiej | zweryfikowana na danych (`docs/09`); metryka nagłówkowa potwierdzona na pełnym oknie, w tym tramwaje (ADR-0005) |
| Obciążenie szczytu | ile traci w godzinach szczytu | kara szczytu W3 | mniej = lepiej | zweryfikowana (Łódź, 9 dni); AM/PM osobno potwierdzone na 16 miastach (M2) |
| Punktualność | czy jedzie według rozkładu | udział przyjazdów "o czasie" W10 | więcej = lepiej | zweryfikowana na 16 miastach, 14-19 dni (M2); progi C11 potwierdzone (ADR-0006) |
| Regularność | czy przyjeżdża w równych odstępach | nadmiar czasu oczekiwania EWT W11 (linie częste) | mniej = lepiej | zweryfikowana na 16 miastach (M2); agregacja i próg potwierdzone (ADR-0006) |
| Oferta | jak często jeździ według rozkładu | rozkładowe odjazdy na godzinę W12 | więcej = lepiej | zweryfikowana na 16 miastach (M2, ADR-0006); ranking tramwajowy niepewny co do metody agregacji; mierzy rozkład, nie wykonanie |

Prędkość jest jednym z pięciu wymiarów, nie nagłówkiem całości. Co jest **poza modelem**, bo nie wynika z GTFS/GTFS-RT: dostępność przystanków i pojazdów, ceny, komfort, bezpieczeństwo, zatłoczenie oraz **realizacja kursów** (nie da się odróżnić odwołanego kursu od kursu, którego pojazd zniknął z feedu, więc `trip_coverage` jest miarą jakości danych, nie usługi).

## 2. Zakres analizy (wspólny dla wszystkich wymiarów)

### 2.1 Obszar miasta (W0, warunek konieczny)

**Bez filtra obszaru ranking jest zniekształcony przez linie podmiejskie i regionalne** (dane 2026-09-24, prędkość autobusów `ΣL/ΣT`, przybliżenie: oba przystanki odcinka w promieniu od środka sieci):

| miasto | cała sieć | R ≤ 8 km (udział obserwacji) | R ≤ 12 km | R ≤ 20 km |
|---|---|---|---|---|
| Praga | 28,1 | **20,9** (38%) | 22,2 (63%) | 23,4 (77%) |
| Poznań | 27,8 | **23,4** (75%) | 25,6 (86%) | 27,6 (98%) |
| Warszawa | 20,1 | 18,1 (62%) | 18,8 (84%) | 19,6 (97%) |
| Rzym | 16,7 | 13,7 (59%) | 15,4 (81%) | 16,6 (97%) |
| Łódź (9 dni) | 18,3 | 17,5 (92%) | | |

Tramwaje prawie się nie zmieniają (Praga 18,7 → 17,6). Prawdopodobna przyczyna (do potwierdzenia w M0): feed PID obejmuje także linie regionalne, a feed ZTM Poznań przewoźników podmiejskich; takie linie mają długie odcinki i wysokie prędkości.

**Pomiar z poligonami (M0, 2026-09-24, prędkość autobusów `ΣL/ΣT`, poligon GISCO Urban Audit 2024; pełna tabela: `docs/data-inventory.generated.md` §7):** Łódź 18,24 → 17,88; Warszawa 20,14 → 19,17; Kraków 21,32 → 19,71; Gdańsk 19,42 → 19,11; Poznań 27,84 → 26,61 (udział obserwacji 73%); Praga 28,10 → 22,22 (70%); Bukareszt 15,64 → 14,04; Zagrzeb 24,09 → 23,40; Nikozja 27,15 → 20,97 (71%). Poligon zmienia wynik o 0,0–6,2 km/h (prawie wcale w Rzymie, Sofii, Lizbonie i Lublanie, najmocniej w Pradze i Nikozji) i obcina do 30% obserwacji. Uwaga: Poznań po filtrze nadal ma najwyższą prędkość autobusów (26,6 km/h wobec 19–21 w Krakowie i Warszawie), co M2 ma wyjaśnić (linie ekspresowe albo metropolitalne w obrębie miasta).

Wymaganie: **odcinek wchodzi do indeksu tylko wtedy, gdy oba jego przystanki leżą wewnątrz wielokąta miasta** (`config/areas/<miasto>.geojson`). Źródło wielokąta jest decyzją M0 (`docs/08`, D12): granica administracyjna z OpenStreetMap (ODbL) albo obszar z Eurostat GISCO. TomTom też zmienił metodę wyznaczania centrów i obszarów metropolitalnych, żeby porównania były standaryzowane (komunikat o edycji 2025). W `summary.json` zapisuj `area.definition`, `source` i `share_of_obs_in_area`. `radius_fallback` (promień od mediany przystanków) jest tylko do testów wewnętrznych i nie wolno go publikować. GZM jest metropolią, nie miastem: osobna etykieta i osobny wielokąt.

### 2.2 Dzień referencyjny

`day_type == WEEKDAY` (z `family_a.calendar_scope.day_type_for_date`) po wyłączeniu:
- świąt państwowych **każdego kraju osobno** (funkcja `day_type_for_date` nie zna świąt; kalendarze generuj biblioteką `holidays` z PyPI i zapisuj w `config/calendars/<miasto>.yaml` jako jawną listę),
- przerw szkolnych (ferie, przerwy świąteczne) tam, gdzie są znane,
- dni anomalnych wykrytych automatycznie (sekcja 7).

### 2.3 Pasma czasu

Godzina lokalna miasta z `obs_local` (kolumna jest już w czasie lokalnym z offsetem strefy, zweryfikowane dla 10 miast: godziny 6–21 lokalnie w Lizbonie, Wilnie i Warszawie; nie konwertuj strefy ponownie). Godzina końca odcinka.

| pasmo | godziny lokalne |
|---|---|
| `all_day` | 6–21 (06:00–22:00) |
| `am_peak` | 7, 8 |
| `midday` | 9–13 (09:00–14:00) |
| `pm_peak` | 14–17 (14:00–18:00) |
| `evening` | 18–21 (18:00–22:00) |
| `h06`…`h21` | pojedyncze godziny (suwak, profil godzinowy) |

Godzina 6 należy tylko do `all_day`; pasma nazwane pokrywają 07:00–22:00 bez luk. Okna są decyzją autora z 2026-09-30 (issue #5; wcześniej propozycja 7–8 / 10–13 / 15–17 / 19–21 z godzinami przejściowymi 9, 14, 18); tabela w sekcji 3 i wyniki M2 były liczone na starych oknach i po zmianie wymagają przeliczenia. Pasmo obowiązuje miasto, gdy nagranie pokrywa ≥ 90% jego godzin.

### 2.4 Tryby i statyka tego samego dnia

`mode_from_route_type()` z `metrics_reference.py`: `tram` = 0 oraz 900–999; `bus` = 3, 700–799 oraz trolejbusy 11, 800–899 (doliczane do `bus`, z etykietą); poza indeksem metro (1, 400–499) i kolej (2, 100–199). Rozszerzone typy są **realnie używane** (Gdańsk: 700 i 900), a Warszawa ma w feedzie metro i kolej, więc filtr jest konieczny. `route_type` bierz ze statyki **tego samego dnia**: statyka z 24.09 mapuje na trasy z 9 dni Łodzi tylko 98,65% wierszy.

## 3. Metryki v1

| ID | nazwa | definicja | jednostka | użycie |
|---|---|---|---|---|
| W1 | prędkość komunikacyjna | `v = 3,6 · ΣL / ΣT` po obserwacjach `ok` w obszarze (L = `seg_dist_m`, T = `seg_time_s`) | km/h | ranking wymiaru Prędkość (miasto × tryb × pasmo) |
| W2 | czas przejazdu 10 km | `600 / v` | min | analog TomTom; obok W1 |
| W3 | **kara szczytu** | `ΣT_pasmo / Σ(L / v_ref) − 1`, gdzie `v_ref` = prędkość tego samego odcinka w pasmach `midday`+`evening`; tylko odcinki z ≥ 10 obserwacji w paśmie i w odniesieniu | % | ranking wymiaru Obciążenie szczytu, mapa (`pen_pm`) |
| W4 | prędkość odcinka | mediana, P20, P80 prędkości odcinka fizycznego w paśmie | km/h | mapa kolorowanych odcinków |
| W5 | rozstaw przystanków | mediana `seg_dist_m` | m | kowariat obok rankingu |
| W6 | prędkość względem rozkładu | `v_zmierzona / v_rozkładowa − 1`, `v_rozkładowa` z `sched_pass_time_s()` | % | informacja |
| W7 | rozrzut czasu przejazdu **(v1.1)** | mediana ważona długością z `P85(T)/P50(T)` dla odcinek × pasmo | bezwym. | informacja |
| W8 | najwolniejsze odcinki | top 10 według W4 z `L ≥ 100 m`, `q = ok` | — | strona miasta |
| W9 | profil godzinowy | W1 dla `h06…h21` (zmierzony i rozkładowy) | km/h | strona miasta |
| W10 | punktualność | udział przyjazdów "o czasie" (sekcja 4.1) | % | **ranking wymiaru Punktualność** |
| W11 | nadmiar czasu oczekiwania (EWT) | sekcja 4.2, tylko linie częste | min | **ranking wymiaru Regularność** |
| W12 | oferta rozkładowa | mediana rozkładowych odjazdów na godzinę na przystanek (sekcja 4.3) | odj./h | **ranking wymiaru Oferta** |
| W3x | spowolnienie względem P85 **(eksperymentalne, poza rankingiem)** | `ΣT_obs / ΣT_ff − 1`, `v_ff` = P85 prędkości odcinka | % | wyłącznie test czułości |

### Dlaczego kara szczytu, a nie spowolnienie względem P85

Pierwotnie W3 było spowolnieniem względem "prędkości swobodnej" (P85). Test na 9 dniach Łodzi pokazał, że **wartość zależy niemal liniowo od wybranego kwantyla**, więc nie ma interpretacji bezwzględnej:

| kwantyl `v_ff` | cały dzień | am | pm | wieczór |
|---|---|---|---|---|
| 0,50 | 4,6% | 6,2% | 11,2% | −2,8% |
| 0,70 | 20,5% | 22,4% | 28,1% | 12,1% |
| 0,85 | 37,0% | 39,1% | 45,6% | 27,4% |
| 0,95 | 57,2% | 59,4% | 66,9% | 46,2% |

Dodatkowo autobusy i tramwaje dają praktycznie ten sam wynik (37,0% vs 37,1%), czyli miara wychwytuje rozrzut postojów i interpolacji, nie różnice modalne. Kara szczytu porównuje te same odcinki w różnych porach (porównanie sparowane) i jest bez arbitralnego kwantyla. Łódź, 9 dni, pasma odniesienia `midday`+`evening`:

| tryb | kara AM | kara PM |
|---|---|---|
| autobus | **+6,7%** | **+13,2%** |
| tramwaj | +1,0% | +3,3% |
| łącznie | +4,5% | +9,4% |

Wynik jest sensowny (autobusy w ruchu mieszanym tracą więcej niż tramwaje na torowiskach; szczyt popołudniowy gorszy od porannego) i stabilny względem wyboru odniesienia (PM vs sam `midday`: +6,5% ogółem; vs sam `evening`: +14,3%). Nazwa robocza: "kara szczytu" (o ile dłużej trwa przejazd w szczycie niż poza nim na tych samych odcinkach). Jest to analog czasu straconego w szczycie u TomTom, ale nie jest z nim porównywalna.

**Konsekwencja dla designu:** sekcja "Liczba" landingu (`design/ui_kits/landing/copy.js`: "−22% wolniej niż 10% najszybszych przejazdów") opiera się na mierze zależnej od kwantyla i ma dane zastępcze. Po podpięciu prawdziwych danych jej copy ma pokazywać karę szczytu W3 (decyzja autora); wtedy zmienia się tekst, nie układ.

### Prędkość rozkładowa `v_sched` (W6)

Użyj `sched_pass_time_s()`: `sched_arr` wiersza minus `sched_arr` poprzedniego przystanku (przejazd-do-przejazdu, jak `seg_time_s`). Kolumna `sched_seg_time_s` w tidy to przyjazd minus **odjazd** z poprzedniego przystanku. Dla autobusów i tramwajów w 15 sprawdzonych miastach średnia różnica wynosi 0–0,7 s (postoje w rozkładzie zwykle zerowe), więc rozbieżność ma znaczenie tylko dla feedów z postojami (np. metro w Pradze), ale konwencja przejazd-do-przejazdu jest bezpieczna wszędzie.

## 4. Wymiary jakości poza prędkością (W10–W12, v1)

Wszystkie trzy wynikają z danych, które już są w tidy (bez dodatkowego zbierania). Obowiązują te same filtry co dla prędkości: obszar W0, tryb ze statyki tego samego dnia, dzień referencyjny, pasma i bramka jakości. Progi w `config/metrics.yaml`.

### 4.1 Punktualność (W10)

Udział przyjazdów w klasach opóźnienia `delay_s` (przyjazd zaobserwowany minus rozkładowy), **bez pierwszego przystanku kursu** (`is_first_stop`), z progami z `transit_charts` C11: za wcześnie `< −60 s`, **o czasie `−60…+180 s`**, spóźniony `+180…+600 s`, bardzo spóźniony `> +600 s`. Wartość rankingowa: udział "o czasie" (więcej = lepiej); pozostałe klasy w `punctuality_share` (`schemas/city_summary.schema.json`).

Wstępnie, 2026-09-24 (jeden dzień, bez filtra obszaru): udział "o czasie" Łódź 66,1%, Warszawa 70,0%, Gdańsk 71,9%, Kraków 72,8%, Poznań 76,2%. **Nie walidowane** (bez testu czułości i bez wielu dni). Uwagi:
- opóźnienie pochodzi z interpolacji i podlega tej samej luce obserwacji co prędkość (pojazd znikający z feedu nie wnosi obserwacji);
- Kraków ma niemal zerowy udział "za wcześnie" (0,5%): sprawdzić, czy feed nie przycina wyników;
- próg +180 s to konwencja `transit_charts`, nie standard; test czułości na progach 120/180/300 s.

### 4.2 Regularność (W11)

**Nadmiar czasu oczekiwania (EWT)** tylko dla linii częstych (`sched_headway_s < frequent_headway_s`, propozycja 600 s), bo przy rzadkich kursach pasażer jedzie według rozkładu, nie przychodzi losowo. Dla odstępów `h` (s) w komórce przystanek × grupa linii × kierunek × pasmo:

```
AWT = Σ h² / (2 Σ h)     # średni czas oczekiwania, odstępy zaobserwowane (headway_s)
SWT = Σ h² / (2 Σ h)     # to samo dla odstępów rozkładowych (sched_headway_s)
EWT = AWT − SWT          # minuty; mniej = lepiej
```

Wartość miasta: sumy `Σh²` i `Σh` zbiorcze po wszystkich komórkach (tak jak `ΣL/ΣT` dla prędkości), z testem czułości względem mediany po przystankach. Wiersze z `headway_spans_outage` wyłączone. Obsługa `headway_skips_vehicles` (pojazd pominięty przez rekonstrukcję) i minimalna liczba odstępów w komórce: **do ustalenia w M2** na podstawie definicji `transit_charts` B6/B8/H29. **Niezweryfikowane na prawdziwych danych.**

### 4.3 Oferta rozkładowa (W12)

Mediana po przystankach w obszarze miasta z liczby **rozkładowych** odjazdów na godzinę w paśmie `midday` (9–13, 09:00–14:00; okno pasma z `config/metrics.yaml`), osobno dla trybu; źródło: `stop_times.txt` statyki tego samego dnia (**rozstrzygnięte, R10**: tidy zaniża ofertę nawet o 64%, bo obejmuje tylko obserwowane kursy). Mediana liczona dzień po dniu (własny kalendarz/`stop_times` każdego dnia), potem mediana po dniach okna. Jednostka: odj./h (obie strony razem).

- To jest **jakość rozkładu, nie wykonania**: metryka nie mówi, czy kursy naprawdę wyjechały (patrz "poza modelem" w §1). Na stronie zawsze podpisana "według rozkładu".
- **Agregacja (T17, M2, ADR-0006):** mediana po przystankach potwierdzona jako odporna dla autobusów (ρ = 0,965/0,939 wobec udziału przystanków ≥ 4/6 odj./h, 16 miast), ale **niepewna dla tramwajów** (ρ = −0,155 — sieci tramwajowe są mniejsze i gęstsze, mediana i próg udziału dają praktycznie niepowiązane rankingi). Mediana zostaje jedyną publikowaną liczbą, ale ranking W12 tramwajów ma jawną adnotację niepewności metodycznej (nie status jakości danych) — forma prezentacji do ustalenia z designem w M5, propozycja R10: mapa (kolor odcinka/przystanku), nie surowa tabela rankingu.
- Godziny obsługi (pierwszy i ostatni kurs) nie są obserwowalne z tidy: nagrywanie obejmuje tylko 06:00–22:00. Poza v1.
- **Zweryfikowane na prawdziwych danych (M2, 16 miast, 14-19 dni).**

### 4.4 Wskaźnik złożony (v2, nie v1)

Jeśli powstanie: rangi percentylowe wymiarów, jawne wagi, **test wrażliwości na wagi** (losowe wagi, stabilność rang Spearmana), i osobna decyzja autora. Do tego czasu strona pokazuje wymiary obok siebie i nie sumuje ich w jedną liczbę.

## 5. Klasy prędkości

Pięć klas (tokeny `--speed-1…5` z `design/tokens/colors.css`, plus `--speed-nodata` dla braku danych), cztery krawędzie w km/h: **`[15, 20, 25, 30]`** → `<15`, `15–20`, `20–25`, `25–30`, `≥30`. Liczba klas wynika z designu (design nadrzędny); wcześniejsza wersja miała sześć klas z krawędzią 10 km/h, ale poniżej niej leżało tylko 3,4% sieci Łodzi.

**Sprawdzone na pełnym oknie (T18, M2, 2026-09-27, ADR-0006): krawędzie zostają bez zmian, ale to nie jest czysty "confirm".** Udział długości sieci w klasach na 16 miastach (tabela w ADR-0006) waha się szeroko: od zrównoważonego Krakowa (9,7/23,2/29,0/19,6/18,4%) po przekrzywioną Lizbonę (40,5/30,6/15,5/7,7/5,7%). 4 z 16 miast (Bukareszt, Lizbona, Turyn, Zagrzeb) przekraczają 35% w jednej klasie; 3 z tych 4 mają już zarejestrowaną wadę feedu w `config/city_defects.yaml` (`weak_coverage`, `no_trip_id`/`trip_id_unstable`, `suburban_lines`), która wiarygodnie tłumaczy przekrzywienie niezależnie od krawędzi. Lizbona nie ma zarejestrowanej wady — możliwe, że jej wolna sieć (wąskie uliczki, zabytkowe tramwaje) to realna cecha, nie błąd danych; do sprawdzenia ręcznie (T25) przed M3. Współdzielone krawędzie i tak nie dopasują się do każdego profilu miasta bez utraty porównywalności, więc zostają.

| miasto (2026-09-24, bus+tram, obserwacje ważone długością) | kwintyle 20/40/60/80% [km/h] |
|---|---|
| Łódź (9 dni, mediany odcinków n ≥ 10) | 16,2 / 20,8 / 25,0 / 30,4 |
| Warszawa | 15,6 / 20,1 / 24,4 / 30,7 |
| Kraków | 16,2 / 20,5 / 25,0 / 31,2 |
| Gdańsk | 14,9 / 19,0 / 23,2 / 29,4 |
| Poznań | 17,3 / 23,2 / 29,3 / 37,8 (bez filtra obszaru) |
| Praga | 19,6 / 26,3 / 35,1 / 46,0 (bez filtra obszaru) |
| Sofia | 13,8 / 18,0 / 22,6 / 30,5 |

Udział długości sieci Łodzi w pięciu klasach: 15,5% / 21,5% / 22,8% / 19,3% / 20,9% (z poprzedniego podziału sześcioklasowego 3,4% + 12,1% / 21,5% / 22,8% / 19,3% / 20,9%). Wcześniej proponowane `[8, 12, 18, 25]` wrzucało 40% sieci do jednej klasy. Po włączeniu filtra obszaru powtórz kalibrację na pełnym oknie pilotażu i **zamroź krawędzie** (te same w każdym mieście i edycji). Krawędzie żyją w `config/metrics.yaml` (jedno źródło prawdy); design dostarcza tylko kolory (test w M5 sprawdza liczbę tokenów i klas). Klasa `i` z `speed_class()` (`metrics_reference.py`, liczona od 0) odpowiada tokenowi `--speed-{i+1}`. Przykładowy podział w prototypie designu (`design/ui_kits/landing/Sections.jsx`, krawędzie 10/14/18/22) jest ilustracją z danymi zastępczymi, nie kalibracją.

## 6. Ranking i bramka jakości

- Domyślny widok: `all_day`, `WEEKDAY`; przełączniki: wymiar, tryb, pasmo. **Jeden ranking na wymiar:** prędkość (W1, malejąco), obciążenie szczytu (W3, rosnąco), punktualność (W10, malejąco), regularność (W11, rosnąco), oferta (W12, malejąco). Obok: `n_days`, `n_obs`, pokrycie sieci, W5. Miasto może być `ranked` w jednym wymiarze i `limited` w innym (np. brak linii częstych dla W11); status wymiaru wynika z jego `n` i progów.
- Miasto bez wartości w wymiarze nie dostaje miejsca w jego rankingu, ale zostaje w pozostałych.
- Status miasta: `ranked`, `limited` (na liście z adnotacją), `excluded` (poza rankingiem z kodem przyczyny, `schemas/ranking.schema.json`).
- **Niepewność [PROPOZYCJA]:** bootstrap po dniach (ok. 200 losowań dni ze zwracaniem), przedział 90%; miasta o nakładających się przedziałach oznacz jako nierozróżnialne. Dzienna zmienność jest mała (Łódź, 9 dni roboczych: `ΣL/ΣT` 17,52–17,69 km/h), więc przedziały będą wąskie, a różnice miast rzędu 1 km/h rozróżnialne.

Bramka na trzech poziomach. Wartości domyślne oparte na progach `family_a` (FA-15: `max_reject_share 0.25`, `min_corrected_route_share 0.40`; FA-16: `max_unknown_trip_share 0.20`) i na obserwowanych rozkładach (15 miast, 2026-09-24: `crossing_rate` 0,71–0,89, udział `ok` 0,64–0,84; najniższe: Bukareszt 0,708 i 0,641, Kraków 0,793 i 0,725):

```yaml
# config/metrics.yaml (fragment)
method_version: "ti-1.0-draft"
speed_classes_kmh: [15, 20, 25, 30]   # 5 klas = --speed-1..5 z design/
bands: {am_peak: [7, 8], midday: [9, 10, 11, 12, 13], pm_peak: [14, 15, 16, 17], evening: [18, 19, 20, 21]}
area: {require_polygon: true}
segment_min:
  ok:   {n_obs: 10, n_days: 5}
  thin: {n_obs: 3}
peak_penalty: {ref_bands: [midday, evening], min_obs_per_segment: 10}
punctuality: {on_time_s: [-60, 180], late_s: 600, exclude_first_stop: true}   # W10, progi C11
regularity: {frequent_headway_s: 600, min_headways_per_cell: null}           # W11; próg do kalibracji w M2
service: {band: midday, min_stop_departures: 1}                               # W12
top_segments: {min_length_m: 100}
day_gate:
  min_crossing_rate: 0.60          # dzień: udział przystanków z zaobserwowanym przejazdem (15 miast: 0,71-0,89)
  min_ok_share: 0.55               # udział wierszy seg_status == ok (15 miast: 0,64-0,84)
  min_plausible_service_date: 0.90
  min_band_recorded_share: 0.90
  anomaly_min_trip_ratio: 0.70
city_gate:                         # progi pilotażu; edycja roczna wymaga innych
  ranked:   {min_valid_days: 40, min_network_coverage: 0.60}
  limited:  {min_valid_days: 20, min_network_coverage: 0.40}
mode_min: {routes: 3, segments: 50}
```

- **Dzień** przechodzi bramkę, gdy spełnia wszystkie `day_gate`. Brak release'u w danym dniu jest normalny (Turyn 2026-09-24 nie ma release'u), liczy się jako dzień niewazny.
- **Miasto**: status według `city_gate`; wykluczenia z `config/city_defects.yaml` mają pierwszeństwo.
- **Odcinek × pasmo**: `segment_quality(n_obs, n_days)`. Na 9 dniach Łodzi udział długości sieci z `q = ok`: całodzienne 95,2%, w pasmach 83,0–86,4%.

## 7. Dni anomalne

Automatyczna detekcja, żeby nie polegać wyłącznie na kalendarzu: dzień anomalny, gdy liczba kursów w tidy (lub na godzinę) spada poniżej `anomaly_min_trip_ratio` mediany tego samego `day_type` (**kryterium obowiązkowe**: `docs/sensitivity-report.md` §3.2 pokazuje dni, w których statyka nie pasuje do części kursów RT, `crossing_rate` i udział `ok` wyglądają zdrowo, a W1 miasta jest zawyżony nawet o 40%, np. Poznań 10.09: 27,3 wobec 19,5 km/h), gdy nagranie ma dużą lukę w paśmie albo gdy mediana prędkości miasta odbiega o więcej niż 3 MAD od mediany dni. Detekcja zwraca powód; lista dni idzie do manifestu.

## 8. Ograniczenia widoczne przy wynikach

1. **Rekonstrukcja, nie pomiar.** Interpolacja liniowa z pozycji co 60 s; pary pingów > 300 s odrzucane.
2. **Optymistyczne obciążenie.** Pojazd znikający z feedu nie wnosi obserwacji; `crossing_rate` 0,71–0,89 (Łódź 0,865).
3. **Prędkość zawiera postoje** i zależy od rozstawu przystanków (stąd W5 obok rankingu). Rozdzielenie jazdy i postoju nie jest możliwe przy próbkowaniu 60 s. Pole `speed` z VehiclePositions ma tylko część feedów.
4. **Bez porównania z TomTom.** Nie zestawiaj liczb.
5. **Obszar miasta jest decyzją metodyczną** (2.1); podawaj źródło wielokąta.
6. **Wakacje.** Dane sprzed 2026-09-01 mają rzadszą ofertę; pilotaż używa okna szkolnego.
7. **Metoda ma wersję.** Wyniki z różnych `method_version` nie są porównywalne.
8. **Wymiary nie są sumowane.** Wysokie miejsce w jednym wymiarze nie oznacza dobrej jakości ogółem; strona nie podaje jednej oceny miasta (v1).
9. **Oferta (W12) to rozkład**, nie wykonanie kursów.

## 9. Test czułości (M2)

Ta tabela dotyczy definicji metryk. Pełny plan testów (parametry zapieczone w tidy, zbieżność po liczbie dni, wiarygodność podziałowa odcinków, bramka, wersje metody, weryfikacja zewnętrzna) jest w `docs/10-input-methodology-and-test-plan.md`.

Raport per miasto i tryb z korelacją rang Spearmana między wariantami:

| wariant | pytanie | wynik wstępny (5 miast PL, 1 dzień) | wynik na pełnym oknie (16 miast, 14-19 dni, M2) |
|---|---|---|---|
| W1 (`ΣL/ΣT`) vs mediana ważona długością | czy ciężkie ogony przestawiają ranking | łącznie i autobusy: identyczna kolejność (ρ = 1,0); **tramwaje: ρ = 0,7** (Kraków/Poznań/Warszawa zamieniają się miejscami) | łącznie ρ = 0,974; autobusy ρ = 0,974; **tramwaje ρ = 0,986** — ostrzeżenie z próbki 1-dniowej się nie potwierdziło (ADR-0005) |
| bez 1% najwolniejszych obserwacji | wpływ postojów pośrednich | do policzenia w M2 | odłożone (niski priorytet, T13 głównego wariantu już potwierdzone) |
| pasma odniesienia W3 (`midday`, `evening`, oba) | wrażliwość kary szczytu | Łódź: kolejność AM < PM i autobus > tramwaj utrzymana w każdym wariancie | potwierdzone na 16 miastach: AM < PM w każdym mieście z danymi (`reports/m2/sensitivity_by_city.csv`) |
| tylko wt–czw | wpływ poniedziałków i piątków | do policzenia w M2 | odłożone do listopada (T7/T9, ≥ 40 dni) |
| bez pierwszej i ostatniej godziny pasma | wpływ brzegów okna nagrania | do policzenia w M2 | odłożone do listopada |
| bootstrap po dniach | szerokość przedziałów | do policzenia w M2 | M3 (`ti gate`) |
| W10: progi 120/180/300 s | czy ranking punktualności zależy od progu "o czasie" | do policzenia w M2 | ρ = 0,953 (120s) i 0,950 (300s) vs bazowe 180s — próg potwierdzony (ADR-0006) |
| W11: `ΣΣ` zbiorcze vs mediana po przystankach; próg linii częstych 480/600/720 s | czy ranking regularności zależy od agregacji i progu | do policzenia w M2 | ρ ≥ 0,965 na obu wymiarach zmienności — agregacja i próg 600s potwierdzone (ADR-0006) |
| W12: mediana po przystankach vs udział przystanków ≥ próg | czy ranking oferty zależy od struktury sieci | do policzenia w M2 | autobus ρ = 0,965 (≥4/h) / 0,939 (≥6/h) — odporne; **tramwaj ρ = −0,155 — niepewne, ADR-0006** |
| korelacja rang między wymiarami | czy wymiary niosą różną informację (jeśli ρ ≈ 1, wymiar jest zbędny) | do policzenia w M2 | W1×W3(pm) ρ = 0,10; W1×W10 ρ = 0,56; W1×W11 ρ = −0,52; **W10×W11 ρ = −0,93 na poziomie miasta, ale ρ = −0,79 (pula) i od −0,92 do +0,38 per miasto na poziomie linii — w większości miast dużo poniżej progu 0,9, więc to głównie zbieżność między miastami, nie ta sama informacja w obrębie miasta (ADR-0006, R3)** |

**Reguła decyzyjna:** jeśli korelacja rang nagłówka z wariantem odpornym < 0,9, publikuj oba lub przejdź na wariant odporny i zapisz decyzję w `docs/adr/`. Dla tramwajów (ρ = 0,7 na jednym dniu) wynik jest sygnałem ostrzegawczym, nie rozstrzygnięciem: wymaga powtórzenia na wielu dniach i po filtrze obszaru.
