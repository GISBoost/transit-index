# Prompt dla Claude Code: przeliczenie po zmianie pasm czasu (issue #5)

Prompt do wklejenia w sesji Claude Code na maszynie z `data/obs/` (L0), `data/static/` i `data/geom/`. Zmiana konfiguracji i kodu jest już w gałęzi `claude/bands-14-18` (PR do przeglądu); ten prompt opisuje **przeliczenie i weryfikację**, którego sandbox chmurowy nie mógł zrobić.

---

## Rola i kontekst

Jesteś agentem projektu `transit-index` (repo `GISBoost/transit-index`, reguły w `CLAUDE.md`). Autor zmienił definicję pasm czasu (issue #5). Zmiana konfiguracji, kodu pomocniczego i testów jest zrobiona i przechodzi na danych syntetycznych. **Twoje zadanie: przeliczyć dane pilotażu na nowych pasmach, sprawdzić, że zmienia się to, co powinno, i tylko to, i zapisać wyniki.** Nie zmieniasz definicji metryk, progów, bramki ani rankingu.

## Nowe pasma (godziny lokalne `obs_local`; godzina `h` = `h:00`–`h+1:00`)

| pasmo | było | jest |
|---|---|---|
| `am_peak` | 07:00–09:00 (7, 8) | bez zmian |
| `midday` | 10:00–14:00 (10–13) | **09:00–14:00** (9–13) |
| `pm_peak` | 15:00–18:00 (15–17) | **14:00–18:00** (14–17) |
| `evening` | 19:00–22:00 (19–21) | **18:00–22:00** (18–21) |
| `all_day` | 06:00–22:00 | bez zmian (godzina 6 należy już tylko do `all_day`) |

Jedyne źródło prawdy: `bands` w `config/metrics.yaml`. `reference/metrics_reference.py::BANDS` jest kopią i musi być z nim zgodne (test `test_bands_config_matches_reference`).

## Cel

1. Wszystkie wyniki pilotażu (`2026-pilot`, dni robocze `2026-09-01`…`2026-09-26`, 16 miast) policzone na nowych pasmach: L1, statystyki dzienne, bramka, ranking, metryki, kafle.
2. Dowód, że zmiana jest **wąska**: wartości `all_day` i `am_peak` nie zmieniają się w ogóle, zmieniają się tylko `midday`, `pm_peak`, `evening` i to, co z nich wynika (W3 `pen_pm`, W12, pokrycie pasm).
3. Raport różnic przed/po i wpis w `docs/progress.md`.

## Co już zrobiono w gałęzi (przeczytaj diff, nie powtarzaj)

- `config/metrics.yaml`: nowe `bands`.
- `reference/metrics_reference.py`: `BANDS` i samotest.
- `src/ti/aggregate.py::apply_config_bands`: **`band` jest wyliczane z `hour` przy wczytywaniu L0** (`reference_day_l0`, `ti daystats`). Pliki L0 przechowują `band` z czasu ingestu (stare okna), więc **nie trzeba ponownie robić `ti ingest`**. Nie ruszaj `data/obs/`.
- `scripts/t17_service.py`, `scripts/m0_report.py`, `docs/03` (§2.3, W12, listing configu), testy.
- Decyzje podjęte w gałęzi, do potwierdzenia przez autora w PR: (a) **`method_version` bez zmian** (`ti-1.0-draft`; definicje są zamrażane w listopadzie, `docs/05`; różnicę widać w `config_sha256` manifestu), (b) **W12 (oferta) podąża za `midday`**, więc jej okno to teraz 09:00–14:00 (5 godzin), bo `service.band: midday` w configu. Jeśli autor chce W12 na starym oknie 10–13, trzeba dodać osobne pole w `config/metrics.yaml` (poza zakresem tego zadania, zapytaj).

## Zakres (rób)

1. **Przygotowanie.** Sprawdź gałąź `claude/bands-14-18`, uruchom `pytest tests -q -m "not network"` (oczekiwane: 72 passed, 1 skipped). Zrób kopię zapasową wyników sprzed zmiany: `data/editions/2026-pilot/` → `data/editions/2026-pilot.before-bands/`, `reports/m2/metrics/` i `reports/m3/` → kopie z sufiksem `.before-bands`. Zapisz `git rev-parse HEAD` i `sha256` starego `config/metrics.yaml` (z `main`).
2. **Przeliczenie, w tej kolejności** (okno `2026-09-01`…`2026-09-26`, edycja `2026-pilot`, wszystkie 16 miast kandydujących; `ti aggregate` jest per miasto):
   1. `ti aggregate --city <miasto> --from 2026-09-01 --to 2026-09-26 --edition 2026-pilot` (L1: `segment_stats.parquet`, `segments.parquet`),
   2. `ti daystats --city <miasto> --from 2026-09-01 --to 2026-09-26 --edition 2026-pilot` (uwaga: Warszawa ~45 min, `docs/progress.md`),
   3. `ti gate --from 2026-09-01 --to 2026-12-18 --edition 2026-pilot` (a jeśli wcześniej robiono drugi przebieg `--valid-only`, powtórz zgodnie z opisem w `docs/progress.md`, sekcja M3 „Przepływ”),
   4. `ti metrics --from 2026-09-01 --to 2026-09-26` (`reports/m2/metrics/<miasto>.json`),
   5. `ti geometry --edition 2026-pilot` (kafle i `segments.geojson.gz` biorą wartości `v_*` z L1),
   6. skopiuj nowe `segments.geojson.gz` do `site-test/geojson/2026-pilot/` (zwarte GeoJSON, tak jak w M4).
3. **Weryfikacja niezmienników** (najważniejsza część; napisz skrypt w `scripts/` lub `reports/`, wynik zapisz do `reports/bands/compare_2026-09-30.md`), porównując kopię `.before-bands` z nowym wynikiem, per miasto:
   - **`all_day` i `am_peak` w `segment_stats.parquet` identyczne** (te same `n_obs`, `v_p50`, `q`, do tolerancji zmiennoprzecinkowej). Każda różnica = błąd, zatrzymaj się i zbadaj.
   - Suma `n_obs` z trzech zmienionych pasm po zmianie ≥ sumie przed zmianą (godziny 9, 14, 18 zostały dołączone do pasm nazwanych); `n_obs(all_day)` niezmienne.
   - **Łódź 2026-09-24, `street`, `all_day`: W1 = 17,29 km/h** po filtrze obszaru (zgodnie z wpisem w `docs/progress.md`; golden 17,58 dotyczy L0 bez filtra obszaru). Bez zmian względem stanu sprzed.
   - `pen_am` niezmienione; `pen_pm` zmienione (nowe okno i zbiór odniesienia `midday`+`evening`); podaj rozkład zmiany (mediana, p5, p95) i miasta z największym przesunięciem.
   - Ile odcinków miało `q_pm = none` przed i po (Łódź przed: 133 z 2284 bez wiersza w `pm_peak`, 9,6% długości sieci, plus 42 `thin`). Oczekiwany spadek; podaj liczby dla 16 miast.
   - Zmiany w rankingach (`ranking.json`) per wymiar: które wymiary i miasta zmieniły kolejność lub status nierozróżnialności, W3 i W12 osobno. **Tylko opisz, nie poprawiaj.**
   - Bramka: czy jakiekolwiek miasto/dzień zmieniło status (`pokrycie pasm` liczone z godzin nowych pasm, próg 90% z `config/metrics.yaml`); podaj przyczyny zmian.
   - Kafle: `ti geometry` kończy się bez błędu, kryterium z14+ (`acceptance.pass`) dla 16 miast, rozmiar artefaktu poniżej 700 MB.
4. **Dokumentacja.** Dopisz w `docs/progress.md` (pod „Łódź: szare odcinki…”, bez nowego nagłówka kamienia) wpis „Zmiana pasm (issue #5)”: co przeliczono, tabelę różnic (skrót z raportu), odchylenia od niezmienników, jeśli były, oraz co autor ma zweryfikować ręcznie. Zaktualizuj w `docs/03` tabelę w sekcji 3 i wyniki M2 **tylko** jeśli liczby tam cytowane wynikają z pasm (podaj nowe wartości z przeliczenia, stare zostaw w nawiasie jako „przed zmianą pasm”).
5. **Zamknij pętlę.** Wypisz komendę wdrożenia strony testowej (workflow „M4 test site”, `workflow_dispatch`) — **nie uruchamiaj jej sam**; publikacja wymaga zgody autora.

## Poza zakresem (nie rób)

- Nie zmieniaj progów, klas prędkości, bramki, ranking ani definicji W1–W12 (poza oknami pasm, które już są zmienione). Nie dodawaj wskaźnika złożonego.
- Nie rób `ti ingest` ani nie modyfikuj `data/obs/`, `data/static/`, `data/geom/`.
- Nie zmieniaj `schemas/`, `design/`, `site/`, M5 (Astro).
- Nie importuj kodu `easy-OTP` (GPL). Nie ruszaj `docs/08` (uwagi prawne).
- Nie commituj danych (`data/` jest w `.gitignore`); do gita idą tylko kod, dokumenty, `reports/` (raporty, nie dane), zwarte GeoJSON w `site-test/geojson/`.
- Nie publikuj niczego (Pages, release) bez zgody autora. Nie otwieraj PR-a ani nie scalaj bez prośby autora; commituj na osobnej gałęzi.

## Kryteria akceptacji

1. `pytest tests -q -m "not network"` przechodzi (oczekiwane 72 passed, 1 skipped, plus ewentualne testy z tego zadania; testy zależne od danych, m.in. `test_m2_golden`, `test_golden_lodz`, uruchom też bez filtra `-m`, jeśli dane są dostępne).
2. Wszystkie niezmienniki z pkt 3 spełnione albo każde odstępstwo wyjaśnione w raporcie.
3. 16 miast przeliczone (L1, day_stats, ranking, metryki, kafle), acceptance z14+ przechodzi.
4. `reports/bands/compare_2026-09-30.md` i wpis w `docs/progress.md` istnieją i podają liczby, nie ogólniki.
5. Uruchom subagenta `milestone-reviewer` na diffie tej zmiany (kryterium: niezmienniki, brak magicznych liczb, zgodność `config` ↔ `reference`) i zapisz werdykt w `docs/progress.md`.

## Jeśli coś nie pasuje

Zatrzymaj się i zapytaj autora, gdy: niezmiennik `all_day`/`am_peak` się nie zgadza; `ti aggregate` lub `ti daystats` rzuca błąd na kolumnie `hour`/`band`; zmieniają się statusy miast w bramce w sposób, który zmienia listę miast rankingowych; albo trzeba zmienić cokolwiek z listy „Poza zakresem”. Nie zgaduj i nie omijaj hooków.

## Co autor sprawdza ręcznie po Twojej pracy

- Mapa testowa Łodzi w paśmie „szczyt popołudniowy (14:00–18:00)”: mniej szarych odcinków niż przed zmianą (133 → ?), popup `65>2579` nadal pokazuje „brak obserwacji w paśmie” tylko tam, gdzie faktycznie nie ma kursów.
- Rankingi W3 i W12 w `reports/`/`data/editions/2026-pilot/`: czy kolejność jest sensowna (autobusy tracą więcej niż tramwaje; szczyt popołudniowy gorszy od porannego, `docs/03` §3).
- Decyzje (a) i (b) z sekcji „Co już zrobiono”.
