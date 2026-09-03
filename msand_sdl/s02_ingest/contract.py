"""Contract for S02 INGEST."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IngestInput:
    """Input contract for S02."""

    # TODO(s02): fields per Build_Manual_v3.md §S02


@dataclass(frozen=True)
class IngestOutput:
    """Output contract for S02."""

    # TODO(s02): fields per Build_Manual_v3.md §S02
