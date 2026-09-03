"""Contract for S12 LEARN."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LearnInput:
    """Input contract for S12."""

    # TODO(s12): fields per Build_Manual_v3.md §S12


@dataclass(frozen=True)
class LearnOutput:
    """Output contract for S12."""

    # TODO(s12): fields per Build_Manual_v3.md §S12
