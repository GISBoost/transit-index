# Notatka robocza, stan 2026-09-27

## Zrobione (bez commita od `041badb`)

- Analiza metodologii i plan testów: `docs/10-input-methodology-and-test-plan.md` (T1-T26, status w §7, ocena GitHub Actions w §8).
- Testy przed M1 zakończone: raport `docs/sensitivity-report.md`, tabele `reports/tests/` (kopia rundy 1 w `round1_backup/`).
- Narzędzia testowe (tymczasowe, `scripts/`): `t_l0.py`, `t_metrics.py`, `t_pool.py`, `t26_pooling.py`, `t_sens.py`, `t17_service.py`, `t2_param_sweep.py`, `t2_summary.py`, `t1_compare_tidy.py`, `t_list_archive_days.py`; testy `tests/test_pool_harness.py` (15 testów w repo przechodzi).
- Dokumenty: `docs/02`, `docs/03`, `docs/07`, `docs/decisions-needed.md` (§2a R1-R10, zakres M1 rozstrzygnięty), `docs/progress.md`, `CLAUDE.md`.
- Dane lokalne (gitignore): `data/l0/` 2,8 GB (16 miast, 2026-09-01…26), `data/raw_snap/` 2,0 GB, `data/t2/` 4,2 GB (pliki robocze sweepu, do skasowania po zatwierdzeniu wyników), `data/raw/`.
- Poza repo (scratchpad sesji): kod `easy-OTP` z `bccb17b` i venv `venv_fa`; odtworzenie: `git archive bccb17b tools/family_a_reconstruction tools/transit_charts`.

## Do zrobienia

1. **Decyzje autora po testach:** R1-R10 (`docs/decisions-needed.md` §2a) oraz GitHub Actions (`docs/10` §8).
2. **T7, T10, T12 powtórzyć** przy >= 40 dniach ważnych (ok. początek listopada); T21 przy każdej zmianie metody.
3. **M1** (po decyzjach): zakres 16 miast kandydujących, wszystkie dni od 2026-09-01.
4. Commit zmian po prośbie autora (nic nie jest zacommitowane od `041badb`).
