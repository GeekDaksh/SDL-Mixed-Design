"""Content-hash the primary sources into MANIFEST.sha256.

Stage: S01 CODIFY
Spec:  Build_Manual_v3.md §S01
Status: scaffold — not implemented.
"""

from __future__ import annotations

from pathlib import Path


def hash_file(path: Path) -> str:
    """Return the content hash of one primary source."""
    raise NotImplementedError("s01_codify.freeze.hash_file — see Build_Manual_v3.md §S01")


def write_manifest(standards_dir: Path) -> Path:
    """Hash every file in the standards directory into MANIFEST.sha256."""
    raise NotImplementedError("s01_codify.freeze.write_manifest — see Build_Manual_v3.md §S01")


def read_manifest(manifest: Path) -> dict[str, str]:
    """Read the manifest as a mapping of file name to content hash."""
    raise NotImplementedError("s01_codify.freeze.read_manifest — see Build_Manual_v3.md §S01")


def verify_source(path: Path, manifest: Path) -> None:
    """Raise unless this file's hash is present in, and matches, the manifest."""
    raise NotImplementedError("s01_codify.freeze.verify_source — see Build_Manual_v3.md §S01")
