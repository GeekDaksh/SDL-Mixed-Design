"""The four cleaning rules.

Stage: S03 PREPARE
Spec:  docs/Build_Manual_v3.md §7.2
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def apply(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the four cleaning rules in order, dropping rather than imputing."""
    raise NotImplementedError("s03_prepare.rules.apply — see docs/Build_Manual_v3.md §7.2")


def names() -> tuple[str, ...]:
    """Return the four cleaning rules by name, in the order they apply."""
    raise NotImplementedError("s03_prepare.rules.names — see docs/Build_Manual_v3.md §7.2")
