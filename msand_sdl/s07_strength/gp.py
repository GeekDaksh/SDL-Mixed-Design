"""The Gaussian process.

Stage: S07 STRENGTH
Spec:  Build_Manual_v3.md §S07
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np


def fit(features: np.ndarray, target: np.ndarray) -> Any:
    """Fit the Gaussian process to a prepared strength dataset."""
    raise NotImplementedError("s07_strength.gp.fit — see Build_Manual_v3.md §S07")


def posterior(model: Any, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return posterior mean and standard deviation on the model's own scale."""
    raise NotImplementedError("s07_strength.gp.posterior — see Build_Manual_v3.md §S07")


def save(model: Any, path: Path) -> Path:
    """Persist a fitted model with the dataset hash it was fitted on."""
    raise NotImplementedError("s07_strength.gp.save — see Build_Manual_v3.md §S07")


def load(path: Path) -> Any:
    """Load a persisted model."""
    raise NotImplementedError("s07_strength.gp.load — see Build_Manual_v3.md §S07")
