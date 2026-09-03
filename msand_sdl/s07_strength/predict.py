"""Mean, standard deviation and interval.

Stage: S07 STRENGTH
Spec:  Build_Manual_v3.md §S07
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import Any

from ..contracts import Prediction
from ..recipe import Recipe


def predict(model: Any, recipe: Recipe, age_days: float) -> Prediction:
    """Predict strength for one recipe. Never returns a bare float."""
    raise NotImplementedError("s07_strength.predict.predict — see Build_Manual_v3.md §S07")


def interval(prediction: Prediction, level: float) -> tuple[float, float]:
    """Return the prediction interval at the requested level."""
    raise NotImplementedError("s07_strength.predict.interval — see Build_Manual_v3.md §S07")
