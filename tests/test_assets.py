from __future__ import annotations

from pathlib import Path
import tomllib

import json
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_codex_environment_and_agents_exist() -> None:
    env_payload = _load_toml(PROJECT_ROOT / ".codex" / "environments" / "environment.toml")
    assert env_payload["runtime"]["preferred_python"] == ".\\.venv\\Scripts\\python.exe"

    agent_files = sorted((PROJECT_ROOT / ".codex" / "agents").glob("*.toml"))
    assert any(path.name == "regulatory-curator.toml" for path in agent_files)
    for path in agent_files:
        payload = _load_toml(path)
        assert "classification impact" in payload["developer_instructions"]


def test_skill_and_obsidian_assets_exist() -> None:
    expected_skills = {
        "classification-governance",
        "source-authority-audit",
        "regulation-unit-splitting",
        "web-clip-intake",
        "obsidian-dashboard",
        "marp-publish",
    }
    actual_skills = {path.name for path in (PROJECT_ROOT / ".agents" / "skills").iterdir() if path.is_dir()}
    assert expected_skills <= actual_skills

    community_plugins = yaml.safe_load((PROJECT_ROOT / ".obsidian" / "community-plugins.json").read_text(encoding="utf-8"))
    assert "dataview" in community_plugins


def test_taxonomy_and_schema_assets_exist() -> None:
    for rel in (
        "taxonomy/phase_registry.yaml",
        "taxonomy/functional_domains.yaml",
        "taxonomy/in_crash_browse_buckets.yaml",
        "taxonomy/compat_active_safety_v1.yaml",
        "taxonomy/compat_passive_buckets_v1.yaml",
        "taxonomy/crosswalk_v1_to_v2.yaml",
        "schemas/regulation_unit.schema.json",
        "schemas/note_frontmatter.schema.json",
        "sources/authority_registry.yaml",
        "sources/document_inventory.csv",
        "docs/operations/notes/generated-surfaces.md",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel


def test_graph_baseline_assets_exist() -> None:
    for rel in (
        "taxonomy/regulatory_connectivity.yaml",
        "tools/build_obsidian_graph_layer.py",
        "harness/scripts/check_generated_surfaces.py",
        "docs/operations/notes/generated-surfaces.md",
        "docs/obsidian_graph_validation.md",
        "docs/obsidian_graph_coverage_matrix.md",
        "docs/obsidian_graph_attach_readiness.md",
        "wiki/indexes/graph-home.md",
        "wiki/indexes/current-wiki-visualization.md",
        "wiki/indexes/graph-cluster-occupant-protection.md",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel


def test_reclassification_pilot_assets_exist_and_are_complete() -> None:
    csv_path = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_20_document_set.csv"
    jsonl_path = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_20_document_adjudications.jsonl"
    unit_csv_path = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_20_unit_samples.csv"
    unit_jsonl_path = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_20_unit_adjudications.jsonl"
    decision_table = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_20_decision_table.md"
    dashboard_delta = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_dashboard_delta.md"
    unit_delta = PROJECT_ROOT / "docs" / "operations" / "pilot" / "reclassification_unit_vs_document_delta.md"
    kmvss_subset = PROJECT_ROOT / "docs" / "operations" / "pilot" / "representative_xml_kmvss_subset.csv"
    pdf_subset = PROJECT_ROOT / "docs" / "operations" / "pilot" / "representative_pdf_ece_subset.csv"
    kmvss_holdout = PROJECT_ROOT / "docs" / "operations" / "pilot" / "kmvss_holdout_set.csv"
    kmvss_negative = PROJECT_ROOT / "docs" / "operations" / "pilot" / "kmvss_negative_control_set.csv"
    kmvss_assumptions = PROJECT_ROOT / "docs" / "operations" / "pilot" / "kmvss_assumptions.md"
    kmvss_analysis = PROJECT_ROOT / "docs" / "operations" / "pilot" / "kmvss_classification_consumption_analysis.md"

    assert csv_path.exists()
    assert jsonl_path.exists()
    assert unit_csv_path.exists()
    assert unit_jsonl_path.exists()
    assert decision_table.exists()
    assert dashboard_delta.exists()
    assert unit_delta.exists()
    assert kmvss_subset.exists()
    assert pdf_subset.exists()
    assert kmvss_holdout.exists()
    assert kmvss_negative.exists()
    assert kmvss_assumptions.exists()
    assert kmvss_analysis.exists()

    csv_lines = [line for line in csv_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(csv_lines) == 21

    json_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(json_rows) == 20
    for row in json_rows:
        assert row["selected_phase"]
        assert row["rejected_alternative_phase"]
        assert row["selected_phase_rationale"]
        assert row["rejected_alternative_rationale"]

    unit_csv_lines = [line for line in unit_csv_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(unit_csv_lines) >= 61
    unit_rows = [json.loads(line) for line in unit_jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(unit_rows) >= 60
    for row in unit_rows:
        assert row["selected_phase"]
        assert row["rejected_alternative_phase"]
        assert row["selected_phase_rationale"]
        assert row["rejected_alternative_rationale"]

    decision_text = decision_table.read_text(encoding="utf-8")
    assert "document-level calibration" in decision_text
    assert "regulation_unit adjudication" in decision_text


def test_kmvss_attachment_round2a_assets_exist() -> None:
    for rel in (
        "docs/operations/pilot/kmvss_attachment_residual_buckets.md",
        "docs/operations/pilot/kmvss_attachment_parser_notes.md",
        "docs/operations/pilot/kmvss_attachment_taxonomy_policy.md",
        "docs/operations/pilot/kmvss_attachment_comparable_evaluation.md",
        "docs/operations/pilot/kmvss_attachment_top20_before_after.csv",
        "docs/operations/pilot/kmvss_round2a_fix_log.md",
        "harness/scripts/kmvss_attachment_residual_audit.py",
        "harness/scripts/kmvss_attachment_comparable_eval.py",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel


def test_kmvss_article_round2b_assets_exist() -> None:
    for rel in (
        "docs/operations/pilot/kmvss_article_residual_buckets_round2b.md",
        "docs/operations/pilot/kmvss_article_taxonomy_policy_round2b.md",
        "docs/operations/pilot/kmvss_article_comparable_evaluation_round2b.md",
        "docs/operations/pilot/kmvss_article_top20_before_after_round2b.csv",
        "docs/operations/pilot/kmvss_round2b_fix_log.md",
        "docs/operations/pilot/kmvss_article_fixture_manifest_round2b.md",
        "harness/scripts/kmvss_article_residual_audit.py",
        "harness/scripts/kmvss_article_comparable_eval.py",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel


def test_kmvss_round2c_assets_exist() -> None:
    for rel in (
        "docs/operations/pilot/kmvss_round2c_repo_reference_map.md",
        "docs/operations/pilot/kmvss_round2c_residual_triage.md",
        "docs/operations/pilot/kmvss_round2c_review_lane_policy.md",
        "docs/operations/pilot/kmvss_round2c_review_lane_register.csv",
        "docs/operations/pilot/kmvss_round2c_comparable_evaluation.md",
        "docs/operations/pilot/kmvss_round2c_top20_before_after.csv",
        "docs/operations/pilot/kmvss_round2c_fix_log.md",
        "docs/operations/pilot/kmvss_round2c_adjudications.jsonl",
        "docs/operations/pilot/kmvss_round2c_trace_diff_summary.md",
        "docs/operations/pilot/kmvss_round2c_fixture_manifest.md",
        "harness/scripts/kmvss_round2c_triage.py",
        "harness/scripts/kmvss_round2c_comparable_eval.py",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel


def test_kmvss_round2d_assets_exist() -> None:
    for rel in (
        "docs/operations/pilot/kmvss_round2d_fix_log.md",
        "docs/operations/pilot/kmvss_round2d_repo_reference_delta.md",
        "docs/operations/pilot/kmvss_round2d_secondary_umbrella_audit.md",
        "docs/operations/pilot/kmvss_round2d_secondary_umbrella_register.csv",
        "docs/operations/pilot/kmvss_round2d_review_lane_promotion_policy.md",
        "docs/operations/pilot/kmvss_round2d_comparable_evaluation.md",
        "docs/operations/pilot/kmvss_round2d_top20_before_after.csv",
        "docs/operations/pilot/kmvss_round2d_trace_diff_summary.md",
        "docs/operations/pilot/kmvss_round2d_adjudications.jsonl",
        "docs/operations/pilot/kmvss_round2d_fixture_manifest.md",
        "harness/scripts/kmvss_round2d_secondary_umbrella_audit.py",
        "harness/scripts/kmvss_round2d_comparable_eval.py",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel
