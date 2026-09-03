"""Record a documented special consideration.

Stage: S05 VERIFY
Spec:  docs/Build_Manual_v3.md §5
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass

from .outcome import CheckResult


@dataclass(frozen=True)
class Override:
    """A documented special consideration against one clause. Never silent, never default."""

    # TODO(s05): fields per docs/Build_Manual_v3.md §5


def apply(result: CheckResult, override: Override) -> CheckResult:
    """Apply a documented override to one clause verdict."""
    raise NotImplementedError("s05_verify.override.apply — see docs/Build_Manual_v3.md §5")


def is_documented(override: Override) -> bool:
    """Whether an override carries the justification the clause requires."""
    raise NotImplementedError("s05_verify.override.is_documented — see docs/Build_Manual_v3.md §5")
