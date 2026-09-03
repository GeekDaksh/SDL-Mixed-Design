"""Structural invariants of the scaffold. Must pass before any stage is implemented."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from msand_sdl.pipeline import FORBIDDEN_IMPORTS, STAGES

ROOT = Path(__file__).resolve().parents[1]


def test_stage_numbers_are_contiguous() -> None:
    assert [s.number for s in STAGES] == list(range(1, 13))


@pytest.mark.parametrize("stage", STAGES, ids=lambda s: s.package)
def test_every_stage_package_exists(stage) -> None:
    pkg = ROOT / "msand_sdl" / stage.package
    assert pkg.is_dir()
    for required in ("__init__.py", "contract.py", "stage.py"):
        assert (pkg / required).is_file(), f"{stage.package} missing {required}"


@pytest.mark.parametrize("stage", STAGES, ids=lambda s: s.package)
def test_every_stage_exports_run(stage) -> None:
    module = importlib.import_module(f"msand_sdl.{stage.package}")
    assert callable(module.run)


@pytest.mark.parametrize("importer,forbidden", FORBIDDEN_IMPORTS)
def test_forbidden_imports_absent(importer: str, forbidden: str) -> None:
    pkg = ROOT / Path(importer.replace(".", "/"))
    target = forbidden.split(".")[-1]
    for path in pkg.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            assert not any(target in n for n in names), (
                f"{path.relative_to(ROOT)} imports {forbidden}; "
                f"{importer} must recompute independently"
            )


def test_no_numeric_constants_in_scaffold() -> None:
    """A scaffold carries no standards values. They load from s01_codify at runtime."""
    allowed = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
    offenders: list[str] = []
    for path in (ROOT / "msand_sdl").rglob("*.py"):
        if path.name == "pipeline.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in allowed:
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} = {node.value}")
    assert not offenders, "numeric literals in scaffold:\n" + "\n".join(offenders)
