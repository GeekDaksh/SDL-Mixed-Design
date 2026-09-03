"""S11 PROPOSE — a requirement to a ranked candidate portfolio.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import ProposeInput, ProposeOutput


def run(inp: ProposeInput) -> ProposeOutput:
    """Execute stage S11."""
    raise NotImplementedError("s11_propose.stage.run")
