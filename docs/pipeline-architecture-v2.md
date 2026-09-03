# M-Sand SDL — Pipeline Architecture v2

**Supersedes `pipeline-architecture-v1.md`.** The twelve stages, their names, numbers, packages and
internal file lists are unchanged — read v1 for those. This document records what changes once the
system is described as serving **three different users** rather than one.

`Build_Manual_v3.md` remains canonical for every engineering rule.

---

## 1. What the three-user framing actually changes

v1 had one implicit entry point: a requirement goes in, a ranked portfolio comes out. That is
User 1's path. User 2 and User 3 were assumed to be the same path used differently. They are not —
they differ in what the optimiser is allowed to prefer, in whether the models are written to, and
in what leaves the system.

| | User 1 — plant engineer | User 2 — researcher | User 3 — data maintainer |
|---|---|---|---|
| Entry | an order | an experiment budget | a delivery of records |
| Stages touched | 04 -> 11 -> 09 -> 07/08 -> 10 -> 05 | same, plus 12 | 02 -> 03 -> 06 -> 07/08 |
| Optimiser prefers | feasible and cheap | informative | — |
| Envelope policy | **must stay inside** | **deliberately at the edge** | — |
| Writes to models | never | yes, via S12 | yes, refit |
| Wants | a mix to cast today | the next four experiments | one command |

The envelope row is the important one. The demonstration run in the Project Report proposed four
recipes that all fell **outside** the training envelope. For User 2 that is correct behaviour — the
acquisition function seeks where the models know least. For User 1 the same output is unusable: a
plant cannot cast a mix the models have never seen anything like. Same stage, opposite requirement.

**This is a mode, not a bug, and it has to be explicit in the code or one user will silently get
the other's answer.**

---

## 2. Changes to the structure

### 2.1 Three entry points — new package `msand_sdl/entry/`

v1's `scripts/00…04` are ordered by *build sequence*. That is the wrong axis now — nobody's job is
"step 03". Keep the build scripts, add an entry layer named for the people:

```
msand_sdl/entry/
├── __init__.py
├── contract.py       Order / Campaign / Delivery, and what each returns
├── serve.py          User 1 — an order in, a ranked portfolio out. Read-only.
├── explore.py        User 2 — a requirement and a budget in, informative experiments out.
└── refresh.py        User 3 — new records in, retrained and re-evaluated models out.
```

Each is a thin composition of stages — no logic of its own. `serve.py` is also the **API boundary
for a future front end**: define its contract now so a form can call it later without the pipeline
being reshaped around a UI.

### 2.2 S11 PROPOSE gets two modes

```python
class Mode(Enum):
    SERVE = "serve"        # User 1
    EXPLORE = "explore"    # User 2
```

What the mode changes:

| | SERVE | EXPLORE |
|---|---|---|
| `envelope.py` | hard reject outside the training envelope | permit, and **flag** each proposal as extrapolated |
| `acquisition.py` | not used — rank feasible candidates on the cost–carbon front | qNEHVI, batch of 4 |
| `constraints.py` | identical probabilistic constraints in both modes | identical |
| output | recipes to cast today | recipes to learn from |

The constraints do **not** relax in EXPLORE mode. Exploration widens where the models may be asked
to predict; it never widens what IS 456 permits.

### 2.3 S05 verdicts travel with the recipe

User 1's stated output includes *"which IS clauses it satisfies."* In v1, S05 is a filter — it
discards failures and the survivors carry nothing. Change: `VerifyOutput` attaches to each surviving
recipe and is returned in the portfolio. A plant engineer signing off a mix needs the clause list,
not the assurance that a filter ran.

### 2.4 New shared module — `msand_sdl/materials.py`

The plant inputs ("entered once, updated when materials change") are not a stage input and not
historical data. They are **state**, and a recipe is only valid against the state it was proposed
under.

```
MaterialState
├── sand: sieve analysis, absorption, specific gravity
├── coarse: absorption, specific gravity, nominal max size
├── cement: type and grade            <- see §3.2
├── scms available
└── state_hash                        <- every proposal records this
```

`zone_from_sieve()` lives here and applies the IS 383 Table 9 rule loaded from S01 — it is the link
from a measured grading curve to the zone that IS 10262 Table 5 needs. `[NV]` IS 383 is still
unread (Build Manual §9 item 3), so this function must return the zone **and** its verification
status, not a bare zone.

Recording `state_hash` on every proposal is what stops a recipe proposed under one sand grading from
being re-used after the quarry changed.

### 2.5 S10 PRICE — values carry provenance

Rates and carbon factors are placeholders today. A portfolio ranked on placeholder numbers that does
not say so is the same failure class as a compliance check that prints PASS without evaluating.

```python
class ValueStatus(Enum):
    MEASURED = "measured"        # from the plant
    PUBLISHED = "published"      # a citable Indian source or EPD
    PLACEHOLDER = "placeholder"  # neither — must be surfaced on every output
```

Cost and carbon each report their worst constituent status. A portfolio whose ranking depends on a
`PLACEHOLDER` carbon factor says so on its face.

### 2.6 Every proposal carries a validation level

The project instructions require these four to stay distinct. Nothing in v1 tracked them.

```python
class ValidationLevel(Enum):
    COMPUTATIONALLY_COMPLIANT = 1
    LAB_VALIDATED = 2
    TRIAL_BATCH_VALIDATED = 3
    PRODUCTION_VALIDATED = 4
```

**Every recipe this system has ever produced is level 1.** No proposal from it has been physically
cast. The level is set by S12 when a measured result comes back, and is printed on every output.
This is the single most important honesty mechanism in the system and it costs almost nothing to
add.

---

## 3. Two gaps that are one gap

### 3.1 The material specification gap

The system takes cement as a mass. It should take **OPC 33 / OPC 43 / OPC 53 / PPC / PSC**, because
the difference is worth roughly 10 MPa at the same water–cement ratio.

### 3.2 …is the same thing as Build Manual §8.5

`[IS]` IS 10262:2019 Fig 1 has three curves, selected by the expected 28-day cement strength —
Curve 1 for >=33 and <43 N/mm², Curve 2 for >=43 and <53, Curve 3 for >=53 and above.
`[V]` Build Manual §4 fits Curve 2 exactly from two annex anchor points. `[NV]` Curves 1 and 3 have
**no verified anchor points**, and the previous engine silently fell back to Curve 2 for all three.

So "the system takes cement as a mass" and "curves 1 and 3 are not digitised" are the same defect
seen from two ends. Adding a `cement_grade` field without digitising the curves changes nothing;
digitising the curves without the field has nothing to select on. **Do both in one task**, in
`s04_design/fig1.py` and `msand_sdl/materials.py`.

`[EI]` Until curves 1 and 3 are read off the printed figure, any OPC 33 or OPC 53 mix must be
flagged as using a Curve 2 approximation — labelled as a project approximation, not as Fig 1 Note 2,
which permits the substitution only for PPC/PSC without strength data.

---

## 4. Build order, re-prioritised

v1 ordered by structural risk. One thing outranks that now.

**Workability is the binding constraint.** At ~18 mm error against a typical ±25 mm band, the
optimiser cannot satisfy a tight slump requirement at any confidence level worth stating. The
Project Report found this itself: the requested band is narrower than the model's own uncertainty.
Improving the strength model — already statistically tied with a formula from 1918 — widens the
feasible region by nothing. Improving the workability model widens it more than everything else
combined.

| | v1 order | v2 order | why |
|---|---|---|---|
| after S06 | S07 then S08 | **S08 then S07** | S08 is the binding constraint |
| S08 first task | fit the model | **`achievability.py`** | it tells User 1 up front that a band cannot be met, before any optimisation runs |

Everything before S06 is unchanged: S01 -> S02 -> S03, with the S04 annex tests and the S05
counter-example tests as the gates that must pass before S11 opens.

`achievability.py` first is worth stressing. It is the cheapest module in S08 and it converts the
project's most awkward limitation into a feature: the system says *"a ±25 mm band cannot be
guaranteed with a model whose uncertainty is ±30 mm"* instead of returning an empty portfolio and
looking broken.

---

## 5. What each user needs before their path is real

| | Blocking | Status |
|---|---|---|
| **User 3** | nothing structural | achievable first — the delivery-to-retrain command is the smallest of the three |
| **User 2** | S01–S09, S11 in EXPLORE mode, S12 | **achievable this semester** — this is the capstone |
| **User 1** | real rates · a front end · validated casts · cement grade · a workability model that can hold a band | follow-on |

User 1 is what makes the patent commercially meaningful rather than merely defensible, and none of
its four blockers is a modelling problem. Three are data and interface work; one is the Site B
feature set.

**Do not describe the system as serving User 1 until a cast has come back.** Today it serves
User 2 — you supply a requirement, it proposes experiments, you cast them and feed results back.
That is a self-driving laboratory. Calling it a plant tool before a level-2 result exists is a claim
the evidence does not carry.

---

## 6. Corrections

- **The template is 104 columns, not 98.** Build Manual §9 item 10 resolved this: 98 is
  `data/meet` (the template minus six retention columns). `Concrete_Data_Entry_Template_BLANK.xlsx`
  is 104. Correct it wherever "98-column template" appears — including in User 3's description.
- **Exposure is a customer input, and so is the use class.** IS 456 cl 6.1.3 means the use field has
  three values — RCC, PCC, and the lean/simple/temporary category — not the binary "whether it's
  reinforced". Build Manual §1.2.

---

## 7. Scaffold delta — hand this to Claude Code

Additive. Nothing built in the v1 scaffold is removed.

```
NEW   msand_sdl/entry/{__init__,contract,serve,explore,refresh}.py
NEW   msand_sdl/materials.py                MaterialState, zone_from_sieve, state_hash
EDIT  msand_sdl/contracts.py                + ValidationLevel, ValueStatus
EDIT  msand_sdl/s11_propose/contract.py     + Mode (SERVE | EXPLORE)
EDIT  msand_sdl/s11_propose/envelope.py     policy differs by mode — docstring the difference
EDIT  msand_sdl/s11_propose/acquisition.py  EXPLORE only; SERVE ranks on the front
EDIT  msand_sdl/s05_verify/contract.py      VerifyOutput attaches to the surviving recipe
EDIT  msand_sdl/s10_price/contract.py       every value carries ValueStatus
EDIT  msand_sdl/s04_design/fig1.py          curve selected by cement grade; approximation flagged
NEW   tests/s11/test_modes.py               SERVE rejects extrapolation; EXPLORE flags it
NEW   tests/test_validation_level.py        no output claims a level above COMPUTATIONALLY_COMPLIANT
                                            without a measured result behind it
```

Same rules as the v1 scaffold: stubs only, `NotImplementedError`, **no numeric constants**.
`tests/test_structure.py` must stay green.
