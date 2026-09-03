"""Random split versus grouped split, side by side.

Stage: S06 EVALUATE
Spec:  Build_Manual_v3.md §S06
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def random_split_score(frame: pd.DataFrame) -> dict[str, float]:
    """Score the model under a naive random split. Reported only for comparison."""
    raise NotImplementedError(
        "s06_evaluate.leakage.random_split_score — see Build_Manual_v3.md §S06"
    )


def grouped_split_score(frame: pd.DataFrame) -> dict[str, float]:
    """Score the model under the design-level grouped split. This is the honest number."""
    raise NotImplementedError(
        "s06_evaluate.leakage.grouped_split_score — see Build_Manual_v3.md §S06"
    )


def gap(random: dict[str, float], grouped: dict[str, float]) -> dict[str, float]:
    """Return the difference between the two, metric by metric."""
    raise NotImplementedError("s06_evaluate.leakage.gap — see Build_Manual_v3.md §S06")
