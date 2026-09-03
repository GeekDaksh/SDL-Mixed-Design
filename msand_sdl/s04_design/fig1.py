"""The Abrams fit and its validity band.

Stage: S04 DESIGN
Spec:  docs/Build_Manual_v3.md §4
Status: scaffold — not implemented.
"""

from __future__ import annotations


def water_cementitious_ratio(target_mean_strength: float, cement_grade: str) -> float:
    """Return the w/cm the IS 10262 Fig 1 relation gives for this target mean strength."""
    raise NotImplementedError(
        "s04_design.fig1.water_cementitious_ratio — see docs/Build_Manual_v3.md §4"
    )


def validity_band(cement_grade: str) -> tuple[float, float]:
    """Return the strength band over which the Fig 1 relation is defined."""
    raise NotImplementedError("s04_design.fig1.validity_band — see docs/Build_Manual_v3.md §4")


def check_within_band(target_mean_strength: float, cement_grade: str) -> None:
    """Raise if a target mean strength falls outside the band Fig 1 covers."""
    raise NotImplementedError("s04_design.fig1.check_within_band — see docs/Build_Manual_v3.md §4")
