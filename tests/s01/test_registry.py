"""S01 — the registry refuses an unverified rule as a hard constraint.

Spec: docs/Build_Manual_v3.md §0.2 and §10
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from msand_sdl.s01_codify import freeze, stage
from msand_sdl.s01_codify import registry as reg_mod
from msand_sdl.s01_codify.rule import Kind, MissingTableRow, Role, table_lookup
from msand_sdl.s01_codify.status import Status


@pytest.fixture(scope="module")
def registry(repo_root: Path) -> reg_mod.Registry:
    """The real registry, loaded against the real manifest."""
    return stage.run(stage.default_input(repo_root)).registry


# --------------------------------------------------------------- the core invariant


def test_unverified_rule_cannot_be_a_hard_constraint(registry: reg_mod.Registry) -> None:
    """§10 non-negotiable: no unverified rule becomes a hard constraint."""
    rule_id = "is9103.dosage_cap.unverified"
    assert registry.rules[rule_id].status is Status.UNVERIFIED
    with pytest.raises(reg_mod.UnverifiedRule) as excinfo:
        reg_mod.as_hard_constraint(registry, rule_id)
    assert "unverified" in str(excinfo.value)


def test_every_unverified_rule_refuses_to_bind(registry: reg_mod.Registry) -> None:
    """Not just the one — no rule outside VERIFIED or PROJECT_CONSTRAINT may gate a mix."""
    for rule in registry:
        if rule.status in (Status.UNVERIFIED, Status.CONFLICT):
            with pytest.raises(reg_mod.UnverifiedRule):
                reg_mod.as_hard_constraint(registry, rule.id)


def test_refusal_explains_what_would_change_it(registry: reg_mod.Registry) -> None:
    """A refusal that does not say what to do about it is a dead end."""
    with pytest.raises(reg_mod.UnverifiedRule) as excinfo:
        reg_mod.as_hard_constraint(registry, "is456.table_5_note_1.scm_credit")
    assert "[NV]" in str(excinfo.value)


def test_an_input_cannot_be_used_as_a_constraint(registry: reg_mod.Registry) -> None:
    """A table of values is not a gate, however well verified it is."""
    table = registry.rules["is10262.table_8.water_cementitious_ratio"]
    assert table.status is Status.VERIFIED
    with pytest.raises(reg_mod.UnverifiedRule, match="not a constraint"):
        reg_mod.as_hard_constraint(registry, table.id)


# --------------------------------------------------------------- status derivation


def test_status_follows_the_ledger_not_the_file(registry: reg_mod.Registry) -> None:
    """IS 383 and IS 9103 are frozen but unread (§0.2), so nothing sourced to them binds."""
    for name in ("is383_2016", "is9103_1999"):
        entry = registry.standards[name]
        assert entry.source_frozen, f"{name} source should be frozen"
        assert not entry.read_from_primary, f"{name} is listed in §0.2 as not read"
    for rule in registry:
        if rule.source_file.endswith(("is383_2016.pdf", "is9103_1999.pdf")):
            assert rule.status is not Status.VERIFIED


def test_read_and_frozen_standards_are_verified(registry: reg_mod.Registry) -> None:
    """IS 456 and IS 10262 are both read (§0.1) and frozen, so their IS rules bind."""
    rule = reg_mod.as_hard_constraint(registry, "is456.cl_8_2_4_2.max_cement")
    assert rule.status is Status.VERIFIED
    assert rule.source_sha256 is not None


def test_unfrozen_source_downgrades_its_rules(tmp_path: Path, repo_root: Path) -> None:
    """Remove a PDF from the manifest and its rules stop binding, with no edit to any rule file."""
    rules_dir = tmp_path / "rules"
    shutil.copytree(repo_root / "msand_sdl" / "s01_codify" / "rules", rules_dir)
    manifest = tmp_path / "standards" / freeze.MANIFEST_NAME
    manifest.parent.mkdir()
    manifest.write_text("# empty manifest\n", encoding="utf-8")

    degraded = reg_mod.load(rules_dir, manifest, tmp_path)
    rule = degraded.rules["is456.cl_8_2_4_2.max_cement"]
    assert rule.status is Status.UNVERIFIED
    with pytest.raises(reg_mod.UnverifiedRule, match="not frozen"):
        reg_mod.as_hard_constraint(degraded, rule.id)


def test_project_constraints_bind_but_are_labelled(registry: reg_mod.Registry) -> None:
    """§8.4 contemplates an unsourced limit becoming a labelled project constraint."""
    rule = registry.rules["is10262.pc.target_mean_resolution"]
    assert rule.status is Status.PROJECT_CONSTRAINT
    assert rule.tag.value == "PC"


def test_declared_conflict_does_not_bind(registry: reg_mod.Registry) -> None:
    """§2.1: both target-mean clauses are in CONFLICT until the resolution is applied."""
    for rule_id in (
        "is456.cl_9_2_2.target_mean_strength",
        "is10262.cl_4_2.target_mean_strength",
    ):
        rule = registry.rules[rule_id]
        assert rule.status is Status.CONFLICT
        assert rule.conflicts_with
        with pytest.raises(reg_mod.UnverifiedRule, match="conflict"):
            reg_mod.as_hard_constraint(registry, rule_id)


# --------------------------------------------------------------- source freezing


def test_every_cited_source_is_frozen_and_matches(
    registry: reg_mod.Registry, repo_root: Path
) -> None:
    """The manifest covers every source the registry cites, and the bytes still match."""
    manifest = repo_root / "standards" / freeze.MANIFEST_NAME
    for name, entry in registry.standards.items():
        digest = freeze.verify_source(entry.source_file, manifest, repo_root)
        assert digest == entry.source_sha256, name


def test_a_tampered_source_is_detected(tmp_path: Path) -> None:
    """A source whose bytes changed since freezing is not frozen any more."""
    standards = tmp_path / "standards"
    standards.mkdir()
    source = standards / "fake.pdf"
    source.write_bytes(b"original")
    manifest = freeze.write_manifest(
        standards,
        [freeze.ManifestEntry(path="standards/fake.pdf", sha256=freeze.hash_file(source))],
    )
    assert freeze.is_frozen("standards/fake.pdf", manifest, tmp_path)

    source.write_bytes(b"tampered")
    assert not freeze.is_frozen("standards/fake.pdf", manifest, tmp_path)
    with pytest.raises(freeze.SourceNotFrozen, match="does not match"):
        freeze.verify_source("standards/fake.pdf", manifest, tmp_path)


# --------------------------------------------------------------- lookup behaviour


def test_unknown_clause_raises(registry: reg_mod.Registry) -> None:
    with pytest.raises(reg_mod.UnknownClause):
        reg_mod.lookup(registry, "is456.cl_99_9_9.invented")


def test_missing_table_row_raises_rather_than_interpolating(registry: reg_mod.Registry) -> None:
    """§10 non-negotiable: no guessed value replaces missing data."""
    table_8 = registry.rules["is10262.table_8.water_cementitious_ratio"]
    assert table_lookup(table_8, target_strength=70, msa_mm=20.0)["wcm"] == 0.33
    with pytest.raises(MissingTableRow):
        table_lookup(table_8, target_strength=74.9, msa_mm=20.0)


def test_incomplete_table_says_so_when_it_misses(registry: reg_mod.Registry) -> None:
    """Table 1 is not codified; asking for a row must read as unfinished work, not bad input."""
    table_1 = registry.rules["is10262.table_1.x_factor"]
    assert not table_1.complete
    with pytest.raises(MissingTableRow, match="incomplete"):
        table_lookup(table_1, grade="M30")


def test_table_5_is_keyed_by_zone_not_column_position(registry: reg_mod.Registry) -> None:
    """§6.1: the printed columns run Zone IV, III, II, I right to left.

    Reading them left to right reverses every row and produces the 0.668 that Annex A
    publishes as 0.648. Keying by zone name is what makes that mistake unrepresentable.
    """
    table_5 = registry.rules["is10262.table_5.coarse_aggregate_volume"]
    assert table_lookup(table_5, msa_mm=20, zone="II")["ca_volume_fraction"] == 0.62
    assert table_lookup(table_5, msa_mm=20, zone="IV")["ca_volume_fraction"] == 0.66
    assert any("RIGHT TO LEFT" in c for c in table_5.caveats)


def test_domain_c_pumpable_reduction_differs_from_domain_b(registry: reg_mod.Registry) -> None:
    """§3.2: 5 percent on the Section 3 route, not the 10 percent of cl 5.5.2."""
    assert registry.rules["is10262.cl_5_5_2.pumpable_reduction_domain_b"].value == 10
    assert registry.rules["is10262.cl_6_2_7.pumpable_reduction_domain_c"].value == 5


# --------------------------------------------------------------- registry integrity


def test_every_rule_carries_a_manual_reference(registry: reg_mod.Registry) -> None:
    """Nothing enters the registry without a line in the manual behind it."""
    for rule in registry:
        assert rule.manual_ref.startswith("§"), rule.id


def test_every_rule_declares_a_known_kind_and_role(registry: reg_mod.Registry) -> None:
    for rule in registry:
        assert isinstance(rule.kind, Kind)
        assert isinstance(rule.role, Role)


def test_is456_rules_carry_the_amendment_caveat(registry: reg_mod.Registry) -> None:
    """§0.3: no IS 456 clause is amendment-current until checked against a current print."""
    rule = registry.rules["is456.cl_8_2_4_2.max_cement"]
    assert any("amendment-current" in c for c in rule.caveats)


def test_unresolved_reports_the_open_items(registry: reg_mod.Registry) -> None:
    """The stage must be able to say what stands between it and a fully verified state."""
    lines = reg_mod.unresolved(registry)
    assert any("is383_2016" in line for line in lines)
    assert any("is9103_1999" in line for line in lines)
    assert any("table_1" in line for line in lines)
