"""The feature list.

Stage: S08 FLOW
Spec:  docs/Build_Manual_v3.md §7.3
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..recipe import Recipe

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd


def names() -> tuple[str, ...]:
    """Return the workability model's features, in the order the model expects them."""
    raise NotImplementedError("s08_flow.features.names — see docs/Build_Manual_v3.md §7.3")


def build(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the feature matrix from a prepared dataset."""
    raise NotImplementedError("s08_flow.features.build — see docs/Build_Manual_v3.md §7.3")


def from_recipe(recipe: Recipe) -> np.ndarray:
    """Build one feature row from a recipe."""
    raise NotImplementedError("s08_flow.features.from_recipe — see docs/Build_Manual_v3.md §7.3")
