# 09 · Weryfikacja specyfikacji na prawdziwych danych (2026-09-26)

Ten dokument opisuje, co sprawdziłem na danych z release'ów `GISBoost/easy-GTFS-RT`, jakie wyniki wyszły i jak to powtórzyć. Zastępuje założenia z pierwszej wersji paczki liczbami. Wszystko jest odtwarzalne skryptami z `reference/` i wartościami z `reference/golden_values.json`.

## 1. Dane i metoda

- **Próbka A:** tidy + statyka z **2026-09-24** (czwartek), 15 miast: Łódź, Warszawa, Kraków, Gdańsk, Poznań, Szczecin, Praga, Rzym, Wilno, Sofia, Bukareszt, Lizbona, Zagrzeb, Lublana, Nikozja. Turyn: brak release'u tego dnia (404).
- **Próbka B:** Łódź, 9 dni roboczych 2026-09-14 … 2026-09-24 (18,4–19,1 MB tidy dziennie), statyka z 24.09.
- Pobieranie: `reference/fetch_release_assets.py` (publiczne adresy release'ów, bez API). Analiza: `reference/probe_release_data.py`, funkcje z `reference/metrics_reference.py`.
- Ograniczenia: dla większości miast jeden dzień; filtr obszaru to przybliżenie promieniem; nie sprawdzałem `matched.csv` ani surowych pozycji (nie są publikowane).

## 2. Ustalenia

**Dostęp do danych**
- F1. Załączniki mają dokładnie te nazwy, jak w dokumentacji: `<miasto>_tidy_<data>.csv.gz` i `<miasto>_static_gtfs_<data>.zip` w tagu `<miasto>-realized-<data>-phone`. Publiczne adresy `https://github.com/GISBoost/easy-GTFS-RT/releases/download/...` działają bez uwierzytelniania (API GitHub w tej sesji było zablokowane, ale adresy plików nie). Lista dni: `git ls-remote --tags` (29 nazw, 1630 par miasto-dzień w tagach, ostatni tag 2026-09-25).
- F2. Luki dzienne istnieją: Turyn ma tagi za 20–23 i 25 września, ale nie za 24.
- F3. Rozmiary: tidy 4,7–80 MB dziennie na miasto (Warszawa 72 MB, Praga 80 MB, Łódź 19 MB); łącznie **433 MB dziennie** dla 15 miast. Statyki: 3,7–108 MB na miasto, łącznie **416 MB dziennie**, ale zmieniają się rzadko, więc trzeba je **deduplikować po skrócie SHA-256**. Wąska tabela obserwacji L0 dla Łodzi (168 507 wierszy `ok`, zstd) waży **1,2 MB** (16 razy mniej niż tidy).

**Schemat i semantyka**
- F4. Wszystkie 15 plików ma dokładnie 34 kolumny tidy, w tej samej kolejności co `TIDY_COLUMNS`.
- F5. `seg_dist_m == |shape_dist_m(przystanek) − shape_dist_m(poprzedni)|` (błąd ~1e-11), `seg_time_s == obs_time(przystanek) − obs_time(poprzedni)` (błąd ~1e-13): definicje z kodu potwierdzone na 5 miastach. Czas odcinka jest przejazd-do-przejazdu.
- F6. `obs_local` jest w czasie **lokalnym miasta** (offsety +01:00 Lizbona, +02:00 Warszawa/Praga, +03:00 Wilno/Sofia); wszystkie 10 sprawdzonych miast (w tym 9 zagranicznych) ma dane w godzinach lokalnych 6–21. Problem stref czasu z pierwszej wersji paczki nie istnieje.
- F7. Łódź 2026-09-24: 207 205 wierszy, 7770 kursów, 107 linii, 2183 przystanki, `crossing_rate` 0,865; statusy: `ok` 81,3%, `gap` 10,5%, `first_pair` 3,7%, `no_previous_stop` 3,7%, `implausible` 0,6%, `stationary` 0,1%.
- F8. `trip_id` z tidy łączy się ze statyką w 100%; wszystkie kursy mają `shape_id` i geometrię (tego dnia, Łódź). `shapes.txt` ma kolumnę `shape_dist_traveled`, ale pustą. `shape_dist_m` ostatniego przystanku to 1,000 długości polilinii liczonej haversine'em (p5 = 0,982, brak przypadków > 1,001), więc **geometrię odcinka wycina się z polilinii między dwoma `shape_dist_m` (skumulowana odległość haversine)**. Mediana 4 wierzchołki polilinii na odcinek (p95 = 20).
- F9. Klucz odcinka fizycznego `from_stop_id>to_stop_id` jest stabilny: 98,3–99,4% odcinków z każdego z 8 wcześniejszych dni występuje też 24.09 (Łódź). Łącznie 2563 odcinki (autobus+tramwaj).
- F10. Typy tras: Łódź, Poznań, Kraków `0`/`3`; Gdańsk `700`/`900`; Warszawa ma też `1` (metro) i `2` (kolej). Statyka z ostatniego dnia mapuje trasy z 9 dni tylko w 98,65% wierszy, więc tryb trzeba brać ze statyki **każdego dnia**.
- F11. Rozkładowy postój (`sched_pass_time_s − sched_seg_time_s`) wynosi 0,0–0,7 s dla autobusów i tramwajów we wszystkich 15 miastach.

**Wyniki metryk**
- F12. Prędkość komunikacyjna (bus+tram, `ΣL/ΣT`, 2026-09-24, bez filtra obszaru): Poznań 22,3; Kraków 20,5; Warszawa 19,7; Gdańsk 18,8; Łódź 17,6 km/h. Tramwaje: Kraków 18,9; Poznań 18,5; Warszawa 18,2; Gdańsk 17,5; Łódź **16,4**. Zmierzona względem rozkładowej: od −8,8% (Bukareszt) do +9,7% (Nikozja); Rzym +8,7% (rozkład z zapasem). Kierunek zgodny z wcześniejszymi rankingami rozkładowymi, w których Łódź bywała ostatnia wśród tramwajów (Puls Gdańska, 2021), ale to porównanie poglądowe: inne dane i lata.
- F13. **Filtr obszaru zmienia wyniki o kilka km/h** (Praga: autobusy 28,1 → 20,9 przy R ≤ 8 km; Poznań 27,8 → 23,4). Tabela w `docs/03` §2.1. Bez tego ranking byłby nieuczciwy.
- F14. Łódź, 9 dni: `ΣL/ΣT` dziennie 17,52–17,69 km/h; pasma: `am_peak` 17,42, `midday` 17,43, `pm_peak` **16,61**, `evening` 18,91; kara szczytu (PM vs midday+evening): autobusy +13,2%, tramwaje +3,3%. Spowolnienie względem P85 zależy od kwantyla od 5% do 57% (tabela w `docs/03` §3), stąd zastąpienie go karą szczytu.
- F15. Prędkość: rankingi `ΣL/ΣT` i mediany ważonej długością dają tę samą kolejność dla łącznie i dla autobusów, ale nie dla tramwajów (ρ = 0,7).
- F16. Pokrycie: przy 9 dniach 95,2% długości sieci Łodzi ma komórkę całodzienną `ok`, 83–86% w pasmach; progi `n_obs ≥ 10`, `n_days ≥ 5` są realistyczne.
- F17. Kwintyle prędkości odcinków są podobne w miastach polskich (~15–17 / 19–21 / 23–25 / 29–31 km/h), co uzasadnia klasy `[15, 20, 25, 30]` (pięć klas, zgodnie z `--speed-1..5` w designie; wcześniej sześć klas z krawędzią 10 km/h, `docs/03` §5).

**Gotowość pozostałych 10 feedów (Szczecin i 9 miast zagranicznych; 2026-09-24)**

| miasto | wiersze | `crossing_rate` | udział `ok` | tryby w tidy | `ΣL/ΣT` bus / tram [km/h] |
|---|---|---|---|---|---|
| Szczecin | 117 067 | 0,874 | 0,822 | bus 67%, tram 33% | 21,4 / 17,0 |
| Praga | 897 844 | 0,878 | 0,777 | bus 69%, tram 23%, metro 4%, kolej 4% | 28,1 / 18,7 |
| Rzym | 816 224 | 0,830 | 0,776 | bus (tramwaj marginalny) | 16,7 / 11,1 |
| Wilno | 212 121 | 0,842 | 0,776 | bus | 18,8 / n.d. |
| Sofia | 334 398 | 0,891 | 0,838 | bus 80%, tram 20% | 18,7 / 15,0 |
| Bukareszt | 424 464 | **0,708** | **0,641** | bus 86%, tram 14% | 15,6 / 14,5 |
| Lizbona | 257 688 | 0,826 | 0,776 | bus | 14,0 / n.d. |
| Zagrzeb | 144 561 | 0,873 | 0,771 | bus 61%, tram 39% | 24,1 / 14,7 |
| Lublana | 46 591 | 0,878 | 0,789 | bus | 17,5 / n.d. |
| Nikozja | 55 252 | 0,886 | 0,783 | bus | 27,2 / n.d. |

Wartości Pragi, Zagrzebia i Nikozji dla autobusów są wysokie prawdopodobnie z powodu linii podmiejskich (do potwierdzenia po filtrze obszaru). Bukareszt jest najsłabszy pod względem pokrycia.

## 3. Wnioski dla projektu

1. Filtr obszaru (W0) jest wymaganiem, nie ulepszeniem (`docs/03` §2.1, decyzja D12).
2. Spowolnienie względem P85 zastąpione karą szczytu; P85 zostaje jako wariant eksperymentalny.
3. Statykę pobieraj i deduplikuj **po skrócie**, tryb i geometrię bierz ze statyki właściwego dnia.
4. Klucz odcinka `from>to` jest stabilny; nadal loguj odsetek odcinków z niepasującym `stop_id` w każdym kroku ingestu.
5. Klasy prędkości `[15, 20, 25, 30]` (pięć klas).
6. Testy wzorcowe (`golden_values.json`) w M1 i M2.

## 4. Jak powtórzyć

```bash
pip install pandas pyarrow jsonschema
python reference/fetch_release_assets.py --city lodz --from 2026-09-14 --to 2026-09-24 --out data/raw --weekdays-only
python reference/probe_release_data.py --city lodz \
    --tidy data/raw/lodz_tidy_2026-09-14.csv.gz [pozostałe dni ...] \
    --static data/raw/lodz_static_gtfs_2026-09-24.zip --area-radius-km 8 12 --out probe_lodz.json
```

Porównaj wynik z `reference/golden_values.json` (klucze `lodz_2026-09-24` i `lodz_2026-09-14_do_2026-09-24_9_dni_roboczych`). Jeśli skróty SHA-256 wejść się różnią, release został przebudowany i wartości trzeba policzyć od nowa.
