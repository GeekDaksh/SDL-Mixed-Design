"""Confine proposals to the training envelope.

Stage: S11 PROPOSE
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..recipe import Recipe

if TYPE_CHECKING:
    import pandas as pd


def fit(frame: pd.DataFrame) -> dict[str, tuple[float, float]]:
    """Describe the region of input space the training data actually covers."""
    raise NotImplementedError("s11_propose.envelope.fit — see docs/Build_Manual_v3.md §10")


def contains(envelope: dict[str, tuple[float, float]], recipe: Recipe) -> bool:
    """Whether a candidate lies inside the training envelope."""
    raise NotImplementedError("s11_propose.envelope.contains — see docs/Build_Manual_v3.md §10")


def reject_outside(
    envelope: dict[str, tuple[float, float]], candidates: tuple[Recipe, ...]
) -> tuple[Recipe, ...]:
    """Drop every candidate the models would have to extrapolate to score."""
    raise NotImplementedError("s11_propose.envelope.reject_outside — see docs/Build_Manual_v3.md §10")
