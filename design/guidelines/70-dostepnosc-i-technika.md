# Dostępność i technika

## Kontrast i widzenie barw

Sprawdzone liczbowo dla obu motywów (WCAG 2, luminancja względna):

- Tekst 4,5:1 na podłożach z jego noty: `ink`, `ink-muted` na `bg`/`surface`, `accent-ink` na `surface` i `accent-soft`, `amber-ink` na `amber-soft`, `idx-on-accent` na `idx-accent` (6,9:1 jasny, 6,8:1 ciemny).
- Elementy sterujące, węzły i linie na mapie 3:1: obrys `idx-control-edge` (5,0:1 i więcej na `surface`), fokus `focus` (6:1 i więcej), klasy `idx-speed-1…6` i `idx-speed-nodata` względem lądu, wody i ulic (najniżej 3,1:1).
- Skala prędkości w skali szarości: różnica L* między sąsiednimi klasami co najmniej 7,9. Symulacja protanopii, deuteranopii i tritanopii (Machado 2009): najmniejsza różnica sąsiednich klas ΔE ≥ 7,8. Skala rozbieżna: każda klasa bursztynowa jest odległa od każdej niebieskiej o ΔE ≥ 51 w każdym z trzech wariantów.
- Pary odziedziczone z GISBoost, które nie przechodzą 4,5:1 i zostają bez zmian (nie używaj ich do tekstu treści): `ink-muted` na `surface-2` (4,44:1 jasny, 4,14:1 ciemny), `chrome-muted` na `chrome` (4,49:1 jasny; tylko krótkie etykiety nawigacji), `ink-faint` na `bg`/`surface` (do 3:1, dekoracja), `ink-muted` na `accent-soft` w ciemnym (4,48:1).
- Kolor nigdy nie jest jedynym nośnikiem: plakietka jakości ma słowo i kształt węzła, wykres podpis, mapa tabelę, błąd ikonę i słowo.

## Fokus, klawiatura, cele

Fokus widoczny zawsze: 2 px `focus`, offset 2 px (na pasie `chrome` w kolorze `chrome-ink`). Cele dotykowe co najmniej 44 px (`idx-tap`): przyciski, opcje przełączników, wiersze rankingu, węzły interaktywne, klasy legendy. Przełączniki to `radiogroup` z obsługą strzałek.

Mapa: fokusowalna (`tabindex="0"`), strzałki przesuwają zaznaczenie po odcinkach i ogłaszają klasę w regionie `aria-live`, Enter otwiera okno odcinka, Esc zamyka i oddaje fokus. **Alternatywny widok tabelaryczny mapy jest zawsze dostępny** (przycisk „Widok tabeli”, `aria-pressed`). Każdy wykres ma tytuł, opis i tabelę.

## Mobile-first

Ruch przyjdzie z mediów społecznościowych. Projektuj od 360 px: jedna kolumna, boczny margines 16 px, liczby hero 72 px, panel mapy jako dolna szuflada, filtry w szufladzie. Układ reaguje na kontener `.idx-frame` (640 i 1024 px). Topbar na telefonie przewija nawigację poziomo z celami 44 px.

## Technika

Statyczny serwis (GitHub Pages). Fonty z Google Fonts, bez własnych plików. Zależności: MapLibre i GSAP, nic więcej. `bundle.js` nie ma zależności i nie używa `eval`. Stan mapy i filtry w adresie URL, żeby link do widoku był udostępnialny.

## Założenia i sprawy otwarte

- Progi klas prędkości (8/12/16/20/26 km/h) to założenie startowe do kalibracji.
- Progi próby i pokrycia (`XX`) oraz kryteria plakietek jakości ustali metodyka.
- Nazwa serwisu jest robocza. Okładka i topbar używają „Indeks prędkości”.
- Miasta, wartości, numery linii poza „11”, licencje i rozmiary plików w podglądach to dane zastępcze.
- Błąd nie ma własnego koloru (decyzja: ikona, słowo, grubszy obrys). Jeśli serwis będzie potrzebował czerwieni, wchodzi jako nowa wersja.
- Nie sprawdzono na urządzeniach: renderowanie dużych liczb mono na Androidzie, zachowanie `animation-timeline` w Safari.
