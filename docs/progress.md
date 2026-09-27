# Dziennik postępu

Jeden wpis na kamień milowy (M0–M7), najnowszy na górze. Wpis powstaje na końcu kamienia i jest uzupełniany o werdykt `milestone-reviewer`. Decyzje techniczne: `docs/adr/`, pytania do autora: `docs/decisions-needed.md`.

## M0: repo, dane na pełnym oknie, decyzje (2026-09-26)

**Status: wykonany, przegląd PASS (warunkowy), decyzje właściciela wprowadzone** (otwarte pozycje: `docs/decisions-needed.md`, żadna nie blokuje M1).

### Co powstało

| wynik | gdzie |
|---|---|
| szkielet repo: `pyproject.toml`, `.gitignore` (dane poza gitem), pytest, venv `.venv` (poza gitem) | korzeń |
| progi i klasy (jedyne miejsce na liczby), lista miast, rejestr wad feedów | `config/metrics.yaml`, `config/cities.yaml`, `config/city_defects.yaml` |
| kalendarze świąt na okno 2026-09-01…12-18 dla 25 miast (biblioteka `holidays`; ferie szkolne puste, do ręcznego uzupełnienia) | `config/calendars/` |
| poligony miast (GISCO, tymczasowo, D12) i rejestr źródeł | `config/areas/` |
| test regresyjny: sonda odtwarza `golden_values.json` dla Łodzi 2026-09-24 (SHA-256 wejść zgodne) | `tests/test_golden_lodz.py` |
| testy konfiguracji, klas prędkości vs tokeny designu, poligonów | `tests/` (13 testów) |
| skrypty M0 (powtarzalne, wznawialne) | `scripts/m0_inventory.py`, `m0_polygons.py`, `m0_area_effect.py`, `m0_calendars.py`, `m0_report.py` |
| inwentarz na oknie 2026-09-01…25 | `docs/data-inventory.generated.md`, surowe: `reports/m0/` |
| audyt licencji (wstępny) | `docs/licenses.md` |
| decyzje i pytania; ADR-y (Astro, poligony, licencje) | `docs/decisions-needed.md`, `docs/adr/` |

### Jak powtórzyć

```
py -m venv --system-site-packages .venv && .venv/Scripts/python.exe -m pip install holidays
.venv/Scripts/python.exe scripts/m0_inventory.py heads --from 2026-09-01 --to 2026-09-25 --out reports/m0/heads.jsonl
.venv/Scripts/python.exe scripts/m0_inventory.py statics --from 2026-09-01 --to 2026-09-25 --out reports/m0/heads.jsonl
.venv/Scripts/python.exe scripts/m0_inventory.py stats --from 2026-09-01 --to 2026-09-25 --heads reports/m0/heads.jsonl --out reports/m0/stats.jsonl   # ~10 GB przez strumień, ~16 min
.venv/Scripts/python.exe scripts/m0_polygons.py fetch && .venv/Scripts/python.exe scripts/m0_polygons.py compare   # wymaga pliku GISCO w data/m0_polygons/
.venv/Scripts/python.exe scripts/m0_area_effect.py
.venv/Scripts/python.exe scripts/m0_report.py
.venv/Scripts/python.exe -m pytest
```

### Najważniejsze ustalenia

1. **Schemat:** 34 kolumny w każdym z 287 plików kandydatów (dni robocze 2026-09-01…25).
2. **Nagrania 1–4.09 są częściowe** (od 11:00, 15:00, 17:00); pełne dni od **2026-09-07**. Bramka dnia odrzuca je w większości miast (nie we wszystkich: np. Lizbona 09-02 ją przechodzi, bo godziny 7–21 pokrywają pasma).
3. **2026-09-17: brak tidy w 11 z 25 miast** (8 bez tagu release'u, 3 z tagiem bez tidy). Przyczyna nieustalona.
4. **Dni ważne od 7.09 (z 15 dni roboczych, po bramce dnia, brakach release'ów i świętach):** Kraków, Łódź, Poznań, Wilno 15; Gdańsk 13 (1 brak, 1 bramka); Lizbona, Lublana, Praga, Rzym, Szczecin, Warszawa 14; Sofia 13 (2 święta); Bukareszt, Nikozja, Zagrzeb 12; **Turyn 7**. Szczegóły: `docs/data-inventory.generated.md` §2.
5. **Poligon (D12):** GISCO i OSM zgodne w 19 z 23 miast; różnice: Sofia, Lizbona, Nikozja, Gdańsk (`docs/decisions-needed.md` §1). Filtr obszaru zmienia prędkość autobusów o 0,0–6,2 km/h (prawie wcale w Rzymie, Sofii, Lizbonie, Lublanie) i odcina do 30% obserwacji.
6. **Statyki zmieniają się prawie codziennie** w większości miast, więc deduplikacja SHA-256 daje małe oszczędności.
7. **`easy-OTP` w workflow bez `ref`** (checkout `main`). Semantyka tidy jednolita od 2026-08-09; ostatni commit narzędzi `bccb17b` (2026-09-04, `perf`). Decyzja właściciela: **bez pinu**, oznaczanie pochodzenia per dzień (ADR-0004, `config/tidy_epochs.yaml`).
8. **Licencje (statyka i RT, `docs/licenses.md`):** Turyn tylko niekomercyjnie (projekt niekomercyjny, więc dopuszczony pod bramką), Rzym RT "wyłącznie jako wsparcie podróży", Warszawa ODbL share-alike dla kształtów, 7 miast bez znalezionej licencji statyki, miasta ze zbiorkom.live bez warunków. **Właściciel: wyniki na CC BY 4.0, wszystkie miasta publikowane z atrybucją (ADR-0003).** Lista adresów RT z telefonu jeszcze potrzebna dla pełnego domknięcia.
9. **Wykonalność W10–W12:** `delay_s` i `headway_s` są dostępne w ok. 92–100% wierszy z obserwacją. Linie częste (< 600 s) to 1–3% wierszy w Poznaniu, Nikozji i Łodzi, więc W11 może mieć małą próbę w polskich miastach.
10. **Poznań:** po filtrze obszaru autobusy nadal 26,6 km/h (Kraków 19,7); do wyjaśnienia w M2.
11. **Liczba miast w `cities.json`:** 27 (dokumentacja podawała 28; `lka` usunięto 2026-09-09).

### Czego M0 nie zrobił / ograniczenia

- Stabilność `stop_id` między dniami dla miast innych niż Łódź: przeniesione do M1 (wymaga statyk).
- Okres 2026-08-03…08-31 nie był sprawdzany (poza oknem pilotażu).
- Pokrycie pasm to przybliżenie ("godzina ma ≥ 1% wierszy `ok`"), nie definicja docelowa z `docs/03` §2.3.
- Kalendarze: ferie szkolne i święta regionalne nie są uwzględnione.
- Poligon dla Przemyśla: tylko OSM (brak w Urban Audit); GZM bez poligonu (metropolia, D8).
- Audyt licencji oparty na wyszukiwaniu i stronach operatorów, nie na pełnych regulaminach; RT dla Zagrzebia, Lublany, Nikozji, Rzeszowa i Kielc bez adresu endpointu (jest na telefonie).
- Nie zmieniano żadnych repo poza tym (`easy-OTP`, `easy-GTFS-RT` czytane tylko do odczytu).

## Ocena ryzyka jakości danych (stan 2026-09-25, wygenerowane z `reports/m0/`)

Pełne dni nagrania od 2026-09-07. Prognoza zakłada, że udział dni ważnych utrzyma się do końca okna pilotażu (2026-12-18; 72–75 dni roboczych na miasto po odjęciu świąt). Progi: `ranked` ≥ 40 dni ważnych, `limited` ≥ 20. Ocena: **OK** = udział dni ważnych ≥ 90% i mediany `crossing_rate` i `ok` co najmniej 0,15 nad progiem; **do obserwacji** = któryś z tych warunków niespełniony; **RYZYKO** = prognoza poniżej progu `ranked`. Nie uwzględnia pokrycia sieci (M2).

| miasto | dni ważne od 09-07 | z dni roboczych | udział od 09-07 | udział ostatnie 2 tyg. | mediana crossing (próg 0.6) | mediana ok (próg 0.55) | prognoza do 12-18 (tempo od 09-07) | prognoza (tempo 2 tyg.) | zapas nad 40 dniami | trend crossing / tydz. | ocena |
|---|---|---|---|---|---|---|---|---|---|---|---|
| turin | 7 | 15 | 47% | 50% | 0.73 | 0.68 | 35 | 37 | -5 | -0.040 | RYZYKO |
| bucharest | 12 | 15 | 80% | 70% | 0.69 | 0.62 | 58 | 51 | 18 | +0.006 | do obserwacji |
| gdansk | 13 | 15 | 87% | 80% | 0.88 | 0.82 | 64 | 59 | 24 | +0.001 | do obserwacji |
| nicosia | 12 | 15 | 80% | 80% | 0.88 | 0.78 | 58 | 58 | 18 | -0.001 | do obserwacji |
| zagreb | 12 | 15 | 80% | 90% | 0.87 | 0.77 | 59 | 67 | 19 | -0.001 | do obserwacji |
| krakow | 15 | 15 | 100% | 100% | 0.78 | 0.71 | 74 | 74 | 34 | +0.010 | OK |
| lisbon | 14 | 15 | 93% | 100% | 0.83 | 0.78 | 67 | 72 | 27 | +0.004 | OK |
| ljubljana | 14 | 15 | 93% | 90% | 0.88 | 0.79 | 70 | 68 | 30 | +0.008 | OK |
| lodz | 15 | 15 | 100% | 100% | 0.86 | 0.81 | 74 | 74 | 34 | -0.004 | OK |
| poznan | 15 | 15 | 100% | 100% | 0.88 | 0.82 | 74 | 74 | 34 | -0.001 | OK |
| prague | 14 | 15 | 93% | 90% | 0.88 | 0.78 | 67 | 65 | 27 | +0.001 | OK |
| rome | 14 | 15 | 93% | 90% | 0.83 | 0.77 | 69 | 67 | 29 | +0.004 | OK |
| sofia | 13 | 13 | 100% | 100% | 0.89 | 0.84 | 73 | 73 | 33 | +0.000 | OK |
| szczecin | 14 | 15 | 93% | 90% | 0.87 | 0.81 | 69 | 67 | 29 | +0.004 | OK |
| vilnius | 15 | 15 | 100% | 100% | 0.84 | 0.77 | 74 | 74 | 34 | +0.002 | OK |
| warszawa | 14 | 15 | 93% | 90% | 0.88 | 0.81 | 69 | 67 | 29 | -0.001 | OK |

**Zagrożenia przy obecnym tempie:**
1. **Liczba dni nie jest wąskim gardłem.** Do `ranked` trzeba ok. 40 z ~74 dni, więc miasto może stracić do ok. 45% dni roboczych. Poza Turynem wszystkie mają zapas 18–34 dni.
2. **Turyn:** 7 z 15 dni ważnych, 4 dni bez release'u, trend jakości spadkowy; prognoza 35–37 dni, czyli `limited`, nie `ranked`.
3. **Bukareszt:** najwęższe marginesy jakości (mediana `crossing_rate` 0,69 przy progu 0,60, `ok` 0,62 przy 0,55) i 3 dni odrzucone na 15 (09-15 o 0,004 poniżej progu), w ostatnich dwóch tygodniach 70% dni ważnych. To najbardziej prawdopodobne miasto, które wypadnie z `ranked`, jeśli jakość się obniży.
4. **Nikozja, Zagrzeb, Gdańsk:** po 80–87% dni ważnych; braki to głównie dni bez release'u (Zagrzeb 3, Nikozja i Gdańsk po 1) i pojedyncze dni z niepełnym pokryciem pasm. Jakość dni, które są, jest dobra.
5. **Pokrycie sieci (drugi próg `city_gate`) nie jest jeszcze zmierzone** (M2). Dla Łodzi przy 9 dniach: 95% długości sieci z odcinkami `ok` (`docs/09` F16), więc progi 0,60 i 0,40 wyglądają na łatwe, ale dla reszty miast to niepotwierdzone.
6. **Zmiana metody w trakcie okna (ADR-0004).** Jeśli poprawka `family_a` zmieni semantykę tidy między ok. **21.10 a 5.11**, żadna z dwóch epok nie ma osobno ≥ 40 dni ważnych, więc wyniki per epoka byłyby co najwyżej `limited`. Bezpieczniej robić takie zmiany przed ok. 20.10 albo po ok. 6.11 (po zmianie jedna z epok ma wtedy ≥ 40 dni), albo zaakceptować wyniki `limited`.
7. **Awarie wspólne** (jak 17.09: 11 z 25 miast bez tidy). Jedna taka doba na 15 kosztuje ok. 7% dni; nawet kilkutygodniowa przerwa telefonu mieści się w zapasie (do ok. 34 dni), ale kolejne przerwy nakładałyby się na braki poszczególnych operatorów. Przyczyny 17.09 nie znamy.
8. **Sezonowość i kalendarz.** Ferie i przerwy szkolne (np. jesienne) nie są jeszcze w `config/calendars/`; dni z mniejszą liczbą kursów odetnie bramka anomalii (M3), co zmniejszy liczbę dni ważnych. Zmiana czasu 25.10 wypada w niedzielę (poza dniami roboczymi). Okno kończy się 18.12, więc okres świąteczny do końca roku nie wchodzi do pilotażu.
9. **Trend jakości** (`crossing_rate` na tydzień) jest bliski zera we wszystkich miastach poza Turynem (−0,04/tydz.); nie widać powolnej degradacji.

### Decyzje właściciela po M0 (2026-09-26)

D12: GISCO, przy różnicach preferować mniejszy obszar, Sofia i Lizbona z OSM (ADR-0002). Projekt niekomercyjny, wyniki na CC BY 4.0, wszystkie miasta publikowane z atrybucją źródeł, Turyn pod bramką jakości (ADR-0003; pełne warunki GTT w `docs/licenses.md` §2a). Audyt GTFS-RT wykonany (`docs/licenses.md` §2b). Astro (ADR-0001). Bez pinu `easy-OTP` (ADR-0004). Surowe pozycje są co miesiąc archiwizowane w `easy-GTFS-RT` (`raw-snapshots-*`), dostępne przez `gtfs-dashboard`. Zmiany w innych repo tylko po pytaniu. Reszta: `docs/decisions-needed.md`.

### Metodologia wejścia i plan testów (2026-09-26, po M0)

Analiza `easy-GTFS-RT` i `easy-OTP` (odczyt): tidy to obserwacje bezpośrednie (`collect_stop_crossings`), nie agregat P50/P85, więc wejściem produkcyjnym pozostają tabele tidy z pojedynczych dni (statyka tego dnia), a surowe pozycje służą do testów parametrów zapieczonych w tidy i do przebudowy po zmianie metody. Plan 25 testów (T1-T25, priorytety, reguły decyzyjne zapisane z góry): `docs/10-input-methodology-and-test-plan.md`. **Testy przed M1 zakończone 2026-09-27** (`docs/sensitivity-report.md`, status T1-T26: `docs/10` §7, ocena uruchamiania w chmurze: `docs/10` §8): T1 zaliczony (9 dni-miast), T2/T3 na 6-7 miastach (powtarzalne na drugim dniu), T4-T22, T25 i T26 na 15 miastach (2026-09-01…26), T17 wykonany (W12: źródło statyka), T24 odpada, T21 opisany. Główne wyniki: dni anomalne w pojedynczych dniach (Poznań, Rzym, Kraków) i konieczność kryterium liczby kursów; W3 AM bez stabilnego rankingu; W10 i W11 prawie redundantne (rho -0,92); FA-20, próg 300 s i okno FA-12 mają znaczenie w konkretnych miastach. Rekomendacje R1-R10 czekają na decyzje autora (`docs/decisions-needed.md` §2a). Zakres M1 rozstrzygnięty 2026-09-27 (16 miast, wszystkie dni od 1.09). M1 nie rozpoczęty.

### Przegląd `milestone-reviewer`

**Werdykt: PASS (warunkowy), brak pozycji blokujących.** Recenzent niezależnie przeliczył kluczowe liczby (Łódź, Poznań po filtrze GISCO, dni ważne od 7.09, liczba wersji statyk, poligony) i zgodziły się z raportem. Uwagi i ich rozstrzygnięcie:

| uwaga | rozstrzygnięcie |
|---|---|
| luka 2026-09-17 opisana jako awaria wspólna/telefon, a to hipoteza (8 miast bez tagu, 3 z tagiem bez tidy) | poprawione w `progress.md`, `decisions-needed.md`, `config/city_defects.yaml`: przyczyna nieustalona |
| brak listy miast kwalifikujących się do pilotażu i macierzy miasto × dzień | dodane do raportu: §4 macierz, §5 prognoza kwalifikacji względem `city_gate` (żaden kandydat nie ma jeszcze 20 dni ważnych, więc prognoza) |
| kolumna "brak trip_id" zawsze 0 (nic nie mierzy) | usunięta z raportu; wpis Turynu w `city_defects.yaml` oznaczony jako niepotwierdzony w M0 |
| magiczne liczby w skryptach (`600`, `0.01`, `500`) | przeniesione do `config/metrics.yaml` (`regularity.frequent_headway_s`, sekcja `inventory`) |
| opis odcisku statyki (SHA-256 ogona vs CRC32 z katalogu zip) | poprawiony; zaznaczone, że to zamiennik, a SHA-256 pliku liczy M1 |
| "filtr zmienia o 0,3–6 km/h" | poprawione na 0,0–6,2 km/h |
| Lizbona 09-02 przechodzi bramkę | zastrzeżenie dodane w ustaleniu 2 |
| mianownik udziału linii częstych | opisany w §3 raportu; liczby zaokrąglone |
| komentarz w `cities.yaml` obiecywał pola, których nie ma | poprawiony |
| test regresyjny wymaga sieci przy pierwszym uruchomieniu | brak sieci daje teraz `skip`, nie błąd |
| `bccb17b` dotyczy tylko narzędzi tworzących tidy (w `tools/` są nowsze commity `family_b`) | doprecyzowane w `decisions-needed.md` §4 |
| nie sprawdza wariantu 9-dniowego (17,59) | odłożone do M1/M2 (kryterium M0 dotyczy 2026-09-24) |
