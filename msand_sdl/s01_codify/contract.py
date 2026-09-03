"""Contract for S01 CODIFY.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0
Status: implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .registry import Registry


@dataclass(frozen=True)
class CodifyInput:
    """Input contract for S01."""

    repo_root: Path
    rules_dir: Path
    standards_dir: Path
    manifest: Path


@dataclass(frozen=True)
class CodifyOutput:
    """Output contract for S01."""

    registry: Registry
    manifest: Path
    status_counts: dict[str, int]
    unresolved: tuple[str, ...]
