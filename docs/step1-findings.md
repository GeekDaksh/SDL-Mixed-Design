# Step 1 — built, tested, and one of my own claims corrected

**Date:** 30 September 2026
**Mode:** D (results check) run on the claim my own plan was built on.
**Files produced:** `layer0/is_workability.py` (in `SDL Implementation`, self-test passes)

---

## Plain words, first

The plan said the slump model "learned the water effect backwards" and that fixing it
with the IS relation would repair it. I checked that against the actual dataset.

The model is not backwards because it is broken. It is backwards because **the data
cannot tell it which way water goes.** Water never moves on its own in this dataset —
every time water goes down, superplasticiser and binder go up.

So the fix stays the same. The reason for it changes: the standard must supply the water
direction because the data **cannot**. That is fail-safe behaviour, not a bug fix. It is a
stronger argument, and it is the honest one.

---

## 1. What was built

`layer0/is_workability.py` — pure arithmetic, no imports, self-test green.

**`[IS]` IS 10262:2019, Table 4 (Clause 5.3)** — water per m³, angular coarse aggregate,
50 mm slump, saturated surface dry:

| nominal max size | water |
|---|---|
| 10 mm | 208 kg |
| 20 mm | 186 kg |
| 40 mm | 165 kg |

**`[IS]` IS 10262:2019 Clause 5.3, verbatim:** *"For the desired workability (other than
50 mm slump), the required water content may be increased or decreased by about 3 percent
for each increase or decrease of 25 mm slump or may be established by trial."*

**`[V]` The 3 percent is taken on the Table 4 base, linear, non-compounding, pro-rata on
fractional 25 mm steps.** Confirmed against both printed worked examples:

```
W(S) = W_table4 x (1 + 0.03 x (S - 50) / 25)

Annex A-6   75 mm, 20 mm agg  ->  191.58 kg   standard prints 191.58   OK
Annex C-6  120 mm, 20 mm agg  ->  201.62 kg   standard prints 201.62   OK
```

**Source-handling warning.** A text extraction of the IS 10262 PDF renders Annex C-6's
"8.4 percent" as "84" — the decimal point is lost. Reading it as 84 percent gives 342 kg
and does not reconcile. The printed 201.62 is what confirms 8.4. Anyone re-deriving this
from extracted text must check against the printed result.

Resulting slope, **`[EI]`** by inversion:

| msa | dW/dS | dS/dW |
|---|---|---|
| 10 mm | 0.2496 kg/mm | 4.006 mm/kg |
| 20 mm | 0.2232 kg/mm | 4.480 mm/kg |
| 40 mm | 0.1980 kg/mm | 5.051 mm/kg |

### The classification matters

`[IS]` Table 4's values, the 50 mm basis, the angular/SSD basis, and "about 3 percent per
25 mm" are Indian Standard requirements.

`[EI]` **Inverting them into a slump-response slope is this project's engineering
interpretation, not an IS requirement.** Clause 5.3 is a *design* rule — how much water to
batch to reach a desired slump. It ends with *"or may be established by trial"*, so the
standard does not assert the inverse as a measured law. IS 10262:2019 states no
slump-response slope anywhere. This must never be written up as an IS requirement.

`[EI]` Clause 5.3 separately allows water reduction of 5–10 percent for water-reducing
admixtures and 20–30 percent and above for superplasticizers; Annex C-6 applies 23 percent
"based on trial data". So this relation holds **at fixed admixture dose**. The admixture
effect is deliberately left to the residual model.

---

## 2. What the data says — the correction

264 usable rows. **12 design groups. And 80.1 percent of the slump variance sits *between*
groups, only 19.9 percent within.** So the model is learning from about 12 points, not 264.

Of those 12 groups, only five are real design families — M20/M25/M30/M35/M40-P-20MS —
carrying 256 of the 264 rows. The other seven are single stray rows whose group keys are
numeric concatenations (`150.0|110.0|0.0|170.`), not design IDs. **Effective independent
sample size is nearer 5 than 12.**

### Water is not identifiable

```
correlation with measured slump      correlation with water
  water           -0.09               superplasticiser %   -0.743
  superplasticiser %   +0.522         superplasticiser kg  -0.793
  scm fraction         +0.796         binder kg            -0.795
  fine frac of agg     +0.523         w/b ratio            +0.850
  binder kg            +0.349
  concrete temp        -0.009
```

Water against slump: **r = −0.09.** Effectively nothing.
Water against superplasticiser: **r = −0.79.** Water against binder: **r = −0.80.**

Water span inside a design group is only **5.1 to 5.8 kg** — worth about 24 mm at the IS
slope, against an observed within-group slump span of 37 to 48 mm. Across the whole
dataset water spans just 152.4 to 173.0 kg, and it moves *opposite* to slump: the M40
family uses the least water (152–158) and shows the highest slump (102–142).

**There is no observation in this dataset where water moved while superplasticiser and
binder were held.** The water coefficient is therefore unidentifiable, and any model
fitting it will return an arbitrary sign. The learned model returning a negative one is
the expected outcome, not a defect.

### What this means for the plan

- **Step 1 is upgraded, not weakened.** Fixing the water slope from IS 10262 is no longer
  "correcting a mis-fit" — it is the fail-safe response to an unidentifiable parameter,
  which is what the project's own fail-safe rule requires.
- **Design choice, now load-bearing:** water must enter the slump prediction **only**
  through `is_slump_baseline()`. The residual model must therefore exclude every feature
  that is a function of batch water — `water_kg_m3`, `wb_ratio`, `paste_frac`, and any
  free-water term. This is enforced by `RESIDUAL_FEATURES_EXCLUDE` in the module. It makes
  gate G1 true **by construction** rather than something to test for, which is the whole
  point.
- **The residual must carry superplasticiser dose.** SP is the strongest legitimate
  correlate of slump here (`+0.52`) and the thing water is confounded with. Leaving it out
  would put the confound straight back into the residual.
- Subtracting the IS baseline raises the marginal spread (slump sd 22.77 mm → residual sd
  32.68 mm). That is expected and is not a failure: the baseline is uncentred by design
  (every mix uses 7–18 percent less water than Table 4 because of superplasticiser, so the
  baseline sits far below the measured level) and the residual model supplies the level.
  It does mean the residual's intercept does real work and must not be forced through zero.

### My overstatement, named

The plan's "wrong way on water in 67.6 percent of the near-feasible region" came from an
earlier grid analysis and is `[U]` here — I have not re-run it in this session. What I have
now verified is *why* it happens. Calling it a bug in the plan was wrong; it is the correct
response to collinear data. The plan text is being corrected.

---

## 3. Step 2 gains a compliance check

**`[IS]` IS 10262:2019 Table 5 (Clause 5.5)** — volume of coarse aggregate per unit volume
of total aggregate, at w/c 0.50, crushed angular aggregate, SSD:

| nominal max size | Zone IV | Zone III | Zone II | Zone I |
|---|---|---|---|---|
| 10 mm | 0.54 | 0.52 | 0.50 | 0.48 |
| 20 mm | 0.66 | 0.64 | 0.62 | 0.60 |
| 40 mm | 0.73 | 0.72 | 0.71 | 0.69 |

**`[IS]` Clause 5.5** — adjust by ±0.01 of CA volume for every ∓0.05 change in w/c.

**`[IS]` Clause 5.5.2** — for pumped concrete or congested reinforcement, CA from Table 5
may be reduced **up to 10 percent**, with the caution that resulting slump, w/c and
strength stay consistent with IS 456 and project specification.

**`[IS]` Table 5, Note 3** — crushed or mixed sand normally needs **lesser** fine aggregate;
in that case the coarse aggregate volume shall be **increased**.

So fine fraction is not one computed number — it is a **narrow band anchored by the
standard.** At 20 mm:

| zone | fine frac at Table 5 | fine frac at cl 5.5.2 −10% CA |
|---|---|---|
| IV | 0.340 | 0.406 |
| III | 0.360 | 0.424 |
| II | 0.380 | 0.442 |
| I | 0.400 | 0.460 |

**Observed in the dataset: 0.389 to 0.481.**

The top of the observed range sits **above 0.460**, which is the most fine aggregate that
Table 5 plus clause 5.5.2 permits at 20 mm even at Zone I. Note 3 pushes the permitted
fine fraction *down* for crushed sand, not up, so it does not license 0.481 either.

**Implication:** some rows in the training data use more fine aggregate than IS 10262
Table 5 with clause 5.5.2 allows. Step 2 must therefore do two things, not one:

1. compute the permitted fine-fraction band from zone, msa and w/c (cl 5.5 + 5.5.2), and
2. **flag every existing row that falls outside it**, rather than silently fitting it.

This is a `[U]` compliance question until each flagged row's zone and w/c are confirmed —
a row at Zone I with a low w/c gets a higher permitted CA and therefore a *lower* permitted
fine fraction, so the flag count may rise once cl 5.5's w/c adjustment is applied per row.

---

## 4. Revised work order

Unchanged in direction. Two steps are re-scoped and one is new.

| # | step | change |
|---|---|---|
| 1 | IS water→slump as the mean function | **done** — module written, self-test green. Justification upgraded to fail-safe. |
| 1b | Residual model excludes all water-derived features; must include SP dose | **new** — this is what makes G1 hold by construction |
| 2 | Fine fraction from Table 5 | **re-scoped** — compute a permitted *band* (cl 5.5 + 5.5.2 + Note 3), and flag the rows already outside it |
| 2b | Quarantine the 7 orphan single-row groups | **new** — malformed group keys, they are not design families |
| 3 | Stop double-counting WhiteKernel noise | unchanged |
| 4 | Turn the slump filter on | unchanged — safe only after 1 and 1b |
| 5 | Exhaustive grid instead of gradient descent | unchanged |
| 6 | Load the records already on disk, grouped by batch | unchanged, and now more urgent: effective n is ~5 design families |
| 7 | Re-export the 89-rule notebook | unchanged |
| 8 | Merge into `SDL1`, SERVE and EXPLORE as separate doors | unchanged |

---

## 5. Gates, restated

| gate | status |
|---|---|
| G1 water slope positive everywhere | **holds by construction** once 1b lands — not a test any more |
| G2 Table 4 / Annex A-6 and C-6 reproduced | **green** — self-test passes |
| G2b Table 5 / Annexes A-8, B-8, C-8, D-8, F-8 | pending Step 2 |
| G3 all 55 fixtures after re-export | pending Step 7 |
| G4 non-verified outcomes cannot decide a mix | pending |
| G5 LOPO slump bias within ±25 mm | pending — and see the weakest link |
| G6 out-of-plant skill above zero | pending |
| G7 same requirement twice, identical output | pending Step 5 |
| G8 no output claims a level above COMPUTATIONALLY COMPLIANT | pending |

---

**Weakest link:** G5 and G6 may not be reachable with five independent design families,
whatever is done to the model — 80.1 percent of the slump variance is between groups, so
leave-one-plant-out is close to leave-one-point-out and its confidence interval will stay
wide. **Check:** before building anything further on the residual model, refit with the five
real families only and report leave-one-group-out error with its interval. If that interval
straddles the ±25 mm band, the honest output is the achievability check in step [3] of the
pipeline — the system states that the band cannot be guaranteed — and not a slump number
dressed up as a prediction.
