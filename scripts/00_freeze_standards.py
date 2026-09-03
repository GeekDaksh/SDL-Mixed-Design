#!/usr/bin/env python3
"""Content-hash every primary source in standards/ into MANIFEST.sha256.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §2
Status: scaffold — not implemented.
"""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    raise NotImplementedError("scripts.00_freeze_standards.parse_args — see docs/Build_Manual_v3.md §2")


def main() -> int:
    """Entry point."""
    raise NotImplementedError("scripts.00_freeze_standards.main — see docs/Build_Manual_v3.md §2")


if __name__ == "__main__":
    raise SystemExit(main())
