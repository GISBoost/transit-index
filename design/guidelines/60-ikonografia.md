# Ikonografia

Jeden spójny zestaw liniowych ikon. Siatka 24 px, kreska 1,5 px (`idx-line-icon`), zakończenia i łączenia okrągłe, bez wypełnień, kolor z `currentColor`. Rozmiary: 16, 20, 24 px. Bez emoji. Bez ikon autobusów, tramwajów i pojazdów: ten motyw niesie linia i przystanek.

Zestaw (16 ikon, `IDX.icon(nazwa, rozmiar)` lub `data-icon` + `IDX.hydrate()`): `arrow-right`, `arrow-up-right`, `download`, `sliders`, `clock`, `map`, `table`, `info`, `warning`, `check`, `close`, `chevron-down`, `external`, `search`, `layers`, `menu`.

## Kiedy której

| Ikona | Użycie |
|---|---|
| `arrow-right` | link „Zobacz”, „Cała metodyka” |
| `download` | karta pobierania |
| `table` / `map` | przełącznik widoku tabelarycznego i mapy |
| `sliders` | otwarcie filtrów na telefonie |
| `info` | stan „za mało danych”, przypis |
| `warning` | błąd i ostrzeżenie (razem ze słowem) |
| `close` | zamknięcie okna odcinka |
| `external` | link poza serwis |
| `check`, `chevron-down`, `search`, `layers`, `menu` | ogólne kontrolki |

## Reguły

- Ikona nigdy nie działa sama: ma słowo albo `aria-label`. Przycisk ikonowy ma cel 44 px.
- Kolor ikony to kolor tekstu obok. Ostrzeżenie może mieć `amber`, błąd nie ma własnego koloru.
- Nowa ikona: ta sama siatka i kreska, jedna metafora, nazwa w kebab-case, dopisana w `bundle.js` i w podglądzie `Icons`.
- Plików SVG nie wgrywamy: ikony są w bundle jako ścieżki `currentColor`, dzięki czemu dziedziczą kolor i motyw.
