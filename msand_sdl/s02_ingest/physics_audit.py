"""Reject a source that fails a concrete-physics check.

Stage: S02 INGEST
Spec:  docs/Build_Manual_v3.md §9
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class AuditReport:
    """The outcome of auditing one source against concrete physics."""

    # TODO(s02): fields per docs/Build_Manual_v3.md §9


def audit(frame: pd.DataFrame, source: str) -> AuditReport:
    """Audit one harmonised source against every physics check."""
    raise NotImplementedError("s02_ingest.physics_audit.audit — see docs/Build_Manual_v3.md §9")


def admits(report: AuditReport) -> bool:
    """Whether a source may enter the raw table."""
    raise NotImplementedError("s02_ingest.physics_audit.admits — see docs/Build_Manual_v3.md §9")
