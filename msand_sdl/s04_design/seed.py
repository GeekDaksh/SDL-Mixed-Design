"""The single valid starting mix handed to S11.

Stage: S04 DESIGN
Spec:  Build_Manual_v3.md §S04
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Requirement
from ..recipe import Recipe


def seed(requirement: Requirement) -> Recipe:
    """Return the one deterministic IS mix the search starts from."""
    raise NotImplementedError("s04_design.seed.seed — see Build_Manual_v3.md §S04")
