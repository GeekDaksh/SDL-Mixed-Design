"""Pipeline declaration — the ordered stages and their dependencies.

This module is the single place the pipeline order is defined. Nothing else
hard-codes a stage sequence.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    """One pipeline stage."""

    number: int
    name: str
    package: str
    depends_on: tuple[int, ...]
    artifact_dir: str | None


STAGES: tuple[Stage, ...] = (
    Stage(1, "CODIFY", "s01_codify", (), None),
    Stage(2, "INGEST", "s02_ingest", (), "data/s02_ingest"),
    Stage(3, "PREPARE", "s03_prepare", (2,), "data/s03_prepare"),
    Stage(4, "DESIGN", "s04_design", (1,), None),
    Stage(5, "VERIFY", "s05_verify", (1,), None),
    Stage(6, "EVALUATE", "s06_evaluate", (3,), "data/s06_evaluate"),
    Stage(7, "STRENGTH", "s07_strength", (3, 6), None),
    Stage(8, "FLOW", "s08_flow", (3, 6), None),
    Stage(9, "PROPAGATE", "s09_propagate", (4,), None),
    Stage(10, "PRICE", "s10_price", (9,), None),
    Stage(11, "PROPOSE", "s11_propose", (4, 5, 7, 8, 9, 10), "data/s11_propose"),
    Stage(12, "LEARN", "s12_learn", (11,), "data/s12_learn"),
)

#: s05_verify recomputes independently and must never import s04_design.
FORBIDDEN_IMPORTS: tuple[tuple[str, str], ...] = (
    ("msand_sdl.s05_verify", "msand_sdl.s04_design"),
)


def stage_by_number(number: int) -> Stage:
    """Return the stage with this number."""
    for stage in STAGES:
        if stage.number == number:
            return stage
    raise KeyError(f"no stage {number}")
