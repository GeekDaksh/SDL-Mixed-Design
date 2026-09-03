"""Contract for S07 STRENGTH."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrengthInput:
    """Input contract for S07."""

    # TODO(s07): fields per Build_Manual_v3.md §S07


@dataclass(frozen=True)
class StrengthOutput:
    """Output contract for S07."""

    # TODO(s07): fields per Build_Manual_v3.md §S07
