"""The mix must close to one cubic metre by absolute volume.

Stage: S05 VERIFY
Spec:  Build_Manual_v3.md §S05
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ...recipe import Recipe
from ...s01_codify.rule import Rule
from ..outcome import CheckResult


CLAUSE = "IS 10262"


def check(recipe: Recipe, rules: dict[str, Rule]) -> CheckResult:
    """Verify one mix against IS 10262. The limit is read from the registry, never inlined."""
    raise NotImplementedError(
        "s05_verify.checks.volume_closure.check — see Build_Manual_v3.md §S05"
    )


def counter_example() -> Recipe:
    """Return a mix this check must fail. A check that cannot fail is vacuous."""
    raise NotImplementedError(
        "s05_verify.checks.volume_closure.counter_example — see Build_Manual_v3.md §S05"
    )
