"""S01 CODIFY — frozen IS PDFs to a clause-tagged rule registry.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import CodifyInput, CodifyOutput


def run(inp: CodifyInput) -> CodifyOutput:
    """Execute stage S01."""
    raise NotImplementedError("s01_codify.stage.run")
