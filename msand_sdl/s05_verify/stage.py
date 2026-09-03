"""S05 VERIFY — a per-clause verdict on a mix.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import VerifyInput, VerifyOutput


def run(inp: VerifyInput) -> VerifyOutput:
    """Execute stage S05."""
    raise NotImplementedError("s05_verify.stage.run")
