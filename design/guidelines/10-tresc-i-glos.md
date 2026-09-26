# Treść i głos

Piszemy po polsku, z przełącznikiem EN. Krótko, rzeczowo, deklaratywnie. Serwis mówi tym, co zmierzył i co ma z tym problem, bez marketingowego wypełniacza.

## Zasady

- Wielkość liter jak w zdaniu, także w nagłówkach i przyciskach. Wersaliki tylko w nadtytułach (`idx-eyebrow`, przez CSS, nie w treści).
- Jedno zdanie na myśl. Nagłówek hero to pełne zdanie z kropką: „Tyle jedzie transport publiczny.”
- Liczby z przecinkiem dziesiętnym: `17,8`. Jednostki `km/h` i `min/10 km`, ze spacją, w mono lub w `idx-kpi__unit`.
- Zawsze rozróżniaj **rozkładowe** (z rozkładu jazdy) i **zmierzone (rekonstrukcja z GTFS-RT)**. Pierwsze użycie na stronie pisz w pełnym brzmieniu, kolejne „zmierzone”.
- Mów wprost, że wyniki są odtworzone, nie zmierzone wprost: „To rekonstrukcja z GTFS-RT, nie pomiar wprost.”
- Ograniczenia i jakość danych pokazuj otwarcie, w tym samym miejscu co wynik (`MethodNote`, `QualityBadge`), nie w stopce ani w osobnym „regulaminie”.
- Próbę poniżej progu nazywaj „za mało danych”, nie „brak” ani „0”. Podaj próg: `n = XX < XX`.

## Czego nie piszemy

Puste hasła (unlock, seamless, empower, „rewolucja w danych”), wykrzykniki, emoji, wymyślone statystyki, opinie użytkowników, lorem ipsum. Dane pokazowe oznacz `dane zastępcze` (`idx-ph`) albo `XX`.

## Przykłady

| Zamiast | Pisz |
|---|---|
| „Odkryj, jak naprawdę jeżdżą Twoje tramwaje!” | „Tyle jedzie transport publiczny.” |
| „Średnia prędkość: 17.8 km/h” | „17,8 km/h · zmierzone (rekonstrukcja z GTFS-RT)” |
| „Brak wyników” | „Za mało danych, żeby podać prędkość dla tego wyboru (n = XX, próg XX).” |
| „Nasze dane są super dokładne” | „Zapisy mają luki. Godziny z próbą poniżej progu pokazujemy jako „za mało danych”.” |
| „Błąd 500” | „Nie udało się wczytać rankingu. Spróbuj ponownie za chwilę.” |

## Etykiety stałe

Plakietki jakości: `w rankingu`, `ograniczone`, `poza rankingiem`. Przełączniki: `Tramwaje` / `Autobusy`, `Dzień` / `Szczyt` / `Poza szczytem`, percentyle `P15` / `P50` / `P85` (P50 to mediana). Legenda: `brak danych`. Wykres: `rozkładowe`, `zmierzone`, `za mało danych`. Język: `PL` / `EN`.
