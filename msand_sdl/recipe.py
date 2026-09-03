"""The mix recipe record — the mass of every constituent in one cubic metre.

Stage: shared
Spec:  Build_Manual_v3.md §S00
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Recipe:
    """One fully specified mix, expressed per cubic metre."""

    # TODO(recipe): fields per Build_Manual_v3.md §S00


def constituent_masses(recipe: Recipe) -> dict[str, float]:
    """Return every constituent of the recipe keyed by name."""
    raise NotImplementedError("msand_sdl.recipe.constituent_masses — see Build_Manual_v3.md §S00")


def water_cementitious_ratio(recipe: Recipe) -> float:
    """Return the free water to cementitious ratio of the recipe."""
    raise NotImplementedError(
        "msand_sdl.recipe.water_cementitious_ratio — see Build_Manual_v3.md §S00"
    )


def cementitious_content(recipe: Recipe) -> float:
    """Return total cementitious content; cement alone is a separate quantity."""
    raise NotImplementedError(
        "msand_sdl.recipe.cementitious_content — see Build_Manual_v3.md §S00"
    )
