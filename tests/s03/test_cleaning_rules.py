"""S03 — a missing value is never imputed."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S03 task")
def test_missing_value_is_dropped_with_a_reason_never_imputed() -> None:
    """A row with a missing required value leaves the dataset and appears in the exclusion ledger. docs/Build_Manual_v3.md §7.2."""
    raise NotImplementedError
