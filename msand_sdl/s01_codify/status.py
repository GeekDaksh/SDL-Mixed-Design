"""VERIFIED / UNVERIFIED / CONFLICT / PROJECT_CONSTRAINT.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0
Status: scaffold — not implemented.
"""

from __future__ import annotations

from enum import Enum


class Status(Enum):
    """The verification status of a codified rule."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONFLICT = "conflict"
    PROJECT_CONSTRAINT = "project_constraint"


def may_bind(status: Status) -> bool:
    """Whether a rule of this status may be applied as a hard constraint."""
    raise NotImplementedError("s01_codify.status.may_bind — see docs/Build_Manual_v3.md §0")
