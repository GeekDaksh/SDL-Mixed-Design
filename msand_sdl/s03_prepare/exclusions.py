"""Every dropped row with its reason.

Stage: S03 PREPARE
Spec:  docs/Build_Manual_v3.md §7.2
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def record(frame: pd.DataFrame, reason: str) -> pd.DataFrame:
    """Record the rows removed by one rule, with the reason they were removed."""
    raise NotImplementedError("s03_prepare.exclusions.record — see docs/Build_Manual_v3.md §7.2")


def write(exclusions: pd.DataFrame, path: Path) -> Path:
    """Write the exclusion ledger beside the dataset it belongs to."""
    raise NotImplementedError("s03_prepare.exclusions.write — see docs/Build_Manual_v3.md §7.2")


def reconcile(raw: pd.DataFrame, kept: pd.DataFrame, exclusions: pd.DataFrame) -> None:
    """Raise unless every raw row is either kept or accounted for by an exclusion."""
    raise NotImplementedError("s03_prepare.exclusions.reconcile — see docs/Build_Manual_v3.md §7.2")
