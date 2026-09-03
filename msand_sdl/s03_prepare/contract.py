"""Contract for S03 PREPARE."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrepareInput:
    """Input contract for S03."""

    # TODO(s03): fields per Build_Manual_v3.md §S03


@dataclass(frozen=True)
class PrepareOutput:
    """Output contract for S03."""

    # TODO(s03): fields per Build_Manual_v3.md §S03
