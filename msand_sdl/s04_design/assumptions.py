"""The cl 4.1 inputs grade and slump cannot supply.

Stage: S04 DESIGN
Spec:  docs/Build_Manual_v3.md §2
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Provenance


@dataclass(frozen=True)
class Assumption:
    """One cl 4.1 input the requirement did not supply, with the provenance of its value."""

    # TODO(s04): fields per docs/Build_Manual_v3.md §2


def required() -> tuple[str, ...]:
    """Return every cl 4.1 input a design needs beyond grade and workability."""
    raise NotImplementedError("s04_design.assumptions.required — see docs/Build_Manual_v3.md §2")


def resolve(supplied: dict[str, float]) -> dict[str, Assumption]:
    """Fill each missing cl 4.1 input, recording where the value came from."""
    raise NotImplementedError("s04_design.assumptions.resolve — see docs/Build_Manual_v3.md §2")


def provenance_of(assumption: Assumption) -> Provenance:
    """Return how this assumed value entered the design."""
    raise NotImplementedError(
        "s04_design.assumptions.provenance_of — see docs/Build_Manual_v3.md §2"
    )
