"""S07 STRENGTH — recipe to compressive strength with uncertainty.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import StrengthInput, StrengthOutput


def run(inp: StrengthInput) -> StrengthOutput:
    """Execute stage S07."""
    raise NotImplementedError("s07_strength.stage.run")
