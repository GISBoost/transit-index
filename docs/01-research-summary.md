# 01 · Podsumowanie researchu (stan na 2026-09-26)

Ten dokument zbiera to, co ustaliłem w researchu: jak działa wzorzec (TomTom Traffic Index), co już istnieje w Polsce i na świecie, co masz w ekosystemie GISBoost, jakie decyzje zapadły i czego brakuje. Liczby i twierdzenia mają źródła na końcu. Tam, gdzie czegoś nie potwierdziłem, jest to napisane.

## 1. Zadanie

Odpowiednik TomTom Traffic Index dla transportu publicznego, ale mierzący **jakość funkcjonowania**, nie samą prędkość. Liczony ze zrekonstruowanych danych taboru (GTFS-RT) i rozkładów (GTFS): prędkość i obciążenie szczytu, punktualność, regularność i oferta rozkładowa (pięć wymiarów, `03` §1), mapy z odcinkami między przystankami kolorowanymi według prędkości, rankingi miast osobno dla każdego wymiaru. Poboczny projekt GISBoost, **nie część doktoratu**. Serwis statyczny na GitHub Pages, stack zbliżony do `mapy-analizy`.

## 2. Jak liczy TomTom (wzorzec)

- Ranking miast według dwóch głównych miar: **średni czas przejazdu 10 km** oraz **poziom zatłoczenia** (Congestion Level). Osobno publikowany jest czas stracony w szczycie (przejazd 10 km dwa razy dziennie w dni robocze).
- Congestion Level porównuje czasy przejazdu przy swobodnym ruchu z rzeczywistymi średnimi czasami i wyraża różnicę w procentach. Przykład z metodyki: poziom 40 oznacza, że przejazdy były średnio o 40% dłuższe niż przy swobodnym ruchu.
- Średnia prędkość jest liczona jako suma dystansów podzielona przez sumę czasów (średnia ważona dystansem), z danych pojazdów (FCD).
- Skala: edycja opublikowana 7 stycznia 2025 (14.) obejmowała 500 miast w 62 krajach; edycja z danymi za 2025 rok ukazała się w styczniu 2026. **Cykl roczny, publikacja w styczniu.**
- Ważne rozróżnienie: TomTom mierzy samochody względem swobodnego przepływu, my mierzymy transport publiczny z postojami na przystankach. **Liczby nie są porównywalne i nie wolno ich zestawiać** (patrz `03-metrics-spec.md` §8).

## 3. Co już istnieje (analogi)

| Źródło | Co robi | Czego nie robi |
|---|---|---|
| Puls Gdańska, raport prędkości tramwajów (edycje 2021, 2022, 2023) | Ranking sieci tramwajowych i linii według prędkości komunikacyjnej, osobno szczyt i poza szczytem | Liczy prędkości **rozkładowe**; autorzy piszą, że rzeczywiste mogą być niższe. Tylko tramwaje |
| Jakdojade, raport 2025 (sześć wskaźników, m.in. wskaźnik prędkości = średnia prędkość handlowa) | Porównanie miast, kategorie dużych i małych miast | Brak map odcinków i pełnej metodyki w dostępnym opisie |
| Cal-ITP / Caltrans "Speeds by Stop Segments" | Percentyle prędkości 20/50/80 na odcinkach przystanek–przystanek, całodzienne i szczytowe; odcinki dłuższe niż 1 km dzielone co 1 km; z GTFS-RT VehiclePositions | Jeden dzień na mapę (przechodzą na średnią kroczącą); Kalifornia |
| Swiftly Speed Map | Percentyle 10/90, prędkość swobodna jako 85. percentyl, zmienność | Produkt komercyjny |
| Biuro Kontrolera Nowego Jorku (2025) | Prędkość autobusów 8,17 mph w 2024 r., dane MTA i GTFS-RT | Jedno miasto |
| Transit Costs Project, "Mapping the Speed of Surface Transit" | Rozkładowe prędkości w 32 miastach | Prędkości planowe, nie zmierzone |

**Luka:** nie znalazłem otwartego rankingu miast opartego na *zmierzonych* prędkościach z GTFS-RT dla polskich miast. Wyszukiwanie nie było wyczerpujące, więc sformułowanie "pierwszy w Polsce" trzeba by zweryfikować przed użyciem publicznie.

Wzorce do wykorzystania: Cal-ITP (definicja odcinka, percentyle, podział długich odcinków), Swiftly (prędkość swobodna jako P85), Puls Gdańska (definicja prędkości komunikacyjnej i podział szczyt/poza szczytem).

## 4. Co masz w ekosystemie GISBoost (zweryfikowane 2026-09-26)

- **easy-GTFS-RT** – telefon (Termux) nagrywa VehiclePositions codziennie ok. 06:00–22:00 co 60 s, jeden proces na miasto; po wysłaniu surowych plików workflow buduje realized GTFS (P50/P85) i publikuje release `<miasto>-realized-<data>-phone`. Od 2026-08-03 do release'u dokładany jest `<miasto>_tidy_<data>.csv.gz` (tabela całego feedu). Raw jest kasowany po zbudowaniu. Dane w release'ach nie są własnością projektu (licencje operatorów).
- **easy-OTP / tools/transit_charts** – tabela tidy i 18 gotowych wykresów; D14 to mediana prędkości segment × pasmo, H28–H31 rankingi linii, J39 porównanie miast. Tabela tidy ma **już kolumny segmentów**: `seg_time_s`, `seg_dist_m`, `seg_speed_kmh`, `seg_status`, `from_stop_id`. Szczegóły w `02-data-inventory.md`.
- **easy-OTP / family_a_reconstruction** – rekonstrukcja z filtrami FA-13/14/18/20; licencja GPL-3.0-or-later.
- **GTFS Dashboard** – katalog nagrań (miasto → miesiąc → dzień), statyczna strona.
- **mapy-analizy** – hub map: vanilla JS + Leaflet, jedna analiza = jeden folder, wdrożenie z `main`, wspólny `gisboost-1.css`, GoatCounter, lustro na Cloudflare Pages dla izochron.
- **gisboost-1.css** – wersjonowane tokeny (zasada: nie edytować, nowa nazwa pliku przy zmianie).

## 5. Decyzje i założenia

Potwierdzone przez Michała:
1. Projekt poza doktoratem; serwis na darmowej domenie GitHub Pages, stack zbliżony do `mapy-analizy` (z MapLibre zamiast Leaflet).
2. **Zakres: kilkanaście miast europejskich**, nie tylko Polska. Serwis to "indeks jakości funkcjonowania transportu publicznego" (nie indeks prędkości) z własną tożsamością wizualną, celowo odrębną od GISBoost.
3. **Wygląd i układ stron projektuje Michał w Claude Design; design jest zbudowany i nadrzędny** (`design/`, zaimportowany 2026-09-26). Ta paczka specyfikuje dane, metryki, potok, build i kontrakt techniczny z designem (`06-site-spec.md` §2); przy konflikcie zmienia się dokument, nie design (`06` §9).

Rekomendacje Claude, przyjęte jako punkt wyjścia (lista w `08-risks-and-open-questions.md`):
4. Nie używać nazwy ani wyglądu "Traffic Index" TomTom. Nazwa robocza: **Transit Index** (nazwa z designu; "Indeks jakości transportu publicznego" jako opis).
5. **Model jakości (D11, rozstrzygnięte 2026-09-26):** pięć osobnych wymiarów bez wskaźnika złożonego w v1: prędkość, obciążenie szczytu (kara szczytu), punktualność, regularność, oferta rozkładowa (`03` §1 i §4). Wskaźnik złożony to cel v2 po teście wag.
6. Rankingi osobno dla trybów (tramwaj, autobus z trolejbusami, łącznie pojazdy drogowe); metro i kolej poza rankingiem.
7. **Filtr obszaru miasta jest obowiązkowy** (W0, D12): feedy zawierają linie podmiejskie, które zawyżają prędkości o kilka km/h (`09` F13).
8. Zamiast "spowolnienia względem P85" (arbitralne) używamy **kary szczytu**: porównanie parami tych samych odcinków w szczycie i poza nim (`03` §3).
9. Serwis statyczny budowany własnym workflow GitHub Actions, MapLibre + PMTiles.

## 6. Co zweryfikowano na prawdziwych danych

Paczka została sprawdzona na release'ach z 2026-09-24 (15 miast) i 9 dniach Łodzi: schemat 34 kolumn, semantyka odcinków, strefy czasu, geometria, stabilność kluczy, wpływ filtra obszaru, kalibracja klas prędkości. Pełna lista ustaleń F1–F17, tabela gotowości feedów i komendy do powtórzenia: **`09-validation-on-real-data.md`**. Wartości wzorcowe do testów: `reference/golden_values.json`.

## 7. Ryzyka (skrót; pełna lista w `08-risks-and-open-questions.md`)

- Dane zrekonstruowane, nie zmierzone wprost; luka nierandomowa (pojazd znikający w korku), stąd optymistyczne obciążenie.
- Licencje danych operatorów są różne; wyniki pochodne mogą dziedziczyć atrybucję lub share-alike.
- Relacja z pracodawcą i własność intelektualna: patrz `08` §3 (dokument tylko do użytku prywatnego).
- PMTiles na GitHub Pages: w 2025 zgłoszono sporadyczne błędy zakresów bajtów; testuj i miej plan B (Cloudflare).

## 8. Źródła

- TomTom Traffic Index, metodyka: https://www.tomtom.com/traffic-index/about/
- TomTom, komunikat o edycji 2025 (7 I 2025): https://www.tomtom.com/newsroom/press-releases/general/605041959/tomtom-traffic-index-2025/
- TomTom, edycja z danymi za 2025 (styczeń 2026): https://www.tomtom.com/newsroom/explainers-and-insights/tomtom-traffic-index-2026-headline-numbers/
- Cal-ITP, mapy prędkości: https://github.com/cal-itp/data-analyses/tree/main/ca_transit_speed_maps
- Caltrans, Speeds by Stop Segments: https://gisdata.dot.ca.gov/arcgis/rest/services/CHrailroad/Speeds_by_Stop_Segments/MapServer/info/iteminfo
- Swiftly, Speed Map: https://www.goswift.ly/blog/speed-map-metrics-and-tools-for-analyzing-transit-speeds
- Puls Gdańska: https://pulsgdanska.pl/raporttramwajowy2022 ; omówienie edycji 2023: https://bydgoszczinformuje.pl/tramwaje-w-bydgoszczy-jezdza-z-najwieksza-przecietna-predkoscia-w-naszym-kraju/
- Jakdojade 2025 (TransInfo): https://transinfo.pl/infotrans/transport-publiczny-pod-lupa-jakdojade-ktore-miasta-wygrywaja-w-punktualnosci-a-ktore-w-predkosci/
- NYC Comptroller: https://comptroller.nyc.gov/reports/behind-schedule-how-new-york-citys-bus-system-slow-rolls-riders/
- GitHub Pages, limity: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- PMTiles na GitHub Pages, zgłoszenie #584: https://github.com/protomaps/PMTiles/issues/584
- GSAP za darmo od kwietnia 2025: https://gsap.com/blog/3-13/
- easy-GTFS-RT: https://github.com/GISBoost/easy-GTFS-RT · easy-OTP: https://github.com/GISBoost/easy-OTP · mapy-analizy: https://github.com/GISBoost/mapy-analizy · GTFS Dashboard: https://gisboost.github.io/gtfs-dashboard/
