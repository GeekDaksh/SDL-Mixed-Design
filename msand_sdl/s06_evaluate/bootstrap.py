"""Paired resampling and P(win).

Stage: S06 EVALUATE
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def paired_resample(
    errors_a: np.ndarray, errors_b: np.ndarray, draws: int, seed: int
) -> np.ndarray:
    """Resample two error vectors in pairs, preserving which design each error came from."""
    raise NotImplementedError(
        "s06_evaluate.bootstrap.paired_resample — see docs/Build_Manual_v3.md §7.1"
    )


def probability_of_win(errors_a: np.ndarray, errors_b: np.ndarray, draws: int, seed: int) -> float:
    """Return the share of resamples in which the model beats its baseline."""
    raise NotImplementedError(
        "s06_evaluate.bootstrap.probability_of_win — see docs/Build_Manual_v3.md §7.1"
    )


def interval(values: np.ndarray, level: float) -> tuple[float, float]:
    """Return the bootstrap interval of a metric at the requested level."""
    raise NotImplementedError("s06_evaluate.bootstrap.interval — see docs/Build_Manual_v3.md §7.1")
