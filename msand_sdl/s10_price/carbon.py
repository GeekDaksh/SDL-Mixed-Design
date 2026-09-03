"""kgCO2e per cubic metre.

Stage: S10 PRICE
Spec:  Build_Manual_v3.md §S10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def carbon_per_cubic_metre(recipe: Recipe, factors: dict[str, float]) -> float:
    """Return the embodied carbon of one cubic metre of this mix."""
    raise NotImplementedError(
        "s10_price.carbon.carbon_per_cubic_metre — see Build_Manual_v3.md §S10"
    )


def breakdown(recipe: Recipe, factors: dict[str, float]) -> dict[str, float]:
    """Return the carbon contribution of every constituent."""
    raise NotImplementedError("s10_price.carbon.breakdown — see Build_Manual_v3.md §S10")
