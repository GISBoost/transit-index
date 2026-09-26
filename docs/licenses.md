# Audyt licencji źródeł danych (M0, 2026-09-26)

**Najważniejsza informacja z audytu: Publikować i poprawnie zatrybutować, np. w stopce strony.**
**Co obejmuje ten audyt.** Dla każdego miasta sprawdzamy dwa źródła: (1) statyczny GTFS (`static_gtfs_url` z `cities.json`) i (2) endpoint GTFS-RT VehiclePositions (adres z konfiguracji nagrywania). Dla każdego pytamy: kto jest autorem danych, jaka licencja lub regulamin obowiązuje, czy dopuszcza przetwarzanie i publikację pochodnych (rankingi, mapy odcinków), czy wymaga atrybucji, czy zabrania użycia komercyjnego, czy narzuca inne ograniczenia (np. "tylko jako wsparcie podróży", klucz API, limity zapytań). Wynik to tabela z poziomem pewności i lista miast, dla których publikacja wymaga potwierdzenia albo zgody operatora. Audyt nie zastępuje porady prawnej.

**Status: wstępny.** Ustalenia pochodzą z wyszukiwania stron portali i operatorów w dniu audytu, nie z lektury pełnych regulaminów. Kolumna "pewność" mówi, co wolno przyjąć: **wysoka** = licencja wprost na stronie źródła, **średnia** = licencja wymieniona w katalogu (Mobility Database, dane.gov.pl, transit.land) albo na stronie pośredniej, **brak** = nie znaleziono. Przed publikacją każdy wiersz o pewności innej niż wysoka wymaga potwierdzenia u źródła (lista w §5). Nic tu nie jest poradą prawną.

## 1. Zakres

- Audytowane: statyczny GTFS z `config/cities.json` w `easy-GTFS-RT` (`static_gtfs_url`), dla miast z `config/cities.yaml` w poziomach `candidate` i `watch`.
- **GTFS-RT:** audytowane w drugim kroku M0 (§2b), z ograniczeniem opisanym tam.
- **Linki do statyk operatorów są w `easy-GTFS-RT/config/cities.json`** (`static_gtfs_url`, część miast ma też `timezone`). Adresy endpointów RT nie są w `cities.json` (siedzą na telefonie); część jest w `easy-OTP/docs/handoffs/eu_vehicle_positions_feeds.md`. Warunki RT bywają inne niż statyki.
- `easy-GTFS-RT` sam zastrzega: licencja repo nie obejmuje danych w release'ach; statyka jest kopią feedu operatora, a "realized" i nasze tidy to jego pochodna, więc obowiązki atrybucji i share-alike przechodzą dalej.

## 2. Wyniki per źródło

| miasto | źródło statyki | licencja / warunki (wg wyszukiwania) | obowiązki | pewność |
|---|---|---|---|---|
| Łódź | otwarte.miasto.lodz.pl | portal danych otwartych Łodzi; licencja "pozwala na użycie, także komercyjne, z podaniem źródła" (brak nazwy licencji w wyniku) | atrybucja | średnia |
| Warszawa | **mkuran.pl/gtfs/warsaw.zip** (pośrednik) | warunki użytkowania ZTM Warszawa + **ODbL dla kształtów tras autobusowych** (z OSM); plik `attributions.txt` | ujawnić wszystkie atrybucje z `attributions.txt` (ZTM, autor feedu, OSM); **share-alike ODbL dla pochodnych baz kształtów** | średnia |
| Kraków | gtfs.ztp.krakow.pl | licencji GTFS nie znaleziono (strona ZTP wymienia dane otwarte i ArcGIS Hub) | do ustalenia | brak |
| Gdańsk | ckan.multimediagdansk.pl | CC BY 4.0 | atrybucja | średnia |
| Poznań | ztm.poznan.pl (Dla deweloperów) | warunki ZTM: podać źródło, datę ostatniej aktualizacji **i fakt przetworzenia danych**; użycie do badań i aplikacji wspierających transport publiczny | 3 informacje na stronie; sprawdzić, czy "wspieranie transportu" obejmuje ranking | wysoka |
| Szczecin | zditm.szczecin.pl | **CC0 1.0** | brak (cytowanie mile widziane: ZDiTM Szczecin) | wysoka |
| Praga | data.pid.cz (PID) | CC BY (wariant do potwierdzenia) | atrybucja | średnia |
| Rzym | romamobilita.it | wymagana akceptacja licencji użytkowania; treść nieustalona | do ustalenia | brak |
| Turyn | gtt.to.it | licencja GTT: **użycie niekomercyjne** (pełny tekst w §2a); ten sam zbiór ma CC BY 4.0 w katalogu AperTO (sprzeczność, strona GTT jest bardziej restrykcyjna) | atrybucja "Data source: GTT S.p.A. – Gruppo Torinese Trasporti" + link https://www.gtt.to.it; zakaz użycia komercyjnego, w tym reklam, bez pisemnej zgody GTT | wysoka (strona GTT) |
| Wilno | stops.lt | zobowiązanie do utrzymywania aktualności rozkładów przy użyciu; nazwy licencji nie znaleziono | do ustalenia | brak |
| Sofia | gtfs.sofiatraffic.bg | CC BY 4.0 (BGNAP) | atrybucja | średnia |
| Bukareszt | gtfs.tpbi.ro | licencji nie znaleziono | do ustalenia | brak |
| Lizbona | gateway.carris.pt | licencji nie znaleziono (pokrewny zbiór na dados.gov.pt: "nie określono") | do ustalenia | brak |
| Zagrzeb | zet.hr | "Otvorena dozvola - Republika Hrvatska" (data.gov.hr) | atrybucja wg licencji | średnia |
| Lublana | data.lpp.si | licencji nie znaleziono | do ustalenia | brak |
| Nikozja | motionbuscard.org.cy | licencji nie znaleziono; źródło formalne: Cyprus NAP (traffic4cyprus.org.cy) | do ustalenia | brak |
| Rzeszów | mpkrzeszow.pl | warunki wykorzystania danych sektora publicznego miasta Rzeszowa | podać źródło, link, czas pobrania i fakt przetworzenia | średnia |
| Kielce | ztm.kielce.pl | warunki miasta Kielce | podać źródło, czas pobrania, zastrzeżenie o braku odpowiedzialności miasta za przetworzenie | średnia |
| Lublin, Radom, Rybnik, Elbląg, Przemyśl, Suwałki | **cdn.zbiorkom.live** (pośrednik) | licencja zależy od operatora źródłowego; dla Radomia MZDiK podaje CC0 1.0 (wg wyszukiwania), dla pozostałych nie ustalono | ustalić źródło pierwotne każdego miasta | brak |
| GZM | otwartedane.metropoliagzm.pl (CKAN) | CC BY (zbiór "wersja rozszerzona") | atrybucja; metropolia poza rankingiem miast (D8) | średnia |
| Boston, Brisbane | poza zakresem (D1) | nie audytowane | — | — |

## 2a. Turyn: pełne warunki licencji GTT (strona `gtt_gtfs_license.html`, sprawdzone 2026-09-26)

Tekst oryginalny (angielski) w pięciu punktach:

1. **Dozwolone użycie:** "The GTFS dataset is released for non-commercial use only. This includes purposes such as academic research, educational activities, civic tech projects, and any initiative not aimed at generating commercial gain."
2. **Atrybucja:** "Any use or redistribution of the data must clearly acknowledge the source as follows: Data source: GTT S.p.A. – Gruppo Torinese Trasporti. Include a link to: https://www.gtt.to.it"
3. **Brak gwarancji:** dane "as is", bez gwarancji kompletności, wiarygodności i dostępności; użytkownik ponosi ryzyko.
4. **Zakaz użycia komercyjnego:** "The data may not be used for commercial purposes, including but not limited to resale, paid services, or advertising-based applications, without prior written authorization from GTT S.p.A."
5. **Dostępność:** GTT może zmienić lub wstrzymać dostęp do danych w każdej chwili bez uprzedzenia.

Strona nie podaje daty wersji ani kontaktu, i nie ma osobnego zapisu o redystrybucji. **Decyzja właściciela (2026-09-26):** Wyniki na licencji CC BY 4.0

## 2b. GTFS-RT VehiclePositions (drugi krok M0)

**Ograniczenie audytu:** aktualne adresy endpointów siedzą w plikach `cities/<miasto>.env` na telefonie nagrywającym i nie są w żadnym repo. Adresy poniżej pochodzą z dokumentów `easy-OTP` (`docs/handoffs/eu_vehicle_positions_feeds.md`, katalog MobilityData z 2026-07-15 i notatki). Dla Zagrzebia, Lublany, Nikozji, Rzeszowa i Kielc adresu RT w dokumentach nie znalazłem: tam ustalenia dotyczą tylko portalu operatora. **Aby zamknąć audyt, wystarczy jedno polecenie na telefonie** (bez tokenów): `grep -h VEHICLE_POSITIONS_URL ~/easy-gtfs-rt-termux/cities/*.env` (uwaga: część adresów może zawierać klucze API, wtedy zakryj klucz).

| miasto | endpoint RT (źródło adresu) | warunki RT (wg wyszukiwania i stron operatorów) | pewność |
|---|---|---|---|
| Łódź | `otwarte.miasto.lodz.pl` (`vehicle_positions.bin`; wydawca: Urząd Miasta Łodzi) | strona zbioru nie podaje nazwy licencji ani atrybucji | brak |
| Warszawa | `mkuran.pl/gtfs/warsaw/vehicles.pb` (pośrednik nad API ZTM; oficjalne API wymaga bezpłatnej rejestracji i klucza) | warunki ZTM: podać źródło, czas wytworzenia i pozyskania oraz fakt przetworzenia | średnia |
| Kraków | `gtfs.ztp.krakow.pl/VehiclePositions.pb` | nie znaleziono warunków | brak |
| Gdańsk | `ckan.multimediagdansk.pl` (zbiór "tristar") | CC BY 4.0 | średnia |
| Poznań | `ztm.poznan.pl/otwarte-dane/gtfs-rt/` (publiczny, bez klucza) | strona RT nie podaje warunków; przyjmujemy warunki statyki (źródło, data aktualizacji, informacja o przetworzeniu), niepotwierdzone | brak |
| Szczecin | `zditm.szczecin.pl` (GTFS i RT razem) | CC0 1.0 | średnia |
| Praga | `api.golemio.cz/v2/vehiclepositions/gtfsrt/...` | dokumentacji warunków nie udało się odczytać; historycznie token | brak |
| **Rzym** | `romamobilita.it/.../rome_rtgtfs_vehicle_positions_feed.pb` | **dane "esclusivamente a titolo di supporto al viaggio" (wyłącznie jako wsparcie podróży); przedstawienie ich w formie zagregowanej i przetworzonej "potrebbe risultare fuorviante"** | wysoka (strona operatora) |
| Turyn | `percorsieorari.gtt.to.it/das_gtfsrt/vehicle_position.aspx` | AperTO: CC BY 4.0 dla RT; strona GTT dla GTFS: niekomercyjnie (§2a) | średnia |
| Wilno | `stops.lt/vilnius/vehicle_positions.pb` | nie znaleziono warunków | brak |
| Sofia | `gtfs.sofiatraffic.bg/api/v1/vehicle-positions` | CC BY 4.0 (portal urbandata.sofia.bg) | średnia |
| Bukareszt | `gtfs.tpbi.ro/api/gtfs-rt/vehiclePositions` | nie znaleziono warunków | brak |
| Lizbona | `gateway.carris.pt/.../realtime/vehiclepositions` | nie znaleziono warunków | brak |
| Zagrzeb | brak adresu w dokumentach | wg Mobility Database dane ZET (statyczne i RT) na "Otwartej licencji Republiki Chorwacji" | średnia |
| Lublana, Nikozja | brak adresu w dokumentach | nie sprawdzano RT | brak |
| GZM | `gtfsrt.transportgzm.pl:5443/gtfsrt/gzm/vehiclePositions` | CC BY 4.0 (portal GZM) | średnia |
| Lublin, Radom, Rybnik, Elbląg, Przemyśl, Suwałki | `cdn.zbiorkom.live/gtfs-rt/<miasto>.pb` (agregator) | strona CDN nie podaje żadnych warunków ani źródeł | brak |
| Rzeszów, Kielce | brak adresu w dokumentach | nie sprawdzano RT | brak |

**Najważniejsze z audytu RT:**
Brak zagrożeń. Publikować wszystko tylko poprawnie zatrybutować źródło danych.

## 3. Wnioski i ryzyka

1. **Warszawa: share-alike ODbL.** Kształty autobusowe pochodzą z OSM (ODbL). Odcinki na mapie zbudowane z tych kształtów to baza pochodna; pliki geometrii dla Warszawy prawdopodobnie na ODbL z atrybucją OSM. Rekomendacja: atrybucja OSM w każdym pliku geometrii, pliki geometrii na licencji zgodnej z ODbL (lub dla Warszawy osobno).
2. **Pośrednicy (mkuran.pl, zbiorkom.live)** nie są autorami danych. Licencja obowiązuje ze źródła pierwotnego, a pośrednik może dokładać własne warunki. Dla miast ze zbiorkom.live nie znamy źródła pierwotnego ani warunków RT. Rekomendacja: publikować.
3. **Brak licencji nie znaczy zgody.** Siedem miast kandydujących nie ma znalezionej licencji statyki (Kraków, Rzym, Wilno, Bukareszt, Lizbona, Lublana, Nikozja), a dla RT braków jest więcej (§2b).
4. **Atrybucja i informacja o przetworzeniu** to wspólny mianownik. Wystarczy strona `/dane/` z listą źródeł per miasto, datą pobrania i zdaniem "dane przetworzone przez Transit Index" oraz stopka w plikach do pobrania. OSM: "(c) OpenStreetMap contributors" przy Warszawie oraz przy poligonach Sofii i Lizbony.
5. **L0 nie jest publiczne.** Tabela obserwacji zawiera `stop_id`, `route_id`, `trip_id` operatora. Publikujemy agregaty (rankingi, komórki odcinek × pasmo), nie L0. Repo z L0 w release'ach ma być prywatne do czasu publikacji.

## 4. Decyzje (stan 2026-09-26)

Rozstrzygnięte przez właściciela (2026-09-26, ADR-0003):
- **Projekt jest niekomercyjny**: Turyn dopuszczony pod bramką jakości (§2a).
- **Wyniki na licencji CC BY 4.0** (D7).
- **Wszystkie miasta mogą być publikowane** pod warunkiem poprawnej atrybucji źródeł (per miasto, na stronie `/dane/`, w plikach do pobrania i w manifeście edycji).
- Audyt RT wykonany (§2b); właściciel ocenia, że nie wykazał zagrożeń dla publikacji.

Nadal otwarte (przed publikacją, nie blokują M1–M6):
- **Pliki geometrii dla Warszawy (ODbL, share-alike):** wyniki są na CC BY 4.0, ale kształty autobusowe pochodzą z OSM (ODbL). Pliki z tymi geometriami (`segments.geojson.gz`, GeoPackage, PMTiles) wymagają atrybucji OSM, a przy share-alike prawdopodobnie licencji ODbL dla samej bazy geometrii. Decyzja: czy tak je oznaczyć (rekomendacja: tak, jednym zdaniem na stronie `/dane/`).
- **Sprawdzenie zdania o Rzymie i Turynie:** dla porządku zapisano tu dosłowne warunki (Rzym RT: "wyłącznie jako wsparcie podróży"; GTT: użycie niekomercyjne). Właściciel zdecydował o publikacji wszystkich miast z atrybucją; zapis pozostaje jako fakt, nie jako blokada.

## 5. Do zrobienia przed publikacją

- [ ] Otworzyć stronę licencji każdego źródła z pewnością innej niż wysoka i zapisać dosłowną nazwę licencji oraz wersję.
- [ ] (opcjonalnie, dobra praktyka) Poinformować operatorów bez znalezionej licencji (Kraków, Rzym, Wilno, Bukareszt, Lizbona, Lublana, Nikozja, Łódź RT, Praga RT) o publikacji; przegląd operatorów i tak jest przewidziany w `docs/05` §5.
- [ ] Ustalić źródła pierwotne dla miast ze zbiorkom.live.
- [ ] Zdobyć listę `VEHICLE_POSITIONS_URL` z telefonu i domknąć §2b (Zagrzeb, Lublana, Nikozja, Rzeszów, Kielce).
- [ ] Sprawdzić licencje: Hanken Grotesk, Archivo Narrow (OFL), Material Symbols (Apache 2.0), GISCO (otwarta licencja Eurostat), OSM (ODbL), GSAP (bezpłatna od 2025), MapLibre (BSD).

## 6. Źródła (sprawdzone 2026-09-26)

- PID: https://pid.cz/en/opendata/
- Mkuran (Warszawa): https://mkuran.pl/gtfs/
- ZTM Gdańsk: https://ckan.multimediagdansk.pl/dataset/tristar
- ZTM Poznań: https://www.ztm.poznan.pl/otwarte-dane/dla-deweloperow/
- ZDiTM Szczecin: https://www.zditm.szczecin.pl/en/zditm/for-developers/gtfs
- GTT (Turyn): https://www.gtt.to.it/gtt_gtfs_license.html
- Sofia Traffic: https://www.sofiatraffic.bg/en/info-center/gtfs-danni
- ZET (Zagrzeb): https://www.zet.hr/odredbe/datoteke-u-gtfs-formatu/669
- Rzym: https://romamobilita.it/sistemi-e-tecnologie/open-data/
- Łódź: https://otwarte.miasto.lodz.pl/
- GZM: https://otwartedane.metropoliagzm.pl/dataset/rozklady-jazdy-i-lokalizacja-przystankow-gtfs-wersja-rozszerzona
- ZTM Rzeszów: https://www.mpkrzeszow.pl/otwartedane/
- zbiorkom.live: https://cdn.zbiorkom.live/
- easy-GTFS-RT, sekcja "Data and attribution": `easy-GTFS-RT/README.md`
- GTT, pełna licencja: https://www.gtt.to.it/gtt_gtfs_license.html
- AperTO (GTT RT): https://aperto.comune.torino.it/dataset/feed-gtfs-real-time-trasporti-gtt
- Roma Servizi per la Mobilità, warunki użycia RT: https://romamobilita.it/sistemi-e-tecnologie/open-data/
- ZTM Poznań GTFS-RT: https://www.ztm.poznan.pl/otwarte-dane/gtfs-rt/
- Łódź, transport: https://otwarte.miasto.lodz.pl/transport_komunikacja/
- Otwarte Dane Transportowe: https://odt.org.pl/en
- easy-OTP, katalog feedów RT: `easy-OTP/docs/handoffs/eu_vehicle_positions_feeds.md`
