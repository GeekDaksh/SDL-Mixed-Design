#!/usr/bin/env python3
"""Content-hash every primary source in standards/ into MANIFEST.sha256.

Stage: S01 CODIFY
Spec:  Build_Manual_v3.md §S01
Status: scaffold — not implemented.
"""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    raise NotImplementedError("scripts.00_freeze_standards.parse_args — see Build_Manual_v3.md §S01")


def main() -> int:
    """Entry point."""
    raise NotImplementedError("scripts.00_freeze_standards.main — see Build_Manual_v3.md §S01")


if __name__ == "__main__":
    raise SystemExit(main())
