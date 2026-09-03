"""Unit names and the conversions permitted between them.

Stage: shared
Spec:  docs/Build_Manual_v3.md §2
Status: scaffold — not implemented.
"""

from __future__ import annotations


def convert(value: float, frm: str, to: str) -> float:
    """Convert a value between two named units of the same dimension."""
    raise NotImplementedError("msand_sdl.units.convert — see docs/Build_Manual_v3.md §2")


def canonical(unit: str) -> str:
    """Return the canonical unit name the pipeline stores this dimension in."""
    raise NotImplementedError("msand_sdl.units.canonical — see docs/Build_Manual_v3.md §2")


def check_dimension(unit: str, dimension: str) -> None:
    """Raise if a unit does not belong to the dimension a field declares."""
    raise NotImplementedError("msand_sdl.units.check_dimension — see docs/Build_Manual_v3.md §2")
