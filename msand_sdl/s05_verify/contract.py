"""Contract for S05 VERIFY."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyInput:
    """Input contract for S05."""

    # TODO(s05): fields per docs/Build_Manual_v3.md §5


@dataclass(frozen=True)
class VerifyOutput:
    """Output contract for S05."""

    # TODO(s05): fields per docs/Build_Manual_v3.md §5
