Motyw „linia i przystanek”: cienka linia z węzłami użyta jako separator sekcji, wskaźnik postępu, łącznik w rankingu i loader.

**Dostarczasz:** rolę (separator, postęp, łącznik, loader) i, dla postępu, wartość `--p` (0–100 %) albo stan kroków.

- Linia `idx-line-track` (2 px), kolor `idx-track`; przebyta część `idx-track-done`. Węzeł 8 lub 10 px, obrys `idx-node`, pełny `.idx-node--solid`.
- Łącznik pionowy: `.idx-conn` z `--first` i `--last`, żeby linia zaczynała się i kończyła w węźle.
- Loader: cztery węzły, kolejne zapalają się co 150 ms. Zawsze z `role="status"` i `aria-label`. Przy reduced-motion statyczny.
- Jedna rola naraz w danym obszarze. Nie używaj węzłów jako tła ani wielobarwnych linii.
