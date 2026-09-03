"""Contract for S08 FLOW."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlowInput:
    """Input contract for S08."""

    # TODO(s08): fields per Build_Manual_v3.md §S08


@dataclass(frozen=True)
class FlowOutput:
    """Output contract for S08."""

    # TODO(s08): fields per Build_Manual_v3.md §S08
