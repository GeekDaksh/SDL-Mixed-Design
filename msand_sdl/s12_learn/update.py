"""Refit, re-evaluate, bump the version.

Stage: S12 LEARN
Spec:  Build_Manual_v3.md §S12
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def refit(ledger: pd.DataFrame) -> dict[str, Path]:
    """Refit every model on the dataset extended by the new trials."""
    raise NotImplementedError("s12_learn.update.refit — see Build_Manual_v3.md §S12")


def re_evaluate(models: dict[str, Path]) -> dict[str, dict[str, float]]:
    """Re-run the evaluation protocol on the refitted models, baselines included."""
    raise NotImplementedError("s12_learn.update.re_evaluate — see Build_Manual_v3.md §S12")


def accept(before: dict[str, dict[str, float]], after: dict[str, dict[str, float]]) -> bool:
    """Whether the refitted models replace the incumbent."""
    raise NotImplementedError("s12_learn.update.accept — see Build_Manual_v3.md §S12")
