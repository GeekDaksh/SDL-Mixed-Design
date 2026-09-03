"""Model version, dataset hash and standards manifest hash on every proposal.

Stage: S12 LEARN
Spec:  docs/Build_Manual_v3.md §10
Status: scaffold — not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VersionRecord:
    """What produced a proposal: model version, dataset hash, standards manifest hash."""

    # TODO(s12): fields per docs/Build_Manual_v3.md §10


def current(model_dir: Path, dataset: Path, manifest: Path) -> VersionRecord:
    """Assemble the version record that must travel with every proposal."""
    raise NotImplementedError("s12_learn.versions.current — see docs/Build_Manual_v3.md §10")


def bump(record: VersionRecord) -> VersionRecord:
    """Return the next model version after a successful update."""
    raise NotImplementedError("s12_learn.versions.bump — see docs/Build_Manual_v3.md §10")


def check_match(record: VersionRecord, manifest: Path) -> None:
    """Raise if a proposal cites a standards manifest that is no longer current."""
    raise NotImplementedError("s12_learn.versions.check_match — see docs/Build_Manual_v3.md §10")
