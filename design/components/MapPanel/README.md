Panel mapy z filtrami (rodzaj, pora), suwakiem godzin, wyborem percentyla, legendą i przełącznikiem widoku tabelarycznego, obok mapy MapLibre w wyciszonym podkładzie.

**Dostarczasz:** instancję MapLibre ze stylem opartym na tokenach `idx-map-*`, warstwę odcinków z polem klasy prędkości, dane o godzinach i percentylach.

- Desktop: panel `idx-panel` (360 px) po lewej, mapa po prawej. Telefon: mapa na pełną szerokość, filtry w dolnej szufladzie (`sliders`).
- Suwak godzin: linia 2 px, uchwyt 20 px z celem 44 px, wartość „8:00–9:00” w mono. Percentyl: `P15`, `P50` (mediana), `P85` w `SegmentedControl --sm`.
- Mapa jest fokusowalna: strzałki przesuwają zaznaczenie po odcinkach i ogłaszają klasę (`aria-live`), Enter otwiera `SegmentPopup`. Widok tabeli (`table`) zawsze dostępny i równoważny.
- Stany warstwy: wczytywanie (loader na podkładzie), brak danych („za mało zapisów o tej porze”, z podpowiedzią co zmienić), błąd (ikona, słowo, „Spróbuj ponownie”). Panel pozostaje aktywny.
- Filtry w adresie URL. Bez zamglonych paneli i szkła: panel to `surface` z linią.
