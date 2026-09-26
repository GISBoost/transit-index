# ADR-0001: Astro z build stepem w GitHub Actions

Status: przyjęta 2026-09-26 (właściciel: GISBoost). Dotyczy D5.

## Kontekst
Strony pod `gisboost.github.io` są celowo bez build stepu (`easy/CLAUDE.md`). Transit Index ma design w React (`design/components`), 15+ miast × PL/EN jako osobne strony, potrzebę prerenderu (SEO, podglądy w mediach społecznościowych) i mapę MapLibre.

## Decyzja
Astro, statyczny output (prerender), komponenty React jako wyspy albo port do `.astro` (sposób rozstrzyga ADR w M5). Build wyłącznie w GitHub Actions, wynik nie trafia do gita. GitHub Pages serwuje tylko gotowe pliki. Wyjątek od reguły "bez build stepu" dotyczy wyłącznie tego repo i jest zapisany w `easy/CLAUDE.md`.

## Rozważone
Bez buildu (ręczny HTML + JS): słabe SEO stron miast, prototyp używa Babel i React z CDN, nieprodukcyjne. Generator w Pythonie: brak bezpośredniego użycia komponentów z `design/`.

## Konsekwencje
Dochodzą Node i workflow `deploy.yml`. Zmiana pojawia się na stronie dopiero po udanym buildzie. Adres i wygląd nadal są widoczne dla użytkowników pozostałych serwisów, więc zasady o URL-ach z `easy/CLAUDE.md` obowiązują.
