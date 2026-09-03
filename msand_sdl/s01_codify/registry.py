"""Clause lookup; refuses an unverified rule as a hard constraint.

Stage: S01 CODIFY
Spec:  Build_Manual_v3.md §S01
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path

from .rule import Rule


def load(rules_dir: Path) -> dict[str, Rule]:
    """Load every rule file in a directory, keyed by clause tag."""
    raise NotImplementedError("s01_codify.registry.load — see Build_Manual_v3.md §S01")


def lookup(registry: dict[str, Rule], clause: str) -> Rule:
    """Return the rule for a clause tag, or raise if it was never codified."""
    raise NotImplementedError("s01_codify.registry.lookup — see Build_Manual_v3.md §S01")


def as_hard_constraint(registry: dict[str, Rule], clause: str) -> Rule:
    """Return a rule for use as a hard constraint; raise unless it is VERIFIED."""
    raise NotImplementedError(
        "s01_codify.registry.as_hard_constraint — see Build_Manual_v3.md §S01"
    )


def clauses(registry: dict[str, Rule], standard: str) -> tuple[str, ...]:
    """Return every clause tag codified from one standard."""
    raise NotImplementedError("s01_codify.registry.clauses — see Build_Manual_v3.md §S01")
