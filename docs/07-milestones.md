# 07 · Kamienie milowe i prompty dla Claude Code

Pracuj **po jednym kamieniu milowym na sesję**. Każdy kończy się przeglądem przez subagenta `milestone-reviewer` (`.claude/agents/milestone-reviewer.md`) i krótkim wpisem w `docs/progress.md`. Nie przechodź dalej, dopóki przegląd nie da PASS. Prompty poniżej są gotowe do wklejenia.

**Co już zrobiono przed M0** (`docs/09`): dostęp do release'ów bez API, schemat tidy, semantyka odcinków, klucz odcinka, geometria, klasy prędkości, kara szczytu, wpływ obszaru miasta, wartości wzorcowe. Kamienie nie powtarzają tego od zera: **rozszerzają to na pełne okno i wszystkie miasta kandydujące** i zamieniają skrypty z `reference/` w produkcyjny kod.

Wygląd i układ stron: Claude Design, zaimportowany do `design/` (nadrzędny, poza zakresem kamieni). Kontrakt techniczny: `docs/06` §2, rozbieżności docs ↔ design: `docs/06` §9.

**Model jakości** (`docs/03` §1): pięć wymiarów (prędkość W1, obciążenie szczytu W3, punktualność W10, regularność W11, oferta W12), bez wskaźnika złożonego. Każdy kamień, który liczy lub pokazuje metryki, dotyczy wszystkich wymiarów, nie tylko prędkości.

---

## M0 · Repo, dane na pełnym oknie, decyzje (1–2 dni)

**Cel:** potwierdzić na wszystkich miastach kandydujących i całym oknie to, co `docs/09` sprawdziło na próbce, oraz rozstrzygnąć decyzje blokujące.
**Wyjście:**
- szkielet repo: `pyproject.toml`, `config/metrics.yaml` (z `docs/03` §6), `config/cities.yaml`, `config/city_defects.yaml` (z `docs/02` §5), `.gitignore`, `pytest` uruchamialny,
- test regresyjny: `reference/probe_release_data.py` na Łodzi 2026-09-24 odtwarza `reference/golden_values.json` (tolerancja z opisu pliku),
- `docs/data-inventory.generated.md`: dla każdego miasta kandydującego i dnia okna: czy jest tidy i statyka, rozmiar, schemat 34 kolumn, `crossing_rate`, udział `ok`; luki dzienne,
- `docs/licenses.md`: audyt warunków użycia źródeł z `cities.json`,
- **wielokąty miast** (`config/areas/<miasto>.geojson`) dla miast kandydujących i decyzja o źródle (`docs/08`, D12),
- `config/calendars/<miasto>.yaml` (święta biblioteką `holidays`),
- `docs/decisions-needed.md`.
**Kryteria akceptacji:** test regresyjny przechodzi; lista miast kwalifikujących się do pilotażu z liczbą ważnych dni; ustalone, z jakiego commitu `easy-OTP` powstaje tidy i jak to oznaczać (bez pinu, ADR-0004); źródło wielokątów i licencja opisane. Żadnego kodu metryk poza istniejącym w `reference/`.

```text
Jesteś agentem M0 projektu transit-index. Przeczytaj CLAUDE.md, docs/02, docs/03 i docs/09 oraz uruchom reference/metrics_reference.py i reference/validate_examples.py. Wykonaj tylko M0 z docs/07-milestones.md. Użyj reference/fetch_release_assets.py i reference/probe_release_data.py na miastach kandydujących dla okna od 2026-09-01 (lista tagów: git ls-remote --tags https://github.com/GISBoost/easy-GTFS-RT.git). Zapisz docs/data-inventory.generated.md, docs/licenses.md, config/, kalendarze i wielokąty miast. Ustal, jaki ref easy-OTP jest używany w workflow easy-GTFS-RT. Nie pisz kodu produkcyjnego metryk. Pytania do Michała zapisz w docs/decisions-needed.md. Na koniec uruchom milestone-reviewer.
```

---

## M1 · Ingest i tabela obserwacji L0

**Cel:** powtarzalnie przekształcić tidy + statykę w wąską tabelę obserwacji.
**Wejście:** `docs/04` §2–§3, `reference/fetch_release_assets.py`, `reference/probe_release_data.py`.
**Wyjście:** `ti ingest`, `ti obs`; L0 w Parquet; **deduplikacja statyk po SHA-256**; walidator schematu tidy (34 kolumny); kopia L0 jako załączniki release'ów; raport odrzuceń per miasto-dzień.
**Kryteria akceptacji:**
- filtr `seg_status == "ok"` i tryb ze statyki **tego samego dnia** (`mode_from_route_type`),
- `sched_pass_time_s` z `sched_arr` (nie z `sched_seg_time_s`),
- filtr obszaru (wielokąt) stosowany na poziomie odcinka; zapisany `share_of_obs_in_area`,
- **test wzorcowy:** dla Łodzi 2026-09-24 liczba obserwacji `ok` = 168 507 i `ΣL/ΣT` (bus+tram) = 17,58 km/h (`golden_values.json`); 9 dni: 17,59,
- idempotencja (skróty zawartości), brak zmian przy ponownym przebiegu; 404 traktowane jako luka dnia, nie błąd.

```text
Jesteś agentem M1. Przeczytaj CLAUDE.md, docs/02, docs/04 (sekcje 2-3), docs/09 i wyniki M0. Zaimplementuj ti ingest i ti obs na podstawie reference/fetch_release_assets.py i reference/probe_release_data.py, dodając deduplikację statyk po SHA-256, filtr obszaru i zapis L0 w Parquet. Nie importuj kodu z easy-OTP (GPL): czytaj wyłącznie pliki danych. Napisz test wzorcowy na golden_values.json. Na koniec uruchom milestone-reviewer.
```

---

## M2 · Segmenty i metryki (rdzeń)

**Cel:** L1 i L2: odcinki fizyczne, metryki W1–W9 i wymiary jakości W10–W12, kara szczytu, klasy prędkości, test czułości.
**Wejście:** `docs/03`, `reference/metrics_reference.py`, wyniki M1.
**Wyjście:** `ti aggregate`, `ti metrics`; `segment_stats.parquet`; **testy P0 i P1 z `docs/10-input-methodology-and-test-plan.md`** (T1-T20, T25; reguły decyzyjne są tam zapisane z góry; T7, T10 i T12 powtarzane przy >= 40 dniach ważnych); implementacja zgodna z referencyjną; **raport czułości** (`docs/sensitivity-report.md`, tabela z `docs/03` §9 na wszystkich miastach i wielu dniach, w tym korelacja rang dla tramwajów); **definicje ostateczne W10, W11 i W12** (progi, agregacja, źródło rozkładu dla W12; ADR) i ich testy czułości oraz korelacje rang między wymiarami; **potwierdzenie lub korekta klas** `[15, 20, 25, 30]` (pięć klas) po filtrze obszaru; ADR wyboru metryki wymiaru Prędkość; kara szczytu na poziomie odcinka (`pen_pm`).
**Kryteria akceptacji:** implementacja produkcyjna zgadza się z `metrics_reference.py` na danych testowych i z `golden_values.json` na rzeczywistych; krzyżowa kontrola z wykresem D14 dla jednej linii (jako osobny proces, bez importu GPL); klasy zamrożone w konfiguracji; W6 liczone z `sched_pass_time_s`.

```text
Jesteś agentem M2. Przeczytaj CLAUDE.md, docs/03, docs/04, docs/09 i reference/metrics_reference.py. Zaimplementuj metryki W1-W9 (w tym karę szczytu W3 i filtr obszaru), odcinki fizyczne i pasma według specyfikacji, bez magicznych liczb w kodzie (wszystko z config/metrics.yaml). Wygeneruj raport czułości z docs/03 sekcja 9 na wszystkich miastach kandydujących i wielu dniach, potwierdź lub skoryguj klasy prędkości i zapisz ADR z uzasadnieniem metryki nagłówkowej. Zweryfikuj wynik z golden_values.json. Na koniec uruchom milestone-reviewer.
```

---

## M3 · Bramka jakości, ranking, manifest

**Cel:** kwalifikacja dni i miast, ranking z niepewnością, manifest edycji.
**Wejście:** `docs/03` §6–§7, `docs/05`, `schemas/`.
**Wyjście:** `ti gate`; detekcja dni anomalnych; `ranking.json`, `summary.json`, `hourly.json`, `lines.csv`, `quality.json`, `manifest.json` (z `license` i `attributions` per miasto) walidowane względem `schemas/`; bootstrap po dniach; oznaczanie miast nierozróżnialnych; rankingi per wymiar (W1, W3, W10, W11, W12) ze statusem wymiaru.
**Kryteria akceptacji:** wszystkie pliki przechodzą walidację schematów; miasta z rejestru wad mają wykluczenie z powodem; brak release'u w dniu liczony jako dzień nieważny; skrót wejść w manifeście odtwarza się; pliki z `placeholder: true` nie przechodzą do edycji.

```text
Jesteś agentem M3. Przeczytaj CLAUDE.md, docs/03 (sekcje 6-7), docs/05 i schemas/. Zaimplementuj ti gate i generację ranking.json, summary.json, hourly.json, lines.csv, quality.json i manifest.json dla okna 2026-09-01..2026-12-18 (lub dostępnego fragmentu). Waliduj pliki względem schemas/. Dodaj bootstrap po dniach i oznaczanie miast nierozróżnialnych. Progi tylko z config. Na koniec uruchom milestone-reviewer.
```

---

## M4 · Geometria i kafle

**Cel:** warstwa mapy: odcinki z geometrią, kafle PMTiles i podkład.
**Wejście:** `docs/04` §4, `docs/06` §4, `schemas/segment_feature.schema.json`.
**Wyjście:** `ti tiles`; geometria z polilinii cięta po `shape_dist_m` (skumulowana odległość haversine, `docs/09` F8); `segments.pmtiles` i `segments.geojson.gz` dla miast pilotażu; własny podkład PMTiles; strona testowa MapLibre wdrożona na Pages; **wynik testu zakresów bajtów** w Chrome, Firefox i Safari (jeśli dostępny); ADR z hostingiem i planem B.
**Kryteria akceptacji:** żaden odcinek ≥ 200 m nie znika przy z14+; właściwości zgodne ze schematem; `geometry_quality` ustawione; łączny rozmiar w budżecie (`docs/06` §5).

```text
Jesteś agentem M4. Przeczytaj CLAUDE.md, docs/04 (sekcja 4), docs/06 (sekcje 1 i 4), docs/09 i schemas/segment_feature.schema.json. Zbuduj geometrię odcinków ze statycznego GTFS (bez importu kodu GPL), wygeneruj PMTiles i GeoJSON, przygotuj własny podkład PMTiles, wdróż stronę testową MapLibre na GitHub Pages i sprawdź ładowanie zakresów bajtów w co najmniej dwóch przeglądarkach (zgłoszenie #584 w protomaps/PMTiles opisuje ryzyko). Zapisz ADR z decyzją hostingu kafli. Na koniec uruchom milestone-reviewer.
```

---

## M5 · Serwis: szkielet, dane i integracja z Claude Design

**Cel:** działająca strona ze wszystkimi trasami i danymi z M3/M4, z eksportem z Claude Design.
**Wejście:** `docs/06`, zaimportowany design w `design/` (bez kopiowania do `site/`).
**Wyjście:** Astro, trasy z `docs/06` §3, prerender, mapa z filtrami i widokiem tabelarycznym, przełącznik PL/EN, workflow Actions do Pages, testy kontraktu z designem (`docs/06` §2).
**Kryteria akceptacji:** build w Actions bez ręcznych kroków; klasy prędkości w tokenach zgodne z `config/metrics.yaml`; brak literalnych kolorów poza tokenami; przykłady z `placeholder: true` blokują deploy; polskie znaki poprawne w każdym foncie stosu.

```text
Jesteś agentem M5. Przeczytaj CLAUDE.md i docs/06. Wykorzystaj design z katalogu design/ (tokeny, komponenty, ui_kits/landing; nie kopiuj go, nie zmieniaj wyglądu; jeśli czegoś brakuje, zatrzymaj się i zgłoś to Michałowi zamiast wymyślać wygląd). Ranking ma przełącznik wymiarów (prędkość, obciążenie szczytu, punktualność, regularność, oferta). Zbuduj serwis Astro z trasami z docs/06 sekcja 3, prerenderem, mapą MapLibre i widokiem tabelarycznym. Dane z public/data/<edycja>/. Dodaj testy kontraktu z designem z docs/06 sekcja 2 i workflow Actions do Pages. Na koniec uruchom milestone-reviewer.
```

---

## M6 · Wydajność, dostępność, i18n, obrazy OG

**Cel:** twarde budżety i jakość.
**Wyjście:** audyt Lighthouse i axe z raportem; tłumaczenie EN; generacja obrazów OG per miasto; wdrożenie animacji z projektu Claude Design zgodnie z zasadami technicznymi (`transform`, `opacity`, `prefers-reduced-motion`, bez przejmowania scrolla).
**Kryteria akceptacji:** budżety z `docs/06` §8; strona w pełni użyteczna bez animacji; nawigacja klawiaturą po mapie; kontrast w obu motywach.

```text
Jesteś agentem M6. Przeczytaj CLAUDE.md i docs/06 (sekcje 2, 6 i 8). Zaimplementuj tłumaczenie EN, obrazy OG per miasto generowane w buildzie, animacje z projektu Claude Design (tylko transform i opacity, pełny fallback dla prefers-reduced-motion) oraz audyt dostępności i wydajności z raportem w docs/. Na koniec uruchom milestone-reviewer.
```

---

## M7 · Edycja pilotażowa i przygotowanie publikacji

**Cel:** pełny przebieg `2026-pilot` i lista kontrolna z `docs/05` §8.
**Wyjście:** edycja w statusie `operator_review`; pakiet dla operatorów; strona metodyki z testem czułości; Zenodo; raport ryzyk.
**Kryteria akceptacji:** wszystkie punkty listy kontrolnej z `docs/05` §8 spełnione albo jawnie odroczone przez Michała.

```text
Jesteś agentem M7. Przeczytaj CLAUDE.md, docs/05 i docs/08. Uruchom pełny przebieg edycji 2026-pilot, przygotuj pakiet dla operatorów (wyniki ich miasta, metodyka, ograniczenia), stronę metodyki z testem czułości i listę kontrolną z docs/05 sekcja 8, oznaczając punkty niespełnione. Nie publikuj niczego bez zgody Michała. Na koniec uruchom milestone-reviewer.
```
