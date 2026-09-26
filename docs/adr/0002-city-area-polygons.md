# ADR-0002: Źródło poligonów miast (filtr obszaru W0)

Status: przyjęta 2026-09-26 (właściciel: GISBoost). Dotyczy D12.

## Kontekst
Odcinek liczy się tylko, gdy oba przystanki leżą w poligonie miasta (`docs/03` §2.1). M0 porównał Eurostat GISCO Urban Audit 2024 z granicami OSM (Nominatim) dla 23 miast (`docs/data-inventory.generated.md` §6-7). W 19 miastach obszary zgadzają się (IoU >= 0,97) i wyniki są praktycznie te same. Różnice: Sofia (GISCO 1342 km2 = gmina stołeczna, OSM 454 km2 = miasto), Lizbona (637 vs 87 km2), Nikozja (OSM dał cały dystrykt 1928 km2 wobec GISCO 220 km2), Gdańsk (OSM zawiera wody morskie, 682 vs 262 km2).

## Decyzja
Domyślnie **GISCO** (jednolita, wersjonowana definicja). Gdy źródła różnią się istotnie, **preferujemy źródło dające mniejszy obszar** (rdzeń miejski), o ile to poprawny administracyjny poligon miasta. Wyjątki (`config/areas/sources.yaml`): **Sofia i Lizbona z OSM** (relacje 4283101 i 5400890). Nikozja i Gdańsk zostają na GISCO (OSM tam jest większy albo błędny). Przemyśl ma tylko OSM, GZM (metropolia, D8) bez poligonu.

## Konsekwencje
Wersja źródeł trafia do manifestu edycji. OSM wymaga atrybucji "(c) OpenStreetMap contributors" (ODbL) przy Sofii i Lizbonie. Mniejszy obszar obcina więcej obserwacji (Sofia 88% zamiast 99,6%, Lizbona 93,5% zamiast 100%), co jest zamierzone. Zmiana źródła dla miasta wymaga nowego ADR i nowej `method_version`.
