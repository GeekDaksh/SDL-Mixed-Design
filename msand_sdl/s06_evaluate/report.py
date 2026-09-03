"""Metric tables.

Stage: S06 EVALUATE
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def metric_table(results: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Assemble model and baseline metrics into one table."""
    raise NotImplementedError("s06_evaluate.report.metric_table — see docs/Build_Manual_v3.md §7.1")


def write(table: pd.DataFrame, path: Path) -> Path:
    """Write a metric table to the report directory."""
    raise NotImplementedError("s06_evaluate.report.write — see docs/Build_Manual_v3.md §7.1")
