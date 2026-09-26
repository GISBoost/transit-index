# Transit Index: skrót całości

Poboczny projekt GISBoost (poza doktoratem). Serwis indeksujący **jakość funkcjonowania** transportu publicznego w kilkunastu miastach europejskich, liczony ze **zmierzonych** danych (zrekonstruowane GTFS-RT z `easy-GTFS-RT`) i z rozkładów. Rankingi miast per wymiar, mapy odcinków między przystankami kolorowane prędkością, strony miast, edycja roczna. Wzorzec: TomTom Traffic Index (liczby nie są porównywalne). Statyczny serwis na GitHub Pages.

**Podział pracy:** wygląd, układ i animacje: Claude Design, **gotowe i zaimportowane do `design/`, nadrzędne wobec docs**. Ten katalog `docs/` to dane, metryki, potok, build i kontrakt techniczny z designem.

**Status (2026-09-26):** design zbudowany; specyfikacja, kod referencyjny i wartości wzorcowe gotowe; potoku i strony jeszcze nie ma. Ten plik to skrót; pełna treść w `docs/01…09`, `reference/`, `schemas/`, `examples/`.

## 1. Mapa repo

| plik | zawartość |
|---|---|
| `README.md`, `CLAUDE.md` | wejście do projektu; zasady dla agenta |
| `design/` | Transit Index Design System (tokeny, komponenty, landing, social-card); nadrzędny |
| `docs/01-research-summary.md` | TomTom, analogi (Cal-ITP, Swiftly, Puls Gdańska), ekosystem GISBoost, decyzje |
| `docs/02-data-inventory.md` | załączniki release'ów, 34 kolumny tidy, rozmiary, znane wady feedów |
| `docs/03-metrics-spec.md` | model jakości, filtr obszaru W0, metryki W1–W12, pasma, klasy prędkości, bramka, czułość |
| `docs/04-segments-and-data-model.md` | odcinki fizyczne, poziomy L0–L3, potok, geometria, układ plików |
| `docs/05-annual-edition.md` | okno edycji, kalendarze per kraj, manifest, prawo do odpowiedzi |
| `docs/06-site-spec.md` | architektura serwisu, kontrakt z designem, CI, budżety, rozbieżności docs ↔ design (§9) |
| `docs/07-milestones.md` | M0–M7 z gotowymi promptami dla Claude Code |
| `docs/08-risks-and-open-questions.md` | decyzje D1–D14 i ryzyka (**nie commituj do publicznego repo**) |
| `docs/09-validation-on-real-data.md` | ustalenia F1–F17 z prawdziwych danych, gotowość feedów, jak powtórzyć |
| `reference/` | `metrics_reference.py` (definicje + samotest), `fetch_release_assets.py`, `probe_release_data.py`, `golden_values.json`, `validate_examples.py` |
| `schemas/`, `examples/` | kontrakty JSON: ranking, city_summary, segment_feature, edition_manifest (przykłady mają `placeholder: true`) |
| `.claude/agents/milestone-reviewer.md` | subagent oceniający każdy kamień milowy |

Start: `pip install pandas pyarrow jsonschema`, `py reference/metrics_reference.py`, `py reference/validate_examples.py`, potem prompt M0 z `docs/07`.

## 2. Dane wejściowe (zweryfikowane, `docs/02`, `docs/09`)

- Release'y `GISBoost/easy-GTFS-RT`, tag `<miasto>-realized-<data>-phone`; załączniki `<miasto>_tidy_<data>.csv.gz` (od 2026-08-03) i `<miasto>_static_gtfs_<data>.zip`. Adresy `https://github.com/GISBoost/easy-GTFS-RT/releases/download/<tag>/<asset>` działają bez API; lista dni z `git ls-remote --tags` (29 nazw, 1630 par miasto-dzień).
- Tidy: 34 kolumny (potwierdzone w 15 plikach); wiersz = przystanek kursu; odcinek = para (`from_stop_id` → `stop_id`); `seg_time_s` przejazd-do-przejazdu; `obs_local` w czasie lokalnym miasta (strefy nie są problemem); filtr `seg_status == "ok"` obowiązkowy.
- Rozmiary: tidy 433 MB/dzień dla 15 miast; statyki 416 MB/dzień, ale zmieniają się rzadko (deduplikacja po SHA-256); tabela L0 dla Łodzi 1,2 MB/dzień (16× mniej).
- Statykę bierz **z tego samego dnia** (statyka z innego dnia mapuje trasy tylko w 98,65% wierszy).
- Luki dzienne istnieją (Turyn bez release'u 24.09). Wady feedów: `docs/02` §5.

## 3. Model jakości i metryki (`docs/03`, kod: `reference/metrics_reference.py`)

**Jakość = pięć osobnych wymiarów, bez wskaźnika złożonego w v1** (D11). Każdy ma własny ranking, `n` i status jakości. Prędkość jest jednym z nich.

| wymiar | metryka | kierunek | status weryfikacji |
|---|---|---|---|
| Prędkość | W1 prędkość komunikacyjna `3,6·ΣL/ΣT`; W2 czas przejazdu 10 km | więcej = lepiej | zweryfikowana (Łódź, golden values) |
| Obciążenie szczytu | W3 **kara szczytu** (te same odcinki, szczyt vs `midday`+`evening`, ≥ 10 obs.) | mniej = lepiej | zweryfikowana (Łódź, 9 dni) |
| Punktualność | W10 udział przyjazdów "o czasie" (`delay_s` −60…+180 s, bez pierwszego przystanku) | więcej = lepiej | 1 dzień, bez filtra obszaru; do walidacji w M2 |
| Regularność | W11 nadmiar czasu oczekiwania EWT, tylko linie częste (odstęp rozkładowy < 600 s) | mniej = lepiej | **niezweryfikowana**; do ustalenia w M2 |
| Oferta | W12 mediana rozkładowych odjazdów na godzinę na przystanek (`midday`) | więcej = lepiej | **niezweryfikowana**; mierzy rozkład, nie wykonanie |

Pozostałe: W4 prędkość odcinka (mediana, P20, P80; mapa), W5 rozstaw przystanków (kowariat), W6 prędkość względem rozkładu, W7 rozrzut czasu przejazdu (v1.1), W8 najwolniejsze odcinki, W9 profil godzinowy.

**Poza modelem** (nie wynika z GTFS/GTFS-RT): dostępność, ceny, komfort, bezpieczeństwo, zatłoczenie oraz realizacja kursów (odwołany kurs nie różni się od pojazdu znikającego z feedu).

**Wspólne reguły:**
- **W0, filtr obszaru (warunek konieczny):** odcinek liczy się tylko, gdy oba przystanki są w poligonie miasta (`config/areas/<miasto>.geojson`, źródło: D12). Bez tego linie podmiejskie zawyżają wyniki (Praga, autobusy: 28,1 → 20,9 km/h przy R ≤ 8 km).
- **Pasma (czas lokalny):** `am_peak` 7–8, `midday` 10–13, `pm_peak` 15–17, `evening` 19–21; godziny 6, 9, 14, 18 tylko w `all_day`. Pasmo obowiązuje miasto, gdy nagranie pokrywa ≥ 90% jego godzin.
- **Tryby z `route_type`:** tramwaj 0/900–999; autobus 3/700–799 + trolejbus 11/800–899; metro i kolej poza indeksem.
- **Dzień referencyjny:** dzień roboczy bez świąt (biblioteka `holidays` per kraj), ferii i dni anomalnych.
- **Klasy prędkości (5, jak `--speed-1..5` w designie):** krawędzie `[15, 20, 25, 30]` km/h, propozycja skalibrowana na danych z 7 miast; zamrażane po M2. Poprzedni podział sześcioklasowy porzucono, bo poniżej 10 km/h leżało 3,4% sieci Łodzi.
- **Jakość danych:** odcinek `ok` (n ≥ 10, dni ≥ 5) / `thin` (n ≥ 3) / `none`; miasto `ranked` / `limited` / `excluded` (bramka w YAML, `docs/03` §6); niepewność przez bootstrap po dniach. Miasto może być `ranked` w jednym wymiarze i `limited` w innym.
- **Wskaźnik złożony:** v2, po teście wrażliwości na wagi (`docs/03` §4.4).

## 4. Kluczowe ustalenia z prawdziwych danych (`docs/09`)

- Łódź 2026-09-24: 168 507 wierszy `ok`, `ΣL/ΣT` = 17,58 km/h (autobus 18,24, tramwaj 16,37); 9 dni: 17,59, dziennie 17,52–17,69.
- Kara szczytu w Łodzi (9 dni): autobusy AM +6,7% / PM +13,2%; tramwaje +1,0% / +3,3%.
- Spowolnienie względem P85 zależało od wyboru kwantyla (5–57% dla tych samych danych), więc zastąpiła je kara szczytu.
- Rankingi `ΣL/ΣT` i mediany ważonej długością zgadzają się dla ogółu i autobusów, dla tramwajów ρ = 0,7, więc rankingi tramwajów pokazuj z przedziałami.
- Punktualność (wstępnie, 1 dzień, bez filtra obszaru): udział "o czasie" Łódź 66,1%, Warszawa 70,0%, Gdańsk 71,9%, Kraków 72,8%, Poznań 76,2%.
- Geometrię odcinka wycina się z polilinii `shape` między dwoma `shape_dist_m` (haversine); klucz odcinka `from_stop_id>to_stop_id` jest stabilny (98,3–99,4% między dniami w Łodzi).
- Gotowość feedów: Bukareszt najsłabszy (`crossing_rate` 0,71, udział `ok` 0,64); reszta 0,83–0,89.

## 5. Model danych i potok (`docs/04`)

- L0 obserwacje (tylko `ok`, w obszarze; z kolumnami opóźnień i odstępów dla W10/W11) → L1 komórki odcinek × pasmo × typ dnia → L2 miasto (wymiary) → L3 rankingi.
- Potok (CLI `ti`): ingest (pobranie, dedup statyk po SHA-256) → obs (L0) → aggregate (L1) → metrics/gate (L2, rankingi, manifest) → tiles (PMTiles) → build-site.
- Wszystkie progi w `config/metrics.yaml`; etapy idempotentne; L0 archiwizowany w release'ach repo.

## 6. Edycja roczna (`docs/05`)

- Pilotaż `2026-pilot`: dni robocze 2026-09-01 – 2026-12-18, publikacja w styczniu 2027; zamrożenie definicji `ti-1.0` do 15 listopada 2026.
- Manifest edycji z przypiętym tagiem `easy_otp_ref` (nie `main`), sumami kontrolnymi wejść i statusem `draft → operator_review → published`; edycje niezmienne, poprawki jako `<id>.1`.
- Przegląd operatorów (ok. 2 tygodnie embarga) przed publikacją; porównania rok do roku tylko przy tej samej wersji metody.

## 7. Serwis i design (`docs/06`)

- Astro (prerender) + MapLibre GL + PMTiles, własny podkład mapy (nie hotlinkuj kafli OSM), własny workflow GitHub Actions do Pages, GoatCounter, PL/EN.
- Trasy: `/` ranking z przełącznikiem wymiarów, `/miasto/<id>/`, `/mapa/`, `/dane/` (ranking CSV, odcinki GeoPackage i GeoJSON, profile godzinowe CSV), `/metodyka/`, `/jakosc/`, `/edycje/`.
- **Design (`design/`) jest nadrzędny; `site/` importuje z niego, nie kopiuje.** Motywy: dzienny (papier) i nocny `[data-theme="night"]`; skala prędkości `--speed-1…5` + `--speed-nodata` (tylko dla wymiaru Prędkość); paleta linii `--line-*` to dekoracja; fonty Hanken Grotesk + Archivo Narrow (OFL), w produkcji hostowane u siebie; komponenty React (prototyp), sposób użycia rozstrzyga ADR w M5; brak literalnych kolorów w kodzie; kontrast, fokus, `prefers-reduced-motion`, widok tabelaryczny mapy.
- **Rozbieżności docs ↔ design** (`docs/06` §9): dostosowano klasy prędkości, fonty, motywy, ścieżkę designu, zakres treści. Do zmiany w designie przy prawdziwych danych: copy sekcji "Liczba" (−22% względem 10% najszybszych przejazdów → kara szczytu), hero i nagłówek rankingu (tylko prędkość), przełącznik wymiarów (D13).
- Limity Pages: 1 GB, 100 GB/mies. (miękki), 10 min deployu; test zakresów bajtów PMTiles w przeglądarkach, plan B: lustro na Cloudflare.
- Budżety: strona rankingu ≤ 100 kB JS (gzip), LCP ≤ 2,5 s, CLS ≈ 0, artefakt < 700 MB.

## 8. Kamienie milowe (`docs/07`, prompty do wklejenia)

| M | cel |
|---|---|
| M0 | szkielet repo, weryfikacja na pełnym oknie, poligony miast, kalendarze, licencje, decyzje |
| M1 | ingest i tabela L0; test wzorcowy względem `golden_values.json` |
| M2 | odcinki i metryki W1–W12, kara szczytu, klasy, ostateczne definicje W10–W12, test czułości |
| M3 | bramka jakości, rankingi per wymiar z niepewnością, manifest |
| M4 | geometria odcinków, kafle PMTiles, podkład |
| M5 | szkielet serwisu Astro + integracja z `design/` |
| M6 | wydajność, dostępność, i18n, obrazy OG |
| M7 | edycja pilotażowa, przegląd operatorów, Zenodo |

Po każdym kamieniu: `milestone-reviewer`, dalej dopiero po PASS.

## 9. Decyzje i ryzyka (`docs/08`)

- **Rozstrzygnięte:** D1 zakres = kilkanaście miast europejskich; **D11 model jakości = pięć osobnych wymiarów, wskaźnik złożony w v2**.
- **Do podjęcia:** D2 metryka wymiaru Prędkość (M2), D3 okno pilotażu, D4 nazwa i adres (robocza: Transit Index, `gisboost.github.io/transit-index/`; nadrzędny `easy/CLAUDE.md` zakłada strony bez build stepu, a tu jest Astro), D7 licencja wyników, D8 GZM jako metropolia, D9 rytm publikacji, **D12 źródło poligonów** (OSM albo Eurostat GISCO), **D13 copy landingu do modelu jakości**, **D14 nazwy wymiarów w UI**.
- **Główne ryzyka:** definicja obszaru miasta, statyki zmieniające się między dniami, luki dzienne, jakość feedów (Bukareszt, Turyn), licencje danych operatorów, PMTiles na Pages, pojedynczy punkt awarii (telefon nagrywający), wymiary mogące się wzajemnie "nie zgadzać", oferta odczytana jako pomiar.
- **Nieweryfikowane:** W11 i W12 nie liczone na danych, W10 tylko 1 dzień; 14 z 15 miast ma tylko jeden dzień próbki; filtr obszaru w próbie to promień, nie poligon; ref `easy-OTP` w workflow; licencje danych, fontów i ikon; progi bramki to propozycja; sformułowanie "pierwszy w Polsce" wymaga sprawdzenia.

## 10. Zasady twarde (`CLAUDE.md`)

- `design/` nadrzędny; przy konflikcie zmienia się dokument. Wątpliwości: pytaj autora.
- Nie importuj kodu `easy-OTP` (GPL-3.0-or-later); czytaj tylko dane.
- Tylko `seg_status == "ok"`, tylko odcinki w obszarze miasta, statyka z tego samego dnia.
- Pięć wymiarów, bez wskaźnika złożonego w v1; prędkość to jeden z wymiarów.
- Brak magicznych liczb (`config/*.yaml`); każda liczba z `n` i statusem jakości.
- Brak zmyślonych danych; przykłady z `placeholder: true` nie trafiają do buildu produkcyjnego.
- Wyniki z różnych `method_version` nie są porównywalne.
- Bez nazwy i wyglądu "Traffic Index"; nic nie publikuj bez zgody autora; ranking operatorów dopiero po przeglądzie.
- Bez branchy, commitów i pushy bez prośby autora.
