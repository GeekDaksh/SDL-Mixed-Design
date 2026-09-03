"""The eight rejection reasons, kept distinct.

Stage: S12 LEARN
Spec:  Build_Manual_v3.md §S12
Status: scaffold — not implemented.
"""

from __future__ import annotations

from enum import Enum


class RejectionReason(Enum):
    """Why a proposal was rejected. Eight reasons, never collapsed into one another."""

    # TODO(s12): the eight reasons per Build_Manual_v3.md §S12


def reasons() -> tuple[RejectionReason, ...]:
    """Return every rejection reason. A review must pick one of these, not free text."""
    raise NotImplementedError("s12_learn.review.reasons — see Build_Manual_v3.md §S12")


def is_model_relevant(reason: RejectionReason) -> bool:
    """Whether this rejection tells the model something, or only the operator."""
    raise NotImplementedError("s12_learn.review.is_model_relevant — see Build_Manual_v3.md §S12")
