"""The classical baseline the model must beat.

Stage: S08 FLOW
Spec:  docs/Build_Manual_v3.md §7.3
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np


def fit(water_content: np.ndarray, workability: np.ndarray) -> Any:
    """Fit Lyse's rule to the same training rows the model saw."""
    raise NotImplementedError("s08_flow.lyse.fit — see docs/Build_Manual_v3.md §7.3")


def predict(model: Any, water_content: np.ndarray) -> np.ndarray:
    """Predict workability from the fitted classical relation."""
    raise NotImplementedError("s08_flow.lyse.predict — see docs/Build_Manual_v3.md §7.3")
