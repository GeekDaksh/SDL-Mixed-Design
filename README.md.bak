# msand-sdl

A Self-Driving Laboratory for manufactured-sand concrete mix proportioning.

Data flows in one direction through twelve numbered stages. Each stage has one entry point
(`stage.run`) and one contract (`contract.py`).

## The twelve stages

| # | Stage | Package | Transformation |
|---|---|---|---|
| 01 | CODIFY | `s01_codify` | frozen IS PDFs → clause-tagged rule registry |
| 02 | INGEST | `s02_ingest` | plant workbooks → one harmonised raw table |
| 03 | PREPARE | `s03_prepare` | raw table → strength + workability datasets |
| 04 | DESIGN | `s04_design` | requirement + rules → deterministic IS mix |
| 05 | VERIFY | `s05_verify` | mix + rules → per-clause verdict |
| 06 | EVALUATE | `s06_evaluate` | model + dataset → LODO metrics, calibration |
| 07 | STRENGTH | `s07_strength` | recipe → MPa + uncertainty |
| 08 | FLOW | `s08_flow` | recipe → mm + uncertainty |
| 09 | PROPAGATE | `s09_propagate` | changed variable → fully recomputed recipe |
| 10 | PRICE | `s10_price` | recipe + rates → ₹/m³, kgCO₂e/m³ |
| 11 | PROPOSE | `s11_propose` | requirement → ranked candidate portfolio |
| 12 | LEARN | `s12_learn` | trial result → updated, versioned models |

The order is declared once, in [`msand_sdl/pipeline.py`](msand_sdl/pipeline.py). Nothing else
hard-codes a stage sequence.

## Four structural rules

1. **`s05_verify` must never import `s04_design`.** Its independence is the reason it exists.
   `tests/test_structure.py` asserts this by parsing the import graph.
2. **`s04_design` splits Section 2 and Section 3 of IS 10262 into separate modules**, with
   `domains.py` routing first. M65+ must be structurally incapable of reaching the Fig 1 path.
3. **Each model package contains its own classical baseline** — `abrams.py` in `s07_strength`,
   `lyse.py` in `s08_flow` — so a model can never be reported without the thing it must beat.
4. **`s11_propose/space.py` holds cement and cementitious as separate decision variables.**
   IS 456 cl 8.2.4.2 caps cement *excluding* fly ash and GGBS; a single `binder` bound cannot
   express that constraint.

## Status

Scaffold only. Every stage module raises `NotImplementedError`. No standards value, coefficient
or bound appears anywhere in this tree — those load from `s01_codify` at runtime.

## Tests

```sh
make install      # pip install -e ".[dev]"
make test         # pytest
pytest tests/test_structure.py    # the structural invariants; green on a bare scaffold
```

`tests/test_structure.py` is the only test that passes today. Every other test is a skipped
placeholder naming the assertion its stage task must satisfy.

## Authority

`Build_Manual_v3.md` is the authority for every engineering rule — standards values, cleaning
rules, model choices and bounds. This repository defines structure only; where a module needs a
number, it cites the clause and loads the value from the rule registry.
