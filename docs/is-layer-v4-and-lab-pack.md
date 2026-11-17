# IS layer v4 and the lab trial pack (2026-10-01)

## Why this was done
Trial 2 of the old run had 90 kg cement + 157.5 kg fly ash + 202.5 kg GGBS (80 % replacement).
It passed because the IS layer counted GGBS in full (IS 455 was not read) and nothing applied
IS 456 cl 5.1. The trials were also not something a lab would cast. This version fixes the IS
layer from the standards and makes every output ready for physical trials.

## What changed in the IS layer (00 → is_rules.py: 102 rules, 63/63 fixtures)
| Standard | Clause | What the code now does | Tag |
|---|---|---|---|
| IS 455:2015 | cl 5 | slag 25–70 % → GGBS counted only up to 0.70/0.30 of the Portland part | [IS] + [EI] method |
| IS 269:2015 | Tables 2, 3; cl 11.1 | OPC 33/43/43S/53/53S certificate check; cement > 3 months = retest (not fail) | [IS] |
| IS 456:2000 | cl 5.2.1.1, 5.2.2 | fly ash / GGBS as part replacement of OPC: allowed | [IS] |
| IS 456:2000 | cl 5.1 (other combinations) | fly ash + GGBS, or PPC + added fly ash → OVERRIDE_REQUIRED unless suitability data recorded | [IS] + [EI] classification |
| IS 456:2000 | cl 5.2.1 | fly ash needs engineer-in-charge permission → reported until recorded | [IS] |
| IS 456:2000 | Table 5 Note 1 | additions counted in cement content and w/c only "if the suitability is established" | [IS] + [EI] reading |
| IS 10262:2019 | cl 5.1.1 NOTE | admixture water added to free water in the w/c check (always) | [IS] + [EI] "always" |
| IS 10262:2019 | cl 5.8, A-14, A-15 | 3 trials: design, w/cm −10 %, +10 % at the same water; +10 % held at the Table 5 limit; −5 % if +10 % would duplicate | [IS] + [EI] cap/fallback |
| IS 10262:2019 | A-10 NOTE, A-11, A-13 | SSD → weighed masses and corrected water; 20/10 mm split | [IS] + [EI] wet case |
| IS 1199 Pt 1/2/3/5, IS 516 Pt 1 Sec 1, IS 2386 Pt 3 | see register | sample size, slump mould, density container (250×280 mm), 150 mm cubes, curing, 14 N/mm²/min, ±15 % rule | [IS] |
| IS 456 cl 15.4 vs IS 516 cl 3.6 | — | ±15 %: "invalid" vs "repeat" → CONFLICT, trial cubes follow IS 516 | [PC] |
| project | — | volume-closure tolerance 0.01 m³ is a project tolerance (IS 10262 cl 5.7 gives no number) | [PC] |
| project | — | the only 450 kg/m³ limit is IS 456 cl 8.2.4.2, on cement. The old total-cementitious cap is removed (owner's decision) | [IS] |

Every claim above was checked a second time, independently, against the PDFs in `IS_codes/`.
That check found and fixed: density container size, moisture units (IS 2386 cl 5.5.1 is % of
SSD), OPC age rule, cl 5.2.1 permission, Note 1 suitability, clause numbers, IS 2386 edition.

## What the plant's data gives (from 04_workability_dataset.csv)
PPC, Class F fly ash added, M-sand Zone II, 20 mm basalt, PCE. Absorption, admixture solids,
20 : 10 mm split and moisture are family medians. **PPC + fly ash** has 256 production batches
with three 28-day cubes each — recorded as the IS 456 cl 5.1 suitability evidence [EI].
Still declared, not measured: fly ash SG 2.20 (assumed), admixture range 0.621–1.476 %
(plant-observed) — see `missing-inputs-check.md`.

## Results — the M30 / 120 mm / severe / pumped order (notebook 12)
5 designs (all meet P(strength) ≥ 0.90 and P(slump) ≥ 0.80):

| # | binder | PPC | fly ash | water | SP % | w/c counted | P(strength) |
|---|---|---|---|---|---|---|---|
| 1 | 410 | 358.75 | 51.25 | 153.9 | 1.421 | 0.440 | 0.935 |
| 2 | 420 | 367.5 | 52.5 | 156.8 | 1.321 | 0.436 | 0.948 |
| 3 | 420 | 367.5 | 52.5 | 153.9 | 1.421 | 0.429 | 0.976 |
| 4 | 430 | 376.25 | 53.75 | 156.8 | 1.321 | 0.426 | 0.981 |
| 5 | 440 | 385 | 55 | 156.8 | 1.321 | 0.417 | 0.994 |

3 physical trials around design 1 (water 153.9 kg in all three, batch 0.050 m³ each):

| trial | binder | PPC | fly ash | w/cm | w/c counted | predicted 28 d |
|---|---|---|---|---|---|---|
| 1 (→2) | 410.0 | 358.8 | 51.3 | 0.375 | 0.440 | 42.8 |
| 3 (−10 %) | 455.6 | 398.6 | 56.9 | 0.338 | 0.397 | 49.0 |
| 4 (+10 %, held at IS 456 max) | 400.4 | 350.3 | 50.0 | 0.384 | 0.450 | 41.4 |

Target mean strength 38.25 MPa.

## Results — every grade in the dataset (notebook 14)
| grade | status | trials |
|---|---|---|
| M20 | refused — IS 456 Table 5: moderate RCC needs M25 | none |
| M25 | 5 designs | 3 (4th trial −5 %: +10 % blocked by Table 5) |
| M30 | 5 designs | 3 (4th trial −5 %) |
| M35 | no design meets P ≥ 0.90 (best 0.89) | 3 learning trials, straddling the target |
| M40 | no design meets P ≥ 0.90 (best 0.30) | 3 learning trials, straddling the target |

## Still open
1. Slump model fails G6 and G9 — every design must be confirmed by trial.
2. IS 383 Table 7 (coarse grading) is not encoded; the 20/10 split is checked in the lab.
3. IS 16415 (composite cement) is not in the library — not used.
4. Fly ash SG and the PCE dosage range need the supplier documents.

**Weakest link:** the trial predictions come from a strength model trained on five design
families of one plant; the trials exist precisely to replace those predictions with
measurements.
