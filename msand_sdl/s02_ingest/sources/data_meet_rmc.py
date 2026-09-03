"""Loader for Data Meet RMC.

Stage: S02 INGEST
Spec:  Build_Manual_v3.md §S02
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def load(path: Path) -> pd.DataFrame:
    """Read Data Meet RMC as it is, without renaming or reshaping anything."""
    raise NotImplementedError(
        "s02_ingest.sources.data_meet_rmc.load — see Build_Manual_v3.md §S02"
    )


def sheets(path: Path) -> tuple[str, ...]:
    """Return the sheets of this workbook that carry mix data."""
    raise NotImplementedError(
        "s02_ingest.sources.data_meet_rmc.sheets — see Build_Manual_v3.md §S02"
    )
