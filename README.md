# Indeks prędkości transportu publicznego (nazwa robocza)

Poboczny projekt GISBoost. Statyczny serwis (GitHub Pages): ranking polskich miast według prędkości transportu publicznego
odtworzonej z danych GTFS-RT taboru oraz mapa odcinków między przystankami, kolorowanych według prędkości. Po polsku,
z przełącznikiem EN, w jasnym i ciemnym motywie.

**Wszystkie dane w repozytorium są zastępcze** („dane zastępcze”): mają prawdziwą strukturę, ale wartości są wymyślone.
Progi próby (`XX`), progi klas prędkości i treść metodyki są do ustalenia (sekcja „Sprawy otwarte”).

## Uruchomienie

Wymagane: Node ≥ 20.19 i npm. Python (`py` na Windowsie, `python3` gdzie indziej) tylko do generatorów.

```bash
npm install
npm run dev
```

Serwer deweloperski: <http://localhost:5173/>. Strony są renderowane przy każdym żądaniu, więc zmiany w szablonach
(`src/pages`, `src/components`) widać po odświeżeniu.

| Polecenie | Co robi |
|---|---|
| `npm run build` | sprawdza typy i buduje `dist/` (wszystkie strony PL + EN jako statyczny HTML) |
| `npm run preview` | serwuje `dist/` pod docelową ścieżką bazową (`/transit-index/`, zmienna `BASE`) |
| `npm run check` | skrypt kontrolny (kolory, kontrast, ruch, i18n, linki), po `npm run build` sprawdza też linki w `dist/` |
| `npm run verify` | `build` + `check` |
| `npm run tokens` | generuje `design/tokens.css` z `design/tokens.json` |
| `npm run data` | generuje dane zastępcze do `public/data/` |

## Jak to jest zrobione

- **Vite (MPA) + czysty TypeScript.** Bez frameworka UI. W przeglądarce działają tylko **MapLibre GL JS** i **GSAP**
  (ScrollTrigger tylko jako zapas dla przelotu kamery); Vite jest narzędziem budowania, nie zależnością runtime.
- **Prerender.** Wtyczka w `vite.config.ts` renderuje każdą stronę (`/`, `/miasto/<slug>/`, `/mapa/`, `/dane/`, `/metodyka/`,
  `/jakosc-danych/`, `/archiwum/`, `404.html`, każda też pod `/en/`) do HTML z szablonów i JSON-ów z `public/data/`.
  Treść jest więc widoczna bez JS, a `src/main.ts` ją tylko ożywia (przełączniki, mapa, ruch).
- **CSS w kolejności:** `gisboost-1.css` (z `https://gisboost.github.io/assets/gisboost-1.css`, w `<head>`, niezmieniony)
  → `design/tokens.css` → `css/bundle.css` (niezmieniona kopia komponentów z `design/`) → `css/site.css` → `css/motion.css`.
- Cała strona jest w `.idx-frame`, układ reaguje na szerokość kontenera (progi 640 i 1024 px).

```
design/            źródło prawdy z systemu projektowego (tokeny, komponenty, wytyczne, ekrany wzorcowe). Nie wdrażane.
css/               bundle.css (kopia), site.css (układ serwisu), motion.css (ruch)
public/data/       dane (zastępcze): manifest, miasta, ranking, odcinki per miasto
src/i18n/          słowniki pl.json / en.json + t(), url()
src/lib/           schema.ts (typy i walidacja danych), data.ts (loader), idx.ts (port IDX), agg.ts, params.ts (stan w URL)
src/components/    małe funkcje generujące markup komponentów z design/components/*/preview.html
src/pages/         szablony stron
src/client/        zachowanie po stronie przeglądarki (ranking, miasto, mapa, scrollytelling, motyw, język)
src/map/           MapLibre: styl z tokenów, warstwa odcinków
src/motion.ts      jedyne miejsce, które uruchamia animacje
tools/             gen_tokens.py, gen_placeholder_data.py, check.mjs
```

`src/lib/idx.ts` to port funkcji `IDX` z `design/components/bundle.js` (ikony, liczby, klasa prędkości, wykres godzinowy)
**bez** `IDX.demo` (sieć pokazowa) i bez `IDX.motion` (zastąpione przez `src/motion.ts`). Dzięki temu ten sam kod
działa przy prerenderze (Node) i w przeglądarce.

## Dane i jak podmienić dane zastępcze na prawdziwe

Interfejs czyta wyłącznie pliki z `public/data/`. Kształt opisuje i sprawdza `src/lib/schema.ts`; **build i serwer
deweloperski przerywają pracę z czytelnym komunikatem, gdy plik nie pasuje**, a przeglądarka pokazuje stan błędu
z „Spróbuj ponownie”. Wartość nieznana to zawsze `null` (UI pokazuje ją jako `XX` albo „za mało danych”, nigdy jako 0).

| Plik | Zawartość |
|---|---|
| `manifest.json` | edycja, godziny szczytu (`peak_hours`), progi próby (`thresholds`, na razie `null`), pliki do pobrania, lista edycji |
| `cities.json` | miasta: `slug`, nazwa (PL/EN), odmiana „w Łodzi”, region, środek mapy, stan jakości (`ranked`/`limited`/`out`), KPI (zmierzone, rozkładowe, n, miejsce), profil godzinowy (`plan` i `meas`, po 24 wartości, `null` = próba za mała), linie |
| `ranking.json` | prędkość miast per rodzaj (`tram`/`bus`) i pora (`day`/`peak`/`off`) |
| `segments/<slug>.geojson` | odcinki między przystankami (`LineString`) z polami `route`, `mode`, `stop_from`, `stop_to`, `plan_kmh`, `kmh_p15`/`kmh_p50`/`kmh_p85` (po 24 wartości, indeks = godzina), `n` |

Kroki:

1. Zastąp pliki w `public/data/` prawdziwymi, zachowując kształt (albo dostosuj `tools/gen_placeholder_data.py`, żeby wypisywał je z Twojego potoku).
2. `npm run dev` i otwórz stronę: błąd schematu wskaże dokładną ścieżkę pola (np. `cities[2].hourly.meas: expected 24 hourly values`).
3. Zmień w `manifest.json` `"placeholder": false`. Znika znacznik „dane zastępcze” z list plików i tabel.
4. Dla tekstów „dane zastępcze” w treści stron (`ph` w słownikach) zdecyduj, co zostaje, dopiero po ustaleniu progów próby w metodyce.

Uwaga: prędkość **pory** (dzień / szczyt / poza szczytem) na mapie to mediana niepustych wartości godzinowych odcinka
(przybliżenie po stronie UI, `src/lib/agg.ts`). Gdy potok policzy agregaty dla pór wprost, warto je podać i zastąpić to przybliżenie.

## Progi

- **Klasy prędkości** (8 / 12 / 16 / 20 / 26 km/h) to wartości startowe w `design/tokens.json` (`idx-speed-t1…t5`).
  Skalibruj je na rozkładzie zmierzonych prędkości po pierwszym przebiegu, potem zamroź w wersji edycji:
  zmień wartości w `tokens.json`, uruchom `npm run tokens` i przebuduj. Legenda, słupki, mapa i wykresy biorą progi z tokenów
  (przy prerenderze z `tokens.json`, w przeglądarce z wyliczonego CSS), nigdzie nie są wpisane ręcznie.
- **Progi próby i pokrycia** (`XX`) ustali metodyka. Wpisz je w `manifest.json` → `thresholds` i uzupełnij `n` w danych;
  do tego czasu UI pokazuje `n = XX`. Reguły „ograniczone” i „poza rankingiem” (`quality` w `cities.json`) nadaje potok danych.

## Dodanie miasta

1. Dopisz obiekt do `cities.json` (unikalny `slug`, `name`, `name_en`, `name_loc`, `region`, `region_en`, `center` `[lon, lat]`, `zoom`, …).
2. Dodaj wiersze miasta do każdej listy w `ranking.json`.
3. Dodaj `segments/<slug>.geojson`.
4. Strona `/miasto/<slug>/` (PL i EN) powstaje sama; miasto pojawia się w rankingu, w wyborze miasta na mapie i w tabeli jakości.

## Mapa i podkład

MapLibre jest ładowany dynamicznie tylko na stronach z mapą (`/mapa/`, mini-mapa na stronie miasta).
Styl podkładu jest budowany z tokenów `idx-map-*` (oba motywy, przełączany razem z motywem strony), odcinki mają kolor z wyrażenia `step`
po prędkości i progach `idx-speed-t*`, „brak danych” to linia przerywana.

**Źródło kafli nie jest wpisane w repozytorium.** Ustaw zmienną `VITE_TILES_URL` (plik `.env`, patrz `.env.example`; w GitHub Actions
jako *Repository variable*): kafle wektorowe w schemacie OpenMapTiles, TileJSON albo szablon `…/{z}/{x}/{y}.pbf`. Dla podpisów dodaj
`VITE_GLYPHS_URL` (+ `VITE_GLYPHS_FONT`). Bez `VITE_TILES_URL` mapa działa bez podkładu i mówi o tym w komunikacie na mapie.
Nie wpisuj kluczy API do repozytorium. Atrybucja „© współtwórcy OpenStreetMap” jest zawsze na mapie i w stopce.

MapLibre 6 ładuje worker jako moduł ES obok swojego pliku; po zbundlowaniu tego pliku nie ma, więc wtyczka Vite w `vite.config.ts`
serwuje i emituje go pod `vendor/maplibre/` (`setWorkerUrl` w `src/map/speedmap.ts`).

Klawiatura na mapie: strzałki przechodzą po odcinkach (komunikat w `aria-live`), Enter otwiera szczegóły, Esc zamyka i oddaje fokus.
„Widok tabeli” jest zawsze dostępny; gdy WebGL nie działa, strona przełącza się na niego sama.

## Język i motyw

- PL to korzeń (`/`), EN mieszka pod `/en/`. Przełącznik zmienia adres, zapisuje wybór w `localStorage` (`idx-lang`) i przy pierwszym
  wejściu z zewnątrz na polską stronę wraca do wybranego angielskiego. Wszystkie teksty są w `src/i18n/*.json`
  (wartości to HTML: literalne `<` zapisz jako `&lt;`); brak klucza przerywa build, a `npm run check` pilnuje zgodności pl/en.
- Motyw: `data-theme` na `<html>`, domyślnie z `prefers-color-scheme`, wybór w `localStorage` (`idx-theme`).

## Ruch

Zasady z `design/guidelines/50-ruch.md`: animujemy tylko `transform` i `opacity`, do 600 ms, czasy i krzywe z tokenów,
bez przejmowania scrolla, bez pętli poza loaderem. Wszystko uruchamia `src/motion.ts`.
Trzy momenty sygnaturowe: odsłonięcie liczby w hero (cyfry po kolei), przelot kamery w scrollytellingu na `/metodyka/`
(`animation-timeline`, w Firefoksie zapas na GSAP ScrollTrigger) i narastanie słupków rankingu.
Zapasy: bez JS treść jest widoczna, `prefers-reduced-motion: reduce` pokazuje stan końcowy, przeglądarki bez View Transitions nawigują zwykle.

## Sprawdzenia

`npm run check` (`tools/check.mjs`, bez zależności) sprawdza: (a) brak literałów kolorów w `src/` i CSS serwisu, (b) kontrast par
tokenów używanych w tekście (4,5:1), kontrolek i linii mapy (3:1) w obu motywach, (c) że nic poza `transform`/`opacity` nie jest
animowane (CSS, keyframes, WAAPI, GSAP, przejścia MapLibre), (d) klucze i18n oraz linki wewnętrzne w `dist/`, (e) że `css/bundle.css`
jest niezmienioną kopią i że w buildzie nie ma `IDX.demo`.

Tryby tylko deweloperskie (znikają z buildu produkcyjnego): `?nogl` przy pierwszym wejściu na `/mapa/` (ścieżka bez WebGL),
`?offline` (stany błędu ładowania danych).

## Wdrożenie

`.github/workflows/deploy.yml`: `npm ci` → sprawdzenie, że `design/tokens.css` jest aktualny → `npm run build` → `npm run check` →
GitHub Pages. Ścieżka bazowa to `/<nazwa-repo>/` (dla repozytorium `*.github.io` to `/`); lokalnie zmienna `BASE`
(domyślnie `/transit-index/`). Włącz w repozytorium *Settings → Pages → Source: GitHub Actions*.

## Odstępstwa i znane problemy systemu projektowego

Pliki z `design/` są niezmienione; poprawki są w `css/site.css` (z komentarzem przy każdej):

- `bundle.css` przejściuje `background-color` na hover (przyciski, opcje przełącznika, wiersze) wbrew regule „tylko transform i opacity”.
  Serwis wyłącza te przejścia (kolor zmienia się od razu).
- `.idx-bar--nd { background: transparent }` (skrót, później w pliku) kasuje kreskowanie z `.idx-hatch`: „poza rankingiem” nie miałoby kreskowania.
- `.idx-rrow .idx-node` ma wyższą specyficzność niż `.idx-node--solid`: pierwszy węzeł łącznika nigdy nie był pełny.
- `.idx-comma` (0,3 em, do lewej) w IBM Plex Mono 500 wpycha przecinek na następną cyfrę (`17,8` wygląda jak `17 ,8`). Przesunięcie `text-indent` centruje go w polu.
- `.idx-map svg { width: 100% }` dotyczy też ikon w mapie (przycisk „Filtry”, zamknięcie okna): ikony mają stały rozmiar.
- Wykres godzinowy z `IDX.chart.hourly` ma stałą geometrię 720 × 320. Serwis rysuje trzy rozmiary (telefon, tablet, desktop) i pokazuje ten, który pasuje do kontenera.
- Nagłówek „Wolne odcinki skupiają się w centrum” z podglądu Scrollytelling jest twierdzeniem o danych: zastąpiony neutralnym „Wolne odcinki widać od razu”.

## Sprawy otwarte

- Progi klas prędkości (8/12/16/20/26 km/h): założenie startowe, do kalibracji na prawdziwych danych.
- Progi próby i pokrycia (`XX`) oraz kryteria plakietek jakości: metodyka.
- Źródło kafli mapy (`VITE_TILES_URL`) i decyzja o hostingu glifów.
- Treść metodyki (`/metodyka/`) to szablon oznaczony „treść wzorcowa”.
- Gęstość danych na mapie zależna od zoomu (odcinki „ograniczone” tylko przy przybliżeniu) czeka na progi próby.
- Obraz OG (okładka z `design/components/Cover`) nie jest wygenerowany: strony mają tylko metadane `og:title` i `og:description`.
- Adres kanoniczny i `hreflang` wymagają znanej domeny.
- Nie sprawdzono na urządzeniach: rendering dużych liczb mono na Androidzie, `animation-timeline` w Safari.
