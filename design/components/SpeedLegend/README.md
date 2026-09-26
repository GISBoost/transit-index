Legenda prędkości: sześć klas sekwencyjnych z progami w km/h, osobny wpis „brak danych” i wariant rozbieżny dla różnicy rozkładowe kontra zmierzone.

**Dostarczasz:** progi z tokenów `idx-speed-t1…t5` i powiązaną warstwę mapy, którą klasa ma filtrować.

- Klasy `idx-speed-1…6`, etykiety progów w mono, wysokość paska 10 px, klasy jako przyciski 44 px. Najechanie lub fokus na klasie przygasza pozostałe (mapa i legenda).
- „Brak danych”: przerywana linia w `idx-speed-nodata`, zawsze obecna.
- Wariant rozbieżny: siedem klas `idx-diff-*`, podpisy „zmierzone wolniej”, „bez zmiany”, „zmierzone szybciej”. Środek z cienkim obrysem.
- Stany: wczytywanie (szkielet), brak wyniku (legenda ustępuje komunikatowi „za mało danych”).
- Nie zmieniaj progów lokalnie: jedno źródło to tokeny.
