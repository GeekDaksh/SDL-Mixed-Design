"""Map each source onto the schema, never the reverse.

Stage: S02 INGEST
Spec:  Build_Manual_v3.md §S02
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def harmonise(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    """Map one source's frame onto the canonical schema."""
    raise NotImplementedError("s02_ingest.harmonise.harmonise — see Build_Manual_v3.md §S02")


def column_map(source: str) -> dict[str, str]:
    """Return the source column to canonical column mapping for one source."""
    raise NotImplementedError("s02_ingest.harmonise.column_map — see Build_Manual_v3.md §S02")


def concatenate(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Stack every harmonised source into the single raw table."""
    raise NotImplementedError("s02_ingest.harmonise.concatenate — see Build_Manual_v3.md §S02")
