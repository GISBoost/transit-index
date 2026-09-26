Ranking miast: karta z przełącznikami rodzaju i pory oraz wierszami z łącznikiem „linia i przystanek”, słupkiem klasy prędkości, plakietką jakości i liczbą tablicową.

**Dostarczasz:** listę miast (nazwa, prędkość zmierzona, stan jakości), wybrane przełączniki, opis metody pod tabelą.

- Wiersz `.idx-rrow`: łącznik `.idx-conn` (pierwszy z `--first`, ostatni z `--last`), pozycja mono, miasto `600`, `QualityBadge`, słupek, liczba `idx-figure-md`. Cały wiersz to link co najmniej 44 px.
- Słupek ma kolor klasy prędkości (`IDX.speedClass`) i skalę od zera. Narasta przy wejściu w widok (`data-k`, `scaleX`). Miasto poza rankingiem: kreskowanie zamiast słupka, `—` zamiast liczby, bez pozycji.
- Stany: najechanie (`.is-hover`, tło `bg`), fokus (2 px `focus`), wczytywanie (szkielety + loader), brak danych (komunikat z progiem), błąd (obrys `ink`, „Spróbuj ponownie”).
- Telefon: nazwa i liczba w jednym wierszu, słupek pod spodem. Tabela linii (`.idx-table`) ma tę samą gramatykę: nagłówki `idx-eyebrow`, liczby mono wyrównane do prawej, plakietki tylko dla prawdziwych numerów.
- Pod tabelą zawsze jedno zdanie o tym, że „zmierzone” to rekonstrukcja z GTFS-RT.
