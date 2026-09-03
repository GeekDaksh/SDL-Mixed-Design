"""Decision variables and their bounds; cement and cementitious separate.

Stage: S11 PROPOSE
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Requirement


@dataclass(frozen=True)
class Variable:
    """One decision variable and the bounds the search may move it between."""

    # TODO(s11): fields per docs/Build_Manual_v3.md §10


def variables(requirement: Requirement) -> tuple[Variable, ...]:
    """Return the decision variables for this requirement.

    Cement and total cementitious are separate variables. IS 456 cl 8.2.4.2 caps cement
    excluding fly ash and GGBS, and a single binder bound cannot express that.
    """
    raise NotImplementedError("s11_propose.space.variables — see docs/Build_Manual_v3.md §10")


def bounds(requirement: Requirement) -> dict[str, tuple[float, float]]:
    """Return the bound on each decision variable, read from the registry and the data."""
    raise NotImplementedError("s11_propose.space.bounds — see docs/Build_Manual_v3.md §10")
