# ADR-0004: Bez przypinania easy-OTP; oznaczamy pochodzenie danych, serwujemy as is

Status: przyjęta 2026-09-26 (właściciel: GISBoost). Zastępuje rekomendację pinu z M0.

## Kontekst
Workflow `easy-GTFS-RT` robi checkout `easy-OTP` bez `ref`, czyli z `main`. Metoda rekonstrukcji (`family_a`) będzie się zmieniać przy poprawkach błędów i ulepszeniach. Dzienne surowe pozycje są kasowane po zbudowaniu, ale co miesiąc trafiają do archiwów `raw-snapshots-<RRRR-MM>` w `easy-GTFS-RT` (kopia zapasowa; przeglądana w `gtfs-dashboard`), więc starsze dni **da się przeliczyć** nowszym kodem, choć kosztownie. Przypięcie tagu zatrzymałoby ulepszenia w codziennych buildach; właściciel tego nie chce.

## Decyzja
Nie przypinamy `easy-OTP` i nie zmieniamy `easy-GTFS-RT`. Zamiast tego **oznaczamy pochodzenie każdego dnia**:
1. Dla każdej pary miasto-dzień zapisujemy czas zbudowania tidy (nagłówek `Last-Modified` pliku tidy, zgodny z czasem utworzenia załącznika) i commit `easy-OTP`, który był wtedy aktualny na `main` (historia commitów tego repo, tylko odczyt).
2. `config/tidy_epochs.yaml` wskazuje, które commity zmieniają znaczenie wiersza tidy (epoki semantyczne). Klasyfikację potwierdza właściciel; przy nowej zmianie semantyki dopisujemy epokę.
3. Manifest edycji zawiera `easy_otp_commits` (commit, zakres dni, epoka, liczba dni) zamiast jednego przypiętego ref-a.
4. Dane są serwowane **as is**: strona metodyki podaje epokę i zakres commitów. Wynik z różnych epok nie jest porównywalny (`method_version`); domyślnie edycja używa dni z jednej epoki, a przy zmianie w trakcie okna właściciel decyduje: osobne wyniki per epoka albo skrócenie okna do jednej epoki.

## Konsekwencje
Nie potrzeba żadnych zmian w `easy-OTP` ani `easy-GTFS-RT`. Historię z okna od 2026-09-01 opisuje jedna epoka `t1` (ostatnia zmiana semantyki 2026-08-09, potem tylko `perf` z 2026-09-04). Domyślnie poprawka błędu w `family_a` obejmuje tylko nowe dni; stare dni zostają w epoce sprzed poprawki, chyba że zostaną przebudowane z miesięcznych archiwów surowych pozycji (`raw-snapshots-*`; wykonalność nieweryfikowana, decyzja i koszt po stronie właściciela, poza tym repo). Po przebudowie release'ów zmieni się `Last-Modified` tidy i dzień dostanie nowy commit/epokę w naszym oznaczeniu. Opcjonalne, tanie ułatwienie po Twojej stronie: zapis SHA commita `easy-OTP` w treści release'u (jedna linia w workflow) zastąpiłby wnioskowanie z czasu.
