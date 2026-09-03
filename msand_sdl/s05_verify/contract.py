"""Contract for S05 VERIFY."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyInput:
    """Input contract for S05."""

    # TODO(s05): fields per Build_Manual_v3.md §S05


@dataclass(frozen=True)
class VerifyOutput:
    """Output contract for S05."""

    # TODO(s05): fields per Build_Manual_v3.md §S05
