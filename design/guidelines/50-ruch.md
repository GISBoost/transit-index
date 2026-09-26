# Ruch

Ruch jest subtelny i uzasadniony treścią. Maksymalnie trzy charakterystyczne momenty na cały serwis. Bez ruchu strona jest kompletna: treść nigdy nie zależy od animacji.

## Trzy momenty

1. **Odsłonięcie liczby w hero.** Cyfry wchodzą kolejno (`data-digits` w `IDX.hydrate`): `opacity` 0→1 i `translateY(0,18 em)`→0, `idx-dur-reveal` (600 ms), krzywa `idx-ease-out`, opóźnienie 40 ms na znak. Nie licz liczby w górę: zmiana tekstu nie jest ani transformem, ani opacity.
2. **Przelot kamery mapy sterowany scrollem.** W scrollytellingu mapa jest przypięta, a jej `transform` (skala i przesunięcie) zależy od pozycji sekcji: CSS `animation-timeline: view()`, `idx-ease-linear`. Nie przejmujemy scrolla, nie blokujemy go i nie robimy scroll-jackingu. GSAP ScrollTrigger tylko jako alternatywa tam, gdzie animation-timeline jest niedostępne.
3. **Narastanie słupków rankingu przy wejściu w widok.** `transform: scaleX(0→k)`, `idx-dur-slow` (400 ms), przesunięcie 30 ms na wiersz.

Poza tym: mikro-stany kontrolek (`idx-dur-fast`, 120 ms: hover, fokus, wciśnięcie skala 0,97), przełączniki i okno odcinka (`idx-dur-base`, 240 ms), loader.

## Reguły

- Animujemy tylko `transform` i `opacity`. Nie `width`, `height`, `top`, `filter`, `clip-path`.
- Do 600 ms. Bez sprężyn, odbić i pętli poza loaderem.
- Domyślnie treść widoczna. Klasa `idx-js` na `html` ukrywa elementy dopiero wtedy, gdy JS działa i nie ma `prefers-reduced-motion`.
- `prefers-reduced-motion: reduce`: wszystkie animacje i przejścia wyłączone, liczba i słupki od razu w stanie końcowym, loader jako statyczna linia z jednym pełnym węzłem.
- Przeglądarki bez scroll-driven animations (Firefox stable): `@supports (animation-timeline: view())` osłania kod, bez niego mapa zostaje nieruchoma, kroki nadal aktywują się przez IntersectionObserver.
- Tokeny: `idx-dur-fast/base/slow/reveal`, `idx-ease-out`, `idx-ease-inout`, `idx-ease-linear`. Nie wpisuj czasów ani krzywych ręcznie.
