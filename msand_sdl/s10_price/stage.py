"""S10 PRICE — recipe and rates to cost and embodied carbon.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import PriceInput, PriceOutput


def run(inp: PriceInput) -> PriceOutput:
    """Execute stage S10."""
    raise NotImplementedError("s10_price.stage.run")
