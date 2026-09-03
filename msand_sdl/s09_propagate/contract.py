"""Contract for S09 PROPAGATE."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PropagateInput:
    """Input contract for S09."""

    # TODO(s09): fields per docs/Build_Manual_v3.md §7.4


@dataclass(frozen=True)
class PropagateOutput:
    """Output contract for S09."""

    # TODO(s09): fields per docs/Build_Manual_v3.md §7.4
