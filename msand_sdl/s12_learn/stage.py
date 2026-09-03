"""S12 LEARN — a trial result to updated, versioned models.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import LearnInput, LearnOutput


def run(inp: LearnInput) -> LearnOutput:
    """Execute stage S12."""
    raise NotImplementedError("s12_learn.stage.run")
