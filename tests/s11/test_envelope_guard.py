"""S11 — proposals stay inside the training envelope."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="scaffold — implemented in the S11 task")
def test_proposal_outside_training_envelope_is_rejected() -> None:
    """A candidate the models would have to extrapolate to score never reaches the portfolio. docs/Build_Manual_v3.md §10."""
    raise NotImplementedError
