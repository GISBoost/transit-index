Pas nawigacji GISBoost z marką, nawigacją serwisu i przełącznikiem języka; ten sam kontrakt co `.topbar` w gisboost-1.css, pod klasą `.idx-topbar`.

**Dostarczasz:** listę linków serwisu (Ranking, Mapa, Dane, Metodyka, Jakość danych, Archiwum), bieżącą stronę (`aria-current="page"`), `LangSwitch`.

- Tło `chrome`, tekst `chrome-ink`, nieaktywne linki `chrome-muted`. Marka „GISBoost” jest osobnym linkiem do portalu, „/ indeks prędkości” osobnym do strony głównej serwisu. Nie zagnieżdżaj jednego w drugim.
- Stany: najechanie (`.is-hover`, jaśniejsze tło z `chrome-ink`), bieżąca strona, fokus (2 px `chrome-ink`).
- Na telefonie nawigacja przewija się poziomo, cele 44 px. Nie zwijaj do hamburgera, jeśli pozycje się mieszczą.
- Nie dodawaj przycisku głównego do topbara: jeden przycisk główny na widok należy do treści.
