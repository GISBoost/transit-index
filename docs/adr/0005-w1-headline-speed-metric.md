# ADR-0005: Metryka nagłówkowa wymiaru Prędkość (W1)

Status: przyjęta 2026-09-27 (właściciel: GISBoost). Dotyczy D2.

## Kontekst

`docs/03` §3 definiuje W1 jako `v = 3,6 · ΣL/ΣT` (suma dystansów przez sumę czasów, ważona długością z definicji), z zastrzeżeniem, że to inna statystyka niż mediana i wymaga testu czułości (§9). Test T13 na próbce sprzed M1 (5 miast PL, 1 dzień) dał ρ = 1,0 dla wariantu łącznego i autobusów wobec mediany ważonej długością, ale **ρ = 0,7 dla tramwajów** (Kraków/Poznań/Warszawa zamieniały się miejscami) — oznaczone jako sygnał ostrzegawczy wymagający powtórzenia na wielu dniach i po filtrze obszaru (`docs/03` §9, reguła decyzyjna: ρ < 0,9 ⇒ publikuj oba warianty albo przejdź na wariant odporny).

## Test na pełnym oknie (M2, 2026-09-27)

`scripts/m2_sensitivity.py` na 16 miastach kandydujących, 14-19 dni roboczych (bez świąt) na miasto, po filtrze obszaru W0 (`reports/m2/sensitivity_by_city.csv`):

| wariant | ρ (Spearman, ranking miast) |
|---|---|
| łącznie (bus+tram): `ΣL/ΣT` vs mediana ważona długością | **0,974** |
| autobusy: `ΣL/ΣT` vs mediana ważona długością | **0,974** |
| tramwaje: `ΣL/ΣT` vs mediana ważona długością | **0,986** |

Wszystkie warianty ≥ 0,9. Ostrzeżenie z próbki 1-dniowej dla tramwajów (ρ = 0,7) nie potwierdziło się na pełnym oknie — było artefaktem małej próby (5 miast, 1 dzień), nie realnym ryzykiem rankingu.

## Decyzja

**W1 = ΣL/ΣT** (`commercial_speed_kmh` w `reference/metrics_reference.py`) zostaje jedyną metryką nagłówkową wymiaru Prędkość, dla wszystkich grup trybów (autobus, tramwaj, łącznie), bez publikowania wariantu odpornego równolegle. Kod produkcyjny (`ti/metrics.py`) już to implementuje od M1 (test wzorcowy Łódź).

## Konsekwencje

`docs/03` §9 i `docs/08` D2 aktualizowane: status tramwajów zmienia się z "ostrzeżenie, wymaga powtórzenia" na "potwierdzone na pełnym oknie". Mediana ważona długością (`length_weighted_median_speed_kmh`) zostaje w kodzie referencyjnym jako test czułości do powtórzenia po ≥ 40 dniach (T7/T13 w listopadzie), nie jako alternatywna publikowana liczba.
