"""Interval coverage against nominal.

Stage: S06 EVALUATE
Spec:  docs/Build_Manual_v3.md §7.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def empirical_coverage(
    actual: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> float:
    """Return the share of held-out observations that fall inside their predicted interval."""
    raise NotImplementedError(
        "s06_evaluate.calibration.empirical_coverage — see docs/Build_Manual_v3.md §7.1"
    )


def coverage_curve(
    actual: np.ndarray, mean: np.ndarray, sd: np.ndarray
) -> dict[float, float]:
    """Return empirical coverage against nominal coverage across levels."""
    raise NotImplementedError(
        "s06_evaluate.calibration.coverage_curve — see docs/Build_Manual_v3.md §7.1"
    )


def is_calibrated(curve: dict[float, float], tolerance: float) -> bool:
    """Whether empirical coverage tracks nominal within the stated tolerance."""
    raise NotImplementedError(
        "s06_evaluate.calibration.is_calibrated — see docs/Build_Manual_v3.md §7.1"
    )
