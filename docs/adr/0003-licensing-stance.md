# ADR-0003: Projekt niekomercyjny, wyniki na CC BY 4.0, publikacja z atrybucją

Status: przyjęta 2026-09-26 (właściciel: GISBoost), uzupełniona tego samego dnia po przeglądzie audytu. Rozstrzyga D7.

## Kontekst
Audyt licencji M0 (`docs/licenses.md`): licencja GTT (Turyn) dopuszcza tylko użycie niekomercyjne i zakazuje m.in. reklam bez pisemnej zgody. Rzym dopuszcza RT "wyłącznie jako wsparcie podróży". Część źródeł nie ma znalezionej licencji.

## Decyzja
Projekt jest **niekomercyjny** (bez reklam, płatnych funkcji i przychodu). Wobec tego dane Turynu nie są wyłączane z góry: Turyn podlega bramce jakości jak inne miasta (dziś 7 z 15 dni ważnych od 7.09). Obowiązuje atrybucja GTT z linkiem. Licencja wyników ma być zgodna z niekomercyjnością (rekomendacja: CC BY-NC 4.0; decyzja D7 przed publikacją). **Wyniki są na licencji CC BY 4.0.** Wszystkie miasta mogą być publikowane pod warunkiem poprawnej atrybucji źródeł (per miasto: nazwa operatora lub portalu, link, data pobrania, informacja o przetworzeniu; OSM przy Warszawie, Sofii i Lizbonie). Przegląd operatorów przed publikacją (`docs/05` §5) pozostaje osobnym krokiem procesu.

## Konsekwencje
Serwis bez reklam. **Zapisane fakty, które właściciel uznał za nieblokujące:** licencja GTT dopuszcza dane tylko niekomercyjnie, a CC BY 4.0 pozwala odbiorcom wyników na użycie komercyjne; Rzym dopuszcza RT "wyłącznie jako wsparcie podróży". Pozostaje otwarta tylko sprawa plików geometrii z kształtami OSM w Warszawie (ODbL, share-alike; `docs/licenses.md` §4). Gdyby projekt miał kiedykolwiek generować przychód, trzeba wrócić do licencji źródeł (GTT: pisemna zgoda). Analityka bez ciasteczek (GoatCounter) nie jest reklamą.
