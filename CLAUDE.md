# CLAUDE.md: Transit Index (`transit-index`)

Indeks **jakości funkcjonowania** transportu publicznego: rankingi kilkunastu miast europejskich w pięciu wymiarach (prędkość, obciążenie szczytu, punktualność, regularność, oferta rozkładowa), liczone ze zrekonstruowanych danych GTFS-RT (`easy-GTFS-RT`), mapy odcinków, strony miast i edycja roczna. Poboczny projekt GISBoost, **poza doktoratem** autora (Michał Kaczorowski). Statyczny serwis na GitHub Pages.

**Prędkość jest jednym z wymiarów, nie celem projektu.** Nie nazywaj projektu ani rankingu "indeksem prędkości" i nie wprowadzaj wskaźnika złożonego w v1 (D11). Model: `docs/03` §1.

## Hierarchia źródeł prawdy

1. **`design/`** (import z Claude Design): zbudowany i **nadrzędny** w sprawach wyglądu, tokenów, komponentów, tonu i treści interfejsu. Przy konflikcie z `docs/` zmienia się dokument, nie design. Nie edytuj `design/` ręcznie; zmiany wracają przez Claude Design i ponowny import.
2. `docs/03` (metryki, bramka) i `docs/04` (model danych), z `config/*.yaml` jako jedynym miejscem na liczby.
3. Reszta `docs/`. Znane rozbieżności docs ↔ design i ich rozstrzygnięcia: `docs/06` §9.

Jeśli czegoś nie wiesz albo dokumenty się wykluczają, **zapytaj autora** zamiast zgadywać. Otwarte decyzje: `docs/08` (D-lista).

## Zanim cokolwiek zrobisz

1. Przeczytaj `docs/07-milestones.md` i wykonaj **tylko bieżący kamień milowy** (stan: M0 wykonany, `docs/progress.md`; następny M1). Nie wybiegaj naprzód.
2. Czytaj dokumenty, na które wskazuje prompt kamienia.
3. Na końcu każdego kamienia uruchom subagenta `milestone-reviewer` i zapisz krótki wpis w `docs/progress.md`.

## Zasady twarde

**Dane i metody**
- **Filtr jakości:** tylko `seg_status == "ok"`. Etykiety odrzuceń w tidy nie są zastosowane; bez filtra postój na pętli wygląda jak korek 1,5 km/h.
- **Filtr obszaru (W0):** tylko odcinki z obu przystankami w poligonie miasta (`config/areas/`); bez niego prędkości są zawyżone o kilka km/h.
- **Statyka:** tryb i geometria ze statyki **tego samego dnia**; statyki deduplikuj po SHA-256.
- **Wymiary jakości:** W1/W3 (prędkość, kara szczytu), W10 (punktualność), W11 (regularność), W12 (oferta). Każdy ma własny ranking, `n` i status; nie sumuj ich w jedną liczbę. W10–W12 są propozycjami do walidacji w M2, nie faktami.
- **Statystyka:** mediany i percentyle są normą. Jedyne agregaty zbiorcze: `ΣL/ΣT` (prędkość) i EWT (regularność), z testem czułości (`docs/03` §9).
- **Testy wzorcowe:** wyniki zgadzają się z `reference/golden_values.json` (Łódź 2026-09-24: ok = 168 507 wierszy, `ΣL/ΣT` = 17,58 km/h; 9 dni: 17,59). W1–W12 to metryki, M0–M7 kamienie milowe, D1–D14 decyzje.
- **Brak magicznych liczb.** Progi, pasma, klasy prędkości (5 klas, `[15, 20, 25, 30]`) i bramka żyją w `config/*.yaml`; kod je czyta.
- **Każda liczba ma `n` i status jakości** (`ok`/`thin`/`none` dla odcinków, `ranked`/`limited`/`excluded` dla miast).
- **Wersje metody:** wyniki z różnych `method_version` nie są porównywalne. **Nie przypinamy `easy-OTP`** (ADR-0004): dla każdego dnia zapisuj czas budowy tidy i commit `easy-OTP` z tej chwili (epoki: `config/tidy_epochs.yaml`), w manifeście `easy_otp_commits`; dane serwujemy as is.
- **Brak zmyślonych danych.** Przykłady zawsze z `placeholder: true` i oznaczone na stronie ("dane zastępcze"). Liczby w `design/ui_kits/landing/copy.js` są placeholderami; nie publikuj ich jako wyników.

**Design**
- `site/` importuje z `design/` (tokeny, komponenty), nie trzyma kopii i nie projektuje wyglądu od nowa. Kontrakt: `docs/06` §2.
- Kolory danych tylko z tokenów `--speed-1..5`, `--speed-nodata` (tylko wymiar Prędkość); paleta `--line-*` to dekoracja i nigdy nie koduje danych. Brak literalnych kolorów w kodzie.
- Ton tekstów z `design/readme.md` (CONTENT FUNDAMENTALS): bez superlatyw, uczciwie o ograniczeniach, każda liczba z flagą jakości. `prefers-reduced-motion` obowiązkowe.

**Licencje i publikacja**
- `easy-OTP` (`tools/family_a_reconstruction`, `tools/transit_charts`) jest GPL-3.0-or-later: **nie importuj jego kodu**, czytaj tylko dane (`*_tidy_*.csv.gz`, statyczny GTFS). Porównania z jego wykresami: osobny proces, tylko do weryfikacji. Decyzje w `docs/adr/`.
- **Wyniki na CC BY 4.0** (D7, ADR-0003). Projekt jest niekomercyjny: bez reklam i płatnych funkcji. Każde źródło z poprawną atrybucją per miasto (`docs/licenses.md`); OSM (ODbL) przy Warszawie, Sofii i Lizbonie; pliki z kształtami OSM mają własny zapis licencji (`docs/licenses.md` §4).
- **Niczego nie publikuj bez zgody autora.** Ranking operatorów dopiero po przeglądzie operatorów (`docs/05`). Bez nazwy i wyglądu "Traffic Index" (TomTom).
- `docs/08` zawiera uwagi prawne i wizerunkowe: nie commituj go do publicznego repo bez przeglądu.

**Git**
- Nie twórz branchy, nie commituj i nie pushuj, dopóki autor o to nie poprosi. Conventional Commits, po angielsku, jeden temat na commit; nie omijaj hooków.

## Konwencje

- Języki: interfejs po polsku (przełącznik EN), kod i komentarze po angielsku, dokumentacja po polsku.
- Python 3.11+, `pandas`, `pyarrow`, `geopandas`, `shapely`, `pytest`; na tej maszynie wołaj `py`, nie `python`. CLI: `ti` (propozycja, `docs/04` §3).
- Serwis: Astro + MapLibre + PMTiles (`docs/06`); komponenty z `design/` są w React (prototyp), sposób użycia rozstrzyga ADR w M5.
- Testy: `pytest`; każdy kamień dodaje testy. Implementacje metryk zgadzają się z `reference/metrics_reference.py`. Kontrakty danych: `schemas/`, generowane pliki walidowane w testach.
- Nie zakładaj, że kod działa, bo się buduje: przy zmianach liczących metryki podaj, co autor ma zweryfikować ręcznie.

## Gdzie co jest

Skrót `docs/03` oznacza plik `docs/03-*.md` (analogicznie `docs/01` … `docs/09`).

| co | gdzie |
|---|---|
| design, tokeny, komponenty, ton | `design/` (start: `design/readme.md`, `design/SKILL.md`) |
| research, źródła, decyzje | `docs/01-research-summary.md` |
| dane wejściowe, kolumny tidy, wady feedów | `docs/02-data-inventory.md` |
| model jakości, metryki W0–W12, pasma, bramka | `docs/03-metrics-spec.md`, `reference/metrics_reference.py` |
| model danych, potok, geometria | `docs/04-segments-and-data-model.md` |
| edycja roczna | `docs/05-annual-edition.md` |
| serwis, kontrakt z designem, rozbieżności | `docs/06-site-spec.md` |
| plan pracy (M0–M7, prompty) | `docs/07-milestones.md` |
| ryzyka i decyzje D1–D14 | `docs/08-risks-and-open-questions.md` |
| weryfikacja na prawdziwych danych | `docs/09-validation-on-real-data.md`, `reference/golden_values.json` |
| skrót całości | `docs/ALL-IN-ONE.md` |
| kontrakty JSON i przykłady | `schemas/`, `examples/` |

## Źródła danych wejściowych i ograniczenia środowiska

- **Linki do statyk operatorów: `easy-GTFS-RT/config/cities.json`** (`static_gtfs_url`); adresy GTFS-RT są na telefonie nagrywającym (`cities/<miasto>.env`), część w `easy-OTP/docs/handoffs/eu_vehicle_positions_feeds.md`.
- Release'y `GISBoost/easy-GTFS-RT`: tag `<miasto>-realized-<data>-phone`, załączniki `<miasto>_tidy_<data>.csv.gz` (od 2026-08-03) i `<miasto>_static_gtfs_<data>.zip`. Opis metody: `HOW-IT-WORKS.pl.md` w easy-GTFS-RT; kod rekonstrukcji: `GISBoost/easy-OTP`.
- Surowe pozycje: dzienne kasowane po zbudowaniu, ale archiwizowane co miesiąc (release `raw-snapshots-<RRRR-MM>` w `easy-GTFS-RT`, przegląd w `gtfs-dashboard`); diagnostyka jakości rekonstrukcji: `docs/02` §8a.
- API GitHub może być zablokowane; działają bezpośrednie adresy release'ów (`reference/fetch_release_assets.py`) i `git ls-remote --tags`. Nie omijaj polityki sieci.
