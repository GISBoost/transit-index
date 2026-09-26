# Motyw „linia i przystanek”

Jeden powtarzalny element graficzny, wzięty ze szwajcarskiego oznakowania i klasycznych schematów sieci: cienka linia z węzłami. Zastępuje ikony autobusów i tramwajów, których nie używamy wcale.

## Budowa

- Linia: `idx-line-track` 2 px (`idx-line-track-thin` 1,5 px przy małych rozmiarach), kolor `idx-track`. Przebyta część: `idx-track-done`.
- Węzeł: okrąg 8 px (`idx-node-sm`) lub 10 px (`idx-node-md`), obrys `idx-node`, klasa `.idx-node`. Pusty = jeszcze nie, pełny (`.idx-node--solid`, `idx-track-done`) = przebyty lub aktywny. Bursztynowy węzeł (`.idx-node--warn`) tylko przy ograniczeniach.
- Węzeł niesie sens, więc ma 3:1 i więcej do tła. Nigdy nie oznacza czegoś samym kolorem: obok zawsze słowo albo numer.

## Cztery role

| Rola | Klasa | Gdzie |
|---|---|---|
| Separator sekcji | `.idx-rule` | między sekcjami zamiast ramki: węzeł pełny na początku, pusty na końcu |
| Wskaźnik postępu | `.idx-rule` + `.idx-rule__done` (`--p`), `.idx-conn` w krokach | scrollytelling, kroki metodyki |
| Łącznik w rankingu | `.idx-conn` (`--first`, `--last`) | lewa kolumna wiersza: linia przechodzi przez wszystkie wiersze |
| Loader | `.idx-loader` | węzły zapalają się kolejno; przy reduced-motion statyczna linia z jednym pełnym węzłem |

Dodatkowo: trasa w oknie odcinka (przystanek A → przystanek B) to ten sam pionowy łącznik.

## Plakietka numeru linii

Prostokąt 24 px o promieniu `idx-radius-xs`, gruby numer Archivo 800, tło `idx-accent`, numer `idx-on-accent` (`.idx-badge`). **Wyłącznie prawdziwe numery linii.** Numer zastępczy to kreskowana plakietka `XX` (`.idx-badge--ph`), nie plakietka z wymyślonym numerem. Nie rysuj plakietki dla nazwy miasta, trybu ani kategorii.

## Tablica odjazdów

Prędkości i czasy w IBM Plex Mono, cyfry tabelaryczne, wyrównane do prawej w kolumnach (`idx-board`, `.is-num`). Jednostkę zapisuj mniejszą i w `ink-muted` obok liczby. To drugi znak rozpoznawczy serwisu, obok linii.

## Dobrze i źle

- Dobrze: separator z dwoma węzłami między hero a rankingiem; łącznik po lewej stronie wierszy rankingu; loader z czterech węzłów.
- Źle: węzły jako ozdoba tła, wielokolorowe linie „jak metro”, ikony pojazdów, linia bez węzłów jako zwykła ramka, więcej niż jedna rola naraz w tym samym obszarze.
