"""The design-level grouping key.

Stage: S03 PREPARE
Spec:  Build_Manual_v3.md §S03
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def key(frame: pd.DataFrame) -> pd.Series:
    """Return the design-level group each row belongs to."""
    raise NotImplementedError("s03_prepare.groups.key — see Build_Manual_v3.md §S03")


def check_disjoint(frame: pd.DataFrame) -> None:
    """Raise if one design's rows carry more than one group key."""
    raise NotImplementedError("s03_prepare.groups.check_disjoint — see Build_Manual_v3.md §S03")
