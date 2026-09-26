Przycisk główny, drugoplanowy i tekstowy: promień 6 px, wysokość co najmniej 44 px, bez cieni i pigułek.

**Dostarczasz:** etykietę (czasownik, wielkość liter jak w zdaniu), ewentualną ikonę z `IDX.icon`, `aria-busy` przy ładowaniu.

- Główny (`.idx-btn--primary`, `idx-accent` z `idx-on-accent`): jeden na widok. Najechanie `idx-accent-hover`, wciśnięcie `idx-accent-press` i skala 0,97.
- Drugoplanowy (`--secondary`): obrys `idx-control-edge`. Tekstowy (`--text`): `accent-ink`, podkreślenie w hover.
- Fokus zawsze widoczny. Ładowanie: mały loader w środku i `aria-busy="true"`. Niedostępny: `disabled`, opacity 0,55, nie zastępuje komunikatu o powodzie.
- Nie rób z przycisku pigułki, nie dawaj mu gradientu ani ikony w kółku.
