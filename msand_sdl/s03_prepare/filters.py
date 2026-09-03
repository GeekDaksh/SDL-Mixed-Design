"""Physically impossible, mortar, unusual-but-possible.

Stage: S03 PREPARE
Spec:  Build_Manual_v3.md §S03
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def physically_impossible(frame: pd.DataFrame) -> pd.Series:
    """Flag rows that cannot describe a real mix."""
    raise NotImplementedError(
        "s03_prepare.filters.physically_impossible — see Build_Manual_v3.md §S03"
    )


def mortar(frame: pd.DataFrame) -> pd.Series:
    """Flag rows that describe mortar rather than concrete."""
    raise NotImplementedError("s03_prepare.filters.mortar — see Build_Manual_v3.md §S03")


def unusual_but_possible(frame: pd.DataFrame) -> pd.Series:
    """Flag rows that are unusual but physically possible; kept, marked, never dropped silently."""
    raise NotImplementedError(
        "s03_prepare.filters.unusual_but_possible — see Build_Manual_v3.md §S03"
    )
