"""S02 — a source failing a physics check does not enter the dataset."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S02 task")
def test_source_failing_physics_check_is_not_ingested() -> None:
    """A source whose rows violate concrete physics is rejected whole, not row-patched. docs/Build_Manual_v3.md §9."""
    raise NotImplementedError
