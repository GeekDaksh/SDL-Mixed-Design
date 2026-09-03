"""The water-demand target variant.

Stage: S08 FLOW
Spec:  Build_Manual_v3.md §S08
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def target(frame: pd.DataFrame) -> pd.Series:
    """Return the water-demand target: water relative to the design's own reference."""
    raise NotImplementedError("s08_flow.delta_water.target — see Build_Manual_v3.md §S08")


def reference_water(frame: pd.DataFrame) -> pd.Series:
    """Return the reference water content each observation is expressed against."""
    raise NotImplementedError("s08_flow.delta_water.reference_water — see Build_Manual_v3.md §S08")


def to_workability(delta: pd.Series, reference: pd.Series) -> pd.Series:
    """Map a water-demand prediction back onto the reported workability scale."""
    raise NotImplementedError("s08_flow.delta_water.to_workability — see Build_Manual_v3.md §S08")
