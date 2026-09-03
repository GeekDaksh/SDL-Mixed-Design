"""VERIFIED / UNVERIFIED / CONFLICT / PROJECT_CONSTRAINT.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0 and §8.4
Status: implemented.
"""

from __future__ import annotations

from enum import Enum


class Status(Enum):
    """The verification status of a codified rule.

    Derived at load time, never declared in a rule file. A rule is VERIFIED only when both
    conditions hold: the manual's ledger records the clause as read from primary text
    (§0.1), and the standard's source document is frozen with a matching hash. Either one
    alone is not enough — §0.2 lists standards whose PDFs we hold but whose clauses nobody
    has read.
    """

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONFLICT = "conflict"
    PROJECT_CONSTRAINT = "project_constraint"


#: Statuses a rule may be applied under as a hard constraint.
#:
#: §10 non-negotiable: "no unverified rule becomes a hard constraint". PROJECT_CONSTRAINT
#: binds because §8.4 explicitly contemplates it — an unsourced limit is reclassified as a
#: project constraint "and labelled so", not dropped. CONFLICT never binds: §2.1 requires
#: the conflict to be declared and resolved before either side is applied.
BINDING: frozenset[Status] = frozenset({Status.VERIFIED, Status.PROJECT_CONSTRAINT})


def may_bind(status: Status) -> bool:
    """Whether a rule of this status may be applied as a hard constraint."""
    return status in BINDING


def requires_label(status: Status) -> bool:
    """Whether applying this rule obliges the caller to label it as not code-derived."""
    return status is Status.PROJECT_CONSTRAINT


def resolve(
    *,
    tag: str,
    read_from_primary: bool,
    source_frozen: bool,
    conflicts_with: tuple[str, ...],
) -> Status:
    """Derive a rule's status from its tag, the ledger and the state of its source.

    `tag` is the manual's own tag (§"How to read this document"): IS, EI, PC, ML, BO, V, NV.
    """
    if conflicts_with:
        return Status.CONFLICT
    if tag in {"PC", "EI", "BO", "ML"}:
        return Status.PROJECT_CONSTRAINT
    if tag == "NV":
        return Status.UNVERIFIED
    if read_from_primary and source_frozen:
        return Status.VERIFIED
    return Status.UNVERIFIED
