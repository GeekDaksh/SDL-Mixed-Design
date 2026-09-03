"""One row per physical trial.

Stage: S12 LEARN
Spec:  Build_Manual_v3.md §S12
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..recipe import Recipe

if TYPE_CHECKING:
    import pandas as pd


def append(ledger: pd.DataFrame, recipe: Recipe, result: dict[str, float]) -> pd.DataFrame:
    """Add one physical trial and its measured result to the ledger."""
    raise NotImplementedError("s12_learn.ledger.append — see Build_Manual_v3.md §S12")


def load(path: Path) -> pd.DataFrame:
    """Load the trial ledger."""
    raise NotImplementedError("s12_learn.ledger.load — see Build_Manual_v3.md §S12")


def write(ledger: pd.DataFrame, path: Path) -> Path:
    """Write the trial ledger. Append only; a trial is never edited out."""
    raise NotImplementedError("s12_learn.ledger.write — see Build_Manual_v3.md §S12")
