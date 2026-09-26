Profil godzinowy prędkości: rozkładowe (linia przerywana) kontra zmierzone (linia ciągła), 24 godziny, oś od zera, bezpośrednie podpisy, kreskowanie tam, gdzie za mało danych.

**Dostarczasz:** dwie tablice po 24 wartości (`plan`, `meas`); w `meas` `null` oznacza próbę poniżej progu. Wywołanie: `IDX.chart.hourly(element, { plan, meas, ymax })`.

- Serie: `idx-chart-plan` i `idx-chart-measured`, siatka `idx-chart-grid`. Podpisy `rozkładowe` i `zmierzone` na końcu linii, bez legendy; podpisy nie zachodzą na siebie.
- Godziny z `null`: kreskowanie `idx-chart-nodata` i napis „za mało danych”, nie pustka i nie zero. Linia zmierzona się przerywa.
- Oś pionowa zawsze od 0 km/h. Wykres ma `title` i `desc` oraz pod spodem zdanie o metodzie. Wersja tabelaryczna jest osobno.
- Stany: wczytywanie (szkielet), brak danych (kreskowana ramka z komunikatem), błąd jak w innych kartach.
- Bez cieni, wypełnień pod krzywą i gładzenia, które zmienia wartości.
