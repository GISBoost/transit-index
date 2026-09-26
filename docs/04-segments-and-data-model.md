# 04 · Segmenty i model danych

Skąd biorą się kolorowane odcinki na mapie i jak z tabeli tidy dojść do rankingu, bez ruszania surowych nagrań. Liczby w tym dokumencie pochodzą z weryfikacji na prawdziwych danych (`09`).

## 1. Pojęcia

| pojęcie | znaczenie | klucz |
|---|---|---|
| obserwacja | jeden przejazd kursu przez parę kolejnych przystanków (wiersz tidy, `seg_status == "ok"`) | `city, service_date, trip_id, stop_sequence` |
| odcinek fizyczny | para przystanków, po której jeżdżą kolejne kursy dowolnych linii | `seg_id = from_stop_id>to_stop_id`, w skali globalnej `<miasto>:<seg_id>` |
| komórka | odcinek fizyczny × pasmo × typ dnia w oknie edycji | `seg_id, band, day_type` |

Kierunki są osobnymi odcinkami (para jest uporządkowana). Odcinek fizyczny zbiera obserwacje wszystkich linii, żeby na mapie nie nakładały się linie tego samego przebiegu; lista linii idzie do właściwości `routes`.

**Stabilność klucza:** dla Łodzi 98,3–99,4% odcinków z każdego z 8 wcześniejszych dni występuje też 24.09 (2563 odcinki bus+tram; `09` F9). Łódź przenumerowuje `trip_id` co 1–3 dni, ale `stop_id` jest stabilny. Dla pozostałych miast stabilność sprawdza M0. Ingest **loguje odsetek odcinków z niepasującym `stop_id`**; jeśli spadnie poniżej progu, klucz zamienia się na (`stop_name`, zaokrąglone współrzędne).


**Podział długich odcinków** (Cal-ITP dzieli odcinki > 1 km co 1 km): w tidy jest tylko czas przejazdu przez przystanki, więc podział nie jest obserwowalny. W v1 długi odcinek jest jedną linią; oznacz `length_m > 1000` i zaznacz w metodyce.

## 2. Poziomy agregacji

```
L0  obs        wiersz = obserwacja                      data/obs/<miasto>/<data>.parquet
L1  segments   wiersz = komórka (odcinek×pasmo×dzień)   data/editions/<ed>/<miasto>/segment_stats.parquet
L2  city       miasto × tryb × pasmo                    summary.json, hourly.json, lines.csv
L3  ranking    lista miast                              ranking.json
```

**Kolumny L0 (`obs`, tylko `ok`):** `city, service_date, day_type, trip_id, route_id, route_short_name, mode, direction_id, from_stop_id, stop_id, seg_id, seg_dist_m, seg_time_s, sched_pass_time_s, obs_local, hour, band` oraz kolumny wymiarów jakości: `delay_s`, `is_first_stop` (W10), `headway_s`, `sched_headway_s`, `headway_spans_outage`, `headway_skips_vehicles` (W11). Oferta (W12) liczona z `sched_dep` wszystkich kursów rozkładu, więc potrzebuje osobnej wąskiej tabeli rozkładowej (`data/sched/<miasto>/<data>.parquet`; decyzja źródła w M2, `03` §4.3).
`sched_pass_time_s` = rozkładowy czas przejazd-do-przejazdu z `sched_arr` (`reference/metrics_reference.py`; różni się od `sched_seg_time_s` tylko przy rozkładowym postoju, w praktyce ~0 s). `mode` z `routes.txt` **statyki tego samego dnia**. Godzina i pasmo z `obs_local` (już lokalne). Dodatkowo dla filtra obszaru: `in_area` (obie współrzędne przystanków w poligonie, W0).

**Kolumny L1 (`segment_stats`):** `seg_id, band, day_type, n_obs, n_days, n_trips, v_p20, v_p50, v_p80, v_ff, v_sched_p50, slowdown, sum_dist_m, sum_time_s, length_m, q` (`ok`/`thin`/`none`), plus `routes` i nazwy przystanków w tabeli wymiarowej `segments.parquet` (jeden wiersz na `seg_id`).

Kontrakty JSON: `schemas/`, przykłady: `examples/` (wartości zastępcze, `placeholder: true`).

## 3. Potok

| etap | polecenie (propozycja) | wejście → wyjście |
|---|---|---|
| A ingest | `ti ingest --city X --from D1 --to D2` | release'y easy-GTFS-RT → `tidy.csv.gz` + `static_gtfs.zip` (weryfikacja schematu 34 kolumn i sumy kontrolnej) |
| A2 statyka | (w ingest) | statyki deduplikowane po SHA-256; każdy dzień wskazuje właściwy skrót |
| B obs | `ti obs` | tidy + statyka dnia → L0 (filtr `ok`, **filtr obszaru W0**, tryb, `seg_id`, pasmo, `sched_pass_time_s`) |
| C aggregate | `ti aggregate --edition E` | L0 z okna edycji → L1 |
| D metrics | `ti metrics`, `ti gate` | L1 → L2 (wymiary: prędkość W1, kara szczytu W3 parami odcinków, punktualność W10, EWT W11, oferta W12), kwalifikacja dni i miast, bootstrap po dniach, `ranking.json` (rankingi per wymiar), `manifest.json` |
| E geometry | `ti tiles` | statyka + L1 → `segments.pmtiles`, `segments.geojson.gz` |
| F site | `ti build-site` | JSON + kafle + `design/` → statyczna strona |

Wszystkie etapy są **idempotentne** (skrót zawartości w nazwie pliku; ponowny przebieg nie zmienia wyniku). Etap A czyta dane publiczne przez `reference/fetch_release_assets.py` (bezpośrednie adresy release'ów, bez API; lista dni z `git ls-remote --tags`); brak pliku (404) to jawny wpis `missing`, nie błąd.

## 4. Geometria odcinka (zweryfikowana)

1. Z `trips.txt` statyki **tego samego dnia** weź `shape_id` kursu; z `shapes.txt` polilinię. Kolumna `shape_dist_traveled` w `shapes.txt` jest pusta (Łódź), więc odległości liczy się samemu.
2. Skumulowana odległość wzdłuż polilinii liczona haversine'em; `shape_dist_m` ostatniego przystanku to 1,000 tej długości (p5 = 0,982, brak > 1,001). **Odcinek = fragment polilinii między `shape_dist_m` przystanku poprzedniego i bieżącego.** Mediana 4 wierzchołki na odcinek (p95 = 20).
3. Brak kształtów: prosta linia między przystankami, `geometry_quality = straight`. Łódź 24.09: 100% kursów ma geometrię; mimo to raportuj udział `straight` w każdej edycji.
4. Dla odcinka fizycznego wybierz geometrię najczęstszego wzorca.
5. Uproszczenie do ok. 5 m dla zoomu ≥ 14. Kafle PMTiles (tippecanoe → `pmtiles convert`); kryterium akceptacji: żaden odcinek ≥ 200 m nie znika przy z14+.
6. Na mapie oba kierunki rysuj z `line-offset`. Nie importuj kodu `family_a` (GPL); przelicz geometrię samodzielnie z danych.

Właściwości kafli: `schemas/segment_feature.schema.json`. Prędkości w pasmach jako osobne pola (`v_all`, `v_am`, `v_mid`, `v_pm`, `v_eve`), kara szczytu `pen_pm`; szczegóły godzinowe (`hourly`) ładowane po kliknięciu, nie w kaflach.

## 5. Układ plików

```
config/
  metrics.yaml         # progi, pasma, klasy prędkości (5), progi W10-W12, bramka (jedyne miejsce na liczby)
  areas/<miasto>.geojson  # poligon obszaru miasta dla W0 (źródło: D12)
  cities.yaml          # miasta indeksu: display_name, strefa czasu, źródło licencji
  city_defects.yaml    # rejestr wad feedów (patrz 02 §5)
  calendars/<miasto>.yaml
data/                  # lokalne, poza gitem
  obs/<miasto>/<data>.parquet
  editions/<edycja>/...
design/                # zaimportowany Claude Design (nadrzędny, nie edytuj ręcznie)
site/                  # Astro; importuje z ../design
  public/data/<edycja>/manifest.json
  public/data/<edycja>/ranking.json
  public/data/<edycja>/<miasto>/{summary.json,hourly.json,lines.csv,segments.geojson.gz}
  public/data/<edycja>/tiles/<miasto>.pmtiles   # albo jeden plik dla wszystkich miast
docs/adr/              # decyzje (np. wybór metryki nagłówkowej)
```

## 6. Trwałość danych pośrednich

Dzienne surowe pozycje znikają po zbudowaniu (są tylko w miesięcznych archiwach `raw-snapshots-*`), a tidy leży w release'ach repo `easy-GTFS-RT`. Ryzyko: usunięcie lub zmiana retencji. Dlatego etap B zapisuje **L0 jako załączniki release'ów nowego repo** (jeden release na miesiąc, np. `obs-2026-10`, jeden plik na miasto-dzień). Z L0 da się odtworzyć dowolną edycję bez ponownego pobierania tidy.

Zmierzone rozmiary (`09` F3): tidy 433 MB dziennie dla 15 miast, L0 dla Łodzi 1,2 MB dziennie (16× mniej), więc rok L0 dla 15 miast to rzędu kilku GB, co mieści się w release'ach. Statyki (416 MB dziennie) deduplikuj po SHA-256 i trzymaj tylko unikalne. Limity Pages: opublikowana witryna ≤ 1 GB, więc stare edycje i pełne GeoJSON trzymaj w release'ach.
