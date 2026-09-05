#!/usr/bin/env python3
"""Content-hash every primary source cited by the registry into standards/MANIFEST.sha256.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §10 step 1
Status: implemented.

Each rules file names both where its source lives in the shared library (`library_file`)
and where the registry expects it frozen (`source_file`). This script copies the first to
the second and hashes it there. The copy is deliberate: a frozen source must not be able to
move or be re-exported out from under the rules that cite it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from msand_sdl.s01_codify import freeze, stage

REPO_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROOT = REPO_ROOT.parent


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--library-root",
        type=Path,
        default=LIBRARY_ROOT,
        help="directory the library_file paths are relative to (default: the repo's parent)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the existing manifest without rewriting it",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    inp = stage.default_input(REPO_ROOT)

    if args.check:
        return _check(inp.rules_dir, inp.manifest)

    entries: list[freeze.ManifestEntry] = []
    missing: list[str] = []

    for path in sorted(inp.rules_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        source_file = data["source_file"]
        library_file = data.get("library_file")
        if not library_file:
            missing.append(f"{path.name}: no library_file declared")
            continue
        source = args.library_root / library_file
        if not source.is_file():
            missing.append(f"{path.name}: library file not found: {source}")
            continue
        target = freeze.adopt(source, inp.standards_dir, Path(source_file).name)
        digest = freeze.hash_file(target)
        key = freeze.manifest_key(source_file, inp.manifest, REPO_ROOT)
        entries.append(freeze.ManifestEntry(path=key, sha256=digest))
        print(f"  frozen  {source_file}  {digest[:12]}…  <- {library_file}")

    manifest = freeze.write_manifest(inp.standards_dir, entries)
    print(f"\n{len(entries)} source(s) frozen into {manifest.relative_to(REPO_ROOT)}")
    print(f"verify with:  cd {manifest.parent.relative_to(REPO_ROOT)} && "
          f"shasum -a 256 -c {manifest.name}")

    for line in missing:
        print(f"  NOT FROZEN  {line}", file=sys.stderr)

    out = stage.run(inp)
    print("\nregistry after freezing:")
    for name, count in out.status_counts.items():
        print(f"  {name:<20} {count}")
    if out.unresolved:
        print("\nunresolved:")
        for line in out.unresolved:
            print(f"  - {line}")
    return 0


def _check(rules_dir: Path, manifest: Path) -> int:
    """Verify every cited source against the manifest without rewriting it."""
    failures: list[str] = []
    for path in sorted(rules_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        source_file = data["source_file"]
        try:
            digest = freeze.verify_source(source_file, manifest, REPO_ROOT)
        except (freeze.SourceNotFrozen, FileNotFoundError) as exc:
            failures.append(str(exc))
            print(f"  FAIL  {source_file}")
        else:
            print(f"  ok    {source_file}  {digest[:12]}…")
    for line in failures:
        print(f"  {line}", file=sys.stderr)
    return len(failures)


if __name__ == "__main__":
    raise SystemExit(main())
