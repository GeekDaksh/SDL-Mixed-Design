"""The design-level grouping key.

Stage: S03 PREPARE
Spec:  docs/Build_Manual_v3.md §7.2
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def key(frame: pd.DataFrame) -> pd.Series:
    """Return the design-level group each row belongs to."""
    raise NotImplementedError("s03_prepare.groups.key — see docs/Build_Manual_v3.md §7.2")


def check_disjoint(frame: pd.DataFrame) -> None:
    """Raise if one design's rows carry more than one group key."""
    raise NotImplementedError(
        "s03_prepare.groups.check_disjoint — see docs/Build_Manual_v3.md §7.2"
    )
