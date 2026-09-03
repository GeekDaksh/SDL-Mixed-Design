"""Target transform.

Stage: S07 STRENGTH
Spec:  Build_Manual_v3.md §S07
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def forward(target: np.ndarray) -> np.ndarray:
    """Transform the target onto the scale the model is fitted on."""
    raise NotImplementedError("s07_strength.transform.forward — see Build_Manual_v3.md §S07")


def inverse(values: np.ndarray) -> np.ndarray:
    """Map values back onto the reported scale."""
    raise NotImplementedError("s07_strength.transform.inverse — see Build_Manual_v3.md §S07")


def inverse_moments(mean: np.ndarray, sd: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map a posterior mean and standard deviation back, without pretending the map is linear."""
    raise NotImplementedError(
        "s07_strength.transform.inverse_moments — see Build_Manual_v3.md §S07"
    )
