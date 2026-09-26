Hero z jedną liczbą KPI jako bohaterem strony: nadtytuł, nagłówek jako pełne zdanie, liczba w mono 104 px, zdanie otwierające i dwie definicje.

**Dostarczasz:** nazwę miasta i porę, prędkość zmierzoną, jednostkę, próg i próbę. Definicje „zmierzone (rekonstrukcja z GTFS-RT)” i „rozkładowe” zostają zawsze.

- Nagłówek `idx-display-xl` (40 px na telefonie), liczba `idx-figure-xl` (72 px na telefonie) w cyfrach tabelarycznych, jednostka `km/h` obok, mniejsza.
- Odsłonięcie liczby: cyfry wchodzą kolejno (transform + opacity, 600 ms), `data-digits`. Bez JS i przy reduced-motion liczba jest od razu.
- Definicje z węzłami: pełny = zmierzone, pusty = rozkładowe.
- Stany: wczytywanie (szkielet + loader), brak danych (`—`, „n = XX < XX”, plakietka `poza rankingiem`), błąd (ikona, słowo, obrys `ink`, „Spróbuj ponownie”).
- Jedna liczba na hero. Nie dokładaj drugiej ani wykresu w tym samym ekranie.
