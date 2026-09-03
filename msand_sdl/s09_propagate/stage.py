"""S09 PROPAGATE — one changed variable to a fully recomputed recipe.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import PropagateInput, PropagateOutput


def run(inp: PropagateInput) -> PropagateOutput:
    """Execute stage S09."""
    raise NotImplementedError("s09_propagate.stage.run")
