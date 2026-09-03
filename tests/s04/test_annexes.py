"""S04 — the six IS 10262 worked annexes as unit tests."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S04 task")
def test_annex_d_water_cementitious_ratio_from_table_8() -> None:
    """Annex D (M70): w/cm must come from Table 8, not Fig 1. docs/Build_Manual_v3.md §8.1."""
    raise NotImplementedError
