# Podstawy wizualne

Charakter: minimalizm w duchu Apple. Dużo pustej przestrzeni, jedna myśl na ekran, wielka pewna typografia z ciasnym trackingiem, dane jako bohater strony, cienkie linie zamiast cieni, precyzyjna siatka. Ekran ma być rozpoznawalny jako GISBoost, ale bardziej przestronny i typograficzny.

## Kolor

Niebieski to kolor transportu. Rampa `idx-blue-50…950` wychodzi z akcentu GISBoost (odcień ok. 212°) i przechodzi przez jego wartości: `idx-blue-100` = `accent-soft`, `600` = `accent`, `700` = `accent-ink` w jasnym, `300`/`400` w ciemnym. Nie wprowadzaj drugiej rodziny barwy.

- Akcent serwisu: `idx-accent` (600 w jasnym, 400 w ciemnym). Tekst na nim: `idx-on-accent` (biały w jasnym, `idx-blue-950` w ciemnym). Nigdy biały tekst na akcencie w ciemnym motywie.
- Neutralne szarości zostają z GISBoost: `bg`, `surface`, `surface-2`, `ink`, `ink-muted`, `ink-faint`, `border`.
- Jeden akcent na widok. Trzy przełączniki nie znaczą trzech akcentów: zaznaczenie to `accent-soft` z `accent-ink`, pełny `idx-accent` ma tylko główny przycisk, linia postępu i seria „zmierzone”.
- Bursztyn: ostrzeżenia, ograniczenia, dane zastępcze, treści eksperymentalne, oznaczenie „wolno”. Nigdy dekoracja.
- Błąd nie ma osobnej barwy. Niesie go ikona `warning`, słowo i grubszy obrys `ink` (`idx-card--error`). Czerwień by ją pomieszała z bursztynem u osób z zaburzeniami widzenia barw.

Zapamiętaj ograniczenia par z GISBoost, które zostają bez zmian: `ink-muted` na `surface-2` ma 4,44:1 (jasny) i 4,14:1 (ciemny); `ink-faint` to element dekoracyjny, nie tekst; `border` nie wystarcza jako obrys kontrolki, do kontrolek służy `idx-control-edge`.

## Typografia

Archivo dla nagłówków (600/700/800), IBM Plex Sans dla tekstu, IBM Plex Mono dla liczb i etykiet technicznych. Drabina wag: 300 / 400 / 600 / 700 / 800. Waga 500 tylko w liczbach mono (`idx-figure-*`, `idx-board`). Waga 300 tylko od 22 px (`idx-lead`).

| Styl | Rozmiar / interlinia | Zastosowanie |
|---|---|---|
| `idx-display-xl` | 64 / 1,03, −0,035 em | jedno zdanie w hero; telefon 40 px |
| `idx-display-lg` | 44 / 1,08 | nagłówek sekcji, strona miasta; telefon 32 px |
| `idx-display-md` | 32 / 1,12 | krok scrollytellingu; telefon 26 px |
| `idx-display-sm` | 22 / 1,2 | tytuł kafla, okna, notki |
| `idx-figure-xl` | 104 / 1, mono | liczba KPI w hero; telefon 72 px |
| `idx-figure-lg` / `-md` | 56 / 32, mono | kafel KPI, wiersz rankingu |
| `idx-board` | 15 / 1,3, mono | prędkości i czasy w tabelach |
| `idx-lead` | 22 / 1,45, waga 300 | zdanie pod nagłówkiem |
| `idx-body` | 17 / 1,5 | tekst; 17 px, nie 16 |
| `idx-ui`, `idx-caption` | 15, 14 | kontrolki, podpisy |
| `idx-eyebrow` | 12, 600, +0,09 em | nadtytuł WERSALIKAMI |

Ujemny tracking tylko od 17 px wzwyż, nigdy w 12 px i mniej. Liczby zawsze tabelaryczne (`font-variant-numeric: tabular-nums` jest w bundle.css). Przecinek dziesiętny w mono skracaj klasą `.idx-comma`, inaczej liczba się rozpada.

## Odstępy i siatka

Baza 8 px: `idx-space-1…10` = 4, 8, 12, 16, 24, 32, 48, 64, 96, 144. Boczny margines telefonu 16 px (`idx-space-4`). Odstęp między sekcjami: 48 (telefon), 64 (tablet), 96 (desktop). Hero zaczyna się 96–144 px od góry. Szerokość tekstu `read` (46 rem), treści `wide` (70 rem). Punkty przejścia: 640 i 1024 px kontenera.

Sekcje rozdziela pusta przestrzeń albo separator „linia i przystanek”, nie ramki. Alternacja jasne/ciemne płótno w stylu Apple jest opcjonalna i tylko w obrębie jednego motywu: `bg` ↔ `surface`.

## Promienie, linie, elevation

Promienie: `idx-radius-sm` 6 px (przyciski, pola), `idx-radius-md` 12 px (karty, panele), `idx-radius-xs` 3 px (plakietki linii i jakości). Bez pigułek w kontrolkach. Linia podziału 1 px (`idx-line-hair`), linia motywu 2 px (`idx-line-track`). Karta ma cienką linię `border`, w hover obrys `idx-accent`. Bez cieni, bez rozmyć, bez gradientów jako ozdoby. Jedyny wyjątek to `idx-shadow-float` pod oknem odcinka i dolną szufladą mapy. Kreskowanie (`idx-hatch`) oznacza „za mało danych”, nie ozdobę.
