"""S08 FLOW — recipe to workability with uncertainty.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import FlowInput, FlowOutput


def run(inp: FlowInput) -> FlowOutput:
    """Execute stage S08."""
    raise NotImplementedError("s08_flow.stage.run")
