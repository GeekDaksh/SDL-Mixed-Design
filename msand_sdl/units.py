"""Unit names and the conversions permitted between them.

Stage: shared
Spec:  Build_Manual_v3.md §S00
Status: scaffold — not implemented.
"""

from __future__ import annotations


def convert(value: float, frm: str, to: str) -> float:
    """Convert a value between two named units of the same dimension."""
    raise NotImplementedError("msand_sdl.units.convert — see Build_Manual_v3.md §S00")


def canonical(unit: str) -> str:
    """Return the canonical unit name the pipeline stores this dimension in."""
    raise NotImplementedError("msand_sdl.units.canonical — see Build_Manual_v3.md §S00")


def check_dimension(unit: str, dimension: str) -> None:
    """Raise if a unit does not belong to the dimension a field declares."""
    raise NotImplementedError("msand_sdl.units.check_dimension — see Build_Manual_v3.md §S00")
