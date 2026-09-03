#!/usr/bin/env python3
"""Run S02 then S03: plant workbooks to the strength and workability datasets.

Stage: S02 INGEST, S03 PREPARE
Spec:  Build_Manual_v3.md §S02, §S03
Status: scaffold — not implemented.
"""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    raise NotImplementedError("scripts.01_build_datasets.parse_args — see Build_Manual_v3.md §S02, §S03")


def main() -> int:
    """Entry point."""
    raise NotImplementedError("scripts.01_build_datasets.main — see Build_Manual_v3.md §S02, §S03")


if __name__ == "__main__":
    raise SystemExit(main())
