# Fixes applied to notebooks 09–13

**Date:** 30 September 2026
**Scope:** every finding in `docs/review-09-13.md`, plus two defects the fixing exposed.
**Status:** all five notebooks run end to end. `selection.py` replaces `select.py`.

---

## The headline

The pipeline now produces usable output.

| | before | after |
|---|---|---|
| predicted slump for a 120 mm order | **276 mm** | **120.2 mm** |
| `P_slump` on the proposals | 1.5 × 10⁻⁷ | 0.81 |
| candidate water | 201.6 kg (30 kg above anything batched) | 152–177 kg (inside the plant's range) |
| SERVE candidates | **0**, structurally | **952** |
| residual mean | +155.7 mm | **+0.16 mm** |
| loop demo: predicted vs measured | — | 120.2 vs 118.0, **inside the 90 % band** |

---

## 1. The root defect, and a second one underneath it

### 1a. Layer 0 never applied the cl 5.3 admixture water reduction

`[IS]` IS 10262 cl 5.3 permits the calculated water to be reduced by chemical admixture —
5–10 percent for water reducers, 20–30 percent and above for superplasticizers — but fixes
no value; Annex C-6 took 23 percent "based on trial data".

**Fixed.** `Requirement.water_reduction_pct` is now a required input whenever an admixture
is dosed. `design_mix` **refuses** rather than designing at 0 percent.

**And the value is fitted from this plant, not borrowed.** Notebook 10 §4b backs the
reduction out of the five design families — the Table 4 + cl 5.3 demand for each batch's
*measured* slump is computable, and the batched water is recorded:

```
reduction% = 3.709 + 14.037 x SP%_of_binder
  n = 256      R2 = 0.7303
  leave-one-family-out MAE = 1.41 percentage points  (about 2.8 kg of water)
  every family's bias within +/- 1.5 pp
```

**This is the one relation in the project that generalises across families.**

`[U]` The plant sits at 12.4–24.4 percent across its dose range, which is *between* cl 5.3's
two quoted bands. Whether the admixture is a water reducer, a mid-range, or a
superplasticizer below its appropriate dosage is a material question for the plant.

### 1b. The baseline inverted the NET water — found while fixing 1a

`[IS]` cl 5.3 carries **two** provisions that had been collapsed:

**(a)** water demand rises with target slump, ~3 percent per 25 mm on the Table 4 base;
**(b)** that water may **then be reduced** by admixture.

Provision (b) is taken *in order to hold the same slump*. Annex A-6 computes 191.58 kg for
75 mm and then batches far less because a superplasticizer is used — it is still a 75 mm
mix. So the slump a batch implies comes from its **gross** water.

Inverting the net water says superplasticizer **lowers** slump. It was visible in the
screen: predicted slump fell from 103 mm to 34 mm as the dose rose.

**Fixed.** The net water is un-reduced first:

```
W_gross = W_net / (1 - reduction/100)
S       = 50 + (W_gross / W_table4 - 1) x (25 / 0.03)
```

The reduction comes from the dose relation, independent of the measured slump, or the
baseline would be circular. Result: baseline mean **109.4 mm** against a measured
**109.5 mm**, residual mean **0.16 mm**.

### 1c. The coupling the project brief asks for now exists

`screen()` rebuilds the requirement **per candidate** from that candidate's own dose. More
superplasticiser → less water → less binder at the same w/c → different aggregate split →
different slump and strength. The admixture knob finally moves something upstream.

---

## 2. Gates

| gate | before | after |
|---|---|---|
| G1 water direction | PASS but **tautological** | **PASS**, and now a real test |
| G2 IS 10262 annex fixtures | PASS (7/7) | **PASS (7/7)** |
| G5 \|bias\| ≤ 25 mm, every family | **FAIL** — worst 40.3 mm | **PASS** — worst 14.5 mm |
| G6 pooled skill > 0 | FAIL — −1.43 | **FAIL** — −0.83 (improved 42 %) |
| G7 determinism | PASS | **PASS** (952 vs 952) |
| G8 validation level | PASS | **PASS** |
| **G9 coverage ≥ 80 % per family** (new) | — | **PASS** — worst 82.1 % (was 39.3 %) |

G6 is the one still failing. With five independent design families, holding one out is
close to holding out a whole grade level, and the model has nothing to extrapolate from.

Other measures that moved: out-of-group RMSE 21.86 → **18.93 mm**; RMS of per-family bias
21.67 → **8.80 mm**; families where `MAE == |bias|` exactly (pure offset, no scatter) 2 of 5
→ **0 of 5**.

---

## 3. My own error, stated plainly

The SCM search range was bounded with **`IS 10262 Table 9`**. That table is
**cl 6.2.6, Section 3 — high-strength concrete, M65 and above**, and `is_rules` records its
status as **GUIDANCE**, which is not in `BINDING` = {verified, project_constraint}.

Using it as a hard bound on an M30 mix was wrong twice: **wrong section**, and **guidance
treated as binding**. It is what made SERVE structurally empty — Table 9's fly-ash range
starts at 15 percent while this plant has only ever run 7–14.

**Fixed.** For Section 2 the binding limits are `[IS]` IS 456 cl 8.2.4.2 on **cement** and
`[IS]` IS 456 Table 5 Note 1 on how much fly ash may **count**, both enforced by
`compliance_gate`. The search range is now a declared `[PC]` project choice printed on every
run, with the step tightened to 0.025 so it reaches the band the plant actually uses.
Table 9 is used only when `route_domain()` returns Section 3.

---

## 4. Guards that now guard

| was | now |
|---|---|
| `volume_closure_m3` **identically 1.0** — a HARD gate check that could never fail | recomputed **independently** from the returned masses and specific gravities. Fixture (g) proves it: a misread CA specific gravity shows up as a 5.56 % closure error |
| `flyash_frac = -0.10` → −40 kg, `decided=True` | refused |
| `training_support(model, …)` → `None` → SERVE accepted everything | takes the training frame only, **raises** on anything else; `inside_support` returns True/False, never None |
| source verification printed and discarded | carried on every mix; `decided` requires `sources_verified` |
| `MixDesign` mutable — `decided` writable | `frozen=True` |
| supplied `wc_ratio` validated then silently discarded | supplying **both** binder and w/c is refused — water is fixed by cl 5.3, so they over-determine the mix |
| fly ash / GGBS specific gravities hardcoded 2.20 / 2.90 | `MaterialState.flyash_sg` / `ggbs_sg`; **refuses** if an SCM is used without one |
| `pumpable` a boolean taking the full cl 5.5.2 allowance, labelled `DERIVED_FROM_STANDARD` | `pumpable_reduction_frac` ∈ [0,1], labelled `[PC]` — cl 5.5.2 says "up to 10 percent" |
| `msa = 20.6` designed off the 20 mm row and recorded 20.6 | refused; `msa_mm` has no default |
| `predict_strength` rescaled noise a second time (908×) | `noise_in_normalised_units` defaults **False**, matching what the fitter stores |
| `concrete_temp = ... if False else 30.0` | training median, stored by notebook 10 |
| `refused` summed to 5 384 against 4 900 | `refused_exclusive` (sums exactly: 43 148 + 952 = 44 100) and `refused_diagnostic` (overlapping, never summed) |
| `assert se["gate_decided"].all()` skipped because serve was empty | asserts on whichever mode produced rows, and fails if neither did |
| **`select.py` could never be imported** — `select` is a C built-in | **`selection.py`** |

`design_mix` now carries seven counter-example fixtures, all firing.

---

## 5. Corrections to what I reported earlier

- **r = −0.09 was the wrong number.** It is computed over all 264 rows including the 8
  orphans that notebook 10 quarantines. On the five fitted families it is **−0.528**; within
  family **+0.101**. The conclusion holds on the within-family figure.
- **Skill −1.71 was the wrong statistic** — the mean of five ratios. Pooled is what is
  reported now.
- **The G1 sweep was tautological.** The GP never sees water, so its output was constant
  across the sweep; the test checked only that an affine function increases. It now asserts
  the GP output is **invariant** to water — a condition that can fail.
- **`out_of_group_sd_mm` was an RMS of MAEs used as a σ.** Split into `rmse_mm` (the width)
  and `bias_rms_mm` (how far the centre moves). Both are reported; both are used.
- **Achievability measured the wrong thing.** It now separates **OFFSET** (the predicted
  mean is already outside the band — bias) from **WIDTH** (the band is narrower than the
  model's uncertainty — variance), and says which.
- **The 600 µm refusal was correct all along.** Table 9 is printed in whole percent and BIS
  states no rule for a fractional value between bands, so 34.5 % is refused rather than
  rounded — already flagged NOT VERIFIED FROM PRIMARY STANDARD SOURCE in the earlier
  specification. Only my docstring ("contiguous and exhaustive") and the error message were
  wrong. Both fixed.

---

## 6. What is still open

1. `[U]` **G6 still fails.** Pooled skill −0.83 on five families. This is a data-coverage
   limit, not a wiring one, and it is why notebook 12 routes to EXPLORE.
2. **The strength arm has never run.** `strength_model.joblib` carries
   `{target, members, noise, q90, feature_range, n_groups}` — no `predict`, no `gp`. So
   `P_strength` is NaN and `rank_serve` **refuses to rank**, which is the fail-safe rule
   behaving correctly. SERVE cannot complete until a usable strength model exists.
3. `[PC]` Every cost and carbon figure is a `PLACEHOLDER` and says so on its face.
4. `[U]` The cl 5.3 reduction is fitted from this plant's history, so it is a plant value,
   not a material property. A change of admixture brand invalidates it — which is what the
   `state_hash` on every proposal exists to catch.
5. `[EI]` Inverting cl 5.3 into a slump response remains an engineering interpretation.
   cl 5.3 ends *"or may be established by trial"*, and **IS 10262 states no slump-response
   slope anywhere.** This must never be written up as an IS requirement.

---

**Weakest link:** the cl 5.3 reduction relation is fitted on five families whose
superplasticiser doses span only 0.62–1.48 percent of binder, and it is now load-bearing —
it sets the water for every candidate. Outside that dose range it is extrapolation, and the
screen searches 0.6–1.5 so it is currently just inside. **Check:** before widening the
admixture grid beyond 1.5 percent, confirm the relation still holds there, or clamp the
reduction at the fitted range and flag anything beyond it.
