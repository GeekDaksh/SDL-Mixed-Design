"""Supplementary cementitious material dosage within the permitted range.

Stage: S05 VERIFY
Spec:  docs/Build_Manual_v3.md §5
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ...recipe import Recipe
from ...s01_codify.rule import Rule
from ..outcome import CheckResult


CLAUSE = "IS 456 cl 5.2"


def check(recipe: Recipe, rules: dict[str, Rule]) -> CheckResult:
    """Verify one mix against IS 456 cl 5.2. The limit is read from the registry, never inlined."""
    raise NotImplementedError(
        "s05_verify.checks.scm_dosage.check — see docs/Build_Manual_v3.md §5"
    )


def counter_example() -> Recipe:
    """Return a mix this check must fail. A check that cannot fail is vacuous."""
    raise NotImplementedError(
        "s05_verify.checks.scm_dosage.counter_example — see docs/Build_Manual_v3.md §5"
    )
