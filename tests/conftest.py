"""Shared pytest fixtures.

Stage: tests
Spec:  Build_Manual_v3.md
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """The repository root."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def rules_dir(repo_root: Path) -> Path:
    """The directory the codified rule files live in."""
    return repo_root / "msand_sdl" / "s01_codify" / "rules"
