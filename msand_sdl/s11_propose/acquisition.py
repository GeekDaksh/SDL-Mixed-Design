"""The acquisition function; no superiority claimed.

Stage: S11 PROPOSE
Spec:  Build_Manual_v3.md §S11
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..contracts import Prediction

if TYPE_CHECKING:
    import numpy as np


def score(prediction: Prediction, incumbent: float) -> float:
    """Score one candidate. The choice of acquisition is recorded, not argued for."""
    raise NotImplementedError("s11_propose.acquisition.score — see Build_Manual_v3.md §S11")


def rank(scores: np.ndarray) -> np.ndarray:
    """Return candidate indices ordered by acquisition score."""
    raise NotImplementedError("s11_propose.acquisition.rank — see Build_Manual_v3.md §S11")


def name() -> str:
    """Return the acquisition function in use, for the proposal record."""
    raise NotImplementedError("s11_propose.acquisition.name — see Build_Manual_v3.md §S11")
