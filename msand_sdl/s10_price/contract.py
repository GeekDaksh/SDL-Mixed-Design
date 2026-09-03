"""Contract for S10 PRICE."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceInput:
    """Input contract for S10."""

    # TODO(s10): fields per docs/Build_Manual_v3.md §10


@dataclass(frozen=True)
class PriceOutput:
    """Output contract for S10."""

    # TODO(s10): fields per docs/Build_Manual_v3.md §10
