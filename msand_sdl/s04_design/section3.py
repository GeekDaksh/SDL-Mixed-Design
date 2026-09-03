"""The IS 10262 cl 6 chain.

Stage: S04 DESIGN
Spec:  Build_Manual_v3.md §S04
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Requirement
from ..recipe import Recipe


def design(requirement: Requirement) -> Recipe:
    """Run the cl 6 chain end to end for a high-strength requirement.

    This module does not import fig1: on the cl 6 route the w/cm is tabulated, and the Fig 1
    relation must be structurally unreachable.
    """
    raise NotImplementedError("s04_design.section3.design — see Build_Manual_v3.md §S04")


def water_cementitious_ratio(requirement: Requirement) -> float:
    """Read the w/cm from the cl 6 table. Never from Fig 1."""
    raise NotImplementedError(
        "s04_design.section3.water_cementitious_ratio — see Build_Manual_v3.md §S04"
    )


def water_content(requirement: Requirement) -> float:
    """Select the water content for the cl 6 route."""
    raise NotImplementedError("s04_design.section3.water_content — see Build_Manual_v3.md §S04")


def cementitious_content(requirement: Requirement) -> float:
    """Select the cementitious content for the cl 6 route."""
    raise NotImplementedError(
        "s04_design.section3.cementitious_content — see Build_Manual_v3.md §S04"
    )
