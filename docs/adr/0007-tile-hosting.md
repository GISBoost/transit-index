# ADR-0007: Hosting kafli PMTiles i podkładu (M4)

Status: **potwierdzone w Chrome** (2026-09-30, patrz `docs/progress.md`); Firefox i Safari jeszcze nie sprawdzone. Dotyczy `docs/06` §1, §4, §5, §7 i `docs/10` §8.

## Kontekst

Mapa (M5) czyta kafle PMTiles przez `pmtiles://` i zapytania HTTP `Range`. Trzeba zdecydować, gdzie kafle leżą, kto je buduje i czy podkład jest własny. Ograniczenia:

- GitHub Pages: witryna ≤ 1 GB, deployment ≤ 10 min, miękki limit 100 GB transferu miesięcznie (`docs/06` §7). Build kończy się błędem powyżej 700 MB (`docs/06` §5).
- Runner na prywatnym repo: 2 vCPU, 7 GB RAM, 2000 min/mies. na darmowym planie (`docs/10` §8; liczby z wiedzy ogólnej, do weryfikacji w ustawieniach rozliczeń). Publiczne repo nie ma limitu minut. Autor zamierza ustawić repo na publiczne.
- Zgłoszenie protomaps/PMTiles #584 opisuje sporadyczne błędy zakresów dla plików z GitHub Pages (stan aktualny nie sprawdzony).
- Sandbox M4 nie ma dostępu do `build.protomaps.com`, więc podkładu nie da się tam zbudować ani sprawdzić.

## Zmierzone (dane pilotażowe, 16 miast)

Rozmiary: patrz `reports/m4/geometry_2026-pilot.json` (per miasto) i tabela poniżej (wygenerowana z tego raportu). Kafle segmentów z tippecanoe 2.49 (`-Z8 -z15`, bez zrzucania cech) są małe: rzędu 1-4 MB na miasto, kilkadziesiąt MB łącznie, czyli ułamek budżetu 700 MB. Jeden plik na miasto nigdzie nie zbliża się do limitu 100 MB na plik w git.

| miasto | odcinki | GeoJSON.gz (kB) | PMTiles (MB) | prosta geometria (długość) | zamienione na prostą (zły stosunek długości) | segmenty ≥ 200 m bez geometrii |
|---|---|---|---|---|---|---|
| bucharest | 2341 | 197 | 1,82 | 0,1% | 1 | 0 |
| gdansk | 1486 | 139 | 1,45 | 0,5% | 6 | 0 |
| krakow | 2407 | 213 | 2,12 | 0,8% | 9 | 0 |
| lisbon | 2549 | 198 | 1,69 | 3,6% | 12 | 0 |
| ljubljana | 626 | 87 | 0,81 | 5,9% | 0 | 0 |
| lodz | 2284 | 199 | 1,92 | 3,2% | 8 | 0 |
| nicosia | 1087 | 103 | 0,93 | 0,1% | 0 | 0 |
| poznan | 1688 | 136 | 1,50 | 3,7% | 31 | 0 |
| prague | 4083 | 394 | 3,46 | 1,2% | 31 | 0 |
| rome | 9497 | 910 | 7,20 | 1,1% | 43 | 0 |
| sofia | 2601 | 245 | 2,00 | 0,0% | 0 | 0 |
| szczecin | 1320 | 109 | 1,17 | 0,3% | 0 | 0 |
| turin | 2721 | 218 | 2,07 | 1,2% | 13 | 0 |
| vilnius | 1744 | 159 | 1,80 | 0,0% | 0 | 0 |
| warszawa | 5051 | 394 | 4,01 | 0,8% | 35 | 0 |
| zagreb | 2105 | 211 | 2,01 | 2,4% | 2 | 0 |
| **razem** | | 3912 | 36,0 | | 191 | |

Artefakt strony testowej (16 miast, bez podkładu): 37,2 MB przy budżecie 700 MB (`docs/06` §5). Podkład dojdzie w workflow; jego rozmiar nie jest znany (patrz niżej).

## Decyzja

1. **Kafle segmentów: jedna paczka `<miasto>.pmtiles` na miasto, hostowana na GitHub Pages razem ze stroną.** Powód: rozmiar jest daleko poniżej limitów, a osobny host to dodatkowy koszt i punkt awarii. Jedno miasto ładuje jeden plik, więc mapa nie pobiera danych innych miast.
2. **Budowa kafli w Actions z zatwierdzonego, zwartego GeoJSON (`site-test/geojson/<edycja>/<miasto>.geojson.gz`), nie z L0/L1/statyk.** Powód: L0, L1 i statyki są poza gitem (CLAUDE.md), a runner ich nie ma. GeoJSON to wynik pochodny (kilkaset kB na miasto), a tippecanoe na runnerze buduje kafle w sekundach. To odstępstwo od `docs/06` §5 pkt 2 (pobranie zamrożonej edycji z release'ów): sandbox M4 nie może tworzyć release'ów. Gdy repo będzie publiczne, GeoJSON i kafle powinny przejść do release'u edycji, a workflow je pobierać i weryfikować sumy kontrolne.
3. **Własny podkład: wycinki `<miasto>.pmtiles` z dziennego buildu Protomaps (OSM, ODbL) przez `go-pmtiles extract --bbox`, `maxzoom` 14**, robione w workflow. Zewnętrzny serwis kafli nie jest używany; atrybucja OSM widoczna na mapie. Styl podkładu jest własny i bierze kolory z tokenów `design/` (bez etykiet, więc bez czcionek i sprite'ów do hostowania).
4. **Plan B (nie wdrożony):** lustro na Cloudflare Pages/R2 albo kafle jako pliki `z/x/y`, jeśli test zakresów w którejś przeglądarce zawiedzie. Strona testowa ma przycisk "Test zakresów bajtów" i wypisuje status 206, `Content-Range` i długości; wynik ręcznego testu wpisuje się do `docs/progress.md`.

## Koszt w minutach runnera

Nie zmierzony (workflow nie był jeszcze uruchomiony na GitHubie). Szacunek z lokalnego przebiegu: budowa 16 kafli i kontrola akceptacji z14+ trwa poniżej minuty na 4 rdzeniach; ekstrakty podkładu zależą od sieci i rozmiaru bbox (do zmierzenia). Ograniczenie ryzyka: workflow odpala się wyłącznie ręcznie (`workflow_dispatch`; publikacja wymaga zgody autora, CLAUDE.md), a `concurrency` anuluje starsze przebiegi.

## Konsekwencje

- Statyki i tidy nie są potrzebne w Actions; geometrię buduje się lokalnie (`ti geometry`), a do repo trafia zwarty GeoJSON.
- Powiększenie liczby miast lub edycji rośnie liniowo (kilka MB na miasto na edycję); przy stu edycjach trzeba przejść na release'y (punkt 2).
- Ranking, bramka i publikacja wyników nie są dotknięte; strona testowa jest oznaczona jako techniczna i nie zawiera rankingów.
- GitHub Pages dla repo prywatnego wymaga płatnego planu; przy repo publicznym nie ma tego ograniczenia.
