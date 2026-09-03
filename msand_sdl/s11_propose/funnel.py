"""Record how many candidates survive each filter.

Stage: S11 PROPOSE
Spec:  Build_Manual_v3.md §S11
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FunnelRecord:
    """How many candidates entered and left one filter, and why the rest went."""

    # TODO(s11): fields per Build_Manual_v3.md §S11


def record(stage_name: str, entered: int, survived: int) -> FunnelRecord:
    """Record one filter's effect on the candidate set."""
    raise NotImplementedError("s11_propose.funnel.record — see Build_Manual_v3.md §S11")


def write(records: tuple[FunnelRecord, ...], path: Path) -> Path:
    """Write the funnel beside the proposal it explains."""
    raise NotImplementedError("s11_propose.funnel.write — see Build_Manual_v3.md §S11")
