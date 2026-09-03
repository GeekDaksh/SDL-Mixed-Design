"""The Rule record and its fields.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from .status import Status


@dataclass(frozen=True)
class Rule:
    """One codified clause. Carries its source, its clause tag and its status."""

    # TODO(s01): fields per docs/Build_Manual_v3.md §0


def is_binding(rule: Rule) -> bool:
    """Whether this rule may be applied as a hard constraint."""
    raise NotImplementedError("s01_codify.rule.is_binding — see docs/Build_Manual_v3.md §0")


def status_of(rule: Rule) -> Status:
    """Return the verification status of a rule."""
    raise NotImplementedError("s01_codify.rule.status_of — see docs/Build_Manual_v3.md §0")
