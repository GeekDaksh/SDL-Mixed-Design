# Review — notebooks 09–13 and their outputs

**Date:** 30 September 2026
**Method:** two independent adversarial reviews, plus my own re-verification of every
finding marked CONFIRMED below. Nothing here is relayed unchecked.

---

## Verdict in three sentences

The notebooks run, the standards lookups are right, and the export mechanism works. But the
**output is not usable**: the pipeline predicts 276 mm of slump for a 120 mm order, SERVE
can never return a candidate for structural reasons, and `select.py` cannot be imported at
all. Several of the guards that were supposed to make this safe do not actually guard.

**Do not use `12_next_experiments.csv` to cast anything.**

---

## A. Severity 1 — the output is meaningless

### A1. The water-convention mismatch (root cause of most of the rest) — CONFIRMED

Layer 0 designs water from IS 10262 Table 4 + cl 5.3 and **never applies the cl 5.3
admixture reduction**. The training mixes did apply it.

```
Layer 0 designs for 120 mm slump : 201.62 kg/m3
plant has ever actually batched  : 152.40 .. 172.89 kg/m3
```

Because `is_slump_baseline` inverts the same cl 5.3 expression Layer 0 used to *set* the
water, the baseline reproduces the ordered slump **identically** — 120.000 mm. The GP then
adds its training-mean residual of **+155.7 mm**. Predicted slump ≈ **276 mm**.

The four trials in `12_next_experiments.csv` carry `P_slump ≤ 1.5e-07`. They are trials the
model itself gives a **0.000015 percent** chance of landing in the band.

### A2. `select.py` can never be imported — CONFIRMED

`select` is a **C built-in** module. `BuiltinImporter` precedes `PathFinder` on
`sys.meta_path`, so `import select` resolves to the standard library whatever the working
directory.

```
'select' in sys.builtin_module_names : True
import select -> <builtin>
hasattr(select, 'pareto_front')      : False
```

The entire selection layer is a write-only artefact. **Rename it `selection.py`.** My fault
— I chose the name.

### A3. SERVE is empty by construction, not by data — CONFIRMED

The grid's `scm_frac` takes `{0} ∪ [0.15, …]` (IS 10262 Table 9 minima: fly ash 15 %, GGBS
25 %). Training support is `[0.0700, 0.1390]`. **The two sets are disjoint.** No grid point
at any grade, any exposure, any slump can ever be inside support on that axis.
`n_candidates: 0` is structural.

Separately, with water pinned at 201.62 and the SEVERE w/c cap of 0.45, binder ≥ 448.1, so
**exactly one** of the 14 binder steps survives. `n_combinations: 4900` overstates the real
search by ~22×, and nothing in the output says the feasible binder set is a single point.

---

## B. Severity 2 — guards that do not guard

### B1. `volume_closure_m3` is identically 1.0 — CONFIRMED

```
v_agg   = (1 - air) - S
closure = S + v_agg + air  ==  1.0     identically, for every input
```

Verified bit-exact at binder 300, 400 and 900. `compliance_gate` tests
`abs(closure - 1.0) <= 0.01`, and closure is **one of the seven `HARD_MIX_CHECKS`** — so it
contributes a guaranteed PASS to `decided`. A wrong specific gravity or a missing
constituent is invisible to it.

**Fix:** recompute the sum independently from the returned masses and specific gravities.

### B2. A negative SCM fraction is accepted — CONFIRMED

```
design_mix(..., flyash_frac=-0.10)
  -> flyash -40.0 kg/m3, cement 440.0 kg/m3, decided = True
```

The guard tests only `flyash_frac + ggbs_frac >= 1.0`. The `if flyash else 0.0` volume guard
tests *truthiness*, so a negative mass is truthy and contributes a **negative volume**,
inflating the aggregate. The current grid never emits negatives, so the hole is latent — but
Layer 0 is the layer whose contract is supposed to be the guarantee.

### B3. `training_support` fails **open** — CONFIRMED

Passing the model (the parameter is literally named `model_or_df`) returns `None`. SERVE
then accepts **all 220** candidates with `inside_training_range = None`, because the filter
is `!= False` and `None != False`. Same per row: `inside_support` returns `None` on the
first NaN feature, which SERVE keeps.

This inverts the project's own fail-safe rule: missing information must reject, not pass.
My notebook happens to pass a DataFrame, so the worked example is correct — the defect is
that the signature invites the failure silently.

### B4. Source verification is printed and discarded — CONFIRMED

`verify_sources()` runs at import, prints, and nothing reads the result. A mix designed with
**all nine standards failing verification** still returns `decided=True`,
`hard_not_verified=[]`. The only trace is stdout that scrolls past in notebooks 10–13.

### B5. `MixDesign` is mutable — CONFIRMED

Declared `@dataclass` without `frozen=True`, unlike `MaterialState` and `Requirement`.
`m.gate['decided'] = True` and `m.validation_level = PRODUCTION_VALIDATED` both succeed on a
refused mix. The one flag designated as authoritative is writable by any caller.

---

## C. Severity 3 — wrong values recorded and modelled

### C1. `wc_ratio` is not the ratio the code governs — CONFIRMED

`MixDesign.wc_ratio = water / total binder`. The gate forms w/c over **counted** binder
(`cement + ggbs + countable_fly_ash`, capped per IS 456 Table 5 Note 1). They diverge above
~35 % fly ash:

| fly ash share | `MixDesign.wc_ratio` | gate's counted w/c | Table 5 max |
|---|---|---|---|
| 0.20 | 0.4354 | 0.435 | 0.45 |
| 0.40 | 0.4354 | **0.472** | 0.45 |
| 0.50 | 0.4354 | **0.566** | 0.45 |

The stored value is invariant to the SCM split while the governing quantity nearly doubles.
`screen.py` exports exactly this field as `wb_ratio` and `dv_wb_ratio`. **The gate is still
safe** (counted binder ≤ total binder, so the gate is the stricter test) — but the number
recorded, exported and modelled is the wrong one.

### C2. A supplied `wc_ratio` is validated, then discarded — CONFIRMED

```
design_mix(..., binder_kg_m3=420.0, wc_ratio=0.30)  ->  wc_ratio 0.4561
provenance['wc_ratio'] == (ENGINEER_INPUT, 'supplied')
```

The provenance dict — described in the notebook as the main honesty mechanism — asserts the
engineer supplied a value that was thrown away.

### C3. Hardcoded fly ash and GGBS specific gravities — CONFIRMED

`2.20` and `2.90` are embedded in the volume arithmetic that sets both aggregate masses.
There is **no `MaterialState` field** to override them, so the notebook's own open item
("must come from the material certificate") is unimplementable as written. About
**12 kg/m³** of aggregate rides on them, and `closure` still reads 1.000 for any value (B1).

**This refutes the notebook's claim that it "adds no standards constants of its own."** No
clause or table *number* is used in logic — that part stands — but these two numbers are.

### C4. `pumpable` takes the extreme of a permissive range — CONFIRMED

```
pumpable=False -> fine fraction 0.3758, fine 668.6 kg/m3   (band FLOOR)
pumpable=True  -> fine fraction 0.4382, fine 779.7 kg/m3   (band CEILING)
```

One boolean moves **111 kg/m³** of sand. cl 5.5.2 permits "up to 10 percent"; the code
always takes the full 10. Both are labelled `DERIVED_FROM_STANDARD`. Taking the extreme of a
permissive range is a `[PC]` choice. Worse: it moves fine aggregate **upward**, the
direction Table 5 Note 3 warns against for crushed sand — which is this entire project.

### C5. IS 383 Table 9 600 µm bands have gaps — CONFIRMED

```
600um = 34.0 -> Zone I
600um = 34.5 -> REFUSED
600um = 35.0 -> Zone II
600um = 59.5 -> REFUSED     600um = 79.5 -> REFUSED
```

Bands are `I (15,34), II (35,59), III (60,79), IV (80,100)`. My docstring calls them
"disjoint, contiguous and exhaustive". **They are not**, for any non-integer reading — and a
sieve analysis reported to one decimal is routine. The error message blames the wrong cause.

Whether the printed table is integer-bounded or half-open is a **primary-source question
that is not resolved**. Until it is, the unique-assignment argument does not hold for
one-decimal data.

### C6. Non-integer `msa` is silently truncated — CONFIRMED

`msa_mm = 20.6` designs successfully off the **20 mm** rows and records `msa_mm = 20.6`. The
fail-safe fixture passes only because its probes (12.5, 16, 25, 31.5) floor to values that
are also absent. Also: `MaterialState.msa_mm` defaults to **20.0** — a table key that the
project's own rules say must never be assumed.

---

## D. Severity 4 — my own evidence was misreported

These are errors in what I told you, not only in the code.

### D1. The r = −0.09 headline is computed on rows the notebook discards — CONFIRMED

```
all 264 usable rows        r = -0.090     <- what I reported
the 5 FITTED families      r = -0.528
WITHIN family (pooled)     r = +0.101
```

I built the "water is unidentifiable" argument on a number calculated over the 8 orphan rows
that notebook 10 then quarantines. The correct figures are −0.528 between families and
**+0.101 within** family. The conclusion — that water and superplasticiser are confounded
and the coefficient is not identifiable from this data — still holds on the within-family
figure, which is the one that matters. But **the headline number was wrong and I should have
computed it on the fitted set.**

### D2. The G1 test is tautological — CONFIRMED

Across the 140→200 kg water sweep the GP's residual output takes **exactly one distinct
value**. The test therefore proves only that `50 + (w/186 − 1)×833.33` increases in `w`.
`check_no_water_leak` already raises at fit time and in the export assertions, so `assert ok`
is unreachable. I presented this as evidence; it is arithmetic that cannot fail.

It also conceals that the baseline is affine and unbounded — it returns **315.5 mm at
199 kg** and negative slumps for every training row.

### D3. The skill statistic is the wrong one — CONFIRMED

Reported: mean of five per-group ratios = **−1.706**. Pooled
`1 − ΣSS_res/ΣSS_base` = **−1.434**. With denominators from 7 682 to 11 767, the mean of
ratios is dominated by the single worst fold. Report the pooled figure. The 5 000-draw
bootstrap over five ratios is decorative.

The reviewers confirmed the metric is **not** rigged against the model — holding out an
extreme grade makes `SS_base` larger, which *flatters* it. So the verdict stands: **bad
model**. And for M20 and M40, `MAE == |bias|` exactly, meaning every held-out row errs the
same way — the GP has reverted to its prior and only the baseline is moving.

### D4. `out_of_group_sd_mm` is not a σ — CONFIRMED

It is the RMS of per-group **MAEs** (22.99), used as the σ of a symmetric normal. About
95 percent of it is family-level systematic offset, not scatter. Measured coverage of the
nominal 90 % interval:

| pooled | M20 | M25 | M30 | M35 | M40 |
|---|---|---|---|---|---|
| 92.6 % | 96.8 | 100.0 | 97.6 | 100.0 | **42.9** |

Pooling hides that 57 percent of one family's rows fall outside their own 90 % band.

### D5. Achievability measures the wrong thing — CONFIRMED

`achievability_report` is a pure function of `(tolerance, sd, confidence)`. It never touches
the model; `state` is an unused parameter. `achievable()` computes `mu` but never compares
it to the target. So a mix predicted **156 mm off** is reported as a **38 mm uncertainty**
problem. It frames a gross systematic bias as model variance, and returns the same answer
for every mix at a plant.

### D6. `predict_strength` double-scales the noise — CONFIRMED

`noise_in_normalised_units` defaults to `True`, but `fit_residual_model` stores `noise_var`
**already in original units** and never writes that key. The default fires and multiplies by
`y_std²` a second time — **908×** here — clamping `sd` to `1e-6` for 100 % of rows and
turning `P_strength` into a 0/1 step.

Moot today: `strength_model.joblib` has keys `{target, members, noise, q90, feature_range,
n_groups}` — no `gp`, no `.predict`. **The strength arm has never executed.**

### D7. Smaller, all confirmed

- `concrete_temp`: `A if False else 30.0` — dead branch, hardcoded. If re-enabled it yields
  NaN everywhere, because `train_temp_median` is never stored. One of seven GP features —
  the one cl 5.3 actually names — is constant across the entire grid.
- `refused` sums to **5 384** against 4 900 combinations: it mixes exclusive causes,
  non-exclusive diagnostics and a total, with no naming convention to tell them apart, and
  changes shape by mode.
- `11_screen_meta.json` records `n_candidates: 0` while `12_next_experiments.csv` holds 4
  explore rows. Nothing records the mismatch.
- The nb11 assertion `if len(se): assert se["gate_decided"].all()` is **skipped entirely**
  because `len(se) == 0`. The check that matters has never run.
- `layer0` restates the IS 383 600 µm bands in a docstring rather than reading them.
- Provenance appends `+ cl 5.5.1 + cl 5.5.2 + Table 5 Note 3` unconditionally, including for
  non-pumpable mixes where cl 5.5.2 was not applied.

---

## E. What is genuinely clean — verified, not assumed

- **The noise rescaling is exactly right.** Recomputed against the direct latent posterior:
  agrees to **1.3e-12 mm²**, zero negatives, zero clamp hits. The fragility is that
  `_y_train_std` is private — if renamed, `y_std` silently becomes 1.0 and the bug this code
  exists to fix returns with no warning.
- **No leakage in leave-one-group-out.** Scaler and `normalize_y` refit on the training fold
  only. The baseline is a fixed deterministic function.
- **`pareto_front` is correct.** Brute-forced against strict dominance on 300 random cases
  with deliberate ties: 0 mismatches.
- **The export mechanism works.** Both modules regenerate byte-identically; no undefined
  names; nothing a caller needs is dropped.
- **The G2 annex fixtures genuinely pass** — A-6 191.58, C-6 201.62, A-8 0.648, C-8 0.5832.
- **EXPLORE really does apply identical standards constraints** — the Layer 0 refusal sits
  above the mode branch. (The assertion claiming it never ran, but the property holds.)
- **`state_hash` is deterministic** across processes.
- **No clause or table number is used in logic** — every table lookup goes through
  `is_rules`. That part of the design held.

---

## F. Fix order

Ordered by what unblocks the most.

1. **Apply the cl 5.3 admixture water reduction in Layer 0**, as an explicit required input
   when an admixture is dosed — never a hardcoded constant, since cl 5.3 gives a range
   (20–30 % and above) and Annex C-6 took 23 % from trial data. Back the value out of the
   five families rather than borrowing Annex C's. **Fixes A1, and most of A3.**
2. **Rename `select.py` → `selection.py`.** Fixes A2. One line.
3. **Make achievability compare `mu` to the target**, not just the half-width. Fixes D5.
4. **Recompute volume closure independently** from the returned masses. Fixes B1.
5. **Guards:** reject negative fractions; make `training_support` fail closed; freeze
   `MixDesign`; carry the source-verification result into the mix and into `decided`.
   Fixes B2–B5.
6. **Record the counted w/c** alongside the total-binder ratio, and export the counted one.
   Fixes C1.
7. **Add `flyash_sg` / `ggbs_sg` to `MaterialState`.** Fixes C3.
8. **Make `pumpable` a fraction of the cl 5.5.2 allowance**, not a boolean at the extreme,
   and label it `[PC]`. Fixes C4.
9. **Resolve the 600 µm band question from the printed standard**, then handle one-decimal
   readings. Fixes C5.
10. **Refuse non-integer `msa`; remove its default.** Fixes C6.
11. **Report pooled skill and per-group coverage**; stop using an MAE-RMS as a σ. Fixes
    D3, D4.
12. **Delete the G1 sweep** or replace it with something that can fail. Fixes D2.
13. **Fix the `noise_in_normalised_units` default to `False`**; build a real strength model
    or keep refusing to rank. Fixes D6.

---

**Weakest link:** items 1 and 3 are one defect with two faces — the deterministic layer and
the residual target are calibrated against different water conventions, so every prediction
is ~156 mm high and the module meant to catch that reports the wrong reason. Until that is
fixed, nothing downstream — skill, coverage, acquisition, ranking — is measuring anything.
**Check:** after the fix, candidate water must land inside 152–173 kg and `P_slump` must
rise off 1e-07. If it does not, the baseline is still not wired through.
