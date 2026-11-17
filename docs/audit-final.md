# Final audit — data leakage and flow logic

**Date:** 1 October 2026
**Scope:** notebooks 09, 10, 10b, 11, 12, 13 as committed, run end to end in a clean
directory with all nine IS sources hash-verified.
**Result:** five defects found, all fixed, chain rerun clean. Two gate results changed.

---

## Clean — checked, nothing found

| check | result |
|---|---|
| **Duplicate rows** | 0 exact duplicates in either dataset; 0 on design family + batch date + batch no + water + slump |
| **Experimental unit** | validation groups by **design family**, which is coarser than batch. A batch can never sit on both sides of a fold |
| **Same batches feed both models** | all 256 `record_id`s appear in both datasets. Not leakage — the two models predict different targets and are never validated against each other |
| **Target leakage, strength** | no feature is derived from the cubes. `cement_28d_strength` is a cement **certificate** value, measured before the concrete is cast (r with fc = +0.001) |
| **Target leakage, slump** | no model feature is derived from slump, flow, compacting factor or Vee-Bee |
| **Per-fold refit** | `StandardScaler` and `normalize_y` are refit from the training fold on every call, in both models. The Fig 1 and Table 4 baselines are fixed by the standard, so they cannot leak |
| **Feature definitions** | `wb_ratio`, `scm_frac`, `sp_pct_binder`, `agg_binder_ratio` recompute exactly from the stored masses (max error 5 × 10⁻⁵) |

---

## Defects found and fixed

### A — the cl 5.3 water fit leaked the held-out family into its own baseline · LEAKAGE

The cl 5.3 reduction relation is fitted on *implied* reductions,
`1 − W / W_demand(measured slump)`. **It is built from measured slump.** Notebook 10 fitted
it once on all five families and reused that fit inside leave-one-family-out, so every
held-out family helped build the baseline it was then scored against.

**Fixed:** refit inside every fold, in both the leave-one-family-out loop and the coverage
loop. The all-family fit is still used for the deployed model, which is correct.

| | leaky | clean |
|---|---|---|
| pooled skill | −0.825 | **−0.922** |
| out-of-family RMSE | 18.93 mm | **19.43 mm** |
| worst family bias | 14.50 mm | **18.94 mm** |

### D — models fed a volume fraction, trained on a mass fraction · FLOW

Both training datasets store `fine_frac_of_agg` as a **mass** fraction,
`fine_kg / (fine_kg + coarse_kg)`. Layer 0 stored it as a **volume** fraction, because
IS 10262 Table 5 is a volume table. Every candidate fed both models a value about **0.008
too high**, and the support box compared candidate volume against training mass.

**Fixed:** `MixDesign.fine_mass_frac_of_agg` added. Candidates now carry the mass fraction
for the models and the volume fraction separately as `fine_vol_frac` for the standards
checks. Verified: the value fed to the models now equals the true mass fraction exactly.

### D2 — a compliance claim that compared mass to a volume limit · WRONG CLAIM

Notebook 10 reported that **none** of the five families exceeded the most permissive
IS 10262 Table 5 + cl 5.5.2 fine-fraction cap (0.460). That compared the mass-fraction
column to a volume-fraction limit.

**Recomputed by volume, with each row's own specific gravities: 9 of 256 rows exceed it —
all in M40-P-20MS-02**, up to 0.4679. And that is the *most* permissive cap
(Zone I, w/c 0.50); `[IS]` cl 5.5.1 lowers the permitted fine fraction as w/c falls, so
each row's own cap is tighter. A compliance question for the plant, flagged — not a verdict.

**I reported the wrong conclusion earlier. This is the correct one.**

### E — calibration scored on the data it was calibrated with · LEAKAGE (minor)

The coverage check widened each family's interval to at least the leave-one-family-out
RMSE — computed over **all** folds, including the family being scored.

**Fixed:** the width floor now comes from the other four families' residuals only, in both
10 and 10b.

| worst family coverage | leaky | clean |
|---|---|---|
| slump | 82.1 % | **75.0 % (M40)** |
| strength | 84.3 % | **82.4 % (M35)** |

### G — a supplied material value never reached the model · FLOW

`MaterialState.cement_28d_strength` existed, but `screen()` never passed it to the strength
model, which silently fell back to the training median (51.3 N/mm²) for every candidate.
Concrete temperature had no order-level input at all.

**Fixed:** `cement_28d_strength` is taken from the `MaterialState` when supplied, and
`Requirement.concrete_temp_c` added. Only when neither is given does a model fall back to
its training median — and every candidate row then carries a `_source` column saying so.

---

## Gates after the clean rerun

| gate | before audit | after audit |
|---|---|---|
| G5 slump bias ≤ 25 mm, every family | PASS (14.5) | **PASS (18.9)** |
| G6 slump pooled skill > 0 | FAIL (−0.83) | **FAIL (−0.92)** |
| **G9 slump coverage ≥ 80 %, every family** | PASS (82.1 %) | **FAIL (75.0 %)** |
| G11 strength bias ≤ 5 N/mm², every family | PASS (1.74) | **PASS (1.74)** |
| G12 strength pooled skill > 0 | PASS (+0.852) | **PASS (+0.852)** |
| G13 strength coverage ≥ 80 %, every family | PASS (84.3 %) | **PASS (82.4 %)** |

**G9 passed before only because of the leak.** The strength model is untouched by every
defect that mattered — its baseline comes from the standard, not from the data — and it
passes on clean numbers.

---

## End-to-end, clean

```
44 100 combinations
  15 541  gate: IS 456 Table 5 max free w/c
   3 530  gate: IS 456 Table 5 min binder
  24 077  outside the training box
      82  outside the cl 5.3 fitted water range
     870  candidates              43 230 + 870 = 44 100, balances

P_strength >= 0.90   143
P_slump    >= 0.80   441     (was 616 with the leak)
both                  74     (was 81)

SERVE, first on the cost-carbon front -- unchanged:
binder 410.0  cement 358.75  fly ash 51.25  water 154.52 kg/m3  SP 1.4 %  w/c 0.377
P_strength 0.925   P_slump 0.801
```

The ranked mix is the same. Its `P_slump` fell from 0.812 to **0.801** — it now clears the
0.80 threshold by one thousandth.

---

**Weakest link:** the recommended mix passes the slump threshold by 0.001, on a slump model
that fails two of its own gates (G6, G9). Any small change — a tolerance, a threshold, one
more family — can drop it. The strength side of that recommendation is sound; the slump
side is a proposal to **trial**, and should be presented that way.
