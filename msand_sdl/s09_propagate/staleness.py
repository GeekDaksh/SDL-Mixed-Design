"""Raise if any value survives a change to one of its inputs.

Stage: S09 PROPAGATE
Spec:  docs/Build_Manual_v3.md §7.4
Status: scaffold — not implemented.
"""

from __future__ import annotations

from ..recipe import Recipe


def stale_fields(before: Recipe, after: Recipe, changed: str) -> tuple[str, ...]:
    """Return every field that should have moved when this variable changed, and did not."""
    raise NotImplementedError(
        "s09_propagate.staleness.stale_fields — see docs/Build_Manual_v3.md §7.4"
    )


def check(before: Recipe, after: Recipe, changed: str) -> None:
    """Raise if any cached value survived a change to one of its inputs."""
    raise NotImplementedError("s09_propagate.staleness.check — see docs/Build_Manual_v3.md §7.4")
