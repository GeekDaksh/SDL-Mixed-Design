"""Source file, batch number and design id on every row.

Stage: S02 INGEST
Spec:  Build_Manual_v3.md §S02
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def stamp(frame: pd.DataFrame, source: str, source_file: Path) -> pd.DataFrame:
    """Attach source file, batch number and design id to every row."""
    raise NotImplementedError("s02_ingest.provenance.stamp — see Build_Manual_v3.md §S02")


def design_id(frame: pd.DataFrame, source: str) -> pd.Series:
    """Derive the design id each row belongs to."""
    raise NotImplementedError("s02_ingest.provenance.design_id — see Build_Manual_v3.md §S02")


def check_complete(frame: pd.DataFrame) -> None:
    """Raise if any row reaches the raw table without full provenance."""
    raise NotImplementedError("s02_ingest.provenance.check_complete — see Build_Manual_v3.md §S02")
