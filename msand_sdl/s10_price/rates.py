"""Load the rate table; arithmetic only, no model.

Stage: S10 PRICE
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path


def load(path: Path) -> dict[str, dict[str, float]]:
    """Load the rate table from config."""
    raise NotImplementedError("s10_price.rates.load — see docs/Build_Manual_v3.md §10")


def validate(rates: dict[str, dict[str, float]], constituents: tuple[str, ...]) -> None:
    """Raise if any constituent of a recipe has no rate; a missing rate is never assumed."""
    raise NotImplementedError("s10_price.rates.validate — see docs/Build_Manual_v3.md §10")
