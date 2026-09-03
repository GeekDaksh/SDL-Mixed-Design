"""Propagate one change through the whole mix-design chain.

Stage: S09 PROPAGATE
Spec:  Build_Manual_v3.md §S09
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def apply_change(recipe: Recipe, variable: str, value: float) -> Recipe:
    """Change one variable and recompute every quantity that depends on it."""
    raise NotImplementedError("s09_propagate.recompute.apply_change — see Build_Manual_v3.md §S09")


def dependents(variable: str) -> tuple[str, ...]:
    """Return every quantity downstream of this variable in the design chain."""
    raise NotImplementedError("s09_propagate.recompute.dependents — see Build_Manual_v3.md §S09")


def order() -> tuple[str, ...]:
    """Return the recomputation order of the design chain."""
    raise NotImplementedError("s09_propagate.recompute.order — see Build_Manual_v3.md §S09")
