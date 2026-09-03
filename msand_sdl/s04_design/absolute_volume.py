"""Volume closure.

Stage: S04 DESIGN
Spec:  docs/Build_Manual_v3.md §3.1
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def close(recipe: Recipe, specific_gravities: dict[str, float]) -> Recipe:
    """Solve the aggregate masses that close the mix to one cubic metre."""
    raise NotImplementedError("s04_design.absolute_volume.close — see docs/Build_Manual_v3.md §3.1")


def total_volume(recipe: Recipe, specific_gravities: dict[str, float]) -> float:
    """Return the absolute volume the recipe currently occupies."""
    raise NotImplementedError(
        "s04_design.absolute_volume.total_volume — see docs/Build_Manual_v3.md §3.1"
    )


def residual(recipe: Recipe, specific_gravities: dict[str, float]) -> float:
    """Return the signed volume by which a recipe fails to close."""
    raise NotImplementedError("s04_design.absolute_volume.residual — see docs/Build_Manual_v3.md §3.1")
