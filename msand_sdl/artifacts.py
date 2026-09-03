"""Read and write stage artifacts under the directories declared in pipeline.py.

Stage: shared
Spec:  Build_Manual_v3.md §S00
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def artifact_dir(stage_number: int) -> Path:
    """Return the artifact directory declared for this stage, or raise if it has none."""
    raise NotImplementedError("msand_sdl.artifacts.artifact_dir — see Build_Manual_v3.md §S00")


def write(stage_number: int, name: str, payload: Any) -> Path:
    """Write one artifact for a stage and return the path it was written to."""
    raise NotImplementedError("msand_sdl.artifacts.write — see Build_Manual_v3.md §S00")


def read(stage_number: int, name: str) -> Any:
    """Read one artifact produced by a stage."""
    raise NotImplementedError("msand_sdl.artifacts.read — see Build_Manual_v3.md §S00")


def fingerprint(path: Path) -> str:
    """Return the content hash of an artifact, for the version record in S12."""
    raise NotImplementedError("msand_sdl.artifacts.fingerprint — see Build_Manual_v3.md §S00")
