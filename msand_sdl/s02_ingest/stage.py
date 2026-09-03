"""S02 INGEST — plant workbooks to one harmonised raw table.

Entry point for the stage. The only public surface of this package.
Status: scaffold — not implemented.
"""

from __future__ import annotations

from .contract import IngestInput, IngestOutput


def run(inp: IngestInput) -> IngestOutput:
    """Execute stage S02."""
    raise NotImplementedError("s02_ingest.stage.run")
