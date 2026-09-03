"""S03 PREPARE — raw table to strength and workability datasets.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import PrepareInput, PrepareOutput


def run(inp: PrepareInput) -> PrepareOutput:
    """Execute stage S03."""
    raise NotImplementedError("s03_prepare.stage.run")
