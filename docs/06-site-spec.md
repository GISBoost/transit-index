# 06 · Serwis: architektura techniczna i kontrakt z Claude Design

**Zakres tego dokumentu:** dane, build, hosting, mapa, wydajność, testy i sposób włączenia designu. **Wygląd, układ stron, animacje i scenografię projektuje Michał w Claude Design**; to nie jest tu specyfikowane. Serwis ma własną tożsamość wizualną, celowo odrębną od GISBoost (GISBoost występuje jako mały podpis autora, `<Logo credit />`).

**Design jest zbudowany i nadrzędny.** Zaimportowany system (Transit Index Design System) leży w `design/` (opis: `design/readme.md`, komponenty i tokeny: `design/components`, `design/tokens`, przykład: `design/ui_kits/landing`). Gdy ten dokument rozjeżdża się z `design/`, zmienia się dokument, nie design. Rozbieżności wykryte przy imporcie są w §9.

## 1. Decyzje techniczne

| obszar | wybór | uzasadnienie |
|---|---|---|
| repo i adres | repo `GISBoost/transit-index`, adres `gisboost.github.io/transit-index/` (nazwa robocza, D4) | ten sam wzorzec co `gtfs-dashboard` i `mapy-analizy` |
| framework | **Astro** (prerender + wyspy JS), TypeScript; alternatywa: Vite + skrypt prerenderu | ranking i strony miast muszą być zrenderowane do HTML (SEO, podglądy w mediach społecznościowych) |
| mapa | **MapLibre GL JS** + PMTiles | tysiące kolorowanych odcinków i sterowanie kamerą (WebGL); Leaflet z `mapy-analizy` tego nie uniesie |
| animacje | biblioteka GSAP + ScrollTrigger (darmowa od kwietnia 2025); CSS `animation-timeline` jako dodatek | implementacja według projektu z Claude Design; Chrome/Edge od 115 i Safari 26 wspierają scroll-driven CSS, Firefox stable nadal za flagą |
| wdrożenie | własny workflow GitHub Actions do Pages | limit 10 buildów/h dotyczy wbudowanego buildu Pages, nie własnego workflow |
| analityka | GoatCounter (jak na stronach GISBoost), bez ciasteczek | |
| języki | PL domyślnie, EN; liczby przez `Intl.NumberFormat` (przecinek dziesiętny w PL) | |
| podkład mapy | **własny podkład PMTiles** (np. wycinek OSM z Protomaps) albo dostawca z darmowym planem; **nie linkuj bezpośrednio kafli `tile.openstreetmap.org` w produkcji** | polityka użycia serwerów OSM (sprawdź aktualne warunki); skok ruchu po publikacji; atrybucja OSM (ODbL) obowiązkowa |

## 2. Kontrakt z eksportem Claude Design

Źródłem prawdy o wyglądzie jest katalog `design/` (import z Claude Design). `site/` **importuje z niego** (alias `@design` albo ścieżka względna) i **nie trzyma kopii**; zmiany wyglądu wracają przez Claude Design i ponowny import. Zasady po stronie kodu, wymuszane testami:

1. **Tokeny jako zmienne CSS** (`--*`, `design/tokens/*.css`, wejście `design/styles.css`) w dwóch motywach: dzienny (papier, domyślny) i nocny `[data-theme="night"]`. `--paper` i `--ink` są rolami, więc komponenty przełączają się same. Kod nie zawiera literalnych kolorów poza tokenami (test: grep po `#[0-9a-f]{3,8}` i `rgb(` w `site/src`).
2. **Skala prędkości na mapie i w wykresach** to tokeny `--speed-1 … --speed-5` (**pięć klas**, od najwolniejszej), plus `--speed-nodata` (brak danych) i szrafowanie dla małej próby (`q = thin`). Klasy odpowiadają `speed_classes_kmh` z `config/metrics.yaml` (4 krawędzie). Test build-time porównuje liczbę tokenów i klas z konfiguracją (jedno źródło prawdy: konfiguracja; design ma tylko kolory). Kolory linii marki (tęczowe wiązki, paleta `--line-*`) są **dekoracją i nie mogą kodować danych**; paski rankingu są w kolorze tuszu, nie tęczowe. Skala prędkości dotyczy tylko wymiaru Prędkość; pozostałe wymiary pokazuje się liczbą i paskiem, nie kolorem `--speed-*`.
3. **Fonty i ikony hostowane u siebie** w produkcji (`woff2`/SVG w repo), bez CDN Google (prywatność odwiedzających z UE). Wybór designu (ostateczny): Hanken Grotesk (400 i 700) i Archivo Narrow, obie OFL; ikony Material Symbols Sharp (licencja Apache 2.0, do sprawdzenia w M0 przy audycie). Prototyp w `design/` ładuje je z CDN i tak zostaje; w produkcji zmienia się tylko źródło plików. Test renderowania polskich znaków: `Zażółć gęślą jaźń, ĄĆĘŁŃÓŚŹŻ`. Cyfry danych tabelaryczne (`font-variant-numeric: tabular-nums`).
4. **Generator wiązek linii** to `TransitGeometry` z `design/components/transit/` (`TransitGeometry.bundle(waypoints, offsets, radius)`); wszystkie motywy linii przechodzą przez niego, żadnych ręcznych polilinii. Jeśli kod serwisu go przenosi lub przepisuje, wymaga testów jednostkowych: stały odstęp równoległych linii przez łuk (łuki koncentryczne), promień 1,6 × szerokość wiązki, kąty tylko 0/45/90°. Ścieżki statyczne generuj w buildzie do SVG; animowane wiązki "podróży" landingu (`design/ui_kits/landing/journey.js`) liczą się w przeglądarce z pozycji stacji w DOM.
5. **Dostępność przenosi się z designu do kodu:** kontrast tekstu ≥ 4,5:1 i klas prędkości ≥ 3:1 względem `--map-base` w obu motywach (karty kolorów w `design/guidelines/` sprawdzają to na żywo), fokus (niebieska ramka 2 px), cele dotykowe ≥ 44 px, `prefers-reduced-motion` (strona statyczna i w pełni narysowana, bez przejmowania scrolla), animowane są tylko `transform`, `opacity` i `stroke-dashoffset`, widok tabelaryczny mapy. Testy: axe w CI + ręczna lista kontrolna.
6. Zmiany w projekcie graficznym nie zmieniają kontraktów danych (`schemas/`). Jeśli design wymaga nowego pola, najpierw zmiana schematu i `docs/04`.
7. **Treść:** ton i reguły liczb z `design/readme.md` (CONTENT FUNDAMENTALS) obowiązują w tekstach serwisu: bez superlatyw, przecinek dziesiętny w PL, minus `−`, przedziały z półpauzą, **każda liczba z flagą jakości** (mała próba, luki w danych), baza każdego porównania podana wprost.
8. **Komponenty:** `design/components/*.jsx` to React w przeglądarce (prototyp); cel produkcyjny to Astro. Sposób użycia (wyspy React w Astro albo port do `.astro`) rozstrzyga ADR w M5. Przenosimy wygląd, nie przepisujemy go.

## 3. Trasy i dane

| adres | dane (pliki z `public/data/<edycja>/`) | uwagi techniczne |
|---|---|---|
| `/` | `ranking.json` | prerender tabeli do HTML; przełączniki **wymiaru**, trybu i pasma działają na JSON w przeglądarce (komponent `Tabs` z designu) |
| `/miasto/<id>/` | `<id>/summary.json`, `hourly.json`, `lines.csv`, `tiles/<id>.pmtiles` | prerender KPI i tabel; mapa i wykres godzinowy ładowane leniwie |
| `/mapa/?miasto=<id>&pasmo=&h=&p=` | kafle PMTiles + `summary.json` | stan w URL-u; `?embed=1` dla osadzania |
| `/dane/` | `manifest.json` + linki do plików w release'ach | pełne pliki poza Pages (limit 1 GB): ranking (CSV), odcinki (**GeoPackage**, `.geojson.gz`), profile godzinowe (CSV): lista pobierań z footera designu |
| `/metodyka/`, `/jakosc/` | `docs`-owe treści + `quality.json` | treści z tych samych źródeł co `docs/03` (jedna definicja) |
| `/edycje/` | `editions.json` (lista manifestów) | edycje niezmienne (`docs/05`) |

## 4. Mapa: warstwa techniczna

- Źródło: PMTiles z właściwościami zgodnymi z `schemas/segment_feature.schema.json` (`v_all, v_am, v_mid, v_pm, v_eve, q_*, pen_pm, v_sched, length_m, n_all, n_days, geometry_quality`). Wybór pasma przełącza wyrażenie stylu na inne pole (`["get","v_pm"]`), bez przeładowania kafli.
- Kolor: wyrażenie `step` po `speed_classes_kmh` → `--speed-N`. `q_* = thin` szrafowane (wzór), `none` osobny szary; wartość `null` nie koduje się kolorem prędkości.
- Dwa kierunki jako osobne cechy, rysowane z `line-offset`.
- Protokół `pmtiles://`; **test zakresów bajtów w Chrome, Firefox i Safari w M4** (zgłoszenie #584 w protomaps/PMTiles opisuje sporadyczne błędy dla plików z GitHub Pages; stan aktualny nie sprawdzony). Plan B: lustro na Cloudflare Pages/R2 (jak dla izochron) albo kafle jako pliki `z/x/y`.
- Widok tabelaryczny: te same dane w `<table>`; źródło: `segments.geojson.gz` lub `lines.csv`.
- Wydajność: wstępny cel ≤ 100 kB JS (gzip) na stronie rankingu bez mapy (założenie, nie pomiar; do zmierzenia w M5, `docs/prompts/2026-09-30-m5-agent.md`); MapLibre ładowany po interakcji lub po pierwszym renderze; `min/maxzoom` warstwy dobrane do kafli (`docs/04` §4).

## 5. Build i CI

Workflow `deploy.yml` (własny, nie wbudowany build Pages):

1. Checkout; instalacja zależności (`npm ci`, `pip install -r requirements.txt`).
2. **Pobranie zamrożonej edycji** (`manifest.json` + pliki) z release'ów repo; weryfikacja sum kontrolnych względem manifestu.
3. **Walidacja schematów** (`reference/validate_examples.py` rozszerzone o pliki edycji) i test zgodności klas prędkości z tokenami.
4. `astro build` (prerender).
5. Testy: Playwright (trasy, przełączniki, stan URL), axe (dostępność), Lighthouse CI z budżetami; sprawdzenie rozmiaru artefaktu (**awaria buildu > 700 MB**, limit Pages 1 GB).
6. Deploy Pages; harmonogram nie jest potrzebny (edycje są niezmienne).

Dane edycji są liczone poza buildem strony (`docs/04`); build tylko je konsumuje.

## 6. SEO i udostępnianie

- Prerender rankingu i stron miast do HTML, sitemap, adresy kanoniczne, `hreflang` PL/EN.
- Obrazy Open Graph per miasto generowane w buildzie skryptem Pythona z `summary.json` i tokenów eksportowanych z designu do JSON (kolory, font), z liczbą i statusem jakości.
- Opisy meta pisane rzeczowo; bez superlatyw w tytułach.

## 7. Limity hostingu

GitHub Pages: witryna ≤ 1 GB, miękki limit 100 GB transferu miesięcznie, deployment ≤ 10 minut, zakaz hostowania sklepu, transakcji i SaaS. Skok ruchu po publikacji w mediach może przebić transfer; lustro na Cloudflare gotowe. Stare edycje i pełne dane trzymaj w release'ach.

## 8. Budżety i kryteria akceptacji technicznej

- Strona rankingu bez mapy ≤ 100 kB JS (gzip) jako wstępny cel (M5 mierzy i proponuje ostateczny limit; komponenty zostają w React, wyspy); LCP ≤ 2,5 s na profilu 4G; CLS ≈ 0.
- Zero literalnych kolorów poza tokenami; klasy prędkości zgodne z konfiguracją; polskie znaki renderują się w każdym foncie stosu.
- Wszystkie liczby na stronie pochodzą z plików danych; przykłady z `examples/` nigdy nie trafiają do buildu produkcyjnego (test: `placeholder: true` w danych blokuje deploy).
- Widok tabelaryczny mapy i nawigacja klawiaturą; brak zależności od animacji do odczytania treści.
- Telefon: brak przewijania poziomego, mapa widoczna, cele dotykowe ≥ 44 px, testy Playwright w emulacji 360x740 i 390x844 (regresja M4: mapa o wysokości 0 px na telefonie).

## 9. Rozbieżności docs ↔ design wykryte przy imporcie

Reguła: `design/` wygrywa. Tabela mówi, co zmieniono w dokumentach i co zostaje do zrobienia przy podpinaniu prawdziwych danych (po stronie designu, poza tą paczką).

| temat | było w docs | jest w designie | rozstrzygnięcie |
|---|---|---|---|
| klasy prędkości | `--speed-0…5`, 6 klas, 5 krawędzi | `--speed-1…5` + `--speed-nodata`, 5 klas | **docs dostosowane** (`03` §5, `metrics_reference.py`): 4 krawędzie `[15, 20, 25, 30]` |
| fonty | TeX Gyre Heros albo alternatywa OFL | Hanken Grotesk + Archivo Narrow (OFL), ostateczne | **docs dostosowane**; hosting u siebie w produkcji zostaje |
| motywy | "jasny i ciemny" | dzienny i `[data-theme="night"]` ("wydanie nocne") | **docs dostosowane** |
| lokalizacja designu | `site/src/design/` (kopia) | `design/` w korzeniu repo | **docs dostosowane**: `site/` importuje z `design/` |
| zakres treści | prędkość | prędkość i jakość ("how well public transport actually works") | **docs dostosowane**: model pięciu wymiarów (`03` §1) |
| sekcja "Liczba" landingu | kara szczytu W3 | "−22% wolniej niż 10% najszybszych przejazdów" (dane zastępcze) | **do zmiany w designie** przy prawdziwych danych; docs zostają przy W3 (`03` §3) |
| hero, nagłówek rankingu, sekcja "Uczciwie" | nie dotyczy | teksty mówią tylko o prędkości ("Miasta według zmierzonej prędkości", "Rozkład nie jest wzorcem") | **do zmiany w designie**: przełącznik wymiarów w rankingu, copy dopasowane do modelu jakości |
| sposób pokazania wymiarów | nie określono | ranking = paski w kolorze tuszu; kolor `--speed-*` tylko dla prędkości | docs zgodne z designem (§2 pkt 2) |
| pobieranie | CSV, GeoJSON, PMTiles | ranking CSV, odcinki GeoPackage, profile godzinowe CSV | **docs dostosowane**: dodać GeoPackage do eksportu (M3/M4) |
| komponenty | HTML/CSS/SVG | React w przeglądarce (prototyp), cel Astro | ADR w M5 (§2 pkt 8) |
