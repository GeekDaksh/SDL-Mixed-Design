"""Rank survivors on the cost-carbon front.

Stage: S11 PROPOSE
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def front(candidates: tuple[Recipe, ...], cost: dict[str, float], carbon: dict[str, float]) -> tuple[Recipe, ...]:
    """Return the non-dominated candidates on the cost and carbon objectives."""
    raise NotImplementedError("s11_propose.portfolio.front — see docs/Build_Manual_v3.md §10")


def rank(candidates: tuple[Recipe, ...]) -> tuple[Recipe, ...]:
    """Order the surviving candidates for presentation."""
    raise NotImplementedError("s11_propose.portfolio.rank — see docs/Build_Manual_v3.md §10")


def diversify(candidates: tuple[Recipe, ...], count: int) -> tuple[Recipe, ...]:
    """Select a spread of candidates rather than a cluster around one point."""
    raise NotImplementedError("s11_propose.portfolio.diversify — see docs/Build_Manual_v3.md §10")
