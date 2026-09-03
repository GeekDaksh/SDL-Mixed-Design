"""S04 — routing sends a grade to exactly one IS 10262 section."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S04 task")
def test_m65_cannot_reach_section2() -> None:
    """M65 routes to the cl 6 chain; the Fig 1 path must be structurally unreachable. docs/Build_Manual_v3.md §1."""
    raise NotImplementedError
