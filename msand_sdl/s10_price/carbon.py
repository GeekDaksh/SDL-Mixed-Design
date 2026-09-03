"""kgCO2e per cubic metre.

Stage: S10 PRICE
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def carbon_per_cubic_metre(recipe: Recipe, factors: dict[str, float]) -> float:
    """Return the embodied carbon of one cubic metre of this mix."""
    raise NotImplementedError(
        "s10_price.carbon.carbon_per_cubic_metre — see docs/Build_Manual_v3.md §10"
    )


def breakdown(recipe: Recipe, factors: dict[str, float]) -> dict[str, float]:
    """Return the carbon contribution of every constituent."""
    raise NotImplementedError("s10_price.carbon.breakdown — see docs/Build_Manual_v3.md §10")
