"""Clause lookup; refuses an unverified rule as a hard constraint.

Stage: S01 CODIFY
Spec:  docs/Build_Manual_v3.md §0.2 and §10
Status: implemented.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import freeze
from . import status as status_mod
from .rule import Role, Rule, from_mapping, validate_mapping
from .status import Status


class UnknownClause(KeyError):
    """A clause was asked for that was never codified."""


class UnverifiedRule(RuntimeError):
    """A rule was requested as a hard constraint but its status does not permit binding.

    §10 non-negotiable: "no unverified rule becomes a hard constraint."
    """


@dataclass(frozen=True)
class StandardFile:
    """One rules file: which standard it codifies and the state of its frozen source."""

    standard: str
    year: int
    title: str
    revision: str | None
    source_file: str
    library_file: str | None
    source_sha256: str | None
    read_from_primary: bool
    source_frozen: bool
    caveats: tuple[str, ...]
    rule_count: int


@dataclass(frozen=True)
class Registry:
    """Every codified rule, keyed by id, with the state of each source behind them."""

    rules: dict[str, Rule]
    standards: dict[str, StandardFile]

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules.values())

    def __contains__(self, rule_id: object) -> bool:
        return rule_id in self.rules


def load(rules_dir: Path, manifest: Path, repo_root: Path) -> Registry:
    """Load every rule file in a directory, deriving each rule's status as it goes.

    Status is never read from the file. It is derived from three things: the manual's tag,
    whether the ledger records the clause as read from primary text (§0.1 vs §0.2), and
    whether the source document is frozen with a matching hash. Dropping a missing PDF into
    standards/ and re-freezing therefore flips its rules to VERIFIED with no edit to any
    rule file — and removing one flips them back.
    """
    rules: dict[str, Rule] = {}
    standards: dict[str, StandardFile] = {}

    for path in sorted(rules_dir.glob("*.yaml")):
        data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        standard = data["standard"]
        year = data["year"]
        source_file = data["source_file"]
        read_from_primary = bool(data.get("read_from_primary", False))
        frozen = freeze.is_frozen(source_file, manifest, repo_root)
        digest = freeze.read_manifest(manifest).get(source_file) if frozen else None
        caveats = tuple(c["text"] for c in data.get("caveats", ()))

        entries = data.get("rules") or []
        for entry in entries:
            validate_mapping(entry)
            derived = status_mod.resolve(
                tag=entry["tag"],
                read_from_primary=read_from_primary,
                source_frozen=frozen,
                conflicts_with=tuple(entry.get("conflicts_with", ())),
            )
            rule = from_mapping(
                entry,
                standard=standard,
                year=year,
                source_file=source_file,
                source_sha256=digest,
                status=derived,
                read_from_primary=read_from_primary,
                inherited_caveats=caveats,
            )
            if rule.id in rules:
                raise ValueError(f"duplicate rule id: {rule.id}")
            rules[rule.id] = rule

        standards[path.stem] = StandardFile(
            standard=standard,
            year=year,
            title=data.get("title", ""),
            revision=data.get("revision"),
            source_file=source_file,
            library_file=data.get("library_file"),
            source_sha256=digest,
            read_from_primary=read_from_primary,
            source_frozen=frozen,
            caveats=caveats,
            rule_count=len(entries),
        )

    return Registry(rules=rules, standards=standards)


def lookup(registry: Registry, rule_id: str) -> Rule:
    """Return the rule with this id, or raise if it was never codified."""
    try:
        return registry.rules[rule_id]
    except KeyError:
        raise UnknownClause(
            f"{rule_id} is not in the registry; it has not been codified"
        ) from None


def as_hard_constraint(registry: Registry, rule_id: str) -> Rule:
    """Return a rule for use as a hard constraint, or refuse it.

    Refuses anything that is not VERIFIED or an explicitly declared PROJECT_CONSTRAINT.
    A CONFLICT must be resolved before either side of it can bind (§2.1).
    """
    rule = lookup(registry, rule_id)
    if not status_mod.may_bind(rule.status):
        detail = _why_not_binding(registry, rule)
        raise UnverifiedRule(
            f"{rule_id} is {rule.status.value} and cannot be used as a hard constraint. "
            f"{detail}"
        )
    if rule.role is not Role.CONSTRAINT:
        raise UnverifiedRule(
            f"{rule_id} is a {rule.role.value}, not a constraint; it cannot gate a mix"
        )
    return rule


def _why_not_binding(registry: Registry, rule: Rule) -> str:
    """Explain what would have to change for this rule to bind."""
    if rule.status is Status.CONFLICT:
        return f"It conflicts with {', '.join(rule.conflicts_with)}; resolve the conflict first."
    if rule.tag.value == "NV":
        return (
            f"It is tagged [NV] in the manual ({rule.manual_ref}); "
            f"no primary source verifies it."
        )
    file = next(
        (s for s in registry.standards.values() if s.source_file == rule.source_file), None
    )
    if file is not None and not file.source_frozen:
        return (
            f"Its source {rule.source_file} is not frozen; "
            f"run scripts/00_freeze_standards.py."
        )
    if file is not None and not file.read_from_primary:
        return (
            f"{file.standard}:{file.year} is listed in §0.2 as not read; "
            f"its clauses must be read from the primary text before they can bind."
        )
    return "It is not backed by a verified primary source."


def clauses(registry: Registry, standard: str) -> tuple[str, ...]:
    """Return every rule id codified from one standard."""
    return tuple(sorted(r.id for r in registry if r.standard == standard))


def by_status(registry: Registry, status: Status) -> tuple[Rule, ...]:
    """Return every rule currently carrying this status."""
    return tuple(r for r in registry if r.status is status)


def status_counts(registry: Registry) -> dict[str, int]:
    """Return how many rules sit at each status."""
    return {s.value: len(by_status(registry, s)) for s in Status}


def unresolved(registry: Registry) -> tuple[str, ...]:
    """Return one line per thing standing between the registry and a fully verified state."""
    out: list[str] = []
    for name, file in sorted(registry.standards.items()):
        if not file.source_frozen:
            out.append(f"{name}: source {file.source_file} is not frozen")
        if not file.read_from_primary:
            out.append(
                f"{name}: {file.standard}:{file.year} not read from primary text (§0.2); "
                f"{file.rule_count} rule(s) cannot bind"
            )
    for rule in registry:
        if rule.status is Status.CONFLICT:
            out.append(
                f"{rule.id}: conflicts with {', '.join(rule.conflicts_with)} "
                f"({rule.manual_ref})"
            )
        if not rule.complete:
            out.append(f"{rule.id}: incomplete — {rule.next_action or 'no next action recorded'}")
    return tuple(out)
