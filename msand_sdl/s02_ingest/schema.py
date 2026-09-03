"""The canonical 104-column template.

Stage: S02 INGEST
Spec:  Build_Manual_v3.md §S02
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def columns() -> tuple[str, ...]:
    """Return the canonical column names, in order."""
    raise NotImplementedError("s02_ingest.schema.columns — see Build_Manual_v3.md §S02")


def dtypes() -> dict[str, str]:
    """Return the declared dtype of every canonical column."""
    raise NotImplementedError("s02_ingest.schema.dtypes — see Build_Manual_v3.md §S02")


def empty_frame() -> pd.DataFrame:
    """Return an empty frame carrying the canonical columns and dtypes."""
    raise NotImplementedError("s02_ingest.schema.empty_frame — see Build_Manual_v3.md §S02")


def validate(frame: pd.DataFrame) -> None:
    """Raise if a frame does not conform to the canonical template."""
    raise NotImplementedError("s02_ingest.schema.validate — see Build_Manual_v3.md §S02")
