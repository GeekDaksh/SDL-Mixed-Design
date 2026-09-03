"""The classical baseline the model must beat.

Stage: S07 STRENGTH
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np


def fit(water_cementitious_ratio: np.ndarray, strength: np.ndarray) -> Any:
    """Fit Abrams' law to the same training rows the model saw."""
    raise NotImplementedError("s07_strength.abrams.fit — see docs/Build_Manual_v3.md §7.1")


def predict(model: Any, water_cementitious_ratio: np.ndarray) -> np.ndarray:
    """Predict strength from the fitted classical relation."""
    raise NotImplementedError("s07_strength.abrams.predict — see docs/Build_Manual_v3.md §7.1")
