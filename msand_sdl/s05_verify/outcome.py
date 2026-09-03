"""PASS / FAIL / NOT_VERIFIED / OVERRIDE_REQUIRED.

Stage: S05 VERIFY
Spec:  Build_Manual_v3.md §S05
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Outcome(Enum):
    """The verdict on one clause."""

    PASS = "pass"
    FAIL = "fail"
    NOT_VERIFIED = "not_verified"
    OVERRIDE_REQUIRED = "override_required"


@dataclass(frozen=True)
class CheckResult:
    """One clause, one verdict, and what the check saw."""

    # TODO(s05): fields per Build_Manual_v3.md §S05


def is_blocking(outcome: Outcome) -> bool:
    """Whether this verdict stops a mix from being proposed."""
    raise NotImplementedError("s05_verify.outcome.is_blocking — see Build_Manual_v3.md §S05")
