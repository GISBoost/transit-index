Sekcja scrollytellingu: przypięta mapa i kolumna kroków ze wskaźnikiem „linia i przystanek”, w której aktywny krok zapala węzeł i przełącza warstwę mapy.

**Dostarczasz:** 3–5 kroków (nagłówek i jedno zdanie), stan mapy dla każdego kroku, wspólny fallback treści.

- Mapa `position: sticky`, po lewej na desktopie (1,4 : 1), na górze na telefonie. Kroki po prawej: `idx-display-md` i `idx-body`, wysokość co najmniej 240 px, nieaktywne 0,55 krycia.
- Wskaźnik: pionowa linia z węzłem na każdy krok. Przebyty i aktywny krok w `idx-track-done`, reszta `idx-track`.
- Ruch (jeden z trzech momentów): przelot kamery jako `transform` sterowany `animation-timeline: view()`, tylko w przeglądarkach, które go mają. Kroki aktywuje IntersectionObserver.
- Nie przejmujemy scrolla. Bez JS i przy reduced-motion wszystkie kroki są czytelne, a mapa pokazuje stan ogólny. Kroki są fokusowalne (`tabindex`), fokus aktywuje krok.
- Jeden krok, jedna myśl. Bez pływających ozdób i paralaksy.
