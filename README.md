# Self-Driving Lab for M-Sand Concrete

An AI lab assistant that designs concrete mixes made with manufactured sand (M-Sand).
It follows the Indian Standards: IS 456 and IS 10262. Then it picks the next lab trials to run.

Final-year capstone, NMIMS MPSTME. Paper submitted to *The Indian Concrete Journal*:
*A code-constrained decision engine for M-sand concrete mix design from Indian ready-mix plant data.*

**[Live demo →](https://geekdaksh.github.io/SDL-Mixed-Design/)** Design an order in your browser. The real rule engine runs on your device, and a distilled copy of the trained models scores every mix.

## What it does

1. **Follows the IS codes.** Every standards value is written as a rule, and each rule names its clause (102 rules, 63 test cases).
2. **Designs the mix.** An IS 10262 design engine works out every mix by the code.
3. **Predicts strength and slump.** Each model averages a ridge regression and several Gaussian processes, with a cross-conformal 90% interval.
4. **Screens candidates.** It tries every legal mix of binder, fly ash and admixture. A mix that fails the durability or IS checks is thrown out.
5. **Optimises.** Bayesian optimisation ranks the mixes that pass on cost and carbon.
6. **Plans the lab work.** It gives 5 designs and 3 physical trials per order, and an Excel pack for the lab.
7. **Learns.** After the lab casts the trials, the results go back into the models, and the next round is planned.

## Results

From the paper. Scores are on whole recipes held out by grouped 10-fold cross-validation, repeated three times.

| | Strength (82 recipes) | Slump (40 recipes) |
|---|---|---|
| R² | 0.922 | 0.791 |
| RMSE | 4.73 MPa | 28.1 mm |
| 90% interval coverage | 91.5% | 92.5% |

| Check (from `PIPELINE.md`) | Result |
|---|---|
| IS layer test cases | 63 / 63 pass |
| IS 10262 worked examples reproduced | 8 / 8 |
| Slump model, out-of-family skill | **fails** (−0.92) |

The slump model is the weak part. Its error is larger than the ±25 mm a plant must hold, so the engine
warns when it can't promise a slump and sends an IS 10262 trial set instead.

**Validation casts.** Two engine trial mixes were cast. Both measured slumps fell inside their predicted
90% ranges. The M15 mix passed its 7-day mark (18.6 against 14.5 MPa). The M30 mix missed it (23.0 against
26.8 MPa), as the model had predicted after the engineer cut the admixture dose. These are two mixes tested
at 7 days: an early check, not an acceptance test.

## Run order

```
00_is_codes_layer          -> is_rules.py
09_layer0_design_engine    -> layer0.py
10 / 10b residual GPs      -> workability_residual.py, strength_residual.py
11_achievability_and_screen-> screen.py
12_select_serve_explore    -> selection.py
14_run_all_grades
15_lab_trial_pack          -> Excel pack for the lab
13_trial_loop_and_update   -> loop.py (after the trials)
```

Notebook 03 trains the strength and slump ensembles reported in the paper. Notebooks 02, 03b, 08 and 08b are the data preparation, plant-transfer check and optimiser benchmark. `docs/index.html` is the live demo.
`PIPELINE.md` explains each step. `docs/` has the audit notes.

## Data

The 401 mix records come from ten ready-mix plants and laboratories in Maharashtra. They are **not included** here; the paper's data statement applies (available from the corresponding author on request, subject to the data partners' consent). The demo's distilled models were trained only on engine-generated mixes, so they hold no plant records.
To run the notebooks, put your own data in `data/01_RAW_dataset.csv`, in the same column format.
The IS code PDFs are copyrighted by BIS, so they are not included either. Put them in `IS_codes/`.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

## Team

Aruja Tiwary, Lubhana Mutha and Daksh Patil, guided by Dr Vaishali Kulkarni (NMIMS MPSTME).
