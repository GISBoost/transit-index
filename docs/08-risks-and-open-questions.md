# 08 · Ryzyka i decyzje do podjęcia

Dokument roboczy: zawiera uwagi wizerunkowe i prawne, więc **nie commituj go do publicznego repo** bez przeglądu.

## 1. Decyzje do podjęcia (z rekomendacją)

| # | Pytanie | Rekomendacja / stan | Kiedy |
|---|---|---|---|
| D1 | Zakres rankingu | **Rozstrzygnięte: kilkanaście miast europejskich.** Status `ranked`/`limited`/`excluded` z bramki jakości (`03` §6); Bukareszt (pokrycie 0,64) już dziś byłby `limited` | — |
| D2 | Metryka wymiaru Prędkość (nie całego indeksu; D11) | `ΣL/ΣT`; test czułości: dla łącznie i autobusów kolejność zgodna z medianą ważoną, dla tramwajów ρ = 0,7 (`09` F15), więc **rankingi tramwajów oznacz przedziałami i nie przeceniaj pojedynczych miejsc** | M2 |
| D3 | Okno pilotażu | 2026-09-01 – 2026-12-18 (okres szkolny); kalendarze świąt i ferii per kraj (`05`) | przed M3 |
| D4 | Nazwa i adres | Robocza: **Transit Index** (z designu), opis "Indeks jakości transportu publicznego"; `gisboost.github.io/transit-index/`. Unikaj "Traffic Index"; sprawdź kolizje nazwy przed publikacją. Uwaga: nadrzędny `easy/CLAUDE.md` zakłada, że strony pod `gisboost.github.io` są bez build stepu; ten projekt wybiera Astro (D5), więc wymaga to zatwierdzenia i dopisania do tabeli w `easy/CLAUDE.md` | przed M5 |
| D5 | Stack | Astro + MapLibre + PMTiles (`06`) | M5 |
| D6 | Tryby | tramwaj, autobus (z trolejbusami), łącznie; metro i kolej poza | M2 |
| D7 | Licencja wyników | Po audycie licencji źródeł w M0; wstępnie CC BY 4.0 dla agregatów, jeśli nie koliduje z warunkami operatorów (przy 15+ krajach warunki różnią się bardziej) | po M0 |
| D8 | GZM: miasto czy metropolia | Osobna etykieta "metropolia", poza rankingiem miast | M3 |
| D9 | Rytm publikacji | Styczeń (jak TomTom) | przed M7 |
| D10 | Płatne treści a Pages | Sprzedaż musi być poza Pages | przy monetyzacji |
| D11 | Wskaźnik złożony czy osobne wymiary | **Rozstrzygnięte (2026-09-26):** osobne wymiary w v1: prędkość, obciążenie szczytu, punktualność, regularność, oferta (`03` §1). Wskaźnik złożony w v2, po teście wag | — |
| D12 | Źródło poligonów obszaru miasta (W0) | Granica administracyjna OSM albo Eurostat GISCO (jedno źródło dla wszystkich miast, ze względu na spójność; zapisz wersję w manifeście). Filtr zmienia wyniki o kilka km/h (`09` F13) | M0/M2 |
| D13 | Copy landingu w designie (sekcja "Liczba", hero, nagłówek rankingu, "Uczciwie") mówi tylko o prędkości | Zmienić przy podpinaniu prawdziwych danych: kara szczytu zamiast "−22% vs 10% najszybszych", przełącznik wymiarów w rankingu (`06` §9). Po stronie designu | przed M5 |
| D14 | Nazwa i skala wymiarów w UI: jak nazwać pięć wymiarów po polsku i angielsku, czy pokazywać je jako kartę miasta | Do zaprojektowania w Claude Design; docs podają tylko identyfikatory (`speed`, `peak_penalty`, `punctuality`, `regularity`, `service`) | przed M5 |

## 2. Ryzyka danych i metody

| ryzyko | skutek | mitygacja |
|---|---|---|
| Rekonstrukcja z pozycji co 60 s, interpolacja | prędkości nie są pomiarem | jawna metodyka, test czułości, oznaczenia |
| Pojazdy znikające w korku | optymistyczne obciążenie | notka na stronie; bez wniosków o "stratach" bezwzględnych |
| Prędkość zawiera postoje | ranking zależy od rozstawu przystanków | W5 obok rankingu, osobne rankingi trybów |
| **Definicja obszaru miasta** | linie podmiejskie zawyżają prędkość (Praga autobusy 28,1 → 20,9) | W0 obowiązkowy, poligony w `config/areas/`, test na wartościach wzorcowych |
| **Statyka zmienia się między dniami** | 1,35% wierszy nie mapuje się na trasę ze statyki innego dnia | statyka per dzień, deduplikacja po SHA-256 |
| **Luki dzienne** (Turyn 24.09 bez release'u) | brak dnia, mniejsza próba | rejestr dni, bramka `n_days`, alert brakującego release'u |
| Jakość feedów (Bukareszt `crossing_rate` 0,71; Turyn bez `trip_id`; Helsinki) | fałszywe wyniki lub luki | rejestr wad, status `limited`/`excluded` z powodem |
| **Wymiary jakości mierzą różne rzeczy i mogą się nie zgadzać** (miasto szybkie, ale nieregularne) | wrażenie sprzeczności, presja na jedną liczbę | brak wskaźnika w v1, korelacje rang wymiarów w M2, jasna baza każdego wymiaru |
| Oferta (W12) to rozkład, nie wykonanie | czytelnik weźmie ją za pomiar | podpis "według rozkładu", brak wniosków o realizacji kursów |
| Zmiana metody w tle (`easy-OTP` na `main`) | nieporównywalne dni | przypięty tag, `method_version`, manifest |
| Święta i ferie | zaburzenie dni roboczych | biblioteka `holidays` per kraj + ferie z konfiguracji + detekcja dni anomalnych |
| Utrata danych wejściowych (retencja w easy-GTFS-RT) | brak odtwarzalności | kopia L0 (1,2 MB/dzień/miasto) w release'ach nowego repo, sumy SHA-256 |
| Pojedynczy punkt awarii: telefon nagrywający | luki w dniach | monitorowanie brakującego release'u, plan zastępczy |

## 3. Ryzyka prawne i wizerunkowe

- **Licencje danych.** Release'y zawierają dane przewoźników; README easy-GTFS-RT ostrzega, że warunki są różne (od CC po własne regulaminy) i mogą przechodzić na pochodne. Audyt w M0 (`docs/licenses.md`) przed publikacją czegokolwiek z nazwą operatora.
- **Ranking operatorów.** Zmierzone wyniki mogą być niekorzystne dla konkretnego przewoźnika. Prawo do odpowiedzi i zasada poprawek tylko przy błędach faktycznych (`docs/05` §5).
- **Znak i nazwa.** Nie używaj nazwy ani grafiki "Traffic Index" ani stylu marki producenta danych o ruchu drogowym.
- **Relacja z pracodawcą.** Autor pracuje w firmie z branży map i danych o ruchu. Przed publikacją: sprawdź politykę działalności pobocznej i własności intelektualnej, uzgodnij na piśmie, jeśli to potrzebne; nie używaj danych, narzędzi ani materiałów pracodawcy; wyraźnie oddziel projekt od pracodawcy w treści strony.
- **Wyniki niekorzystne bez kontekstu.** Nie publikuj rankingów bez `n`, przedziałów i ograniczeń.
- **Treść wygenerowana przez AI.** Jeśli fragmenty raportów powstają z pomocą AI, oznacz to (wzór: tag "eksperymentalne" na stronie `mapy-analizy`).

## 4. Ryzyka techniczne

- PMTiles na GitHub Pages (zgłoszenie #584): test i plan B.
- Limity Pages: 1 GB, 100 GB/mies. (miękki), 10 minut na deployment; skok ruchu po publikacji w mediach może przebić transfer, lustro na Cloudflare gotowe.
- Kod GPL w `easy-OTP`: nie importować; czytać dane.
- MapLibre (WebGL) wymaga fallbacku dla słabych urządzeń: widok tabelaryczny.
- Podkład mapy: nie hotlinkuj kafli `tile.openstreetmap.org`; własny podkład PMTiles (`06` §1).

## 5. Czego nie zweryfikowano

- Nie zbudowano potoku ani strony; paczka to specyfikacja, kod referencyjny i wartości wzorcowe.
- Dla 14 z 15 miast tylko jeden dzień (24.09); stabilność rang w czasie zbadana tylko dla Łodzi (`09`).
- Filtr obszaru w próbie to przybliżenie promieniem, nie poligon; wyniki końcowe będą się różnić.
- Nie sprawdzono `matched.csv` ani surowych pozycji (nie są publikowane).
- Progi bramki jakości to propozycja do kalibracji w M3.
- Nie potwierdzono, że w Polsce nie istnieje podobny ranking zmierzonych prędkości; sformułowanie "pierwszy" wymaga weryfikacji.
- Licencje danych operatorów oraz fontów i ikon (Hanken Grotesk, Archivo Narrow: OFL; Material Symbols: Apache 2.0) do potwierdzenia w M0.
- **Wymiary W11 (regularność) i W12 (oferta) nie były liczone na prawdziwych danych**; W10 (punktualność) tylko na jednym dniu bez filtra obszaru. Definicje to propozycja do walidacji w M2 (`03` §4).
- Rozbieżność designu z modelem jakości (D13) nie jest jeszcze naniesiona w `design/`.
