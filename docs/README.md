# docs/

`Build_Manual_v3.md` is the **canonical authority** for every engineering rule, standards clause,
measured figure and open item in this project. Every module in `msand_sdl/` cites a section of it.
It supersedes `Build_Manual_Mix_Design_SDL.docx` (v2), `Implementation_Plan_SDL.docx` and `poa.md`
wherever they disagree.

Do not restate a value from it in code. Values load from `s01_codify` at runtime.

## Citation map — stage to manual section

| Stage | Section | What it covers |
|---|---|---|
| shared (`msand_sdl/*.py`) | §2 | the two inputs and what they unlock |
| S01 CODIFY | §0 | verification ledger; what is read, what is `[NV]` |
| S02 INGEST | §9 | the four data sources and what each is worth |
| S03 PREPARE | §7.2 | replicates, grouping, what the 463 cubes are worth |
| S04 DESIGN | §1, §2.1, §3, §4 | domains, target mean, both chains, Fig 1 |
| S05 VERIFY | §1.2, §5, §5.1, §5.2, §8.4 | the nine checks and the 450 rule |
| S06 EVALUATE | §7.1 | grouped validation, bootstrap, calibration |
| S07 STRENGTH | §7.1 | Abrams predictor, GP on the residual |
| S08 FLOW | §7.3 | model the water, not the slump; Lyse baseline |
| S09 PROPAGATE | §7.4 | why the models are not independent |
| S10 PRICE | §10 | — see open item below |
| S11 PROPOSE | §10 | build order steps 11 and 14 |
| S12 LEARN | §10 | — see open item below |

## Open

**S10 PRICE and S12 LEARN have no dedicated section in the manual.** Cost, carbon and the
human-in-the-loop protocol are described in the Project Report and the project instructions but
were never written into the canonical manual. Both currently cite §10 (build order) as a
placeholder. Add §11 (objectives) and §12 (review protocol) to the manual, then remap.
