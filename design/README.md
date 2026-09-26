Indeks prędkości transportu publicznego (nazwa robocza) to poboczny projekt GISBoost: ranking miast według prędkości transportu publicznego, liczonej ze zrekonstruowanych danych GTFS-RT taboru, oraz mapy z odcinkami między przystankami kolorowanymi według prędkości. Ten system rozszerza GISBoost, nie zastępuje go. Ma kojarzyć się z Apple dyscypliną i rytmem, a z transportem kolorem i motywem linii i przystanku. Ma wyglądać na zaprojektowany przez człowieka.

## Jak ładować

1. Fonty z Google Fonts: Archivo 600/700/800, IBM Plex Sans 300/400/600, IBM Plex Mono 400/500/600. Bez własnych plików fontów.
2. `gisboost-1.css` bez zmian. Definiuje tokeny bez prefiksu (`bg`, `surface`, `ink`, `accent`, `amber`…).
3. Warstwa serwisu: tokeny `idx-` (`tokens.css` tego systemu) i `components/bundle.css`. Ten plik CSS ładuje się po `gisboost-1.css`.
4. Cała strona w kontenerze `.idx-frame`. Układ komponentów reaguje na jego szerokość (progi 640 i 1024 px), nie na okno.
5. `components/bundle.js` (globalnie `IDX`) tylko dla ikon, wykresu godzinowego, formatowania liczb i wejścia w widok. Poza tym wyłącznie MapLibre i GSAP.

Tokenów GISBoost nie zmieniaj ani nie usuwaj. Wszystko nowe ma prefiks `idx-` i mieszka w osobnym pliku. Zmiana wartości istniejącego tokenu oznacza nową wersję (`gisboost-2.css`), nie edycję na miejscu.

## Hierarchia źródeł

Gdy źródła się różnią, wygrywa wyższe.

1. Tokeny i zasady GISBoost: kolory, fonty, promienie 6 i 12 px, tryb ciemny.
2. Zasady układu, rytm odstępów, proporcje skali typograficznej i ruch z niezależnej analizy DESIGN.md Apple. To zasady, nie zasoby: bez SF Pro, znaków, obrazów i palety Apple.
3. Referencje funkcjonalne: struktura rankingu i strony miasta (nie wygląd), interakcja mapy, gęstość danych na mapie, wykresy `transit_charts` z easy-OTP.

## Dziesięć twardych reguł

1. Kolory tylko z tokenów. Zero hexów w komponentach, wykresach i mapie.
2. Jeden akcent na widok: `idx-accent`. Bursztyn (`amber`) tylko dla ostrzeżeń, treści eksperymentalnych, danych zastępczych i oznaczenia „wolno”.
3. Skala prędkości ma 6 klas różniących się jasnością, nie tylko odcieniem: `idx-speed-1…6`. Brak danych to osobny szary `idx-speed-nodata`, zawsze linią przerywaną.
4. Każde „zmierzone” to „zmierzone (rekonstrukcja z GTFS-RT)”. Zawsze odróżniaj je od „rozkładowe”. Wynik jest odtworzony, nie zmierzony wprost.
5. Liczby prędkości i czasów w IBM Plex Mono, cyfry tabelaryczne, przecinek dziesiętny, jednostki `km/h` i `min/10 km`.
6. Jedna myśl na ekran, cienka linia zamiast cienia i ramki-ozdobnika. Jedyny cień to `idx-shadow-float` nad mapą.
7. Motyw „linia i przystanek” jest jedynym powtarzalnym elementem graficznym. Bez ikon autobusów i tramwajów.
8. Ruch: tylko `transform` i `opacity`, do `idx-dur-reveal` (600 ms), bez przejmowania scrolla. Pełna treść bez ruchu.
9. Kontrast tekstu co najmniej 4,5:1, elementów sterujących i linii na mapie 3:1, w obu motywach. Cel dotykowy 44 px (`idx-tap`).
10. Dane pokazowe zawsze z widocznym znacznikiem „dane zastępcze” albo wartością `XX`. Bez wymyślonych statystyk, opinii i lorem ipsum.

## Szybka ściąga po tokenach

| Potrzebujesz | Token |
|---|---|
| Tło strony, karta, ciche pole | `bg`, `surface`, `surface-2` |
| Tekst, tekst drugorzędny | `ink`, `ink-muted` |
| Akcent (przycisk, aktywny stan, seria „zmierzone”) | `idx-accent`, `idx-on-accent` |
| Obrys kontrolki | `idx-control-edge` |
| Cienka linia podziału | `border` przez `idx-line-hair` |
| Linia i węzły motywu | `idx-track`, `idx-track-done`, `idx-node` |
| Prędkość na mapie i w słupkach | `idx-speed-1…6`, `idx-speed-nodata` |
| Różnica rozkładowe kontra zmierzone | `idx-diff-slower-3…1`, `idx-diff-0`, `idx-diff-faster-1…3` |
| Stan jakości | `idx-q-ranked-*`, `idx-q-limited-*`, `idx-q-out-*` |
| Dane zastępcze | `idx-placeholder-ink`, `idx-placeholder-bg` |
| Odstępy | `idx-space-1…10` (4, 8, 12, 16, 24, 32, 48, 64, 96, 144 px) |
| Czas i krzywa | `idx-dur-*`, `idx-ease-*` |

Szczegóły w sekcjach poniżej: treść i głos, podstawy wizualne, linia i przystanek, wizualizacja danych, ruch, ikonografia, dostępność i technika.
