"""S06 — leave-one-design-out keeps designs whole."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S06 task")
def test_no_design_appears_in_both_train_and_test() -> None:
    """Every split holds out one entire design; no design id crosses the split.

    Spec: docs/Build_Manual_v3.md §7.1
    """
    raise NotImplementedError
