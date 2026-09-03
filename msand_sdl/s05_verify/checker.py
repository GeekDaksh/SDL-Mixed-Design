"""Run every check, return a verdict per clause.

Stage: S05 VERIFY
Spec:  docs/Build_Manual_v3.md §5
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe
from ..s01_codify.rule import Rule
from .outcome import CheckResult, Outcome


def checks() -> tuple[str, ...]:
    """Return every registered check by name, one per clause."""
    raise NotImplementedError("s05_verify.checker.checks — see docs/Build_Manual_v3.md §5")


def run_all(recipe: Recipe, rules: dict[str, Rule]) -> tuple[CheckResult, ...]:
    """Run every check against a mix. This stage recomputes; it never trusts a design's own numbers."""
    raise NotImplementedError("s05_verify.checker.run_all — see docs/Build_Manual_v3.md §5")


def verdict(results: tuple[CheckResult, ...]) -> Outcome:
    """Reduce every clause verdict to one outcome for the mix."""
    raise NotImplementedError("s05_verify.checker.verdict — see docs/Build_Manual_v3.md §5")
