"""Record a documented special consideration.

Stage: S05 VERIFY
Spec:  Build_Manual_v3.md §S05
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from .outcome import CheckResult


@dataclass(frozen=True)
class Override:
    """A documented special consideration against one clause. Never silent, never default."""

    # TODO(s05): fields per Build_Manual_v3.md §S05


def apply(result: CheckResult, override: Override) -> CheckResult:
    """Apply a documented override to one clause verdict."""
    raise NotImplementedError("s05_verify.override.apply — see Build_Manual_v3.md §S05")


def is_documented(override: Override) -> bool:
    """Whether an override carries the justification the clause requires."""
    raise NotImplementedError("s05_verify.override.is_documented — see Build_Manual_v3.md §S05")
