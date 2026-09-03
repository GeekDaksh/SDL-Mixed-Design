"""Rupees per cubic metre.

Stage: S10 PRICE
Spec:  Build_Manual_v3.md §S10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def cost_per_cubic_metre(recipe: Recipe, rates: dict[str, float]) -> float:
    """Return the material cost of one cubic metre of this mix."""
    raise NotImplementedError(
        "s10_price.cost.cost_per_cubic_metre — see Build_Manual_v3.md §S10"
    )


def breakdown(recipe: Recipe, rates: dict[str, float]) -> dict[str, float]:
    """Return the cost contribution of every constituent."""
    raise NotImplementedError("s10_price.cost.breakdown — see Build_Manual_v3.md §S10")
