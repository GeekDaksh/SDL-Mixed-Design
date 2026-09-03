"""S06 EVALUATE — LODO metrics and calibration for a model.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import EvaluateInput, EvaluateOutput


def run(inp: EvaluateInput) -> EvaluateOutput:
    """Execute stage S06."""
    raise NotImplementedError("s06_evaluate.stage.run")
