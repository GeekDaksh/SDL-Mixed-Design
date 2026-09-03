"""S01 CODIFY — frozen IS PDFs to a clause-tagged rule registry.

Entry point for the stage. The only public surface of this package.
Spec:  docs/Build_Manual_v3.md §0
Status: implemented.
"""

from __future__ import annotations

from pathlib import Path

from . import registry as registry_mod
from .contract import CodifyInput, CodifyOutput
from .freeze import MANIFEST_NAME


def default_input(repo_root: Path | None = None) -> CodifyInput:
    """The standard layout: rules beside this package, sources frozen in standards/."""
    root = repo_root or Path(__file__).resolve().parents[2]
    standards = root / "standards"
    return CodifyInput(
        repo_root=root,
        rules_dir=Path(__file__).resolve().parent / "rules",
        standards_dir=standards,
        manifest=standards / MANIFEST_NAME,
    )


def run(inp: CodifyInput) -> CodifyOutput:
    """Execute stage S01."""
    reg = registry_mod.load(inp.rules_dir, inp.manifest, inp.repo_root)
    return CodifyOutput(
        registry=reg,
        manifest=inp.manifest,
        status_counts=registry_mod.status_counts(reg),
        unresolved=registry_mod.unresolved(reg),
    )
