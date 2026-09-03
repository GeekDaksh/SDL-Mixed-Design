"""Contract for S01 CODIFY."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodifyInput:
    """Input contract for S01."""

    # TODO(s01): fields per Build_Manual_v3.md §S01


@dataclass(frozen=True)
class CodifyOutput:
    """Output contract for S01."""

    # TODO(s01): fields per Build_Manual_v3.md §S01
