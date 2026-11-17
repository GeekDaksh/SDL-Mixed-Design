# The Optimised Pipeline — Final Plan

**Date:** 30 September 2026
**Repo:** `github.com/GeekDaksh/SDL1` (folder `SDL Implementation`, branch `main`, 32 files tracked)
**Language of this document:** plain. Every engineering rule still carries its standard and clause.

> **CORRECTION, same day — read `docs/step1-findings.md` alongside this.**
> Step 1 is built and its self-test passes. Checking it against the dataset changed the
> *reason* for Steps 1 and 2, not their direction:
> - The slump model is not "wrong-signed" because it is broken. Water is collinear with
>   superplasticiser (r = −0.79) and binder (r = −0.80) and never moves independently, so
>   the water coefficient is **unidentifiable**. Supplying it from IS 10262 is fail-safe
>   behaviour, not a bug fix. Section 1's "gets the answer backwards" overstates it.
> - Effective sample size is **~5 design families**, not 40 groups: 80.1% of slump variance
>   is between groups.
> - Step 2 is re-scoped: fine fraction is a permitted **band** (Table 5 + cl 5.5 + cl 5.5.2
>   + Note 3), and some existing rows sit above it and must be flagged.
> - Two steps added: 1b (residual model excludes all water-derived features) and 2b
>   (quarantine 7 malformed single-row groups).

---

## 0. The one idea that fixes everything

Right now the system tries to **learn** things the standard already **tells** it.

The models are asked to learn how water affects slump, and how sand share affects slump.
IS 10262:2019 already answers both. So the model spends its small amount of data
re-learning a known answer, gets the answer backwards, and then the optimiser follows
that backwards answer.

**The fix:** let the standard supply the main effect. Let the model learn only the
small left-over part.

That single change is what turns two half-working pipelines into one working one.

```
OLD:  slump  = model(everything)              <- model must discover physics
NEW:  slump  = IS_formula(water, slump_base)  <- standard supplies the direction
                + model(left-over)            <- model learns only plant quirks
```

Same data. Same code base. Correct sign, guaranteed.

---

## 1. Why this is needed (one paragraph, no excuses)

Both folders ship the **same** workability model file — verified by opening both pickles:
identical noise `0.09119264135846167`, identical q90 `1.6393`, 40 groups, identical
scaler means. That one shared model:

- points the **wrong way on water** in 67.6% of the near-feasible region
- points the **wrong way on sand share** in 100% of it
- misses slump by −29% to +110% when moved to a plant it was not trained on
- has **negative** out-of-plant skill: −0.28, confidence interval [−0.91, −0.06]

Negative skill means: on a new plant, the model is worse than just guessing the average.

And FinalSDL's own safety guard, which is meant to catch exactly this, asks only that
+10 kg of water must raise predicted slump by **0.65 mm**. IS 10262:2019 cl 5.3 with
Table 4 says the true answer is about **45 mm**. The guard is **~69× too weak** to
catch the very error it was written for.

Nothing above needs new data to fix. All of it is a wiring problem.

---

## 2. The pipeline, end to end

```
                    ENGINEER / CLIENT REQUIREMENT
                    grade · slump · exposure · RCC/PCC · msa
                                  |
   [1] INPUT GATE ................|  every value labelled: from standard /
                                  |  standard default / engineer / material /
                                  |  plant / experimental. Nothing silently filled.
                                  v
   [2] LAYER 0 — IS MIX DESIGN (deterministic, no ML allowed)
       target mean strength .......  IS 10262:2019 cl 4.2, Table 1, Table 2
       max free w/c ...............  IS 456:2000 Table 5
       min binder .................  IS 456:2000 Table 5
       min grade ..................  IS 456:2000 Table 5
       max cement 450 kg/m3 .......  IS 456:2000 cl 8.2.4.2  (cement only,
                                     fly ash and GGBS are NOT counted)
       water ......................  IS 10262:2019 Table 4 + cl 5.3
       coarse aggregate volume ....  IS 10262:2019 Table 5  (zone x msa)
       fine volume = 1 - CA volume   IS 10262:2019 Table 5
       volume closes to 1 m3 ......  IS 10262:2019 cl 5.5
       sand zone from 600 um ......  IS 383:2016 Table 9 + cl 6.3
                                  |
                                  v
   [3] ACHIEVABILITY CHECK  <-- runs BEFORE any optimisation
       "can this slump band be held at all, given how uncertain we are?"
       if no: say so now, in plain words, and stop. Do not return an empty list
       and look broken.
                                  |
                                  v
   [4] EXHAUSTIVE LEGAL SCREEN  (replaces gradient search)
       only 3 things are free:  binder total · SCM split · admixture dose
       water and fine share are COMPUTED in [2], not searched
       every point on a grid -> enumerate all of them, keep the legal ones
                                  |
                                  v
   [5] RESPONSE MODELS — standard first, model second
       strength = IS/Abrams baseline + GP on left-over
       slump    = IS 10262 cl 5.3 relation + GP on left-over
       then: calibrate the uncertainty (cross-fitted k)
             check we are inside known ground (support guard)
             adjust for this plant (LOPO tau)
                                  |
                                  v
   [6] RANK, DO NOT CHASE
       serving a real order   -> rank legal + achievable mixes on cost and carbon,
                                 subject to P(pass) thresholds
       running research       -> Bayesian optimisation over WHICH TRIALS TO CAST,
                                 not over the surrogate's own peak
                                  |
                                  v
   [7] EXPERT REVIEW  (human in the loop)
       rejection reasons are typed and stored separately:
       human-rejected-before-cast · material unavailable · too costly ·
       not constructable · physically failed · other
       a human "no" with no cast is NOT a data point for the model
                                  |
                                  v
   [8] CAST · MEASURE · LOG
       7-day result steers the next pick; 28-day result is the verdict
       cubes from one batch stay grouped as ONE experiment
       validation level stamped on every output:
       COMPUTATIONALLY COMPLIANT -> LAB -> TRIAL BATCH -> PRODUCTION
                                  |
                                  v
   [9] UPDATE
       refit the left-over model only, with batch-grouped cross-validation
       update this plant's tau
                                  |
                                  v
  [10] PLANT-SIDE SLUMP TRIM ......  IS 10262:2019 cl 5.8
       final workability correction happens at the plant, on the trial mix,
       the way the standard says — not inside the optimiser
                                  |
                                  +--> back to [4] for the next experiment
```

---

## 3. What comes from where

Nothing is rebuilt from scratch. Every block already exists in one of the two folders.

| Block | Take from | What it is |
|---|---|---|
| [1] input gate, provenance labels | A · `SDL Implementation` | the `Provenance` / `Status` enums already written |
| [2] Layer 0 | A · `is_rules.py` | 2,321 lines, 81 rules, `BINDING` + `HARD_MIX_CHECKS` + `decided` logic |
| [3] achievability | B · `FinalSDL` idea | small new module, cheapest thing in the plan |
| [4] exhaustive screen | B · `FinalSDL` | B already enumerates instead of descending |
| [5] calibration, support guard | B · `FinalSDL` | cross-fitted k, mean-vs-specimen separation |
| [5] plant transfer tau | A · `SDL Implementation` | `03b_plant_transfer_check.ipynb` |
| [6] BO over trials | A · `08_bayesian_optimiser_standalone.ipynb` | qNEHVI, priced survey, joint batch risk |
| [7] typed rejections | A | A is the only side that separates human "no" from a failed cast |
| [8] 7-day steering, batch grouping | A | already implemented |
| [8] batchable output | B | B outputs something a plant can actually weigh out |
| [9] grouped CV | B | B's tests already enforce it |
| [10] cl 5.8 trim | IS 10262:2019 | the standard, not either folder |

**A gives governance and honesty. B gives the search and the statistics. The merge keeps both.**

---

## 4. Build order — 8 steps, in this exact order

Each step is small, testable, and needs no data beyond what is on disk.

### Step 1 — Put the IS water→slump relation in as the mean function
**Where:** the workability model's fit and predict path.
**What:** predicted slump = IS baseline + GP(left-over).

The IS part, from **IS 10262:2019 Table 4** (186 kg/m³ at 20 mm nominal max size,
50 mm slump) and **cl 5.3** (water changes ±3% per ±25 mm of slump):

```
186 kg x 3%      = 5.58 kg of water per 25 mm of slump
25 mm / 5.58 kg  = 4.48 mm of slump per 1 kg of water
so +10 kg water  ~ +45 mm slump
```

The GP is then fitted on `measured_slump − IS_predicted_slump`.

**Why first:** this is the root cause. Every downstream number improves for free.
**Test that must pass:** slope on water is positive at 100% of grid points (it is
now wrong at 67.6%).

### Step 2 — Compute the fine share, stop searching it
**Where:** the decision space definition.
**What:** delete `fine_vol_frac` from the searched variables. Compute it from
**IS 10262:2019 Table 5** (coarse aggregate volume by zone × nominal max size),
fine volume = 1 − coarse volume, per **cl 5.5**.

**Why:** this is the dimension where the model is wrong 100% of the time — and it is
the one dimension the standard fully determines. Searching it is searching noise.
**Bonus:** the search drops from 5–6 dimensions to 3, which makes Step 5 possible.
**Test:** reproduces IS 10262:2019 Annex A-8 = 0.648, B-8 = 0.5891, C-8 = 0.5832,
D-8 = 0.6672, F-8 = 0.776 exactly. (Already verified in `is_zone_features.py`.)

### Step 3 — Fix the double-counted noise
**Where:** A's optimiser, prediction block.
**Now:**
```python
sds.append(np.sqrt((sd * m['ysd'])**2 + model['noise']**2))
```
The GP's own `sd` already includes the WhiteKernel noise. Adding `noise` again makes
every mix look more uncertain than it is, so the feasibility test rejects good mixes.
**Fix:** for a **mean-strength** or **mean-slump** question, remove the WhiteKernel
term from `sd` instead of adding it. Keep it only when asking about a **single
specimen**. The two questions are different — IS 456:2000 cl 15.1.1 and cl 16.1 treat
individual and mean results differently, and so must we.

### Step 4 — Turn the slump filter on
**Where:** A's optimiser.
**Now:** `p_slump_used = P_slp[k] if self.slump_filter else 1.0` — and it ships **off**.
So slump is not constraining anything. Turn it on. It only becomes safe to turn on
*after* Step 1, because before Step 1 the slump model points the wrong way.

### Step 5 — Replace gradient search with the exhaustive grid
**Where:** A's optimiser inner loop.
**Now:** L-BFGS-B runs over a surface that `snap_scm` has made flat in steps.
A gradient method on a staircase finds nothing meaningful.
**Fix:** after Step 2 there are only three free knobs on fixed steps —
binder total, SCM split, admixture dose. Enumerate every legal combination.
It is exact, repeatable, and fast enough because the space is now small.
**Test:** the same requirement given twice returns the identical ranked list.

### Step 6 — Load the records already on disk
**What:** the 12 mix designs in a partner plant's extracted sheet
(10 of them carry slump) and the 16 Plant A trials.
**How:** each physical batch is **one** group. Cubes from one batch never count as
separate experiments. Report the true number of independent conditions, not the
number of cubes.
**Why here and not earlier:** loading data into a wrong-signed model makes it
confidently wrong. Fix the sign first (Steps 1–2), then feed it.

### Step 7 — Export the rule set that was never exported
**Where:** `00_is_codes_layer-1.ipynb` holds **89** rules and 55 fixtures — including
the countable-GGBS 70% cap. Its export cell reads
`NOTEBOOK = "00_is_codes_layer.ipynb"` — the **other**, 81-rule file. So the extra
8 rules have never reached `is_rules.py`.
**Fix:** point the constant at the right file, re-export, re-run all 55 fixtures.
**Note:** the 70% cap must carry its own verification status. If it is not traceable
to a clause, it ships as a **project constraint**, not as an IS requirement.

### Step 8 — One repo, one entry point
`SDL1` becomes the single home. FinalSDL is not a rival pipeline any more — it is a
parts bin that gets ported in.

```
SDL1/
  layer0/        <- is_rules.py + the IS mix-design maths     (from A)
  materials/     <- plant state: zone from 600 um, absorption, sp. gravity,
                    cement type/grade, state hash             (new, small)
  models/        <- strength + slump, each = IS baseline + GP on left-over
  screen/        <- exhaustive legal enumeration, achievability check   (from B)
  select/        <- rank for serving · BO for research        (from A)
  loop/          <- expert review, trial log, refit, validation level  (from A)
  tests/         <- annex reproductions, counter-examples, grouped CV  (both)
  docs/
```

Two ways in, and they must not be confused:

| | **SERVE** (a real order) | **EXPLORE** (a research trial) |
|---|---|---|
| stays inside known ground? | **yes — hard reject outside** | no — goes to the edge on purpose, and says so |
| how it picks | rank on cost + carbon | Bayesian optimisation |
| standards constraints | identical | **identical — never relaxed** |
| output | a mix to cast today | a mix to learn from |

Exploration widens *where the model may be asked to predict*. It never widens
*what IS 456 permits*.

---

## 5. How you know it worked

These are the gates. No step is "done" until its gate is green.

| Gate | Check |
|---|---|
| G1 | Water slope positive at **100%** of grid points (was 67.6% wrong) |
| G2 | Fine share reproduces IS 10262:2019 Annex A-8/B-8/C-8/D-8/F-8 exactly |
| G3 | All **55** fixtures pass after the re-export, not 50 |
| G4 | Every `is_rules` outcome that is not `verified` or `project_constraint` cannot decide a mix |
| G5 | LOPO slump bias inside ±25 mm — the band engineers actually order against |
| G6 | Out-of-plant skill **above zero** (it is −0.28 today) |
| G7 | Same requirement twice → identical ranked output |
| G8 | No output claims a validation level above COMPUTATIONALLY COMPLIANT without a measured result behind it |

G5 and G6 are the real ones. G1–G4 and G7 are how you get there.

---

## 6. What this system is, and is not

**It is:** a decision-support and experiment-design tool. It proposes mixes that are
code-legal, ranks them, and tells you which trial is most worth casting next.

**It is not:** a replacement for engineering judgement, laboratory validation, plant
quality control, or any statutory or contractual requirement.

**Every mix it has produced so far is COMPUTATIONALLY COMPLIANT — level 1.**
Nothing it has proposed has been physically cast yet. That stamp appears on every
output and is raised only when a measured result comes back.

The final workability adjustment belongs at the plant, on the trial mix, per
**IS 10262:2019 cl 5.8** — not inside the optimiser.

---

## 7. Standards used in this plan

| Standard | Where used | What for |
|---|---|---|
| IS 10262:2019 cl 4.2, Table 1, Table 2 | [2] | target mean strength, X factor, assumed S |
| IS 10262:2019 Table 4 | [2], Step 1 | water content baseline |
| IS 10262:2019 cl 5.3 | [2], Step 1 | ±3% water per ±25 mm slump |
| IS 10262:2019 Table 5 | [2], Step 2 | coarse aggregate volume by zone × msa |
| IS 10262:2019 cl 5.5 | [2], Step 2 | mix calculation, volume closure |
| IS 10262:2019 cl 5.8 | [10] | trial-mix workability adjustment |
| IS 10262:2019 Annexes A–F | G2 | worked examples used as tests |
| IS 456:2000 Table 5 | [2] | min grade, max free w/c, min cement by exposure |
| IS 456:2000 cl 8.2.4.2 | [2] | max 450 kg/m³ **cement** — fly ash and GGBS excluded |
| IS 456:2000 cl 15.1.1, cl 16.1 | Step 3 | individual vs mean result, acceptance |
| IS 383:2016 Table 9, cl 6.3 | [2] | grading zones; 600 µm passing assigns the zone uniquely |

Anything in this plan that is **not** in the table above is a project design choice,
an engineering interpretation, or a research method — not an IS requirement.
Bayesian optimisation in particular is a **project research method**. No Indian
Standard requires it.

---

## 8. Order of work, one line each

1. IS water→slump as the mean function. *(fixes the root cause)*
2. Compute the fine share from Table 5; remove it from the search.
3. Stop double-counting the WhiteKernel noise; split mean from specimen.
4. Turn the slump filter on.
5. Exhaustive grid instead of gradient descent on a staircase.
6. Load the 12 + 16 records already on disk, grouped by batch.
7. Re-export the 89-rule notebook; all 55 fixtures green.
8. Merge into `SDL1` with SERVE and EXPLORE as separate doors.

Steps 1 and 2 are the whole fight. Steps 3–7 are cheap once those two land.
