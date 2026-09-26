# Wizualizacja danych

Dane są bohaterem strony. Nic nie konkuruje z kolorami prędkości.

## Skala prędkości

Sekwencyjna, 6 klas, jedna rodzina barwy (odcień ok. 212°), progi zdefiniowane raz jako tokeny `idx-speed-t1…t5`.

| Klasa | Token | Zakres (km/h) |
|---|---|---|
| 1 | `idx-speed-1` | poniżej 8 |
| 2 | `idx-speed-2` | 8 do 12 |
| 3 | `idx-speed-3` | 12 do 16 |
| 4 | `idx-speed-4` | 16 do 20 |
| 5 | `idx-speed-5` | 20 do 26 |
| 6 | `idx-speed-6` | od 26 |
| brak danych | `idx-speed-nodata` | linia przerywana, nazwana w legendzie |

Progi 8/12/16/20/26 to wartości startowe: skalibruj je na rozkładzie zmierzonych prędkości po pierwszym przebiegu i zamroź w wersji edycji. Klasę wylicza `IDX.speedClass(km/h)` z tokenów.

- Klasy różnią się jasnością (krok L* ok. 8 do 10), nie tylko odcieniem, więc skala działa w skali szarości i dla osób z zaburzeniami widzenia barw. Bez czerwono-zielonej.
- Wolno = najwięcej „wagi” na podkładzie: w jasnym motywie klasa 1 jest najciemniejsza, w ciemnym najjaśniejsza. Historia serwisu to wolne odcinki.
- Odcinek bez danych ma osobny szary, przerywany, i wpis „brak danych” w legendzie. Nigdy nie pomijaj go ani nie kolorujesz klasą 1.
- Linia na mapie: 3:1 do wyciszonego podkładu w obu motywach (sprawdzone dla lądu, wody i ulic), grubość 3–3,5 px.

## Skala rozbieżna: rozkładowe kontra zmierzone

Niebieski i bursztyn z GISBoost, neutralny środek. Bursztyn = zmierzone wolniej niż rozkładowe (strata), niebieski = szybciej (zysk). Siedem klas: `idx-diff-slower-3…1`, `idx-diff-0`, `idx-diff-faster-1…3`. Środek ma cienki obrys, bo jest bliski podkładu. Kierunek odróżnia odcień i znak w etykiecie („−1,8 km/h”), nie sama jasność. Niebieski/bursztyn jest bezpieczny dla protanopii i deuteranopii.

## Podkład mapy

Wyciszony, desaturowany, w obu motywach: `idx-map-land`, `-water`, `-road`, `-boundary`, `-label`. Ulice cieńsze niż linie danych i bez kontrastu do nich. Podpisy 4,5:1. Interakcja w stylu Chronotrains: najedź lub przypnij odcinek, suwak godzin przesuwa porę dnia, wybór percentyla (P15/P50/P85) zmienia warstwę bez przeładowania.

## Gęstość danych

Odcinek między przystankami to jedna linia. Przy oddaleniu pokazuj odcinki tylko z próbą powyżej progu, przy przybliżeniu także słabsze, oznaczone jako „ograniczone”. Ile pokazać na danym zoomie ustala progi próby (`n ≥ XX`), nie estetyka.

## Wykresy

- Bez ozdobników: bez cieni, 3D, gradientów, zaokrąglonych słupków.
- Bezpośrednie podpisy zamiast legendy tam, gdzie się da (`IDX.chart.hourly` podpisuje serie na końcu linii: `rozkładowe`, `zmierzone`).
- Rozkładowe: linia przerywana `idx-chart-plan`. Zmierzone: linia ciągła `idx-chart-measured`. Siatka `idx-chart-grid`, 1 px.
- Oś zaczyna się od sensownego zera (prędkość od 0 km/h).
- Próby poniżej progu: kreskowanie `idx-chart-nodata` z podpisem „za mało danych”, nie pustka i nie zero.
- Każdy wykres ma `title` i `desc` (SVG) oraz zawsze dostępną wersję tabelaryczną.
- Wartość liczbowa zawsze obok koloru. Kolor nigdy nie jest jedynym nośnikiem znaczenia.
