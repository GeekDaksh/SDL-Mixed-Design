"""Requested band against model uncertainty, checked before optimising.

Stage: S08 FLOW
Spec:  Build_Manual_v3.md §S08
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import Any

from ..contracts import Prediction, Requirement


def is_achievable(model: Any, requirement: Requirement) -> bool:
    """Whether the requested workability band lies inside what the model can resolve."""
    raise NotImplementedError(
        "s08_flow.achievability.is_achievable — see Build_Manual_v3.md §S08"
    )


def band_width(requirement: Requirement) -> float:
    """Return the width of the requested workability band."""
    raise NotImplementedError("s08_flow.achievability.band_width — see Build_Manual_v3.md §S08")


def check(model: Any, requirement: Requirement) -> None:
    """Raise before optimisation if the requested band is narrower than the model's uncertainty."""
    raise NotImplementedError("s08_flow.achievability.check — see Build_Manual_v3.md §S08")


def resolution(prediction: Prediction) -> float:
    """Return the finest band this prediction can distinguish."""
    raise NotImplementedError("s08_flow.achievability.resolution — see Build_Manual_v3.md §S08")
