from __future__ import annotations

import hashlib
from pathlib import Path

from wiki_obsidian.classification import classify_text
from wiki_obsidian.dashboard import dashboard_refresh
from wiki_obsidian.ingest.service import ingest_wiki
from wiki_obsidian.normalize.service import normalize_collection
from wiki_obsidian.parse.service import parse_collection
from wiki_obsidian.query.service import query_writeback
from wiki_obsidian.source_audit import source_audit


def _write_common_project_layout(project_root: Path) -> None:
    for rel in (
        "raw/collections/xml_fmvss",
        "raw/collections/web_clipper",
        "raw/collections/official_web",
        "configs/collections/xml_fmvss",
        "configs/collections/web_clipper",
        "configs/collections/official_web",
        "configs/wiki",
        "taxonomy",
        "schemas",
        "sources",
        "artifacts/reports/runs",
        "wiki/regulation_documents",
        "wiki/regulation_units",
        "wiki/jurisdictions",
        "wiki/analyses",
        "docs/operations/notes",
        "docs/operations/plans",
        "docs/operations/dashboards",
        "docs/architecture/adr",
    ):
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    (project_root / "index.md").write_text("# Index\n", encoding="utf-8")
    (project_root / "log.md").write_text("# Log\n", encoding="utf-8")
    (project_root / "docs" / "operations" / "LOG.md").write_text("# Operations Log\n", encoding="utf-8")
    (project_root / "configs" / "wiki" / "taxonomy.yaml").write_text(
        (Path(__file__).resolve().parents[1] / "configs" / "wiki" / "taxonomy.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in (
        "taxonomy/phase_registry.yaml",
        "taxonomy/functional_domains.yaml",
        "taxonomy/in_crash_browse_buckets.yaml",
        "schemas/note_frontmatter.schema.json",
        "schemas/regulation_unit.schema.json",
        "sources/authority_registry.yaml",
        "sources/document_inventory.csv",
    ):
        src = Path(__file__).resolve().parents[1] / rel
        (project_root / rel).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    for idx, name in enumerate(
        (
            "ADR-0001-classification-model.md",
            "ADR-0002-regulation-unit-granularity.md",
            "ADR-0003-authoritative-source-policy.md",
            "ADR-0004-obsidian-note-contract.md",
        ),
        start=1,
    ):
        src = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "adr" / name
        (project_root / "docs" / "architecture" / "adr" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    (project_root / "configs" / "collections" / "xml_fmvss" / "profile.yaml").write_text(
        """collection_id: xml_fmvss
collection_kind: regulatory-xml-section
input_root: raw/collections/xml_fmvss
parser_mode: xml_fmvss_section
language: en
review_defaults:
  source_summary: false
  claim: false
jurisdiction: US
regulatory_layer: technical_requirement
source_classes: [xml_fmvss]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "web_clipper" / "profile.yaml").write_text(
        """collection_id: web_clipper
collection_kind: markdown-intake
input_root: raw/collections/web_clipper
parser_mode: markdown_clip
language: en
review_defaults:
  source_summary: true
  claim: true
jurisdiction: US
regulatory_layer: technical_requirement
source_classes: [web_clipper]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "official_web" / "profile.yaml").write_text(
        """collection_id: official_web
collection_kind: official-web-snapshot
input_root: raw/collections/official_web
parser_mode: official_web_capture
language: en
review_defaults:
  source_summary: true
  claim: true
jurisdiction: US
regulatory_layer: framework_admin
source_classes: [official_web]
""",
        encoding="utf-8",
    )


def test_pipeline_and_raw_immutability(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)

    raw_path = project_root / "raw" / "collections" / "xml_fmvss" / "571.208.xml"
    raw_path.write_text(
        '<?xml version="1.0"?><DIV8><HEAD>FMVSS 208 Occupant Crash Protection</HEAD><P>S1. Occupant crash protection.</P></DIV8>',
        encoding="utf-8",
    )
    before_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    parse_payload = parse_collection(project_root=project_root, collection="xml_fmvss", run_id="run-1")
    normalize_payload = normalize_collection(project_root=project_root, collection="xml_fmvss", run_id="run-1")
    ingest_payload = ingest_wiki(project_root=project_root, collection="xml_fmvss", run_id="run-1")

    after_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert before_hash == after_hash
    assert parse_payload["document_count"] == 1
    assert normalize_payload["unit_count"] >= 1
    assert ingest_payload["pages_written"] >= 2

    payload = query_writeback(project_root=project_root, question="Occupant crash protection", writeback=True, run_id="run-2")
    assert payload["analysis_written"] is True


def test_dashboard_refresh_and_source_audit(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    clip_path = project_root / "raw" / "collections" / "web_clipper" / "pedestrian-aeb.md"
    clip_path.write_text("# AEB for Pedestrian\nAEB for pedestrian and VRU response.\n", encoding="utf-8")
    html_path = project_root / "raw" / "collections" / "official_web" / "fmvss-landing.html"
    html_path.write_text("<html><head><title>FMVSS Landing</title></head><body><h1>FMVSS Landing</h1></body></html>", encoding="utf-8")

    ingest_wiki(project_root=project_root, collection="web_clipper", run_id="run-clip")
    dashboard_payload = dashboard_refresh(project_root=project_root, run_id="run-dashboard")
    audit_payload = source_audit(project_root=project_root, run_id="run-audit", write_baseline=True)

    assert dashboard_payload["status"] == "refreshed"
    assert audit_payload["baseline_written"] is True
    assert (project_root / "docs" / "operations" / "dashboards" / "coverage-by-phase.md").exists()


def test_gold_case_classification() -> None:
    assert classify_text("AEB for Pedestrian")["phase"] == "pre_crash"
    assert classify_text("AEB for Pedestrian")["legacy_domain"] == "active_safety"
    assert classify_text("FMVSS 208 Occupant Crash Protection")["phase"] == "in_crash"
    assert classify_text("FMVSS 208 Occupant Crash Protection")["primary_topic"] == "frontal_impact"
    assert classify_text("Door retention")["phase"] == "in_crash"
    assert classify_text("Post-crash egress")["phase"] == "post_crash"
    assert classify_text("Windscreen visibility and glazing retention")["phase"] == "cross_phase"
