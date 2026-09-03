"""The Gaussian process.

Stage: S08 FLOW
Spec:  Build_Manual_v3.md §S08
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np


def fit(features: np.ndarray, target: np.ndarray) -> Any:
    """Fit the Gaussian process to a prepared workability dataset."""
    raise NotImplementedError("s08_flow.gp.fit — see Build_Manual_v3.md §S08")


def posterior(model: Any, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return posterior mean and standard deviation on the model's own scale."""
    raise NotImplementedError("s08_flow.gp.posterior — see Build_Manual_v3.md §S08")


def save(model: Any, path: Path) -> Path:
    """Persist a fitted model with the dataset hash it was fitted on."""
    raise NotImplementedError("s08_flow.gp.save — see Build_Manual_v3.md §S08")


def load(path: Path) -> Any:
    """Load a persisted model."""
    raise NotImplementedError("s08_flow.gp.load — see Build_Manual_v3.md §S08")
