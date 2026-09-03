"""Contract for S11 PROPOSE."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProposeInput:
    """Input contract for S11."""

    # TODO(s11): fields per Build_Manual_v3.md §S11


@dataclass(frozen=True)
class ProposeOutput:
    """Output contract for S11."""

    # TODO(s11): fields per Build_Manual_v3.md §S11
