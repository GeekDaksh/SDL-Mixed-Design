"""Probabilistic strength and workability constraints plus the S05 gate.

Stage: S11 PROPOSE
Spec:  Build_Manual_v3.md §S11
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Prediction, Requirement
from ..recipe import Recipe


def strength_satisfied(prediction: Prediction, requirement: Requirement) -> float:
    """Return the probability this candidate meets the strength requirement."""
    raise NotImplementedError(
        "s11_propose.constraints.strength_satisfied — see Build_Manual_v3.md §S11"
    )


def workability_satisfied(prediction: Prediction, requirement: Requirement) -> float:
    """Return the probability this candidate lands in the requested workability band."""
    raise NotImplementedError(
        "s11_propose.constraints.workability_satisfied — see Build_Manual_v3.md §S11"
    )


def code_gate(recipe: Recipe) -> bool:
    """Pass a candidate through the verification stage. A failing candidate never ranks."""
    raise NotImplementedError("s11_propose.constraints.code_gate — see Build_Manual_v3.md §S11")
