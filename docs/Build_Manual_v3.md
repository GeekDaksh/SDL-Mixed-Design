# MIX-DESIGN SDL — Build Manual v3

**Status: canonical.** This supersedes `Build_Manual_Mix_Design_SDL.docx` (v2, 26 Aug),
`Implementation_Plan_SDL.docx` (23 Aug) and `poa.md` (31 Aug) wherever they disagree.
Those three stay on disk as history. This is the document to build from.

**No code was changed to produce this.** `is_sdl/` is untouched. Section 8 lists the defects
found in it so the from-scratch rewrite does not reproduce them.

---

## How to read this document

Every substantive line carries one tag. There are no untagged claims.

| Tag | Meaning |
|---|---|
| `[IS]` | Indian Standard requirement, read from the primary BIS text in this project, clause cited |
| `[EI]` | Engineering interpretation — a reading of a standard, not its literal text |
| `[PC]` | Project choice — ours, not the code's |
| `[ML]` | Machine-learning assumption |
| `[BO]` | Bayesian-optimisation choice |
| `[V]` | Measured on project data, method stated |
| `[NV]` | **NOT VERIFIED FROM PRIMARY STANDARD SOURCE** |

An `[IS]` tag means I opened the PDF and read the clause. It does not mean the edition is current —
see §0.3.

---

## §0 Verification ledger

### 0.1 Read from primary text in this project

**IS 456 : 2000** — `IS_codes/is.456.2000.pdf`
cl 5.5.1 · cl 6.1.1 · cl 6.1.2 · cl 6.1.3 · cl 8.2.4.2 · cl 9.1.1 · cl 9.2.2 ·
Table 5 · Table 6 · Table 9

**IS 10262 : 2019** — `IS102622019.pdf` (project library)
Foreword · cl 1.2 · cl 1.3 · cl 3.1 · cl 3.2 · cl 4.1 · cl 4.2 · cl 4.2.1.3 · cl 5.1 · cl 5.1.1 ·
cl 5.1.2 · cl 5.2 · cl 5.3 · cl 5.4.1 · cl 5.5 · cl 5.5.2 · cl 5.7 · cl 5.8 ·
cl 6 · cl 6.2.3 · cl 6.2.4 · cl 6.2.5 · cl 6.2.6 · cl 6.2.7 · cl 9.2 ·
Tables 1–13 · Annexes A, B, C, D, E, F, G

### 0.2 NOT read — every rule sourced to these is `[NV]`

- **IS 383 : 2016** — sand grading zones, CA grading. `is_sdl` cites "IS 383 Table 9" for sand
  zones and "Table 7" for CA grading. Neither verified here.
- **IS 9103 : 1999** — `is_sdl` enforces a 2.0% admixture dosage cap citing IS 9103. See §8.4.
- **IS 455** — slag-cement limits, referenced by IS 456 Table 5 Note 1. Not in the project library.
- **IS 1489 (Part 1)** — pozzolana limits, referenced by the same note. In the library, not read.
- **IS 516 / IS 1199 / IS 2386 / IS 3812** — test methods. Not needed by Layer 0; needed for §7.

### 0.3 Edition currency — the one thing that is unresolved for every clause

`[NV]` The IS 456 copy in `IS_codes/` is the **2000 base print**; its "Amendments Issued Since
Publication" table is blank. IS 456:2000 has carried amendments. **No `[IS]` tag in this document
should be treated as amendment-current until each cited clause is checked against a current BIS
print.** This is one bounded task, not a reason to stop building.

`[V]` **RESOLVED — IS 383:2016 is the Third Revision.** `poa.md` was right; IS 10262:2019's own
reference list, which prints it as "(second revision)", is wrong. Verified from the frozen copy
`standards/is383_2016.pdf`: the title page reads "( Third Revision )" and the Foreword opens "This
Indian Standard (Third Revision) was adopted by the Bureau of Indian Standards…" and records the
publication history — first published 1952, subsequently revised 1963 and 1970.

`[NV]` This closes the *revision* question only. The IS 383 sand grading zones and coarse aggregate
grading tables remain unread — see §9 item 3, which stays open.

### 0.4 The measured numbers, and their single point of failure

`[V]` Every measured figure in §7 was produced by GroupKFold (8 splits) on mix signature over
`Mixed Design Data.xlsx`, with every transform fitted inside the fold, by
`analysis/bakeoff.py`, `bakeoff2.py` and `decide.py`.

**RESOLVED — the workbook is `source_b_workbook.xlsx`.** The scripts load
`/home/claude/Mixed Design Data.xlsx`, a stale path from a prior sandbox, but the file itself is in
the project root under a different name. `[V]` Verified two ways: every column the three scripts
reference exists in its `MODEL_READY` and `STRENGTH_LONG` sheets (zero missing), and re-running the
scripts' exact filter chain reproduces every headline figure —

```
MODEL_READY records                            103
after exclude_reason filter                     72   <- Implementation Plan: 72
cv_groups in the strength set                   59   <- Implementation Plan: 59
slump modelling set                     n=39, g=33   <- "R2 0.18 on 39 records"
slump-flow modelling set                n=27, g=21   <- "R2 0.005 on 27"
STRENGTH_LONG cube results                     463   <- Implementation Plan: 463
     at 28 days                                251   <- 251
mixes with >=3 cubes at 28 d                    68   <- 68
pooled within-mix SD at 28 d              2.88 MPa   <- 2.88 MPa
```

**All measured figures in §7 are reproducible.** Fix the hard-coded path in the three scripts to
point at `source_b_workbook.xlsx`.

`[V]` Figures corroborated across two independent documents: RMSE 6.50 / 6.16, R² 0.856 / 0.871,
CI `[-0.34, +1.03]`.
`[NV]` Figures appearing in `poa.md` only, with no source anywhere in the project — **do not use**:
`RMSE 9.46`, `R² 0.848`, `28.8 → 33.2 MPa`, `3,598 strength rows`, `1,789 slump rows`,
`88 Maharashtra rows`, "UCI / Guangxi / Khartoum", "14 shared-design rows".

---

## §1 Scope, and why the grade range splits into three domains

`[IS]` **IS 10262:2019 cl 1.2** — the standard covers ordinary, standard and high strength grades,
plus SCC and mass concrete.
`[IS]` **IS 10262:2019 cl 1.3** — "All requirements of IS 456 in so far as they apply, shall be
deemed to form part of this standard."

The declared M5–M65 range is **not one design problem**. It is three, and they use different clauses.

| Domain | Grades | Route | Authority |
|---|---|---|---|
| **A — Nominal / lean** | M5, M7.5 (and M10–M20 where cl 9.1.1 applies) | Nominal mix proportions, **no design mix** | `[IS]` IS 456 Table 9 (cl 9.3, 9.2.1); cl 9.1.1 |
| **B — Ordinary & standard** | M10 – M60 | IS 10262 **Section 2** — cl 5.1 Fig 1, Table 4, Table 5 | `[IS]` IS 10262 cl 5 |
| **C — High strength** | **M65 and above** | IS 10262 **Section 3** — cl 6, **Table 8**, Table 7, Table 6, Table 10 | `[IS]` IS 10262 cl 6 |

### 1.1 M5 and M7.5 have no design-mix route

`[IS]` IS 10262:2019 **Table 1** (X factor, cl 4.2) starts at **M10**.
`[IS]` IS 10262:2019 **Table 2** (assumed standard deviation, cl 4.2.1.3) starts at **M10**.
`[IS]` IS 456:2000 **Table 9** "Proportions for Nominal Mix Concrete" (cl 9.3, 9.2.1) is the only
place M5 and M7.5 appear: M5 → 800 kg aggregate per 50 kg cement, 60 kg water max;
M7.5 → 625 kg, 45 kg; M10 → 480 kg, 34 kg; M15 → 330 kg, 32 kg; M20 → 250 kg, 30 kg.
Fine:coarse generally 1:2, upper limit 1:1½, lower limit 1:2½.

`[EI]` Therefore the engine **must not attempt a design mix below M10.** For M5 and M7.5 it should
return the Table 9 nominal proportions and label them as such. Attempting cl 4.2 there means
inventing an X and an S that the standard does not publish.

### 1.2 Why M10–M20 look infeasible, and the clause that resolves it

`[IS]` IS 456 cl 6.1.2 — "The minimum grade of concrete for plain and reinforced concrete shall be
as per Table 5."
`[IS]` IS 456 Table 5, moderate exposure, reinforced concrete → minimum grade **M25**.

So under an RCC + moderate default, M10/M15/M20 must fail the minimum-grade check. That is correct
behaviour, not a bug. The clause that legitimises them is:

`[IS]` **IS 456 cl 6.1.3** — "Concrete of grades lower than those given in Table 5 may be used for
plain concrete constructions, lean concrete, simple foundations, foundation for masonry walls and
other simple or temporary reinforced concrete construction."

`[EI]` The `use` field therefore needs **three** values, not two — `RCC`, `PCC`, and a
**cl 6.1.3 category** for lean/simple/temporary work. The low grades are valid only in the third.
Widening the minimum-grade check to let them through would be wrong; adding the category is right.

---

## §2 The two inputs, and exactly what they unlock

`[PC]` The client supplies **grade** and **target slump**. Everything else is derived from the codes
or set to a declared default that says so.

`[IS]` IS 10262:2019 **cl 4.1** lists what mix proportioning actually requires: (a) grade;
(b) cement type and grade; (c) maximum nominal aggregate size; (d) minimum cementitious content and
maximum w/c, **or** exposure per IS 456 Tables 3 and 5; (e) workability at placement;
(f) transportation time; (g) placing method; (h) degree of site control or established standard
deviation; (j) coarse aggregate type; (k) fine aggregate type; (m) maximum cement content;
(n) chemical admixture; (p) mineral admixture; (q) other requirements.

`[EI]` Grade and slump cover (a) and (e). **Fourteen of the seventeen inputs the standard names are
not derivable from them.** Every one must be surfaced as `[ASSUMED]` with its default stated, never
silently filled. This is the honest form of "two inputs in".

**Derived from GRADE**

| Value | Source |
|---|---|
| assumed standard deviation | `[IS]` IS 10262 Table 2 (cl 4.2.1.3) |
| X factor | `[IS]` IS 10262 Table 1 (cl 4.2) |
| target mean strength | `[IS]` IS 10262 cl 4.2 |
| domain A / B / C | `[IS]` IS 10262 cl 1.2, cl 6; IS 456 cl 9.1.1 |
| w/c or w/cm | `[IS]` IS 10262 Fig 1 (cl 5.1) **for domain B**; **Table 8 (cl 6.2.5) for domain C** |

**Derived from SLUMP**

| Value | Source |
|---|---|
| water content | `[IS]` IS 10262 Table 4 + cl 5.3 (domain B); **Table 7 + cl 6.2.4 (domain C)** |
| workability degree, placing conditions | `[NV]` cited to IS 456 Table 7 — not read in this pass |

**Must be confirmed, never derived**

`[EI]` Exposure class (set by environment), use class (RCC / PCC / cl 6.1.3), nominal maximum
aggregate size, cement type and grade, sand zone, specific gravities, aggregate absorption and
moisture, transportation time, placing method, degree of site control.

### 2.1 Two standard-deviation routes, and one conflict to declare

`[IS]` IS 10262 cl 4.2.1.1 — a calculated standard deviation needs **not less than 30** test
results, recalculated after every change of mix proportioning, checked monthly.
`[IS]` IS 10262 cl 4.2.1.3 — where sufficient results are not available, Table 2 may be assumed
"in the first instance", and replaced by the actual value as soon as results exist.
`[IS]` Table 2 Note 1 — the tabulated values assume **good** site control. For fair control,
**add 1 N/mm²**.

`[EI]` **Declare a conflict.** IS 456 cl 9.2.2 states the target mean as `fck + 1.65 S`.
IS 10262:2019 cl 4.2 states `max(fck + 1.65 S, fck + X)`. IS 10262 is the later, more specific
mix-proportioning document and its formula is the stricter of the two.
`[PC]` **Take the maximum.** Record this as an interpretation, not as a clause.

---

## §3 Layer 0 — the deterministic chains

No machine learning. This is what makes every output legal.

### 3.1 Domain B — ordinary and standard grades, M10 to M60

`[IS]` All of IS 10262:2019 Section 2.

```
target mean   f'ck = max(fck + 1.65 S, fck + X)              cl 4.2, Tables 1 and 2
w/c           Fig 1 for the expected 28-d cement strength    cl 5.1
              then take the LOWER of this and the IS 456
              Table 5 durability cap                          cl 5.1.1
              where SCM is used, work in w/cm per
              IS 456 Table 5                                  cl 5.1.2
air           Table 3: 10 mm 1.5% | 20 mm 1.0% | 40 mm 0.8%   cl 5.2
water         Table 4 base (50 mm slump, angular, SSD):
                10 mm 208 | 20 mm 186 | 40 mm 165 kg          cl 5.3
              shape:  -10 sub-angular, -15 gravel with some
                      crushed particles, -20 rounded gravel
              slump:  +/- 3% per 25 mm from 50 mm
              admix:  water reducer -5 to -10%
                      superplasticiser -20 to -30% and above
binder        binder = water / (w/c or w/cm)                  cl 5.4.1
              if fly ash >= 20%, an increase may be warranted;
              +10% for preliminary trial, then RECALCULATE w/cm
              check against IS 456 minimum, adopt the GREATER
              maximum cement per IS 456                        cl 5.4.1
CA volume     Table 5 at w/c 0.50, by msa and sand zone        cl 5.5
              +0.01 per 0.05 DECREASE in w/c
              -0.01 per 0.05 INCREASE in w/c                   cl 5.5.1
              pumpable / congested: reduce by up to 10%        cl 5.5.2
masses        absolute volume; volumes sum to 1 m3 less air    cl 5.7
trials        proportions SHALL be checked by trial batches;
              trial 1 -> adjust water/admixture -> trial 2 at
              the same w/c; trials 3 and 4 at w/c +/- 10%      cl 5.8
```

`[IS]` **Table 5 — volume of coarse aggregate per unit volume of total aggregate, at w/c 0.50.**
The columns are printed **Zone IV, III, II, I — right to left.**

| msa | Zone IV | Zone III | Zone II | Zone I |
|---|---|---|---|---|
| 10 mm | 0.54 | 0.52 | 0.50 | 0.48 |
| 20 mm | 0.66 | 0.64 | 0.62 | 0.60 |
| 40 mm | 0.73 | 0.72 | 0.71 | 0.69 |

`[IS]` Table 5 Note 4 — fine aggregate of Zone IV shall not be used in reinforced concrete unless
tests establish suitability.
`[IS]` Table 5 Note 3 — for crushed or mixed sand, less fine aggregate is normally needed and the
coarse aggregate volume shall be suitably increased. **This is the standard's own hook for the
M-sand correction.**

### 3.2 Domain C — high strength, M65 and above

`[IS]` IS 10262:2019 Section 3, cl 6. **A different chain. Fig 1, Table 3, Table 4 and Table 5 do
not apply here.**

```
target mean   same as cl 4.2                                  cl 6.2.1 -> 4.2
msa           generally restricted to 20 mm; for M80 and
              above, 10.0 to 12.5 mm may be preferable        cl 6.2.2
air           Table 6: 10.0 mm 1.0% | 12.5 mm 0.8%
                       | 20.0 mm 0.5%                          cl 6.2.3
water         Table 7 MAXIMUM (50 mm slump):
                10.0 mm 200 | 12.5 mm 195 | 20.0 mm 186 kg/m3  cl 6.2.4
              +/- 3% per 25 mm slump; PCE reduces >= 30%
w/cm          Table 8, by target strength and msa              cl 6.2.5
binder        from water and w/cm; must satisfy the IS 456
              max/min cementitious limits                      cl 6.2.6
              if OPC exceeds the IS 456 maximum, special
              consideration in design is required               cl 6.2.6
SCM dosage    Table 9                                          cl 6.2.6
CA volume     Table 10, base w/cm 0.30                         cl 6.2.7
              pumpable: reduce by up to 5% (NOT 10%)           cl 6.2.7
```

`[IS]` **Table 8 — recommended w/cm for high strength concrete made with HRWRA** (cl 6.2.5).
Note: values are for 28-day cement strength 53 MPa and above.

| Target strength at 28 d, N/mm² | 10.0 mm | 12.5 mm | 20.0 mm |
|---|---|---|---|
| 70 | 0.36 | 0.35 | 0.33 |
| 75 | 0.34 | 0.33 | 0.31 |
| 80 | 0.32 | 0.31 | 0.29 |
| 85 | 0.30 | 0.29 | 0.27 |
| 90 | 0.28 | 0.27 | 0.26 |
| 100 | 0.26 | 0.25 | 0.24 |

`[IS]` **Table 10 — CA volume per unit volume of total aggregate, at w/cm 0.30** (cl 6.2.7).
There is **no Zone IV column** here.

| msa | Zone III | Zone II | Zone I |
|---|---|---|---|
| 10.0 mm | 0.56 | 0.54 | 0.52 |
| 12.5 mm | 0.58 | 0.56 | 0.54 |
| 20.0 mm | 0.68 | 0.66 | 0.64 |

`[IS]` **Table 9 — recommended mineral admixture dosages, % by mass of total cementitious**
(cl 6.2.6): fly ash 15–30 · GGBS 25–50 · metakaoline 5–15 · silica fume 5–10.

### 3.3 The M65 worked example, from the standard

`[IS]` IS 10262:2019 **Annex D**, M70, severe RCC, 20 mm, 120 mm slump, OPC 53, PCE:
target mean **79.9** → Table 8 at 20 mm → **w/cm 0.29** → Table 7 water 186 → 120 mm slump
201.624 → PCE −30% → **141 kg** → cement 141/0.29 = 486 → +10% cementitious = **535** →
fly ash 15% = 80.25, silica fume 5% = 26.75, **cement 428** → revised w/cm **0.264** →
check 450 > 428, **OK**.

`[EI]` Note what this shows: on the correct Section 3 route, a genuine M70 lands at **428 kg of
OPC** — under the 450 ceiling — with only 20% total SCM, chosen from Table 9 rather than sized to
dodge the cap. Any engine that reports M65 needing ~33% fly ash to get under 450 has taken the
wrong route. See §8.1.

---

## §4 Fig 1 — turning the graph into a formula, and where the formula stops being valid

`[IS]` IS 10262:2019 **Fig 1** gives the free w/c against 28-day strength as three curves:
Curve 1 for expected 28-day cement strength ≥33 and <43 N/mm²; Curve 2 for ≥43 and <53;
Curve 3 for ≥53 and above.
`[IS]` Fig 1 Note 1 — absent actual cement strength data, curves 1, 2, 3 may be used for OPC 33,
OPC 43, OPC 53 respectively.
`[IS]` Fig 1 Note 2 — for PPC/PSC use the curve matching actual strength; absent that data,
**curve 2** may be used.

`[EI]` The standard's own annexes give exact anchor points on **Curve 2 (OPC 43)**:

```
[IS] Annex A-5 :  target 48.25 N/mm2  ->  w/c 0.36
[IS] Annex F-5 :  target 20.77 N/mm2  ->  w/c 0.61

[PC] two points fit the Abrams form exactly:   ln(f) = a - b*(w/c)
     b = (ln 48.25 - ln 20.77) / (0.61 - 0.36)  =  3.3715
     a = ln 48.25 + 3.3715 * 0.36               =  5.0902

     check:  w/c at 48.25 -> 0.3600   published 0.36   exact
             w/c at 20.77 -> 0.6100   published 0.61   exact
```

### 4.1 The validity range — this is a hard boundary, not a caveat

`[EI]` The fit is anchored at **w/c 0.36 and 0.61** and is validated **only between them**.

| Grade | w/c from the fit | Status |
|---|---|---|
| M25, M30, M35 | ~0.49 – 0.39 | inside the anchors |
| M40 | 0.360 | at the lower anchor |
| M45 – M60 | below 0.36 | **extrapolation — flag every output** |
| M65+ | — | **do not use Fig 1 at all; Table 8 applies** |

`[EI]` Below w/c 0.36 the engine is extrapolating a two-point fit. Either read four or five more
points off the printed curve, or mark every domain-B output below 0.36 as extrapolated. Do not do
neither.

`[NV]` Curves 1 (OPC 33) and 3 (OPC 53) have **no verified anchor points** in the annexes. Falling
back to Curve 2 is what Fig 1 Note 2 permits **for PPC/PSC without strength data** — it says
nothing about substituting for OPC 33 or OPC 53. `[EI]` Using it for those is a project
approximation and must be labelled as one, not as Note 2.

`[IS]` cl 5.1 — "the relationship between strength and free water-cement ratio **should preferably
be established for the materials actually to be used**." Fitting Abrams to your own trials is the
standard asking for it, not a shortcut around it.

---

## §5 The compliance gate

`[PC]` Every proposed mix passes the gate before anyone sees it. No learned model emits a mix
directly. Each check names its clause so a failure explains itself.

| # | Check | Rule | Authority |
|---|---|---|---|
| 1 | maximum cement | OPC, **excluding fly ash and GGBS**, ≤ 450 kg/m³ | `[IS]` IS 456 cl 8.2.4.2 |
| 2 | minimum binder | ≥ Table 5 minimum + Table 6 msa adjustment | `[IS]` IS 456 Table 5, Table 6 |
| 3 | maximum free w/c or w/cm | ≤ Table 5 value for the exposure and use | `[IS]` IS 456 Table 5, cl 5.1.1 |
| 4 | minimum grade | ≥ Table 5 value, **unless cl 6.1.3 applies** | `[IS]` IS 456 cl 6.1.2, cl 6.1.3 |
| 5 | design vs nominal | nominal permitted only ≤ M20, with permission | `[IS]` IS 456 cl 9.1.1 |
| 6 | volume closure | sums to 1 m³ less entrapped air | `[IS]` IS 10262 cl 5.7 |
| 7 | SCM dosage in domain C | within Table 9 ranges | `[IS]` IS 10262 Table 9 (cl 6.2.6) |
| 8 | admixture | complies with IS 9103 | `[IS]` IS 456 cl 5.5.1 |
| 9 | admixture dosage cap | **no verified numeric cap** | `[NV]` see §8.4 |

### 5.1 The 450 rule, in full

`[IS]` **IS 456 : 2000, cl 8.2.4.2 — Maximum cement content.** Verbatim:

> "Cement content **not including fly ash and ground granulated blast furnace slag** in excess of
> 450 kg/m³ **should not be used unless special consideration has been given in design** to the
> increased risk of cracking due to drying shrinkage in thin sections, or to early thermal cracking
> and to the increased risk of damage due to alkali silica reactions."

`[IS]` Corroborated throughout IS 10262:2019: Annex A-1(j) "Maximum cement content **not including
fly ash** : 450 kg/m³"; D-1(k), D-7, E-1(h), F-1(j); and cl 6.2.6 restates the special-consideration
condition.

Three consequences, all of which change the implementation:

1. `[IS]` It caps **cement**, not cementitious material. Fly ash and GGBS are excluded from the
   count. Capping total binder at 450 is wrong.
2. `[IS]` The verb is **"should not … unless"**. `[EI]` Encoding it as a hard silent reject is
   **stricter than the code**. `[PC]` Implement it as a constraint with a documented override that
   records the special consideration — which is what the clause contemplates.
3. `[IS]` IS 10262's worked examples apply it to OPC content only.

### 5.2 The asymmetry that is easy to get wrong

`[IS]` IS 456 **Table 5 Note 1** — the tabulated **minimum** cement content "is inclusive of
additions mentioned in 5.2. The additions such as fly ash or ground granulated blast furnace slag
may be taken into account … **if the suitability is established and as long as the maximum amounts
taken into account do not exceed the limit of pozzolana and slag specified in IS 1489 (Part 1) and
IS 455** respectively."

So: **the maximum (cl 8.2.4.2) excludes SCM. The minimum (Table 5) includes it — conditionally.**
`[NV]` Those IS 1489 (Part 1) and IS 455 limits are not verified here. Until they are, counting
full binder toward the minimum is unbacked. Check 2 must carry that caveat.

### 5.3 IS 456 Table 5, as read

`[IS]` Table 5 (clauses 6.1.2, 8.2.4.1, 9.1.2), 20 mm nominal maximum size, normal weight aggregate:

| Exposure | PCC min cement | PCC max w/c | PCC min grade | RCC min cement | RCC max w/c | RCC min grade |
|---|---|---|---|---|---|---|
| Mild | 220 | 0.60 | — (Note 2) | 300 | 0.55 | M20 |
| Moderate | 240 | 0.60 | M15 | 300 | 0.50 | M25 |
| Severe | 250 | 0.50 | M20 | 320 | 0.45 | M30 |
| Very severe | 260 | 0.45 | M20 | 340 | 0.45 | M35 |
| Extreme | 280 | 0.40 | M25 | 360 | 0.40 | M40 |

`[IS]` Note 2 — minimum grade for plain concrete under mild exposure is not specified.
`[IS]` **Table 6** (cl 8.2.4.1), adjustment to the Table 5 minimum for other aggregate sizes:
10 mm **+40** · 20 mm **0** · 40 mm **−30** kg/m³.

`[V]` Four cells are independently corroborated by IS 10262:2019's annexes: severe RCC 320 kg/m³
and 0.45 (Annexes A-7, B-5, C-7), and moderate PCC 240 kg/m³ with the −30 msa adjustment giving
210 (Annex F-7).
`[NV]` **The remaining cells were read from an OCR'd scan with visible character damage.** Confirm
the whole table visually against a clean print before encoding. This is a five-minute task and it
gates the entire durability layer.

### 5.4 Characteristic strength, and where the 5% actually comes from

`[IS]` IS 456 **cl 6.1.1** — "The characteristic strength is defined as the strength of material
below which not more than **5 percent** of the test results are expected to fall."
`[IS]` IS 456 **cl 9.2.2** — "The mix shall be designed to produce the grade of concrete having the
required workability and a characteristic strength not less than appropriate values given in
Table 2. The target mean strength … should be equal to the characteristic strength plus 1.65 times
the standard deviation."

`[EI]` **Correction to earlier project documents.** The 5% is defined in **cl 6.1.1**, not
cl 9.2.2. cl 9.2.2 carries the 1.65 multiplier, which is the one-sided 5% normal quantile — the
same 5%, arrived at from the definition. Citing "cl 9.2.2 allows at most 5%" is the wrong clause
for the right number. Cite cl 6.1.1 for the fractile and cl 9.2.2 for the formula.

`[PC]` The optimiser constraint `P(f28 < fck) ≤ 0.05` is a **project decision rule** built on the
cl 6.1.1 definition. It is **not** an IS 456 acceptance criterion. Acceptance is a separate,
sampling-based procedure in IS 456 clause 16, `[NV]` not read in this pass. Keep these apart:
*characteristic · target mean · predicted mean · individual specimen · batch · acceptance.*

---

## §6 Verification — the standard is its own test suite

`[IS]` IS 10262:2019 contains six worked examples with published answers:
**Annex A** (M40, OPC/PPC) · **B** (M40, fly ash) · **C** (M40, GGBS) · **D** (M70, high strength) ·
**E** (M30, SCC) · **F** (M15, mass concrete).

`[PC]` All six become unit tests. Passing all six verifies Layer 0 against the standard rather than
against our reading of it.

`[V]` Coverage of the previous engine, per Build Manual v2: 13 assertions, drawn from Annexes A, D
and F only. **B, C and E were never tested.** `[EI]` And the D assertions covered only the water
step, not the w/cm step — which is precisely why §8.1 went unnoticed.

**Minimum assertions per annex for the rewrite:**

```
A   target 48.250 | w/c 0.360 | water 148 | cement 412
    | CA volume fraction 0.648 | volume closure 1.000
B   water 201.62 -> 155 | cement 431 | cementitious 474 (+10%)
    | fly ash 30% = 142 | OPC 332 | w/cm 0.327
C   cement 431 | GGBS 40% = 172 | OPC 259 | w/cm 0.36
    | CA volume 0.648 -> 0.583 after the 10% pumpable reduction
D   target 79.9 | *** w/cm 0.29 FROM TABLE 8 ***  <- the assertion that catches SS8.1
    | water 186 -> 201.624 -> 141 | cement 486 -> cementitious 535
    | fly ash 80.25 | silica fume 26.75 | OPC 428 | revised w/cm 0.264
E   target 38.25 | w/c 0.43 | powder 520 | water/powder by volume 0.99
F   target 20.775 -> x1.25 wet sieving = 26.0 | w/c 0.61 capped to 0.60
    | cement 192 -> cementitious 221 (+15%) | fly ash 25% = 55 | OPC 166
    | min cement 240 - 30 = 210
```

`[EI]` The Annex A cement of 412 comes from 148/0.36 = 411.11 rounded up in the standard's own text.
Assert to ±1 kg, not to the decimal.

### 6.1 A real bug the annex tests caught, worth repeating

`[V]` IS 10262 Table 5 prints its columns **Zone IV, III, II, I — right to left**. Reading them
left to right reverses every row. The previous engine produced a CA volume of 0.668 where Annex A
publishes 0.648; every other number looked fine. Without the Annex A test it would have shipped,
and every mix would have carried the wrong sand-to-stone ratio.

---

## §7 The two models

### 7.1 Strength — the measured result that decides the architecture

`[V]` GroupKFold, 8 splits, grouped on mix signature. 72 records containing **59 independent
mixes**. Every transform fitted inside the fold.

| Predictor | RMSE | R² |
|---|---|---|
| Abrams, 2 parameters, code form | **6.50 MPa** | 0.856 |
| Gaussian Process, 3 features | **6.16 MPa** | 0.871 |
| difference | 0.34 MPa | — |

`[V]` Bootstrapped 5,000 times: **95% CI on (Abrams RMSE − GP RMSE) = [−0.34, +1.03] MPa.**
P(GP better) = 0.83. Per-fold difference: `+0.50 +1.85 +0.75 +0.77 +1.50 −1.06 −1.29 −0.62`.
GP wins 5 folds, **loses 3**.

`[EI]` **The interval crosses zero. The GP is not reliably better at predicting strength.** The
0.34 MPa gap is smaller than the between-fold swing (±1.3 MPa). This is a finding, not a setback.

`[PC]` **Architecture that follows:** Abrams is the **predictor**; the GP supplies only the
**uncertainty**, fitted on the residual. Day one the residual is zero and the answer is exactly
IS 10262's, so the system cannot be worse than current practice. Put the ML where the code has no
answer — the **water demand** — and the novelty in the closed loop.

`[ML]` Strength mean: `ln(f28) = a − b·(w/b)`, OLS on log strength.
`[V]` Fitted on project data: `ln(f) = 5.061 − 3.319·(w/b)`.
`[ML]` Strength spread: `sklearn` GaussianProcessRegressor,
`ConstantKernel × Matérn(ν = 2.5, isotropic) + WhiteKernel`, on the residual.
Features: `w_b_free`, `scm_pct_of_binder`, `paste_vol_frac`. `[V]` PICP90 = 0.889 — close to nominal.
`[V]` Adding `mean_7d` drops RMSE to 3.90 MPa and narrows the 90% band from ±10.8 to ±6.5.

### 7.2 What the 463 cubes are worth — quality, not quantity

`[V]` 463 cube results · 251 at 28 days · 68 mixes with ≥3 cubes at 28 days.
Pooled within-mix SD = **2.88 MPa** (test repeatability). SD of a 3-cube mean = **1.66 MPa**
(label noise). Of the GP's 6.16 MPa error, 1.66 is label noise and **5.93 is genuine model
error — 96%**.

`[EI]` Better labels will not help. More mixes and better features will.

`[V]` Replicate counts across the 72 records: 12 records have **0** cubes at 28 d (their "28-day"
value came from tests at 30–37 days) · 1 record has 2 · 44 have 3 · 15 have 6.
`[EI]` Those 12 are biased upward — concrete keeps gaining strength after 28 days. Fix them before
refitting.

`[V]` Fixing the GP's noise term at the measured 1.66 MPa **made it worse**: RMSE 6.16 → 15.11,
calibration degraded. `[EI]` The noise term was absorbing model error, not just measurement error.

`[EI]` **Do not expand to one row per cube.** Three cubes from one trial are three measurements of
one point. 463 rows would make the model think it has more evidence than it does; CV scores would
rise while real accuracy stayed flat. `[PC]` Instead: report 2.88 MPa as measured repeatability;
weight records by cube count; and treat a trial landing within 2.88 MPa of prediction as a hit.

### 7.3 Workability — model the water, not the slump

`[V]` Predicting slump directly **failed**: R² **0.18** on 39 records; slump flow R² **0.005** on 27.
`[EI]` The cause is not the model. In historical plant records the operator targeted a slump and
kept adding water until they hit it — **slump was an input, not an outcome.**

`[PC]` **Target `Δ = water_actually_used − water_from_IS 10262`.** Not slump.
`[ML]` Same GP class. Prior: mean 0, wide variance — day one the system is exactly the code.
Features: msa, target slump, admixture % of binder, sand type. Add sand fines and temperature when
available.
`[PC]` Fit only on trials where **the optimiser set the water**, never on operator-chased records.
Log `slump_achieved − slump_target` separately as the convergence evidence.

`[IS]` The standard endorses this framing. cl 5.3 requires water content to be established by trial;
cl 5.8 requires trial mixes and adjustment of water/admixture. `[IS]` And the **Foreword** names
both principles explicitly: *"the proportioning of mixes are **Abram's law** for strength
development and **Lyse's rule** for making mix with adequate workability."*
`[EI]` A Foreword statement, **not** a clause requirement — so neither may be used as a compliance
gate. But it does mean both baselines are the standard's own, which is a stronger position than
"declared benchmark". `[PC]` Layer 08 needs a Lyse-form baseline, so the workability model has
something to beat, exactly as Abrams serves strength.

### 7.4 The coupling — why the models are not independent

`[EI]` Strength and workability are coupled through the mix-design equations, not through a joint
fit. One workability observation propagates automatically:

```
water changes by DELTA
  -> binder = water / (w/b)                  binder moves
  -> paste volume = binder/SG + water + air  paste volume moves
  -> aggregate volume = 1 - paste            aggregates move
  -> paste_vol_frac is a STRENGTH feature    the strength prediction moves
```

`[PC]` Never fit the two jointly. Let the mix-design chain do the coupling, the way the code does.
`[PC]` No cached value may survive an input change — recompute the whole chain per candidate.

---

## §8 Defects in the existing `is_sdl/` — recorded, not fixed

`[PC]` Code untouched by request. These are the things the from-scratch rewrite must not reproduce.

### 8.1 M65 uses the wrong section of IS 10262 — **the serious one**

`[V]` `Build_Manual_Mix_Design_SDL.docx` §2.1 and §6 derive M65's w/b as **0.230**, attributed to
"IS 10262 Fig 1". That number is the two-point Fig 1 fit extrapolated to the M65 target mean of
74.90: `(5.0902 − ln 74.90)/3.3715 = 0.2296`.

`[IS]` M65 is **domain C**. IS 10262:2019 cl 6.2.5 and **Table 8** apply, not Fig 1. At 20 mm msa,
Table 8 gives 0.33 at target 70 and 0.31 at target 75 → for 74.90, **w/cm ≈ 0.31**.

`[EI]` 0.230 against 0.31 is a **26% error in w/cm**, and it propagates directly into binder. The
Build Manual's showcase result — *"M65 binder 645 kg/m³, therefore 33% fly ash is needed to hold
OPC under 450"* — is an artifact of the wrong clause. On the Section 3 route (Table 7 water,
PCE −30%, w/cm 0.31) binder lands far lower, and Annex D shows a genuine M70 finishing at
**428 kg OPC** with 20% SCM taken from Table 9.

**Consequences:**
- The M65 and M50 rows of Build Manual v2 §6 are **withdrawn**. So is the §2.2 escalation narrative.
- `[EI]` The whole v2 §6 sweep was generated by this engine. Treat every row as unverified until
  regenerated by corrected code.
- The catch is one assertion: **Annex D, w/cm = 0.29 from Table 8.** Add it first.

### 8.2 A compliance check that can never fail

`[V]` `is_sdl/is_check.py`:

```python
out.append(('design mix required above M20',
            not (req.grade > T.NOMINAL_MIX_MAX_GRADE and False),
```

`and False` makes the inner expression always `False`, so `not False` is **always `True`**. The
check prints PASS in every report ever produced, including the M65 one, having evaluated nothing.

`[EI]` A gate that prints PASS for a check it does not run is the exact failure the gate exists to
prevent. In the rewrite: implement it against IS 456 cl 9.1.1 — a nominal mix above M20 fails —
or delete it. Never leave it printing.

### 8.3 The default `use` and `exposure` make M10–M20 unreachable

`[V]` `is_sdl/derive.py` defaults `use='RCC'` and `exposure='moderate'`.
`[IS]` IS 456 Table 5, moderate + RCC → minimum grade M25. So checks must fail for M10/M15/M20 —
yet v2 §6 reports them as feasible (238 / 248 / 162 cold-start mixes). Either §6 was generated with
different settings than §2.1 documents, or the feasible-count path never called the gate.

`[EI]` The resolution is **not** to weaken the check. It is IS 456 cl 6.1.3 — add the third `use`
category for plain, lean, simple-foundation and temporary work. See §1.2.

### 8.4 An admixture dosage cap with no verified source

`[V]` `is_check.py` enforces `admix_pct <= T.MAX_ADMIX_PCT` (2.0% of binder), attributed to IS 9103.
`[IS]` IS 456 cl 5.5.1 says only: "Admixture, if used shall comply with IS 9103." No dosage cap.
`[NV]` **No 2.0% cap has been verified in IS 9103 : 1999.** For context, IS 10262 Annex G gives
*typical* doses — plasticisers 0.3–0.5%, superplasticisers 0.5–1.5% — as guidance, not as limits,
and the annex is informative.

`[EI]` Until the source is found, this check must report `NOT VERIFIED`, not `PASS`. If no numeric
cap exists in IS 9103, reclassify it as a **project constraint** and label it so.

### 8.5 Known gap carried forward from v2

`[V]` Fig 1 curves 1 (OPC 33) and 3 (OPC 53) are not digitised; the engine falls back to curve 2.
`[EI]` This is a live correctness issue for OPC 33 and OPC 53 mixes, compounding the §4.1
extrapolation problem below w/c 0.36.

---

## §9 What is explicitly not settled

1. `[NV]` Amendment currency of every IS 456 clause cited here. §0.3.
2. `[NV]` IS 456 Table 5 cells not corroborated by the IS 10262 annexes — OCR-damaged source. §5.3.
3. `[NV]` IS 383 sand zones and CA grading. Cited by the engine, never verified. **Still open.**
   The edition question is closed (§0.3 — it is the Third Revision), but that settles which
   document to read, not what it says. The zone and grading tables have not been read.
4. `[NV]` IS 9103 dosage limits. §8.4.
5. `[NV]` IS 1489 (Part 1) and IS 455 pozzolana/slag limits that gate Table 5 Note 1. §5.2.
6. `[NV]` IS 456 Table 7 (workability degrees) — cited by `derive.py`, not read.
7. `[NV]` IS 456 clause 16 acceptance criteria — needed to keep *acceptance strength* distinct.
8. ~~`Mixed Design Data.xlsx` is missing.~~ **RESOLVED — it is `source_b_workbook.xlsx`.** See §0.4.
   The open item is now trivial: the three scripts hard-code a stale sandbox path.
9. `[V]` **RESOLVED — `source_a_workbook.xlsx` is NOT in the 72 records.** It holds 22 records from
   Plant A (`L1` Site A1, `L2` Site A2), all `lab trial mix`, 22 unique `design_id`, all
   M-sand, grades M10–M55. `source_b_workbook` contains only `Plant B` (68), `Plant C` (28) and `PLT` (7).
   Zero `design_id` overlap. Merging it is the largest single gain available: **+22 independent
   mix designs onto 96**.
10. `[V]` **RESOLVED — the schema is consistent; there are no competing schemas.**
    `Concrete_Data_Entry_Template_BLANK.xlsx` is **104 columns**, not 98. All four workbooks share
    the same core and the same first eight columns:
    `data/meet` 98 = template minus the six retention columns (`slump_60/120/180min`,
    `flow_60/120/180min`) · `source_a_workbook` 105 = template plus `flow_initial` ·
    `source_b_workbook` DATA 126 = template plus 22 trial-sheet fields (`aim_of_trial`, `cement_brand`,
    `wc_ratio_sheet`, `t500_sec`, `vfunnel_sec`, `fibre_kg`, …). `MODEL_READY` (38 derived columns)
    is a computed view over `DATA`, not a rival schema. Correct "98-column template" to
    **104-column template** wherever it appears in project documents.
11. `[NV]` `data/source_e/` — 8 mix-design PDFs, not converted into any workbook.
12. `[V]` **`data/meet/Data_Compiled.xlsx` — 256 batches of 5 approved designs from a genuine RMC
    plant and testing facility (confirmed by the supplier).** Single plant `Plant D`,
    1 May – 31 Aug 2026, all PPC / M-sand / Zone II / 20 mm / RCC / PCE / cube 150.
    Traceable by `batch_no` (256/256 populated, 245 unique, format `PIC-YYMMDD-NN`) and
    `batch_date`; 11 `batch_no` values repeat and need checking.

    **Internally consistent.** Reading the aggregate columns as **as-batched wet masses** (which is
    what `ca_moisture` and `sand_moisture` are recorded for) and fly ash as separately batched,
    absolute volume closes at **mean 1.0087 m3 with 5/256 outside +/-3%**, and batched mass agrees
    with measured `fresh_density` to **+8.2 kg** on average. Fly ash varies by design
    (7.45 / 9.60 / 11.56 / 13.20 / 11.40 % of binder), so it is a design variable, not a PPC
    breakdown. Within-test CV across three 28-day cubes is **1.40-2.42%** — tight, consistent with
    one well-run QC lab repeating five mixes, and not comparable to the project's 2.88 MPa, which
    pools lab trial mixes across three different facilities.

    **Its unique value — IS 10262 cl 4.2.1.1 established standard deviation.** The clause requires
    not less than 30 results. Four designs qualify, and every established S is below the Table 2
    assumed value:

    | design_id | n | grade | established S | Table 2 assumed S | cl 4.2.1.1 |
    |---|---|---|---|---|---|
    | M20-P-20MS-01 | 31 | M20 | 3.41 | 4.0 | yes |
    | M25-P-20MS-01 | 64 | M25 | 2.63 | 4.0 | yes |
    | M30-P-20MS-01 | 82 | M30 | 2.75 | 5.0 | yes |
    | M35-P-20MS-02 | 51 | M35 | 3.28 | 5.0 | yes |
    | M40-P-20MS-02 | 28 | M40 | 2.50 | 5.0 | no (n<30) |

    `[EI]` This feeds cl 4.2 directly. For M30 the assumed S gives a target mean of
    max(30 + 8.25, 36.5) = 38.25; the established S = 2.75 gives max(30 + 4.54, 36.5) = **36.5**,
    where the X floor binds. A 1.75 MPa lower target permits a higher w/c, hence less binder, hence
    less cement, cost and carbon — the project's objective reached through a clause rather than a
    model. **No other dataset in the project can do this:** `source_b_workbook`'s 103 records spread across
    96 designs, so no single design reaches 30 results.

    **Limits, and these do not depend on origin.** 5 `design_id` values means **5 design points** for
    a strength model regardless of how many batches sit behind them; twelve categorical columns have
    zero variance so carry no signal; 100% M-sand and 100% Zone II means no sand contrast for the
    correction tier (`source_b_workbook` supplies that: 73 M-sand / 28 blended / 2 natural); all three lot
    IDs are blank. `[IS]` And 31 rows — every M20 batch, labelled moderate exposure + RCC — sit below
    the IS 456 Table 5 minimum grade of M25, with 22 exceeding the Table 5 maximum free w/c. Confirm
    with the plant whether `exposure` and `concrete_use` were recorded per batch or defaulted during
    transcription; if recorded, this is a real compliance finding and evidence the Layer 05 checker
    earns its place.

    **Use it for:** the cl 4.2.1.1 established-SD result; batch-to-batch process variance at fixed
    design; a compliance-checker fixture with a known answer key; and a leakage demonstration
    (random split vs GroupKFold on `design_id`). **Not for:** training the strength model, or the
    M-sand correction tier.

13. `[IS]` **Crusher dust is not crushed sand — and the project has not confirmed which it has.**
    IS 383:2016 **Foreword**, referencing **cl 3.1.2**, states verbatim:

    > "A crusher dust (or quarry dust) produced from the fine screening of quarry crushing cannot
    > be called crushed sand as per **3.1.2**. It may not be generally in conformity to the
    > requirement of crushed sand as per the standard and is not expected to perform as efficiently
    > as properly crushed sand, **unless it is processed to meet the requirement of this standard**."

    `[EI]` Note the qualifier. This is **not an outright exclusion**: processed crusher dust that
    meets cl 3.1.2 does qualify. Recording it as a ban would be stricter than the standard, the same
    error §5.1 warns about for the 450 rule.

    `[EI]` **It is a Foreword statement, not a clause requirement**, so it cannot become a compliance
    gate — exactly the treatment §7.3 gives Abrams and Lyse, which the Foreword also names. It
    informs how M-sand is described and stratified, not whether a mix passes.

    `[NV]` **Unconfirmed for this project's data.** Nothing on record establishes whether the M-sand
    in `source_b_workbook`, `source_a_workbook` or `data/meet` is properly crushed sand per cl 3.1.2, processed
    crusher dust, or unprocessed quarry dust. The workbooks carry a sand *type* but no cl 3.1.2
    conformity evidence. Since the M-sand correction tier is the project's subject matter, the
    distinction matters: three sources may not be describing the same material. **Do not resolve
    this by inference from the column labels.** It needs the crusher's own test data or a statement
    from the supplier, per source.

    `[NV]` cl 3.1.2 itself has not been read — see item 3.

    `[V]` **And it cannot be read by machine.** `standards/is383_2016.pdf` is a scanned image with
    **no text layer**: `pdftotext` yields 22 characters, all form feeds — 22 page breaks and not one
    character of content. Every value in IS 383 must be read from page images by a human or a
    vision model, and **no script can ever verify a value against this file**. Any IS 383 rule
    entering the registry is therefore attested by a reading, not by an extraction, and the
    `[NV]` → `[IS]` promotion for those rules will always rest on that. By contrast
    `standards/is10262_2019.pdf` (114,400 characters) and `standards/is456_2000.pdf` (256,703) do
    carry text layers and can be cross-checked mechanically.

---

## §10 Build order for the rewrite

Ordered by risk. The step most likely to invalidate everything after it goes first.

| # | Build | Done when |
|---|---|---|
| 0 | `git init`. Nothing below is auditable without it. | first commit exists |
| 1 | Repoint the three scripts at `source_b_workbook.xlsx`; hash and freeze the source PDFs | `decide.py` runs unmodified otherwise; a manifest of hashes exists |
| 1b | Merge `source_a_workbook.xlsx` (22 designs) into `MODEL_READY`; convert `data/source_e/` (8 PDFs) | independent design count rises from 96 toward ~126 |
| 2 | Re-run the bake-off on the recovered data | Abrams / GP land near 6.50 / 6.16, or §7 is rewritten |
| 3 | Confirm IS 456 Table 5 visually; resolve §9 items 3–7 | the `[NV]` list shortens |
| 4 | `is_tables` — both chains kept separate, Section 2 and Section 3 | Table 8 and Table 10 exist as first-class tables |
| 5 | `derive` — three `use` categories, three grade domains, everything else `[ASSUMED]` | M5 returns nominal; M65 routes to Section 3 |
| 6 | `is_design` — the two chains of §3 | — |
| 7 | **All six annexes as tests, Annex D's w/cm assertion first** | 6/6 annexes reproduce to the printed values |
| 8 | `is_check` — nine checks of §5, no vacuous ones, `NOT VERIFIED` is a real outcome | a failure names its clause; nothing prints PASS unevaluated |
| 9 | Fix the 12 off-age records; log 2.88 MPa repeatability | dataset note written |
| 10 | Abrams predictor + GP residual for uncertainty | RMSE reproduces; PICP90 near 0.90 |
| 11 | Envelope, candidate sampling, `P(f28 < fck) ≤ 0.05` filter | requirement in, compliant mixes out |
| 12 | Workability Δ-water model, initialised at zero, with a Lyse-form baseline | water rule reproduces Annex A |
| 13 | Full recomputation coupling; no cached value survives an input change | stale-value test passes |
| 14 | Acquisition and batch portfolio | proposals carry intervals and clause citations |

`[PC]` Steps 11–14 stay closed until 7 and 8 pass. `[BO]` Acquisition-function choice is deferred;
no claim of superiority without a comparison.

`[PC]` **Non-negotiable:** no unverified rule becomes a hard constraint · no guessed value replaces
missing data · no source record is silently overwritten · no cube is an independent mix experiment ·
no human rejection is a physical failure · no candidate bypasses the deterministic engine or the
gate · no model claims production readiness, guaranteed strength, or compliance outside its
verified domain.

`[PC]` **What this system is:** a standards-traceable, uncertainty-calibrated research prototype for
mix-design prediction and constrained optimisation, using a deterministic Indian-Standard baseline,
comparing a GP against an Abrams baseline, modelling strength and workability separately, and
proposing candidate research mixes inside a declared verified domain. It is **not** an RMC
production-control or automatic mix-approval system.

---

## Weakest link

The data-availability blocker is gone — §0.4 is resolved and §7 reproduces exactly.

What remains is **thin coverage at the ends of the grade range, and a workability set too small to
carry the project's novelty.** The 72-record strength set holds M10 x1, M15 x3, M60 x1 against
M40 x19 and M35 x11, so domain-A and high-domain-C behaviour rests on one or three points each.
The workability sets are smaller still: slump n=39 across 33 groups, slump-flow n=27 across 21 —
and §7.3 forbids merging them. The Δ-water model is where the novelty lives and it has the least
data behind it.

**Check:** merge `source_a_workbook.xlsx` and convert `data/source_e/`, then recount groups per grade and
per workability metric. If slump still sits below ~50 groups after the merge, the honest move is to
narrow the declared grade domain rather than model across a range the data cannot support.
