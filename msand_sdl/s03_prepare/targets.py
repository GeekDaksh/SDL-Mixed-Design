"""Strength long form and workability form.

Stage: S03 PREPARE
Spec:  Build_Manual_v3.md §S03
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def strength_long(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the strength dataset in long form, one row per specimen age."""
    raise NotImplementedError("s03_prepare.targets.strength_long — see Build_Manual_v3.md §S03")


def workability(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the workability dataset."""
    raise NotImplementedError("s03_prepare.targets.workability — see Build_Manual_v3.md §S03")
