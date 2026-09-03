"""The Rule record and its fields.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0.1 and §0.2
Status: implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .status import Status, may_bind


class Tag(Enum):
    """The manual's own provenance tags. Every substantive line carries exactly one."""

    IS = "IS"
    EI = "EI"
    PC = "PC"
    ML = "ML"
    BO = "BO"
    V = "V"
    NV = "NV"


class Kind(Enum):
    """The shape of a rule's value, which decides how it may be read."""

    SCALAR = "scalar"
    TABLE = "table"
    FORMULA = "formula"
    STATEMENT = "statement"


class Role(Enum):
    """What the engine does with a rule."""

    CONSTRAINT = "constraint"
    INPUT = "input"
    PROCEDURE = "procedure"
    GUIDANCE = "guidance"


class MissingTableRow(KeyError):
    """A table was asked for a row it does not carry.

    Raised rather than interpolated or defaulted. §10 non-negotiable: "no guessed value
    replaces missing data."
    """


@dataclass(frozen=True)
class Rule:
    """One codified clause, with everything needed to apply it and to audit it."""

    id: str
    standard: str
    year: int
    clause: str
    title: str
    tag: Tag
    kind: Kind
    role: Role
    status: Status
    value: Any
    manual_ref: str
    source_file: str
    source_sha256: str | None = None
    unit: str | None = None
    applies_to: str | None = None
    override: str | None = None
    key: tuple[str, ...] = ()
    complete: bool = True
    notes: tuple[str, ...] = ()
    caveats: tuple[str, ...] = ()
    conflicts_with: tuple[str, ...] = ()
    next_action: str | None = None
    read_from_primary: bool = False

    def __str__(self) -> str:
        return f"{self.standard}:{self.year} {self.clause} [{self.status.value}]"


def is_binding(rule: Rule) -> bool:
    """Whether this rule may be applied as a hard constraint."""
    return may_bind(rule.status) and rule.role is Role.CONSTRAINT


def status_of(rule: Rule) -> Status:
    """Return the verification status of a rule."""
    return rule.status


def citation(rule: Rule) -> str:
    """Return the clause citation a failure or a proposal must carry."""
    return f"{rule.standard} : {rule.year}, {rule.clause}"


def table_lookup(rule: Rule, **keys: Any) -> dict[str, Any]:
    """Return the single table row matching every key, or raise.

    Never interpolates between rows and never falls back to a nearest match. A table
    marked incomplete says so in the error, so a missing row reads as an unfinished
    codification rather than as an out-of-range input.
    """
    if rule.kind is not Kind.TABLE:
        raise TypeError(f"{rule.id} is {rule.kind.value}, not a table")
    rows: list[dict[str, Any]] = list(rule.value)
    matches = [row for row in rows if all(row.get(k) == v for k, v in keys.items())]
    if len(matches) > 1:
        raise MissingTableRow(f"{rule.id}: {keys} matches more than one row")
    if not matches:
        detail = "" if rule.complete else " (table is incomplete — see next_action)"
        raise MissingTableRow(f"{rule.id}: no row for {keys}{detail}")
    return matches[0]


def table_column(rule: Rule, column: str) -> tuple[Any, ...]:
    """Return one column of a table, in the order the rows were codified."""
    if rule.kind is not Kind.TABLE:
        raise TypeError(f"{rule.id} is {rule.kind.value}, not a table")
    return tuple(row[column] for row in rule.value)


def scalar(rule: Rule) -> float:
    """Return a scalar rule's value."""
    if rule.kind is not Kind.SCALAR:
        raise TypeError(f"{rule.id} is {rule.kind.value}, not a scalar")
    return float(rule.value)


def from_mapping(
    data: dict[str, Any],
    *,
    standard: str,
    year: int,
    source_file: str,
    source_sha256: str | None,
    status: Status,
    read_from_primary: bool,
    inherited_caveats: tuple[str, ...] = (),
) -> Rule:
    """Build a Rule from one entry of a rules YAML file."""
    return Rule(
        id=data["id"],
        standard=standard,
        year=year,
        clause=data["clause"],
        title=data["title"],
        tag=Tag(data["tag"]),
        kind=Kind(data["kind"]),
        role=Role(data["role"]),
        status=status,
        value=data.get("value"),
        manual_ref=data["manual_ref"],
        source_file=source_file,
        source_sha256=source_sha256,
        unit=data.get("unit"),
        applies_to=data.get("applies_to"),
        override=data.get("override"),
        key=tuple(data.get("key", ())),
        complete=bool(data.get("complete", True)),
        notes=tuple(data.get("notes", ())),
        caveats=inherited_caveats + tuple(data.get("caveats", ())),
        conflicts_with=tuple(data.get("conflicts_with", ())),
        next_action=data.get("next_action"),
        read_from_primary=read_from_primary,
    )


#: Fields every rule entry in a YAML file must declare.
REQUIRED_FIELDS: tuple[str, ...] = ("id", "clause", "title", "tag", "kind", "role", "manual_ref")


def validate_mapping(data: dict[str, Any]) -> None:
    """Raise if a rule entry is missing a field the record requires."""
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ValueError(f"rule {data.get('id', '<no id>')} missing fields: {missing}")
    if data["kind"] == Kind.TABLE.value and "key" not in data:
        raise ValueError(f"rule {data['id']} is a table but declares no key columns")
