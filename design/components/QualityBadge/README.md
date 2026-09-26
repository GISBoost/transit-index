Plakietka jakości danych miasta lub odcinka w trzech stanach: w rankingu, ograniczone, poza rankingiem.

**Dostarczasz:** stan wynikający z progów próby i pokrycia (progi `XX` ustala metodyka).

- `w rankingu`: `idx-q-ranked-*`, węzeł pełny. `ograniczone`: `idx-q-limited-*` (bursztyn), węzeł pusty. `poza rankingiem`: obrys `idx-control-edge` na `surface`, węzeł przerywany.
- Stan niesie słowo, kształt węzła i kolor. Nigdy sam kolor.
- Plakietka stoi obok liczby, której dotyczy, nie w stopce. Prostokąt o promieniu 3 px, bez pigułki.
- Miasto „poza rankingiem” nadal pokazuje dostępne dane, ale bez pozycji.
