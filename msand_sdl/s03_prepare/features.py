"""Derived ratio features.

Stage: S03 PREPARE
Spec:  Build_Manual_v3.md §S03
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def derive(frame: pd.DataFrame) -> pd.DataFrame:
    """Add every derived ratio feature to the frame."""
    raise NotImplementedError("s03_prepare.features.derive — see Build_Manual_v3.md §S03")


def names() -> tuple[str, ...]:
    """Return the derived feature names."""
    raise NotImplementedError("s03_prepare.features.names — see Build_Manual_v3.md §S03")
