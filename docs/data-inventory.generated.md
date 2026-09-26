# Inwentarz danych na oknie 2026-09-01 … 2026-09-25 (wygenerowane)

Wygenerowane przez `scripts/m0_inventory.py` i `scripts/m0_report.py`. Nie edytuj ręcznie. Surowe wyniki: `reports/m0/`.

Metoda: (1) `heads`: dla każdej pary miasto-dzień zapytanie zakresowe o rozmiar tidy i statyki (bez pobierania) oraz odcisk zawartości statyki (SHA-256 z listy nazw, CRC32 i rozmiarów członków zip odczytanej z katalogu centralnego; tani zamiennik, **nie** SHA-256 pliku wymagany do deduplikacji w M1); (2) `stats`: dla miast `candidate` i dni roboczych pobranie tidy strumieniowo, statystyki, skasowanie pliku. Definicja dnia ważnego: `config/metrics.yaml` → `day_gate` (`crossing_rate ≥ 0.6`, udział `ok ≥ 0.55`, wiarygodność `service_date ≥ 0.9`, pokrycie godzin każdego pasma ≥ 0.9, gdzie godzina jest pokryta, jeśli ma ≥ 1% wierszy `ok`; to przybliżenie), bez świąt państwowych z `config/calendars/`.

## Jak czytać te tabele

**Pojęcia.** *Obserwacja* = jeden przejazd kursu przez parę przystanków (wiersz tidy ze `seg_status = ok`). *Dzień ważny* = dzień, którego dane wolno użyć do indeksu. *Bramka* = zestaw progów jakości; progi żyją w `config/metrics.yaml` (ta sekcja czyta je stamtąd) i są **propozycjami** wyprowadzonymi z progów `family_a` (FA-15, FA-16) oraz z obserwowanych rozkładów w 15 miastach; kalibracja w M3.

**Trzy poziomy bramki (od najdrobniejszego):**

| poziom | co ocenia | próg |
|---|---|---|
| dzień (`day_gate`) | czy dzień miasta jest użyteczny | `crossing_rate` ≥ 0.6; udział `ok` ≥ 0.55; wiarygodność daty serwisowej ≥ 0.9; każde pasmo pokryte nagraniem w ≥ 0.9 godzin; liczba kursów na godzinę ≥ 0.7 mediany dnia tego samego typu (dni anomalne, liczone w M3) |
| odcinek × pasmo (`segment_min`) | czy odcinek ma dość obserwacji, by go kolorować | `ok`: ≥ 10 obserwacji z ≥ 5 dni; `thin` (mała próba, szrafowane): ≥ 3 obserwacji; poniżej: `none` (szary) |
| miasto (`city_gate`) | czy miasto trafia do rankingu | `ranked`: ≥ 40 dni ważnych i pokrycie sieci ≥ 0.6; `limited` (na liście z adnotacją): ≥ 20 dni i pokrycie ≥ 0.4; poniżej: `excluded`. Tryb (autobus, tramwaj) wchodzi, gdy ma ≥ 3 linii i ≥ 50 odcinków. Rejestr wad (`config/city_defects.yaml`) ma pierwszeństwo |

Inne progi metryk: kara szczytu liczona tylko dla odcinków z ≥ 10 obserwacjami w paśmie i w odniesieniu; najwolniejsze odcinki: długość ≥ 100 m; klasy prędkości `[15, 20, 25, 30]` km/h (5 klas).

**Co znaczą kolumny:**
- `crossing_rate`: jaki odsetek rozkładowych przystanków kursów miał zaobserwowany przejazd (`obs_time` niepuste). To miara **pokrycia obserwacjami**: pojazdy, które zniknęły z feedu albo nie zostały dopasowane, obniżają ją. Typowo mediana miasta 0,78–0,89 (2026-09); poniżej 0.6 dzień odpada.
- udział `ok`: jaki odsetek wierszy przeszedł filtry `family_a` (nie jest pierwszą parą przystanków, nie jest postojem, prędkość wiarygodna, para pingów nie za daleko). Typowo mediana miasta 0,62–0,84 (2026-09); poniżej 0.55 dzień odpada.
- pokrycie pasm: pasma to `am_peak` 7–8, `midday` 10–13, `pm_peak` 15–17, `evening` 19–21. Godzina liczy się jako nagrana, jeśli ma ≥ 1% wierszy `ok` (przybliżenie); 1.00 = wszystkie godziny pasma, 0.5 = połowa. Dzień odpada, jeśli którekolwiek pasmo ma poniżej 0.9. Stąd wczesne dni września (nagranie startowało w ciągu dnia).
- statyka "liczba różnych wersji": ile różnych zawartości pliku statycznego GTFS pojawiło się w oknie. Jeśli statyka zmienia się co dzień, do każdego dnia trzeba użyć statyki z tego samego dnia.

**Jak czytać sekcje raportu:**
1. *Pokrycie*: czy plik istnieje. `dni robocze bez tidy` to dni bez danych (luki). Nie mówi nic o jakości.
2. *Jakość dni*: czy istniejące dni przechodzą bramkę dnia. `dni ważne` = dni z danymi, które przeszły wszystkie progi i nie są świętem. Poniżej lista dni odrzuconych z wartościami.
3. *Gotowość pod W10–W12*: czy w danych są kolumny potrzebne dla punktualności i regularności (`delay_s`, `headway_s`) i ile jest wierszy linii częstych. To wykonalność, nie wynik.
4. *Macierz miasto × dzień*: to samo co 2, w widoku dziennym.
5. *Prognoza kwalifikacji*: jeśli udział dni ważnych od pełnych dni nagrania utrzyma się do końca okna, ile dni ważnych będzie i jaki status miasta z `city_gate` z tego wyjdzie (bez pokrycia sieci, które liczy M2).
6. *Poligony*: porównanie źródeł granic miast. `iou` = część wspólna / suma (1,0 = ten sam obszar); `gisco_only_share` i `osm_only_share` = jaka część obszaru jednego źródła leży poza drugim.
7. *Wpływ poligonu*: `obs_share` = jaki odsetek obserwacji zostaje po filtrze obszaru; prędkości pokazują, jak filtr zmienia wynik.

## 1. Pokrycie: obecność plików (wszystkie miasta w zakresie)

| miasto | poziom | dni z tidy | dni robocze z tidy | dni robocze bez tidy | tidy GB | statyka: liczba różnych wersji | statyka: zmiany w dniach |
|---|---|---|---|---|---|---|---|
| bucharest | candidate | 24 | 18 | 09-01 | 0.65 | 3 | 09-05, 09-09 |
| gdansk | candidate | 24 | 18 | 09-17 | 0.26 | 22 | 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| krakow | candidate | 25 | 19 | - | 0.48 | 15 | 09-04, 09-05, 09-06, 09-10, 09-11, 09-15, 09-16, 09-17, 09-18, 09-20, 09-22, 09-23, 09-24, 09-25 |
| lisbon | candidate | 25 | 19 | - | 0.43 | 20 | 09-04, 09-05, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| ljubljana | candidate | 24 | 18 | 09-17 | 0.1 | 24 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| lodz | candidate | 25 | 19 | - | 0.4 | 9 | 09-04, 09-11, 09-16, 09-17, 09-21, 09-22, 09-24, 09-25 |
| nicosia | candidate | 24 | 18 | 09-17 | 0.09 | 24 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| poznan | candidate | 24 | 18 | 09-03 | 0.31 | 10 | 09-02, 09-04, 09-07, 09-10, 09-15, 09-16, 09-17, 09-21, 09-24 |
| prague | candidate | 24 | 18 | 09-17 | 1.54 | 24 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| rome | candidate | 24 | 18 | 09-17 | 1.47 | 20 | 09-02, 09-03, 09-04, 09-05, 09-07, 09-08, 09-09, 09-10, 09-11, 09-14, 09-15, 09-16, 09-18, 09-19, 09-21, 09-22, 09-23, 09-24, 09-25 |
| sofia | candidate | 24 | 19 | - | 0.63 | 23 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-08, 09-09, 09-10, 09-11, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| szczecin | candidate | 24 | 18 | 09-17 | 0.19 | 3 | 09-16, 09-23 |
| turin | candidate | 21 | 15 | 09-10, 09-11, 09-17, 09-24 | 0.26 | 12 | 09-04, 09-05, 09-08, 09-09, 09-12, 09-15, 09-16, 09-17, 09-18, 09-19, 09-22 |
| vilnius | candidate | 25 | 19 | - | 0.38 | 23 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| warszawa | candidate | 24 | 18 | 09-17 | 1.37 | 25 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| zagreb | candidate | 21 | 15 | 09-03, 09-08, 09-10, 09-17 | 0.23 | 1 | - |
| elblag | watch | 24 | 18 | 09-17 | 0.03 | 1 | - |
| gzm | watch | 21 | 16 | 09-17, 09-21, 09-22 | 0.85 | 21 | 09-02, 09-03, 09-04, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-18, 09-19, 09-20, 09-23, 09-24, 09-25 |
| kielce | watch | 25 | 19 | - | 0.11 | 8 | 09-03, 09-04, 09-09, 09-10, 09-11, 09-17, 09-24 |
| lublin | watch | 24 | 18 | 09-23 | 0.17 | 2 | 09-04 |
| przemysl | watch | 25 | 19 | - | 0.01 | 25 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| radom | watch | 25 | 19 | - | 0.09 | 2 | 09-06 |
| rybnik | watch | 25 | 19 | - | 0.03 | 25 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |
| rzeszow | watch | 25 | 19 | - | 0.11 | 4 | 09-14, 09-20, 09-21 |
| suwalki | watch | 25 | 19 | - | 0.01 | 25 | 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14, 09-15, 09-16, 09-17, 09-18, 09-19, 09-20, 09-21, 09-22, 09-23, 09-24, 09-25 |

Łącznie plików tidy w oknie: 601, 10.2 GB.

## 2. Jakość dni (miasta kandydujące, dni robocze)

| miasto | dni robocze z danymi | schemat 34 kol. OK | dni święta | dni ważne | crossing min/med/max | udział ok min/med/max | dni ważne od 09-07 | min. pokrycie pasma | wiersze/dzień (med.) |
|---|---|---|---|---|---|---|---|---|---|
| bucharest | 18 | 18/18 | 0 | 12 | 0.58/0.69/0.72 | 0.52/0.62/0.66 | 12 | 0.0 | 420882 |
| gdansk | 18 | 18/18 | 0 | 13 | 0.71/0.88/0.88 | 0.65/0.82/0.82 | 13 | 0.0 | 145763 |
| krakow | 19 | 19/19 | 0 | 15 | 0.65/0.78/0.80 | 0.59/0.70/0.73 | 15 | 0.0 | 296610 |
| lisbon | 19 | 19/19 | 0 | 15 | 0.70/0.83/0.85 | 0.65/0.77/0.79 | 14 | 0.0 | 256392 |
| ljubljana | 18 | 18/18 | 0 | 14 | 0.73/0.88/0.89 | 0.65/0.79/0.80 | 14 | 0.0 | 46429 |
| lodz | 19 | 19/19 | 0 | 15 | 0.69/0.86/0.87 | 0.64/0.81/0.82 | 15 | 0.0 | 201813 |
| nicosia | 18 | 18/18 | 0 | 12 | 0.69/0.88/0.89 | 0.60/0.78/0.78 | 12 | 0.0 | 54568 |
| poznan | 18 | 18/18 | 0 | 15 | 0.47/0.88/0.89 | 0.42/0.82/0.83 | 15 | 0.0 | 217309 |
| prague | 18 | 18/18 | 0 | 14 | 0.71/0.88/0.88 | 0.62/0.78/0.78 | 14 | 0.0 | 895908 |
| rome | 18 | 18/18 | 0 | 14 | 0.70/0.82/0.87 | 0.65/0.77/0.81 | 14 | 0.0 | 805823 |
| sofia | 19 | 19/19 | 2 | 13 | 0.71/0.89/0.90 | 0.66/0.84/0.85 | 13 | 0.0 | 302589 |
| szczecin | 18 | 18/18 | 0 | 14 | 0.73/0.87/0.88 | 0.68/0.81/0.82 | 14 | 0.0 | 115178 |
| turin | 15 | 15/15 | 0 | 7 | 0.00/0.73/0.86 | 0.00/0.68/0.81 | 7 | 0.0 | 176287 |
| vilnius | 19 | 19/19 | 0 | 15 | 0.68/0.83/0.84 | 0.61/0.77/0.78 | 15 | 0.0 | 211682 |
| warszawa | 18 | 18/18 | 0 | 14 | 0.71/0.88/0.88 | 0.64/0.81/0.82 | 14 | 0.0 | 810684 |
| zagreb | 15 | 15/15 | 0 | 12 | 0.74/0.87/0.88 | 0.64/0.77/0.78 | 12 | 0.0 | 143331 |

Dni niewazne (powód):

| miasto | dzień | crossing_rate | ok_share | min. pokrycie pasma | święto | schemat OK |
|---|---|---|---|---|---|---|
| lodz | 2026-09-03 | 0.792 | 0.744 | 0.0 | False | True |
| lodz | 2026-09-04 | 0.689 | 0.639 | 0.0 | False | True |
| lodz | 2026-09-01 | 0.791 | 0.745 | 0.0 | False | True |
| lodz | 2026-09-02 | 0.804 | 0.756 | 0.5 | False | True |
| warszawa | 2026-09-03 | 0.792 | 0.728 | 0.0 | False | True |
| warszawa | 2026-09-01 | 0.858 | 0.794 | 0.0 | False | True |
| warszawa | 2026-09-04 | 0.706 | 0.643 | 0.0 | False | True |
| warszawa | 2026-09-02 | 0.81 | 0.746 | 0.5 | False | True |
| krakow | 2026-09-01 | 0.775 | 0.705 | 0.0 | False | True |
| krakow | 2026-09-03 | 0.727 | 0.662 | 0.0 | False | True |
| krakow | 2026-09-04 | 0.654 | 0.589 | 0.0 | False | True |
| krakow | 2026-09-02 | 0.726 | 0.658 | 0.5 | False | True |
| gdansk | 2026-09-01 | 0.86 | 0.788 | 0.0 | False | True |
| gdansk | 2026-09-02 | 0.858 | 0.659 | 0.0 | False | True |
| gdansk | 2026-09-04 | 0.706 | 0.647 | 0.0 | False | True |
| gdansk | 2026-09-03 | 0.736 | 0.682 | 0.0 | False | True |
| gdansk | 2026-09-14 | 0.816 | 0.759 | 0.75 | False | True |
| poznan | 2026-09-02 | 0.465 | 0.423 | 0.0 | False | True |
| poznan | 2026-09-01 | 0.865 | 0.805 | 0.0 | False | True |
| poznan | 2026-09-04 | 0.732 | 0.672 | 0.0 | False | True |
| szczecin | 2026-09-01 | 0.857 | 0.804 | 0.0 | False | True |
| szczecin | 2026-09-03 | 0.803 | 0.753 | 0.0 | False | True |
| szczecin | 2026-09-04 | 0.732 | 0.679 | 0.0 | False | True |
| szczecin | 2026-09-02 | 0.817 | 0.765 | 0.5 | False | True |
| prague | 2026-09-03 | 0.797 | 0.709 | 0.0 | False | True |
| prague | 2026-09-01 | 0.86 | 0.762 | 0.0 | False | True |
| prague | 2026-09-04 | 0.71 | 0.624 | 0.0 | False | True |
| prague | 2026-09-02 | 0.801 | 0.707 | 0.5 | False | True |
| rome | 2026-09-01 | 0.731 | 0.681 | 0.0 | False | True |
| rome | 2026-09-03 | 0.762 | 0.712 | 0.0 | False | True |
| rome | 2026-09-04 | 0.699 | 0.647 | 0.0 | False | True |
| rome | 2026-09-02 | 0.792 | 0.74 | 0.5 | False | True |
| turin | 2026-09-01 | 0.835 | 0.78 | 0.0 | False | True |
| turin | 2026-09-02 | 0.815 | 0.761 | 0.5 | False | True |
| turin | 2026-09-03 | 0.001 | 0.0 | 0.0 | False | True |
| turin | 2026-09-04 | 0.725 | 0.671 | 0.0 | False | True |
| turin | 2026-09-14 | 0.727 | 0.68 | 0.0 | False | True |
| turin | 2026-09-16 | 0.598 | 0.537 | 1.0 | False | True |
| turin | 2026-09-09 | 0.689 | 0.632 | 0.67 | False | True |
| turin | 2026-09-22 | 0.656 | 0.599 | 0.67 | False | True |
| vilnius | 2026-09-01 | 0.772 | 0.708 | 0.0 | False | True |
| vilnius | 2026-09-03 | 0.737 | 0.672 | 0.0 | False | True |
| vilnius | 2026-09-04 | 0.675 | 0.609 | 0.0 | False | True |
| vilnius | 2026-09-02 | 0.774 | 0.709 | 0.5 | False | True |
| sofia | 2026-09-03 | 0.819 | 0.77 | 0.0 | False | True |
| sofia | 2026-09-04 | 0.714 | 0.661 | 0.0 | False | True |
| sofia | 2026-09-01 | 0.82 | 0.769 | 0.0 | False | True |
| sofia | 2026-09-07 | 0.896 | 0.846 | 1.0 | True | True |
| sofia | 2026-09-02 | 0.842 | 0.791 | 0.5 | False | True |
| sofia | 2026-09-22 | 0.902 | 0.851 | 1.0 | True | True |
| bucharest | 2026-09-03 | 0.675 | 0.613 | 0.0 | False | True |
| bucharest | 2026-09-04 | 0.585 | 0.524 | 0.0 | False | True |
| bucharest | 2026-09-02 | 0.701 | 0.638 | 0.5 | False | True |
| bucharest | 2026-09-15 | 0.596 | 0.531 | 1.0 | False | True |
| bucharest | 2026-09-17 | 0.617 | 0.553 | 0.33 | False | True |
| bucharest | 2026-09-23 | 0.669 | 0.6 | 0.75 | False | True |
| lisbon | 2026-09-01 | 0.799 | 0.747 | 0.0 | False | True |
| lisbon | 2026-09-03 | 0.742 | 0.69 | 0.0 | False | True |
| lisbon | 2026-09-04 | 0.697 | 0.646 | 0.0 | False | True |
| lisbon | 2026-09-10 | 0.782 | 0.728 | 0.33 | False | True |
| zagreb | 2026-09-01 | 0.854 | 0.754 | 0.0 | False | True |
| zagreb | 2026-09-02 | 0.828 | 0.729 | 0.5 | False | True |
| zagreb | 2026-09-04 | 0.741 | 0.644 | 0.0 | False | True |
| ljubljana | 2026-09-01 | 0.813 | 0.731 | 0.0 | False | True |
| ljubljana | 2026-09-03 | 0.792 | 0.71 | 0.0 | False | True |
| ljubljana | 2026-09-02 | 0.827 | 0.738 | 0.5 | False | True |
| ljubljana | 2026-09-04 | 0.73 | 0.65 | 0.0 | False | True |
| nicosia | 2026-09-01 | 0.809 | 0.7 | 0.0 | False | True |
| nicosia | 2026-09-03 | 0.793 | 0.697 | 0.0 | False | True |
| nicosia | 2026-09-02 | 0.83 | 0.727 | 0.5 | False | True |
| nicosia | 2026-09-04 | 0.693 | 0.598 | 0.0 | False | True |
| nicosia | 2026-09-07 | 0.803 | 0.702 | 0.0 | False | True |
| nicosia | 2026-09-25 | 0.798 | 0.699 | 0.5 | False | True |

## 3. Gotowość danych pod wymiary W10–W12 (mediany po dniach)

Odsetek wierszy z wartością w kolumnach potrzebnych do punktualności (`delay_s`; liczone tylko dla wierszy z obserwacją, więc zawsze ok. 1,0 i mało informacyjne), regularności (`headway_s` wśród wierszy z obserwacją; `sched_headway_s` wśród wszystkich wierszy) oraz udział wierszy linii częstych (`sched_headway_s < frequent_headway_s`). **Mianownik udziału linii częstych to wiersze z `sched_headway_s`** (67–89% wszystkich), nie wszystkie wiersze. To wskaźnik wykonalności, nie wartość metryk.

| miasto | delay_s dostępne (W10) med. | headway_s dostępne (W11) med. | sched_headway dostępne med. | udział wierszy linii częstych | trip_coverage śr. |
|---|---|---|---|---|---|
| bucharest | 1.0 | 0.977 | 0.67 | 0.372 | 0.686 |
| gdansk | 1.0 | 0.957 | 0.837 | 0.056 | 0.876 |
| krakow | 1.0 | 0.961 | 0.738 | 0.152 | 0.775 |
| lisbon | 1.0 | 0.972 | 0.803 | 0.078 | 0.826 |
| ljubljana | 1.0 | 0.96 | 0.842 | 0.094 | 0.879 |
| lodz | 1.0 | 0.953 | 0.824 | 0.026 | 0.863 |
| nicosia | 1.0 | 0.928 | 0.818 | 0.01 | 0.882 |
| poznan | 1.0 | 0.947 | 0.834 | 0.01 | 0.88 |
| prague | 1.0 | 0.922 | 0.808 | 0.293 | 0.876 |
| rome | 1.0 | 0.968 | 0.798 | 0.088 | 0.824 |
| sofia | 1.0 | 0.975 | 0.87 | 0.106 | 0.893 |
| szczecin | 1.0 | 0.959 | 0.83 | 0.085 | 0.866 |
| turin | 1.0 | 0.947 | 0.695 | 0.11 | 0.728 |
| vilnius | 1.0 | 0.966 | 0.806 | 0.212 | 0.834 |
| warszawa | 1.0 | 0.97 | 0.85 | 0.176 | 0.878 |
| zagreb | 1.0 | 0.962 | 0.836 | 0.23 | 0.869 |

## 4. Macierz miasto × dzień roboczy (kandydaci)

`✓` dzień ważny, `g` odrzucony przez bramkę dnia, `H` święto państwowe, `–` brak tidy. Dla wszystkich dni: `reports/m0/stats.jsonl` (crossing, udział `ok`, pokrycie pasm, rozmiary, SHA-256 tidy).

| miasto | 09-01 | 09-02 | 09-03 | 09-04 | 09-07 | 09-08 | 09-09 | 09-10 | 09-11 | 09-14 | 09-15 | 09-16 | 09-17 | 09-18 | 09-21 | 09-22 | 09-23 | 09-24 | 09-25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bucharest | – | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | g | ✓ | g | ✓ | ✓ | ✓ | g | ✓ | ✓ |
| gdansk | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | g | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| krakow | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| lisbon | g | ✓ | g | g | ✓ | ✓ | ✓ | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ljubljana | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| lodz | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| nicosia | g | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | g |
| poznan | g | g | – | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| prague | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| rome | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| sofia | g | g | g | g | H | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | H | ✓ | ✓ | ✓ |
| szczecin | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| turin | g | g | g | g | ✓ | ✓ | g | – | – | g | ✓ | g | – | ✓ | ✓ | g | ✓ | – | ✓ |
| vilnius | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| warszawa | g | g | g | g | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| zagreb | g | g | – | g | ✓ | – | ✓ | – | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 5. Prognoza kwalifikacji miast do pilotażu

Założenie: udział dni ważnych od 2026-09-07 utrzyma się do końca okna (2026-12-18). Progi z `config/metrics.yaml` → `city_gate` (`ranked` ≥ 40 dni ważnych, `limited` ≥ 20). **Do dziś żaden kandydat nie ma jeszcze 20 dni ważnych** (okno ma 15 dni roboczych od 2026-09-07), więc to prognoza, nie kwalifikacja. Nie uwzględnia pokrycia sieci (`min_network_coverage`, liczone w M2) ani licencji (`docs/licenses.md`).

| miasto | dni ważne od 09-07 | dni robocze bez świąt | udział dni ważnych | prognoza dni ważnych do 12-18 | status wg bramki (bez pokrycia sieci) |
|---|---|---|---|---|---|
| bucharest | 12 | 15 | 0.8 | 58 | ranked |
| gdansk | 13 | 15 | 0.87 | 64 | ranked |
| krakow | 15 | 15 | 1.0 | 74 | ranked |
| lisbon | 14 | 15 | 0.93 | 67 | ranked |
| ljubljana | 14 | 15 | 0.93 | 70 | ranked |
| lodz | 15 | 15 | 1.0 | 74 | ranked |
| nicosia | 12 | 15 | 0.8 | 58 | ranked |
| poznan | 15 | 15 | 1.0 | 74 | ranked |
| prague | 14 | 15 | 0.93 | 67 | ranked |
| rome | 14 | 15 | 0.93 | 69 | ranked |
| sofia | 13 | 13 | 1.0 | 73 | ranked |
| szczecin | 14 | 15 | 0.93 | 69 | ranked |
| turin | 7 | 15 | 0.47 | 35 | limited |
| vilnius | 15 | 15 | 1.0 | 74 | ranked |
| warszawa | 14 | 15 | 0.93 | 69 | ranked |
| zagreb | 12 | 15 | 0.8 | 59 | ranked |

## 6. Poligony miast: GISCO vs OSM (D12)

GISCO = Urban Audit 2024, `URAU_RG_100K_2024_4326_CITIES`; OSM = relacja administracyjna z Nominatim. IoU liczone w EPSG:3035.

| city | gisco_code | osm_relation | osm_admin_level | gisco_km2 | osm_km2 | area_ratio_osm_to_gisco | iou | gisco_only_share | osm_only_share |
|---|---|---|---|---|---|---|---|---|---|
| lodz | PL002C | 2907537 | 7 | 293.3 | 293.3 | 1.0 | 0.999 | 0.0 | 0.0 |
| warszawa | PL001C | 336075 | 6 | 517.2 | 517.2 | 1.0 | 1.0 | 0.0 | 0.0 |
| krakow | PL003C | 2768921 | 7 | 326.8 | 326.9 | 1.0 | 0.999 | 0.0 | 0.0 |
| gdansk | PL006C | 1553098 | 6 | 261.7 | 682.3 | 2.607 | 0.383 | 0.0 | 0.617 |
| poznan | PL005C | 2456294 | 6 | 261.9 | 261.9 | 1.0 | 0.999 | 0.0 | 0.0 |
| szczecin | PL007C | 2873415 | 7 | 300.6 | 300.6 | 1.0 | 0.998 | 0.001 | 0.001 |
| prague | CZ001C | 435514 | 4 | 496.4 | 496.3 | 1.0 | 0.996 | 0.002 | 0.002 |
| rome | IT001C | 41485 | 8 | 1286.0 | 1285.6 | 1.0 | 0.995 | 0.003 | 0.002 |
| turin | IT004C | 43992 | 8 | 130.1 | 130.1 | 1.0 | 0.999 | 0.001 | 0.001 |
| vilnius | LT001C | 1529146 | 8 | 400.5 | 396.7 | 0.99 | 0.988 | 0.011 | 0.001 |
| sofia | BG001C | 4283101 | 8 | 1341.8 | 454.1 | 0.338 | 0.338 | 0.662 | 0.0 |
| bucharest | RO001C | 377733 | 4 | 238.9 | 239.0 | 1.001 | 0.998 | 0.001 | 0.001 |
| lisbon | PT001C | 5400890 | 7 | 636.7 | 86.8 | 0.136 | 0.136 | 0.864 | 0.005 |
| zagreb | HR001C | 226224 | 4 | 641.4 | 641.2 | 1.0 | 0.998 | 0.001 | 0.001 |
| ljubljana | SI001C | 1675898 | 8 | 275.0 | 275.0 | 1.0 | 0.999 | 0.001 | 0.001 |
| nicosia | CY001C | 3264382 | 5 | 219.9 | 1927.5 | 8.765 | 0.077 | 0.3 | 0.92 |
| lublin | PL009C | 2206549 | 6 | 147.4 | 147.5 | 1.0 | 0.998 | 0.001 | 0.001 |
| rzeszow | PL015C | 446049 | 8 | 126.6 | 129.0 | 1.019 | 0.98 | 0.001 | 0.019 |
| kielce | PL012C | 2904506 | 7 | 109.7 | 109.7 | 1.0 | 0.998 | 0.001 | 0.001 |
| radom | PL025C | 2904795 | 7 | 111.8 | 115.1 | 1.029 | 0.971 | 0.001 | 0.029 |
| rybnik | PL060C | 2425998 | 8 | 148.3 | 148.3 | 1.0 | 0.998 | 0.001 | 0.001 |
| elblag | PL063C | 1600068 | 6 | 79.8 | 79.7 | 0.998 | 0.994 | 0.004 | 0.002 |
| suwalki | PL021C | 3891982 | 6 | 65.5 | 65.5 | 1.0 | 0.999 | 0.001 | 0.001 |
| przemysl |  | 1748162 | 8 |  | 46.1 |  |  |  |  |

## 7. Wpływ poligonu na wyniki (2026-09-24, bus + tram)

`obs_share` = udział obserwacji `ok` z obu przystankami w poligonie; prędkości `ΣL/ΣT` [km/h].

| city | n_obs_all | source | obs_share | bus_kmh | bus_n | tram_kmh | tram_n |
|---|---|---|---|---|---|---|---|
| lodz | 168507 | none | 1.0 | 18.24 | 111103 | 16.37 | 57404 |
| lodz | 168507 | gisco | 0.959 | 17.88 | 106626 | 16.21 | 54896 |
| lodz | 168507 | osm | 0.958 | 17.88 | 106565 | 16.21 | 54896 |
| warszawa | 671976 | none | 1.0 | 20.14 | 511576 | 18.22 | 160400 |
| warszawa | 671976 | gisco | 0.881 | 19.17 | 431905 | 18.22 | 160400 |
| warszawa | 671976 | osm | 0.881 | 19.17 | 431905 | 18.22 | 160400 |
| krakow | 217854 | none | 1.0 | 21.32 | 144208 | 18.91 | 73646 |
| krakow | 217854 | gisco | 0.877 | 19.71 | 117355 | 18.91 | 73646 |
| krakow | 217854 | osm | 0.877 | 19.71 | 117355 | 18.91 | 73646 |
| gdansk | 119649 | none | 1.0 | 19.42 | 80942 | 17.48 | 38707 |
| gdansk | 119649 | gisco | 0.934 | 19.11 | 73035 | 17.48 | 38707 |
| gdansk | 119649 | osm | 0.934 | 19.11 | 73035 | 17.48 | 38707 |
| poznan | 109941 | none | 1.0 | 27.84 | 44768 | 18.54 | 65173 |
| poznan | 109941 | gisco | 0.727 | 26.61 | 14781 | 18.54 | 65173 |
| poznan | 109941 | osm | 0.727 | 26.6 | 14761 | 18.54 | 65173 |
| szczecin | 96244 | none | 1.0 | 21.45 | 64435 | 16.99 | 31809 |
| szczecin | 96244 | gisco | 0.917 | 20.47 | 56401 | 16.99 | 31809 |
| szczecin | 96244 | osm | 0.919 | 20.51 | 56603 | 16.99 | 31809 |
| prague | 643568 | none | 1.0 | 28.1 | 481456 | 18.7 | 162112 |
| prague | 643568 | gisco | 0.702 | 22.22 | 289867 | 18.7 | 162112 |
| prague | 643568 | osm | 0.702 | 22.24 | 289939 | 18.7 | 162112 |
| rome | 633753 | none | 1.0 | 16.75 | 630907 | 11.06 | 2846 |
| rome | 633753 | gisco | 0.997 | 16.73 | 628804 | 11.06 | 2846 |
| rome | 633753 | osm | 0.998 | 16.72 | 629325 | 11.06 | 2846 |
| vilnius | 164560 | none | 1.0 | 18.81 | 164560 |  | 0 |
| vilnius | 164560 | gisco | 0.957 | 18.51 | 157446 |  | 0 |
| vilnius | 164560 | osm | 0.952 | 18.47 | 156600 |  | 0 |
| sofia | 280211 | none | 1.0 | 18.73 | 223078 | 14.99 | 57133 |
| sofia | 280211 | gisco | 0.996 | 18.72 | 221997 | 14.99 | 57133 |
| sofia | 280211 | osm | 0.881 | 17.39 | 190590 | 14.95 | 56205 |
| bucharest | 271871 | none | 1.0 | 15.64 | 234737 | 14.46 | 37134 |
| bucharest | 271871 | gisco | 0.855 | 14.04 | 195259 | 14.46 | 37134 |
| bucharest | 271871 | osm | 0.856 | 14.05 | 195595 | 14.46 | 37134 |
| lisbon | 199964 | none | 1.0 | 13.95 | 199964 |  | 0 |
| lisbon | 199964 | gisco | 1.0 | 13.95 | 199964 |  | 0 |
| lisbon | 199964 | osm | 0.935 | 13.58 | 186902 |  | 0 |
| zagreb | 111462 | none | 1.0 | 24.09 | 67549 | 14.71 | 43913 |
| zagreb | 111462 | gisco | 0.951 | 23.4 | 62088 | 14.71 | 43913 |
| zagreb | 111462 | osm | 0.951 | 23.4 | 62088 | 14.71 | 43913 |
| ljubljana | 36762 | none | 1.0 | 17.54 | 36762 |  | 0 |
| ljubljana | 36762 | gisco | 0.996 | 17.44 | 36611 |  | 0 |
| ljubljana | 36762 | osm | 0.996 | 17.44 | 36611 |  | 0 |
| nicosia | 43249 | none | 1.0 | 27.15 | 43249 |  | 0 |
| nicosia | 43249 | gisco | 0.712 | 20.97 | 30772 |  | 0 |
| nicosia | 43249 | osm | 0.973 | 26.81 | 42067 |  | 0 |
