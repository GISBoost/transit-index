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
7. **`easy-OTP` w workflow bez `ref`** (checkout `main`). Semantyka tidy jednolita od 2026-08-09; ostatni commit narzędzi `bccb17b` (2026-09-04, `perf`). Rekomendacja pinu w `docs/decisions-needed.md` §4.
8. **Licencje (statyka i RT, `docs/licenses.md`):** Turyn tylko niekomercyjnie (projekt jest niekomercyjny, więc dopuszczony pod bramką), **Rzym: RT "wyłącznie jako wsparcie podróży", publikacja po zgodzie operatora**, Warszawa ODbL share-alike dla kształtów, 7 miast bez znalezionej licencji statyki, miasta ze zbiorkom.live bez warunków. Lista adresów RT z telefonu jeszcze potrzebna dla pełnego domknięcia.
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

### Decyzje właściciela po M0 (2026-09-26)

D12: GISCO, przy różnicach preferować mniejszy obszar, Sofia i Lizbona z OSM (ADR-0002). Projekt niekomercyjny, Turyn pod bramką jakości (ADR-0003; pełne warunki GTT w `docs/licenses.md` §2a). Audyt GTFS-RT wykonany (`docs/licenses.md` §2b). Astro (ADR-0001). Zmiany w innych repo tylko po pytaniu. Reszta: `docs/decisions-needed.md`.

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
