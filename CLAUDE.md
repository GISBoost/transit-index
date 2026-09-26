# CLAUDE.md — indeks prędkości transportu publicznego

Statyczny serwis (GitHub Pages): ranking miast wg prędkości transportu publicznego zrekonstruowanej z GTFS-RT
oraz mapa odcinków. Poboczny projekt GISBoost. Pełny brand book: `design/README.md` i `design/guidelines/`. Uruchomienie, dane, wdrożenie: `README.md`.

## Reguły

- **Kolory tylko z tokenów.** `idx-*` oraz odziedziczone z GISBoost (`bg`, `surface`, `ink`, `accent`…). Zero hexów w HTML, CSS, JS i na mapie (styl MapLibre czyta wartości tokenów z CSS w czasie działania).
- **Tokenów GISBoost nie ruszamy.** `gisboost-1.css` ładowany jako pierwszy (`<head>`, z `https://gisboost.github.io/assets/gisboost-1.css`), niezmieniony (zmiana wartości = nowy plik `gisboost-2.css`). Wszystko nowe ma prefiks `idx-`.
- **Skala prędkości z tokenów:** `idx-speed-1…6`, progi `idx-speed-t1…t5`. „Brak danych” (`idx-speed-nodata`) zawsze linią przerywaną i nazwane w legendzie.
- **Ruch:** tylko `transform` i `opacity`, do 600 ms (`idx-dur-*`, `idx-ease-*`), pełny fallback dla `prefers-reduced-motion` (treść kompletna bez animacji), bez JS treść widoczna. Animacje uruchamia wyłącznie `src/motion.ts`.
- **Zależności w przeglądarce:** wyłącznie MapLibre i GSAP. Fonty z Google Fonts. Vite + TypeScript to narzędzia budowania (bez frameworka UI); nie dokładaj kolejnych pakietów runtime.
- **Treść:** po polsku (EN w `src/i18n/en.json`), przecinek dziesiętny (`17,8 km/h`), zawsze „rozkładowe” kontra „zmierzone (rekonstrukcja z GTFS-RT)”. Dane zastępcze oznaczone `XX` albo „dane zastępcze”. Teksty tylko przez słownik i18n.
- **Adresy stron** (`/`, `/miasto/<slug>/`, `/mapa/`, `/dane/`, `/metodyka/`, `/jakosc-danych/`, `/archiwum/`, `/en/…`) się nie zmieniają: linki do nich będą krążyć publicznie.

## Układ repo

- `design/` — źródło prawdy z systemu projektowego, **niezmieniane**, nie wdrażane. `design/screens/*.dc.html` to wzorce układu, nie kod do wdrożenia.
- `design/tokens.css` — **generowany**: `py tools/gen_tokens.py` z `design/tokens.json` (i commitowany; CI sprawdza, że jest aktualny). Nie edytuj ręcznie.
- `css/bundle.css` — niezmieniona kopia `design/components/bundle.css` (pilnuje tego `npm run check`). Poprawki do niej idą do `css/site.css` z komentarzem. `css/motion.css` — ruch.
- Kolejność CSS na stronie: `gisboost-1.css` → `design/tokens.css` → `css/bundle.css` → `css/site.css` → `css/motion.css`.
- `src/lib/idx.ts` to port `IDX` z `design/components/bundle.js` **bez** `IDX.demo` (dane pokazowe nie idą na produkcję).
- Komponenty to funkcje w `src/components/`, markup kopiowany z `design/components/<Nazwa>/preview.html`. Strony w `src/pages/`, prerender w `vite.config.ts` + `src/render.ts`.
- Dane w `public/data/` (zastępcze, `py tools/gen_placeholder_data.py`); kształt i walidacja w `src/lib/schema.ts`. Podmiana na prawdziwe dane nie powinna wymagać zmian w UI.

## Zanim oddasz zmianę

`npm run verify` (build + skrypt kontrolny: kolory, kontrast, ruch, i18n, linki). Zmiany wyglądu porównuj z odpowiednim `design/screens/*.dc.html`.
Nie commituj ani nie pushuj, dopóki użytkownik o to nie poprosi.

## Do ustalenia, nie zgaduj

- Progi próby (`XX`) ustala metodyka. Do tego czasu zostaje `XX` i „dane zastępcze”.
- Progi prędkości 8/12/16/20/26 km/h to wartości startowe: skalibruj na prawdziwych danych przed zamrożeniem edycji.
- Źródło kafli mapy (`VITE_TILES_URL`): nie wpisuj kluczy ani adresów z kluczami do repozytorium.
