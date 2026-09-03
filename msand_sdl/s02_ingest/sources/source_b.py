"""Loader for SBM Site B.

Stage: S02 INGEST
Spec:  docs/Build_Manual_v3.md §9
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def load(path: Path) -> pd.DataFrame:
    """Read SBM Site B as it is, without renaming or reshaping anything."""
    raise NotImplementedError(
        "s02_ingest.sources.source_b.load — see docs/Build_Manual_v3.md §9"
    )


def sheets(path: Path) -> tuple[str, ...]:
    """Return the sheets of this workbook that carry mix data."""
    raise NotImplementedError(
        "s02_ingest.sources.source_b.sheets — see docs/Build_Manual_v3.md §9"
    )
