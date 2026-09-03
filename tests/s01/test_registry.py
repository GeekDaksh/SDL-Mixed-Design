"""S01 — the registry refuses an unverified rule as a hard constraint."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S01 task")
def test_unverified_rule_cannot_be_a_hard_constraint() -> None:
    """An UNVERIFIED rule must raise when requested as a hard constraint, not be applied. docs/Build_Manual_v3.md §0."""
    raise NotImplementedError
