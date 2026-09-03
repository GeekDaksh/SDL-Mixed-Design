"""Contract for S06 EVALUATE."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluateInput:
    """Input contract for S06."""

    # TODO(s06): fields per Build_Manual_v3.md §S06


@dataclass(frozen=True)
class EvaluateOutput:
    """Output contract for S06."""

    # TODO(s06): fields per Build_Manual_v3.md §S06
