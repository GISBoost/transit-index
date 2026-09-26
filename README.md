# Transit Index: indeks jakości transportu publicznego

Poboczny projekt GISBoost (poza doktoratem): serwis, który mierzy, **jak dobrze transport publiczny naprawdę działa** w kilkunastu miastach Polski i Europy. Nie na podstawie rozkładów, ale ze zrekonstruowanych danych GTFS-RT (`easy-GTFS-RT`). Jakość to pięć osobnych wymiarów, bez jednej łącznej oceny w v1:

| wymiar | pytanie | metryka |
|---|---|---|
| Prędkość | jak szybko jedzie | prędkość komunikacyjna `ΣL/ΣT` (W1) |
| Obciążenie szczytu | ile traci w szczycie | kara szczytu na tych samych odcinkach (W3) |
| Punktualność | czy jedzie według rozkładu | udział przyjazdów "o czasie" (W10) |
| Regularność | czy przyjeżdża w równych odstępach | nadmiar czasu oczekiwania, linie częste (W11) |
| Oferta | jak często jeździ według rozkładu | rozkładowe odjazdy na godzinę (W12) |

Serwis publikuje rankingi miast per wymiar (z flagami jakości danych), strony miast, mapę odcinków między przystankami kolorowanych prędkością, pliki do pobrania, metodykę i archiwum edycji. Statyczny serwis na GitHub Pages, edycja roczna. Wzorzec: TomTom Traffic Index (liczby nie są porównywalne).

**Status (2026-09-26):**
- **Design: gotowy i zaimportowany** do `design/` (Claude Design, commit `ed69a7c`). Jest nadrzędny wobec dokumentów.
- **Specyfikacja techniczna: gotowa** (`docs/`, `schemas/`, `reference/`), sprawdzona na prawdziwych danych dla prędkości i kary szczytu.
- **M0 wykonany** (`docs/progress.md`): dane na pełnym oknie sprawdzone, decyzje zebrane w `docs/decisions-needed.md`. **Potoku i strony jeszcze nie ma.** Następny krok to M1 (ingest i tabela obserwacji), potem prawdziwa analiza danych i podpięcie ich do serwisu.

## Co gdzie leży

```
README.md                   ten plik
CLAUDE.md                   zasady pracy agenta (czytane automatycznie przez Claude Code)
design/                     Transit Index Design System (import z Claude Design): tokeny,
                            komponenty React, karty wytycznych, landing, szablon social-card
docs/
  ALL-IN-ONE.md             skrót całości (jedna strona)
  01-research-summary.md    TomTom, analogi, ekosystem GISBoost, decyzje
  02-data-inventory.md      dane wejściowe: załączniki, 34 kolumny tidy, rozmiary, wady feedów
  03-metrics-spec.md        model jakości, obszar W0, metryki W1-W12, pasma, klasy, bramka, czułość
  04-segments-and-data-model.md  odcinki, poziomy L0-L3, potok, geometria, układ plików
  05-annual-edition.md      cykl edycji, kalendarze per kraj, manifest, prawo do odpowiedzi
  06-site-spec.md           architektura serwisu, kontrakt z designem, rozbieżności docs-design
  07-milestones.md          M0-M7 z gotowymi promptami dla Claude Code
  08-risks-and-open-questions.md  decyzje D1-D14 i ryzyka (nie commituj do publicznego repo)
  09-validation-on-real-data.md   ustalenia F1-F17 z prawdziwych danych, jak powtórzyć
schemas/                    JSON Schema: ranking, city_summary, segment_feature, edition_manifest
examples/                   przykłady zgodne ze schematami (WARTOŚCI ZASTĘPCZE, placeholder: true)
reference/                  metrics_reference.py (definicje + samotest), fetch_release_assets.py,
                            probe_release_data.py, golden_values.json, validate_examples.py
.claude/agents/milestone-reviewer.md   subagent oceniający każdy kamień milowy
```

W dokumentach `docs/03` oznacza plik `docs/03-*.md`. **M0–M7** to kamienie milowe, **W0–W12** metryki, **D1–D14** decyzje do podjęcia.

## Jak zacząć

1. **Sprawdź paczkę:** `pip install pandas pyarrow jsonschema`, potem `py reference/metrics_reference.py` i `py reference/validate_examples.py`.
2. **Obejrzyj design:** otwórz `design/ui_kits/landing/index.html` przez serwer HTTP (np. `py -m http.server` w katalogu `design/`). Liczby w nim są zastępcze.
3. **Otwórz Claude Code w tym repo** i wklej prompt **M0** z `docs/07-milestones.md`. M0 niczego nie buduje: potwierdza na pełnym oknie to, co sprawdzono na próbce, i zbiera decyzje blokujące.
4. **Idź kamieniami po kolei** (M1–M7). Po każdym uruchom `milestone-reviewer`; dalej dopiero po PASS.
5. **Po stronie designu:** wybrane elementy copy trzeba dopasować do modelu jakości przy podpinaniu prawdziwych danych (D13, `docs/06` §9).

## Stan danych i weryfikacja (2026-09-26)

- `easy-GTFS-RT`: 27 miast w `cities.json`, tagi do 2026-09-25, ok. 1385 par miasto-dzień od 2026-08-03 (załącznik `tidy`).
- **Sprawdzone na prawdziwych danych:** 15 miast z 2026-09-24 (tidy + statyka) i 9 dni Łodzi: 34 kolumny, semantyka odcinków, strefy czasu, geometria, stabilność kluczy, rozmiary (433 MB/dzień tidy), gotowość feedów (`docs/09`).
- **Najważniejsze ustalenia:** filtr obszaru zmienia prędkości o kilka km/h (obowiązkowy); "spowolnienie względem P85" zastąpiono karą szczytu; statykę bierz z każdego dnia i deduplikuj po SHA-256; klasy prędkości `[15, 20, 25, 30]` (pięć klas, jak w designie).
- Dane sprzed 2026-09-01 to wakacje. Pilotaż używa okna 2026-09-01 – 2026-12-18.

## Czego NIE zweryfikowano

- **Wymiary W11 (regularność) i W12 (oferta) nie były liczone na prawdziwych danych**, W10 (punktualność) tylko na jednym dniu bez filtra obszaru. To propozycje definicji do walidacji w M2.
- Większość miast tylko na jednym dniu; stabilność rang w czasie tylko dla Łodzi.
- Filtr obszaru w próbie to promień, nie poligon (D12).
- Ref `easy-OTP` używany przez workflow; luki dzienne poza Turynem.
- Licencje danych, fontów i ikon; progi bramki jakości (propozycja).
- Wskaźnika złożonego świadomie nie ma w v1 (D11); nazwa i adres to robocze propozycje (D4).

## Zasady, które trzeba znać od razu

- `design/` jest nadrzędny wobec `docs/`; przy konflikcie zmienia się dokument.
- Nie importuj kodu z `easy-OTP` (GPL-3.0-or-later); czytaj dane.
- Kolory danych tylko z tokenów `--speed-*` (i tylko dla prędkości); żadnych zmyślonych danych, przykłady mają `placeholder: true`.
- Nie używaj nazwy ani stylu "Traffic Index". Niczego nie publikuj bez zgody autora.
