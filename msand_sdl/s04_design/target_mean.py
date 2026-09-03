"""Target mean strength, assumed and established standard deviation.

Stage: S04 DESIGN
Spec:  Build_Manual_v3.md §S04
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Provenance


def assumed_standard_deviation(grade: str) -> tuple[float, Provenance]:
    """Return the tabulated standard deviation for a grade, with its provenance."""
    raise NotImplementedError(
        "s04_design.target_mean.assumed_standard_deviation — see Build_Manual_v3.md §S04"
    )


def established_standard_deviation(results: list[float]) -> tuple[float, Provenance]:
    """Return the standard deviation established from plant test results, with its provenance."""
    raise NotImplementedError(
        "s04_design.target_mean.established_standard_deviation — see Build_Manual_v3.md §S04"
    )


def target_mean_strength(grade: str, standard_deviation: float) -> float:
    """Return the target mean strength; both IS 456 expressions are evaluated where required."""
    raise NotImplementedError(
        "s04_design.target_mean.target_mean_strength — see Build_Manual_v3.md §S04"
    )
