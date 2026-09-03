"""The IS 10262 cl 5 chain.

Stage: S04 DESIGN
Spec:  docs/Build_Manual_v3.md §3.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Requirement
from ..recipe import Recipe
from . import fig1


def design(requirement: Requirement) -> Recipe:
    """Run the cl 5 chain end to end for an ordinary-domain requirement."""
    raise NotImplementedError("s04_design.section2.design — see docs/Build_Manual_v3.md §3.1")


def water_cementitious_ratio(requirement: Requirement) -> float:
    """Select the w/cm for the cl 5 route; the Fig 1 relation applies on this route only."""
    raise NotImplementedError(
        "s04_design.section2.water_cementitious_ratio — see docs/Build_Manual_v3.md §3.1"
    )


def water_content(requirement: Requirement) -> float:
    """Select the water content for the cl 5 route and correct it for the requested workability."""
    raise NotImplementedError("s04_design.section2.water_content — see docs/Build_Manual_v3.md §3.1")


def coarse_aggregate_fraction(requirement: Requirement) -> float:
    """Select the coarse aggregate volume fraction for the cl 5 route."""
    raise NotImplementedError(
        "s04_design.section2.coarse_aggregate_fraction — see docs/Build_Manual_v3.md §3.1"
    )


def fig1_band(requirement: Requirement) -> tuple[float, float]:
    """Return the validity band of the Fig 1 relation for this requirement."""
    raise NotImplementedError("s04_design.section2.fig1_band — see docs/Build_Manual_v3.md §3.1")
