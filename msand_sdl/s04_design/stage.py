"""S04 DESIGN — deterministic IS 10262 mix proportioning.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import DesignInput, DesignOutput


def run(inp: DesignInput) -> DesignOutput:
    """Execute stage S04."""
    raise NotImplementedError("s04_design.stage.run")
