"""Raise if any value survives a change to one of its inputs.

Stage: S09 PROPAGATE
Spec:  Build_Manual_v3.md §S09
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def stale_fields(before: Recipe, after: Recipe, changed: str) -> tuple[str, ...]:
    """Return every field that should have moved when this variable changed, and did not."""
    raise NotImplementedError(
        "s09_propagate.staleness.stale_fields — see Build_Manual_v3.md §S09"
    )


def check(before: Recipe, after: Recipe, changed: str) -> None:
    """Raise if any cached value survived a change to one of its inputs."""
    raise NotImplementedError("s09_propagate.staleness.check — see Build_Manual_v3.md §S09")
