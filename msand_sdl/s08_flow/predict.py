"""Mean, standard deviation and interval.

Stage: S08 FLOW
Spec:  Build_Manual_v3.md §S08
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import Any

from ..contracts import Prediction
from ..recipe import Recipe


def predict(model: Any, recipe: Recipe) -> Prediction:
    """Predict workability for one recipe. Never returns a bare float."""
    raise NotImplementedError("s08_flow.predict.predict — see Build_Manual_v3.md §S08")


def interval(prediction: Prediction, level: float) -> tuple[float, float]:
    """Return the prediction interval at the requested level."""
    raise NotImplementedError("s08_flow.predict.interval — see Build_Manual_v3.md §S08")
