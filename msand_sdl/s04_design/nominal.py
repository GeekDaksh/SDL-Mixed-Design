"""IS 456 Table 9 proportions; never a design mix.

Stage: S04 DESIGN
Spec:  docs/Build_Manual_v3.md §1.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Requirement
from ..recipe import Recipe


def proportions(requirement: Requirement) -> Recipe:
    """Return the tabulated nominal-mix proportions for this requirement."""
    raise NotImplementedError("s04_design.nominal.proportions — see docs/Build_Manual_v3.md §1.1")


def is_permissible(requirement: Requirement) -> bool:
    """Whether IS 456 permits a nominal mix here at all."""
    raise NotImplementedError("s04_design.nominal.is_permissible — see docs/Build_Manual_v3.md §1.1")
