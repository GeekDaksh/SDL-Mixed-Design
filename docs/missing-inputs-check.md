# The two missing inputs: fly ash SG and PCE dose range (checked 2026-10-01)

## What was searched
All three connected folders (SDL, FinalSDL, SDL Implementation), skipping virtual environments.
The dataset comes from `SDL/data/meet/Data_Compiled.xlsx` (plant Plant D).
That folder has only this one workbook. It records:
- fly ash: only "Class F fly ash" / "Class F". No specific gravity, no supplier, no certificate.
- admixture: only "PCE superplasticizer", plus solids % and SG for each batch. No product name and no recommended dose.
- notes column: nothing about certificates.

The other data folders belong to **other plants** and are not part of this repo.
Their fly ash and admixture are not this plant's material, so their numbers were NOT used.

## Result
NOT FOUND. Both values stay labelled as unverified in notebook 14, cell 3:
- `FLYASH_SG = 2.20`: the IS 10262:2019 Annex B-2(d) worked-example value. IS 3812 (Part 1):2013 Table 2 has no specific gravity, so no standard value exists. Only the supplier certificate can give it.
- `ADMIXTURE_RANGE_PCT = (0.621, 1.476)`: the range the plant actually dosed. IS 9103:1999 cl 10.2(f) says the manufacturer declares the recommended dose, so only the PCE datasheet can give it.

## Does it change the answer? (sensitivity run of notebook 14)
| case | M20 | M25 | M30 | M35 | M40 |
|---|---|---|---|---|---|
| fly ash SG 2.0 / 2.2 / 2.4, dose range 0.621–1.476 % | refused | 400 binder, 50 FA, SP 0.721 %, P_s 0.901 | 410 binder, 51.25 FA, SP 1.321 %, P_s 0.916 | no feasible mix | no feasible mix |
| fly ash SG 2.0 / 2.2 / 2.4, dose range 0.4–2.0 % | refused | 370 binder, 46.25 FA, SP 1.20 %, P_s 0.911 | 410–440 binder, SP 0.9–1.4 %, P_s 0.91–0.95 | no feasible mix | no feasible mix |

- **Fly ash SG:** a change of ±0.2 does not change any recommended mix. It only shifts the sand mass by a few kg.
- **Dose range:** it changes which grid point is picked. All picked doses still lie inside what the plant used. The verdict for each grade does not change.
- **When it matters:** if the datasheet maximum is **below 1.32 %**, the M30 recommendation (SP 1.321 %) would break the manufacturer's limit and must be rerun.

## To close this
Get from the plant (Plant D):
1. the Class F fly ash test certificate, for the specific gravity;
2. the PCE product datasheet, for the recommended dose range.

Then put both into notebook 14, cell 3, change the `_SOURCE` strings to the document names, and rerun 14.
