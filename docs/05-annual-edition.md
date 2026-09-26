# 05 · Edycja roczna

Wzorzec: TomTom publikuje Traffic Index raz w roku, w styczniu (7 I 2025, styczeń 2026). Dla transportu publicznego dochodzi problem sezonowości (wakacje, ferie, przerwy świąteczne), więc **okno edycji jest zdefiniowane jawnie**, a pierwsza edycja jest pilotażowa. Daty poniżej są **orientacyjne** i do potwierdzenia. Zakres: kilkanaście miast europejskich, więc kalendarz dni jest **per kraj**.

## 1. Rodzaje edycji

| edycja | okno danych | publikacja | status |
|---|---|---|---|
| `2026-pilot` | dni robocze **2026-09-01 – 2026-12-18** (okres szkolny, przed przerwą świąteczną) | styczeń 2027 | pilotaż: mało miast, oznaczenie "pilotaż", pełna metodyka |
| `2027` | dni robocze roku kalendarzowego 2027 poza świętami i przerwami | styczeń 2028 | pierwsza edycja pełna |
| `2027.1` … | erraty | w razie potrzeby | tylko poprawki błędów faktycznych |

Dane sprzed 2026-09-01 (lipiec–sierpień) to wakacje: oferta rzadsza, kalibracje `family_a` też z tego okresu. Nie wchodzą do pilotażu (mogą służyć do testów pipeline'u).

## 1a. Kalendarz dni roboczych (wiele krajów)

- Dni robocze i święta: biblioteka `holidays` (kod kraju, a dla Hiszpanii/Niemiec/Włoch regiony, jeśli miasto tego wymaga), plik `config/calendars/<miasto>.yaml` dodaje ferie szkolne i lokalne wyłączenia.
- Pasma godzinowe są w **czasie lokalnym miasta** (`obs_local`), więc okno edycji jest wspólne w datach, a nie w godzinach UTC; nie ma przeliczania stref (`09` F6).
- Miasto jest w rankingu, jeśli ma dość dni roboczych **po odjęciu własnych świąt i ferii** (`n_days`, bramka `03` §6). Różne kalendarze nie są błędem, ale uwaga na stronie metodyki: okno porównywalne datami, nie liczbą dni.
- Dni anomalne (mediana prędkości miasta poza pasmem wokół mediany dni, luka nagrania, strajk) wykrywane statystycznie i wyłączane z powodem w manifeście (`03` §7).

## 2. Harmonogram pilotażu (orientacyjny)

| kiedy | co |
|---|---|
| do połowy października 2026 | M0–M3: inwentarz, ingest, metryki, bramka (na danych od września) |
| do 15 listopada | **zamrożenie definicji** `ti-1.0`: tag repo + tag `easy-OTP` używanego do tidy; od tej chwili zmiany tylko przez `ti-1.1` |
| do końca listopada | M4–M6: kafle, serwis, ruch |
| 2026-12-18 | koniec okna danych |
| do 5 stycznia 2027 | przebieg edycji, raport jakości, przegląd wewnętrzny (M7) |
| 5–18 stycznia | **przegląd operatorów** pod embargiem (patrz niżej) |
| ostatni tydzień stycznia | publikacja: strona, dane, metodyka, DOI, komunikacja |

Zamrożenie definicji następuje *przed* przebiegiem edycji na pełnym oknie, żeby nie dopasowywać metody do wyniku.

## 3. Cykl życia edycji

1. **Definicja edycji** (`config/editions/<id>.yaml`): okno, lista miast kandydatów, kalendarze wyłączeń, `method_version`.
2. **Przebieg**: `ti aggregate/metrics/gate` → pliki w `data/editions/<id>/`.
3. **Manifest** (`schemas/edition_manifest.schema.json`): `edition`, `method_version`, okno, `ti_commit`, **`easy_otp_ref` przypięty tag (nie `main`)**, skrót konfiguracji, dla każdego miasta status, liczba dni i **skrót sumy kontrolnej plików wejściowych**. Pozwala odtworzyć wynik.
4. **Status** manifestu: `draft` → `operator_review` → `published` → (`superseded`).
5. **Publikacja niezmienna**: `/edycje/<id>/` nigdy nie zmienia liczb po publikacji. Poprawka to nowa edycja `<id>.1` z wpisem w `errata` i widocznym dziennikiem zmian.

## 4. Porównania rok do roku

`delta_vs_previous_edition` wolno pokazać tylko gdy: obie edycje mają ten sam major `method_version`, miasto przeszło bramkę w obu, a zmiana pokrycia sieci jest mała (próg w konfiguracji). W przeciwnym razie pole jest `null`, a strona mówi dlaczego. Pilotaż jesienny i edycja całoroczna **nie są porównywalne** (inna sezonowość).

## 5. Prawo do odpowiedzi operatorów

Przed publikacją wyślij każdemu operatorowi/organizatorowi wyniki jego miasta (embargo ok. dwóch tygodni). Zapisz odpowiedzi w `docs/operator-feedback/`. Zmiany wolno wprowadzić tylko przy **błędzie faktycznym w danych** (np. feed, wadliwe kształty, błędny tryb), nie z powodu niekorzystnego wyniku. Miasto ze sporną jakością danych dostaje status `limited` lub `excluded` z powodem `operator_dispute`. Jeśli operator nie odpowie, opublikuj z notatką.

## 6. Cytowanie i trwałość

- Wydanie GitHub na każdą edycję, integracja z Zenodo (DOI w manifeście, pole `doi`).
- Zalecany zapis cytowania w stopce edycji.
- Dane pochodne: atrybucja OpenStreetMap i operatorów (patrz `docs/licenses.md` z M0; licencje źródeł są różne, README easy-GTFS-RT ostrzega, że część wymaga atrybucji, a niektóre share-alike).

## 7. Komunikacja (szkic)

- Strona edycji + raport skrócony (jedna strona metodyki, ograniczenia na górze, nie w stopce).
- Posty LinkedIn/YouTube GISBoost; użyj skilla stylu postów Michała. Materiały wizualne (karty miast, nagranie mapy) wg projektu z Claude Design; dane do nich z `summary.json`.
- Zakaz nadpisywania wniosków ("najgorsze miasto") bez `n`, przedziału i ograniczeń.

## 8. Kryteria gotowości do publikacji (lista kontrolna)

- [ ] Definicja zamrożona i otagowana; `easy_otp_ref` przypięty.
- [ ] Każde miasto w rankingu ma status, `n_days`, `n_obs`, pokrycie sieci; wykluczone mają powód.
- [ ] Test czułości opublikowany na stronie metodyki.
- [ ] Przegląd operatorów zakończony, odpowiedzi zapisane.
- [ ] Licencje danych sprawdzone, atrybucje w stopce i w plikach do pobrania.
- [ ] Dostępność (kontrast w obu motywach, klawiatura na mapie, widok tabelaryczny) i budżet wydajności spełnione.
- [ ] Poligony obszaru miast (W0) zatwierdzone; wersja źródła granic w manifeście.
- [ ] Sprawdzenie polityki pracodawcy i uzgodnienie wizerunku (patrz `08`).
- [ ] Zenodo/DOI, manifest, sumy kontrolne.
