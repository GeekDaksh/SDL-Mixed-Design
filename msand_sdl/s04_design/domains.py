"""Route a grade to its IS 10262 section before anything runs.

Stage: S04 DESIGN
Spec:  Build_Manual_v3.md §S04
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..contracts import Domain, Requirement, UseClass


def route(requirement: Requirement) -> Domain:
    """Return the domain that decides which route this requirement takes."""
    raise NotImplementedError("s04_design.domains.route — see Build_Manual_v3.md §S04")


def domain_of_grade(grade: str) -> Domain:
    """Return the domain a grade designation belongs to."""
    raise NotImplementedError("s04_design.domains.domain_of_grade — see Build_Manual_v3.md §S04")


def permits_nominal(domain: Domain, use: UseClass) -> bool:
    """Whether a nominal mix is permissible for this domain and structural use."""
    raise NotImplementedError("s04_design.domains.permits_nominal — see Build_Manual_v3.md §S04")
