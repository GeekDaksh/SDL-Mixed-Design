"""Mean, standard deviation and interval.

Stage: S07 STRENGTH
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import Any

from ..contracts import Prediction
from ..recipe import Recipe


def predict(model: Any, recipe: Recipe, age_days: float) -> Prediction:
    """Predict strength for one recipe. Never returns a bare float."""
    raise NotImplementedError("s07_strength.predict.predict — see docs/Build_Manual_v3.md §7.1")


def interval(prediction: Prediction, level: float) -> tuple[float, float]:
    """Return the prediction interval at the requested level."""
    raise NotImplementedError("s07_strength.predict.interval — see docs/Build_Manual_v3.md §7.1")
