"""Leave-one-design-out splitting.

Stage: S06 EVALUATE
Spec:  Build_Manual_v3.md §S06
Status: scaffold — not implemented.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def splits(frame: pd.DataFrame) -> Iterator[tuple[pd.Index, pd.Index]]:
    """Yield train and test indices, holding out one whole design at a time."""
    raise NotImplementedError("s06_evaluate.protocol.splits — see Build_Manual_v3.md §S06")


def check_disjoint(train: pd.Index, test: pd.Index, frame: pd.DataFrame) -> None:
    """Raise if any design appears on both sides of a split."""
    raise NotImplementedError("s06_evaluate.protocol.check_disjoint — see Build_Manual_v3.md §S06")
