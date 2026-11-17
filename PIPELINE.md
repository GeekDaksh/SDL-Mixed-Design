# The pipeline — notebooks 00 to 15

Every stage is a notebook. A notebook that holds reusable logic writes its own `.py` from
the cells it just ran (`00` → `is_rules.py`, `09` → `layer0.py`, …), so the code that ships
is the code that was tested.

## Run order

```
00_is_codes_layer.ipynb           -> is_rules.py      RE-RUN NOW (v4: 102 rules, 63 fixtures)
      |
09_layer0_design_engine.ipynb     -> layer0.py        (+ IS 10262 trial set, lab batch sheet)
      |
10_workability_residual_GP.ipynb  -> workability_residual.py   + workability_residual_model.joblib
10b_strength_residual_GP.ipynb    -> strength_residual.py      + strength_residual_model.joblib
      |
11_achievability_and_screen.ipynb -> screen.py        (+ the plant's own materials: plant_orders)
      |
12_select_serve_explore.ipynb     -> selection.py     the M30 / 120 mm / severe order
      |
14_run_all_grades.ipynb           every grade in the dataset
      |
15_lab_trial_pack.ipynb           15_lab_trial_pack.xlsx  <- give this to the lab
      |
13_trial_loop_and_update.ipynb    -> loop.py  (after the trials: log results, refit 10 / 10b)
```

Run every cell, top to bottom, in this order. `IS_codes/` must hold the 16 PDFs listed in
`00` — each is hash-checked; a `missing` or `mismatch` makes every mix "not decided".

**Packages:** `numpy pandas scikit-learn scipy joblib openpyxl`.

## What comes out for each order

| file | what it is |
|---|---|
| `12_next_designs.csv` / `14_all_grades_designs.csv` | **5 designs** per order (SERVE): inside the data, through the full IS gate, ranked on cost and carbon |
| `12_next_experiments.csv` / `14_all_grades_trials.csv` | **3 physical trials** per order: IS 10262 cl 5.8 Trial Mix 1 (→ 2), 3 and 4 — same water, w/cm about −10 % and +10 % |
| `12_trial_batches.csv` / `14_all_grades_trial_batches.csv` | what to weigh for each trial (0.050 m³ batch), corrected for aggregate moisture |
| `12_explore_proposals.csv` / `14_all_grades_explore_proposals.csv` | 3 optional exploration proposals (where the models know least) — expert review first |
| `15_lab_trial_pack.xlsx` | everything above for the lab, with editable moisture cells, tests and clauses, results log, report checklist |

Every mix is `COMPUTATIONALLY_COMPLIANT` only. None has been cast.

## What each notebook does

**00 — IS layer.** Every standards value, read from the frozen PDF, with its clause. v4 adds
IS 455 : 2015 (GGBS counting), IS 269 : 2015 (OPC), IS 456 cl 5.1 / 5.2.1 / Table 5 Note 1
(which cement + addition combinations are allowed, and what may be counted), IS 10262 cl 5.1.1
NOTE (admixture water in w/c), and the trial / test layer (IS 10262 cl 5.8 + Annex A,
IS 1199 Parts 1, 2, 3, 5, IS 516 Part 1/Sec 1, IS 2386 Part 3).

**09 — Layer 0.** One `design_mix()` built only from `is_rules`. New: `trial_set()` (the three
IS 10262 cl 5.8 trials) and `batch_sheet()` (Annex A-10 / A-11 weights).

**10 / 10b — Models.** Slump and strength = IS 10262 baseline + a learned correction.

**11 — Screen.** Every legal combination of binder, fly ash share and admixture dose, checked
by the gate. New: `plant_orders()` builds each order from the plant's own materials; the only
450 kg/m³ limit is the IS one, on cement.

**12 — Select.** `lab_package()`: 5 designs + 3 IS trials + 3 exploration proposals.

**14 — All grades.** The same `lab_package()` for every family in the dataset.

**15 — Lab pack.** The Excel workbook the laboratory works from.

**13 — Loop.** After the lab: eight outcomes kept apart, validation levels, refit.

## Gates

| gate | checks | status |
|---|---|---|
| G1 | water direction positive everywhere | PASS |
| G2 | IS 10262 Annexes A-6, C-6, A-8, C-8 + cl 5.8 / A-11 reproduced | PASS — 8/8 |
| G5 | slump bias within ±25 mm, every family | PASS |
| G6 | slump pooled out-of-family skill > 0 | **FAIL** — −0.92 |
| G7 | same requirement twice, identical output | PASS |
| G9 | slump coverage ≥ 80 % per family | **FAIL** — worst 75.0 % |
| G10–G13 | strength direction, bias, skill (+0.852), coverage | PASS |
| S01 | IS layer fixtures | PASS — 63/63 |

The slump model is the weak part. That is why every design goes to physical trials.


## Notebook 18 — plant P1 orders on PPC, planned by the AI models

`18_P1_PPC_ai_models_next_experiments.ipynb` -> `p1_ppc_loop.py`

- Inputs: P1's M30 (150 mm) and M35 (180 mm) from `Concrete_Data_Entry_Template_R1.xlsx`; cement switched
  to PPC and the materials the models were trained on (Plant D), so notebooks 10 / 10b apply.
- Out: `18_P1_PPC_lab_pack.xlsx` (give this to the lab: designs, trials, learning mixes, batch sheets,
  results log) + one CSV per grade: `18_P1_PPC_best_next_experiment_M30.csv` / `_M35.csv`.
- Trials are picked to teach the slump model most (information worked out before casting) [BO].
- Loop: lab fills `P1_PPC_results_log.csv` -> re-run 18 -> both models learn (exact Bayesian update,
  saved as `18_*_model_updated.joblib`; the 10 / 10b files are untouched) -> next round planned.
- The old OPC notebook 17 is in `_to_delete/notebook17_opc/`.

## Notebook 19 — M10 and M15 on PPC, planned by the AI models

`19_M10_M15_PPC_ai_models_next_experiments.ipynb` (run 18 once first: it writes `p1_ppc_loop.py`).
Both notebooks are built from one builder, so they work the same way.

- IS 456 Table 5 / cl 6.1.2: RCC needs M20 or more, so M10 / M15 are planned as PCC, mild exposure,
  130 mm slump (ASSUMED). IS 456 Table 11 prints no M10 row: the engineer sets M10 acceptance.
- At 130 mm the IS water + Table 5 w/c 0.60 + the models' range (binder >= ~327) give the SAME mix for
  M10 and M15 -> one batch serves both (the log says so).
- Out: `19_M10_M15_PPC_lab_pack.xlsx` + `19_M10_M15_PPC_best_next_experiment_M10.csv` / `_M15.csv`.
- Lab pack sheet 'Leanest IS mix': the leanest mix the IS code alone allows (265 kg/m3 PPC),
  outside the models' range; added as an optional learning cast, engineer approval first.
- Lab fills `M10_M15_PPC_results_log.csv`; re-running 18 or 19 makes the models learn from ALL PPC logs.

Only the best-next-experiment CSVs are written for 18 / 19; everything else is in the lab pack. The results-log CSV
appears once the lab saves the 'Results log' sheet as CSV. Older 16/18/19 CSVs are in `_to_delete/old_case_csvs/`.
