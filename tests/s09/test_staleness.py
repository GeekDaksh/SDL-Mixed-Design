"""S09 — a change propagates through the whole chain."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S09 task")
def test_no_cached_value_survives_an_input_change() -> None:
    """Changing one variable must move every quantity downstream of it.

    Spec: docs/Build_Manual_v3.md §7.4
    """
    raise NotImplementedError
