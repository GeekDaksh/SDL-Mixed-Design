"""The feature list.

Stage: S07 STRENGTH
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..recipe import Recipe

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd


def names() -> tuple[str, ...]:
    """Return the strength model's features, in the order the model expects them."""
    raise NotImplementedError("s07_strength.features.names — see docs/Build_Manual_v3.md §7.1")


def build(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the feature matrix from a prepared dataset."""
    raise NotImplementedError("s07_strength.features.build — see docs/Build_Manual_v3.md §7.1")


def from_recipe(recipe: Recipe, age_days: float) -> np.ndarray:
    """Build one feature row from a recipe at a test age."""
    raise NotImplementedError("s07_strength.features.from_recipe — see docs/Build_Manual_v3.md §7.1")
