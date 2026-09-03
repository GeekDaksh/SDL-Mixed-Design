"""S05 — every check can fail."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S05 task")
def test_every_check_fails_on_its_counter_example() -> None:
    """Each checks/*.py must return FAIL for a constructed violating mix. docs/Build_Manual_v3.md §5."""
    raise NotImplementedError
