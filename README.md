# Self-Driving Lab for M-Sand Concrete

An AI lab assistant that designs concrete mixes made with manufactured sand (M-Sand).
It follows the Indian Standards: IS 456 and IS 10262. Then it picks the next lab trials to run.

Final-year capstone, NMIMS MPSTME. Paper submitted to *The Indian Concrete Journal*.

## What it does

1. **Follows the IS codes.** Every standards value is written as a rule, and each rule names its clause (102 rules, 63 test cases).
2. **Designs the mix.** An IS 10262 design engine works out every mix by the code.
3. **Predicts strength and slump.** Each model starts from the IS 10262 baseline, and a Gaussian Process learns the correction.
   Each prediction comes with an uncertainty band.
4. **Screens candidates.** It tries every legal mix of binder, fly ash and admixture. A mix that fails the durability or IS checks is thrown out.
5. **Optimises.** Bayesian optimisation ranks the mixes that pass on cost and carbon.
6. **Plans the lab work.** It gives 5 designs and 3 physical trials per order, and an Excel pack for the lab.
7. **Learns.** After the lab casts the trials, the results go back into the models, and the next round is planned.

## Results (from the gates in `PIPELINE.md`)

| Check | Result |
|---|---|
| IS layer test cases | 63 / 63 pass |
| IS 10262 worked examples reproduced | 8 / 8 |
| Strength model, out-of-family skill | +0.85 (pass) |
| Strength bias and coverage | pass |
| Slump model, out-of-family skill | **fails** (−0.92) |

The slump model is the weak part. So every design goes to a physical trial before anyone uses it.
Every mix here is computed to comply with the code. None has been cast yet.

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

Notebooks 02, 03, 03b, 08 and 08b are the data preparation, model audit and optimiser benchmark.
`PIPELINE.md` explains each step. `docs/` has the audit notes.

## Data

The batch data comes from partner ready-mix plants. It is **not included** in this repo.
To run the notebooks, put your own data in `data/01_RAW_dataset.csv`, in the same column format.
The IS code PDFs are copyrighted by BIS, so they are not included either. Put them in `IS_codes/`.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

## Team

Daksh Patil and Aruja Tiwary.
