# 11 · Pomysł: interaktywna wizualizacja pipeline'u (strona `/metodyka/`)

**Status: pomysł autora (2026-09-27), niezdecydowane, nie blokuje M1/M2.** Miejsce docelowe: `/metodyka/`
(`docs/06-site-spec.md` §3, zaplanowana już wcześniej — "strona metodyki z testem czułości", `docs/07` M7).
Do dopracowania z designem, realizacja najwcześniej M5–M7.

## Pomysł autora

Zamiast opisu tekstowego, pokazać metodykę jako serię plansz/map, po jednej na etap pipeline'u,
w miarę możliwości interaktywnie (np. suwak albo kolejne kroki), tak żeby czytelnik zobaczył
**to samo miejsce na mapie na kolejnych etapach przetwarzania**, a nie tylko czytał o filtrach.

## Weryfikacja: czy etapy z pomysłu odpowiadają rzeczywistemu pipeline'owi

Autor podał przykładowo: (1) surowe pozycje pojazdów jako punkty na mapie, (2) agregacja/przypisanie
do kursu jako linia kursu na mapie. Sprawdziłem to względem `easy-GTFS-RT/HOW-IT-WORKS.pl.md` §2 i
`docs/04-segments-and-data-model.md` — **kolejność się zgadza, ale łańcuch ma więcej kroków** i po
drodze rozjeżdża się na dwie gałęzie (family_a robi P50/P85, transit-index korzysta z osobnej,
wcześniejszej gałęzi — tidy). Poprawiona, zweryfikowana kolejność:

| # | etap | źródło (do wglądu, nie do cytowania w treści strony bez przeglądu) | co realnie się dzieje | pomysł na planszę |
|---|---|---|---|---|
| 1 | **Nagrywanie** | HOW-IT-WORKS §2.1 | GTFS-RT VehiclePositions odpytywane co 60 s | mapa punktów: jeden punkt = jedna pozycja pojazdu w jednej chwili |
| 2 | **Dopasowanie** | HOW-IT-WORKS §2.2, FA-12 | pozycja przypisywana do trasy/kursu (linia + kierunek); okno FA-12 zawęża szukanie do odcinka między sąsiednimi przystankami, gdy feed podaje `current_stop_sequence`/`stop_id` | te same punkty, teraz pokolorowane/przyciągnięte do linii trasy |
| 3 | **Zakotwiczenie przystanków** | HOW-IT-WORKS §2.3, FA-10/FA-11 | ustalenie, między którą parą kolejnych przystanków znajduje się pojazd (`shape_dist_traveled`) | podświetlony pojedynczy odcinek (para przystanków) z punktami, które do niego należą |
| 4 | **Interpolacja** | HOW-IT-WORKS §2.4, FA-13/FA-14/FA-18/FA-20 | liniowa interpolacja między dwoma pingami wyznacza moment przejazdu przez przystanek; tu odrzucane są przejścia niewiarygodne (zbyt szybkie/wolne, przerwa > 300 s, pierwsza para przystanków) | oś czasu (nie mapa): dwa pingi i interpolowany moment "przejazdu" między nimi, plus przykład odrzuconego przypadku z etykietą powodu (`seg_status`) |
| 5 | **Tidy (obserwacje)** | `transit_charts.cli extract`, `docs/02` | jeden wiersz = jedno przejście kursu przez parę przystanków, z etykietą `seg_status` (odrzucenia widoczne, nie ukryte) | tabela/lista obok mapy: "to jest jeden wiersz danych" |
| 6 | **L0 (transit-index, M1)** | `docs/04` §2 | filtr `seg_status == ok`, tryb i statyka tego samego dnia, flaga obszaru (`in_area`) | mapa: punkty/odcinki poza obszarem miasta wyszarzone, reszta zostaje |
| 7 | **L1 (transit-index, M2)** | `docs/04` §2 | agregacja wielu dni do poziomu odcinek fizyczny × pasmo × typ dnia (mediany, `ΣL/ΣT`) | mapa pokolorowanych odcinków wg prędkości (klasy `--speed-1..5`) — to już wygląda jak docelowa mapa serwisu |
| 8 | **L2/L3 (ranking)** | `docs/04` §2 | jedna liczba na miasto na wymiar, ranking | plansza z rankingiem, strzałka z powrotem do etapu 1 dla wybranego miasta |

**Ważne zastrzeżenie do zapamiętania:** family_a ma **swoją własną** "Agregację" i "Przebudowę"
(HOW-IT-WORKS §2.5–2.6), które produkują skorygowany rozkład P50/P85 — to jest **inny produkt**,
którego transit-index nie używa. Nasz pipeline odgałęzia się wcześniej, na poziomie pojedynczych
dopasowanych obserwacji (`matched.csv` → tidy), i robi własną agregację dopiero w M2 (L1). Plansza
o "agregacji" nie może więc pokazywać P50/P85 z family_a — to byłoby mylące (dwie różne rzeczy o tej
samej nazwie).

## Otwarte pytania (do rozstrzygnięcia, gdy wrócimy do tematu)

1. Realna interaktywność (suwak/scrollytelling z prawdziwymi danymi jednego kursu) czy statyczne
   plansze z podpisami — pierwsze jest ładniejsze, drugie dużo tańsze w M5/M6 (czas budżetu wydajności,
   `docs/06` §8).
2. Dane do plansz 1–5 (pojedyncze pozycje, interpolacja) nie istnieją w L0/L1 — trzeba by osobno
   wyciągnąć mały, ręcznie wybrany przykład (jeden kurs, jeden dzień) z surowych pozycji/`matched.csv`,
   wyłącznie do celów ilustracyjnych na stronie metodyki, nie z pipeline'u produkcyjnego.
3. Czy pokazywać to per miasto (z prawdziwymi, nieanonimowymi danymi wybranego kursu) czy jako jeden
   uniwersalny przykład dla całego serwisu.
4. Licencja/atrybucja przykładowych danych — dotyczy tych samych zasad co reszta (`docs/licenses.md`).

Nic z powyższego nie jest zdecydowane; to notatka do rozwinięcia razem z designem, nie specyfikacja.
