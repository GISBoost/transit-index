Przełącznik segmentowy dla wyborów wykluczających się: rodzaj (tramwaje/autobusy), pora (dzień/szczyt/poza szczytem), percentyl (P15/P50/P85).

**Dostarczasz:** etykietę grupy (`aria-label`), listę opcji i wybraną. Markup to `role="radiogroup"` z przyciskami `role="radio"` i `aria-checked`.

- Zaznaczenie: tło `accent-soft`, tekst `accent-ink`, waga 600. To nie jest pełny `idx-accent`: kilka przełączników na widoku nie tworzy kilku akcentów.
- Obrys `idx-control-edge`, opcja co najmniej 44 px. Strzałki przełączają wewnątrz grupy.
- Najwyżej cztery opcje. Więcej opcji to lista wyboru, nie segmenty. Wariant `--sm` dla ciasnych paneli.
