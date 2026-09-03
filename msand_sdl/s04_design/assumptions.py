"""The cl 4.1 inputs grade and slump cannot supply.

Stage: S04 DESIGN
Spec:  Build_Manual_v3.md §S04
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Provenance


@dataclass(frozen=True)
class Assumption:
    """One cl 4.1 input the requirement did not supply, with the provenance of its value."""

    # TODO(s04): fields per Build_Manual_v3.md §S04


def required() -> tuple[str, ...]:
    """Return every cl 4.1 input a design needs beyond grade and workability."""
    raise NotImplementedError("s04_design.assumptions.required — see Build_Manual_v3.md §S04")


def resolve(supplied: dict[str, float]) -> dict[str, Assumption]:
    """Fill each missing cl 4.1 input, recording where the value came from."""
    raise NotImplementedError("s04_design.assumptions.resolve — see Build_Manual_v3.md §S04")


def provenance_of(assumption: Assumption) -> Provenance:
    """Return how this assumed value entered the design."""
    raise NotImplementedError(
        "s04_design.assumptions.provenance_of — see Build_Manual_v3.md §S04"
    )
