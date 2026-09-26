Okno odcinka nad mapą: trasa przystanek A → przystanek B, linie, prędkość zmierzona kontra rozkładowa, zakres P15–P85, próba i jakość.

**Dostarczasz:** nazwy przystanków, numery linii z GTFS, wartości P15/P50/P85 i n odcinka, rozkładową z rozkładu.

- Karta `surface`, promień 12 px, jedyny cień systemu (`idx-shadow-float`). Trasa to pionowy łącznik z węzłami na przystankach.
- Liczby `idx-figure-md`, jednostka mniejsza w sansie. Kolejność: zmierzone, rozkładowe, zakres, próba, jakość.
- Za mało danych: bez liczb, komunikat „Za mało danych” z progiem i plakietka `poza rankingiem`. Wczytywanie: loader i szkielety.
- Fokus wchodzi do okna po otwarciu, Esc zamyka i wraca na odcinek. Przycisk „Zamknij” 44 px. Na telefonie okno staje się dolną szufladą.
