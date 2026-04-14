from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml


def test_harness_scripts_pass_on_valid_fixture(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    for rel in (
        "configs/wiki",
        "taxonomy",
        "schemas",
        "wiki/regulation_units",
        "wiki/regulation_documents",
        "docs/operations/notes",
        "docs/operations/plans",
        "docs/operations/dashboards",
        "docs/operations/pilot",
        "docs/architecture/adr",
        "sources",
        "raw/collections/demo",
    ):
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    (project_root / "index.md").write_text("# Index\n", encoding="utf-8")
    (project_root / "log.md").write_text("# Log\n", encoding="utf-8")
    (project_root / "docs" / "operations" / "LOG.md").write_text("# Operations Log\n", encoding="utf-8")

    (project_root / "configs" / "wiki" / "taxonomy.yaml").write_text(
        """types:
  regulation_document:
    dir: regulation_documents
    index_section: Regulation Documents
    required_headings: ["## Snapshot", "## Source Details", "## Canonical Classification", "## Authority", "## Related Units"]
  regulation_unit:
    dir: regulation_units
    index_section: Regulation Units
    compact: true
    required_headings: ["## Statement", "## Classification", "## Basis", "## Authority", "## Related Notes"]
  concept_node:
    dir: concepts
    index_section: Concept Nodes
    required_headings: ["## Definition", "## Classification Role", "## Evidence", "## Related Notes"]
  jurisdiction_overview:
    dir: jurisdictions
    index_section: Jurisdictions
    required_headings: ["## Snapshot", "## Source Landscape", "## Phase Coverage", "## Related Notes"]
  analysis:
    dir: analyses
    index_section: Analyses
    required_headings: ["## Question", "## Answer", "## Evidence", "## Counterarguments or Alternatives"]
""",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "phase_registry.yaml").write_text(
        "phases:\n- id: pre_crash\n- id: in_crash\n- id: post_crash\n- id: cross_phase\n- id: non_phase_admin\n",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "functional_domains.yaml").write_text(
        "functional_domains:\n- id: crash_avoidance_and_vehicle_control\n- id: occupant_protection_and_restraints\n- id: other_or_review\n",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "in_crash_browse_buckets.yaml").write_text(
        """browse_buckets:
- bucket_id: frontal_impact
- bucket_id: side_impact
- bucket_id: rear_impact
- bucket_id: rollover
- bucket_id: occupant_restraints
- bucket_id: occupant_compartment_integrity
- bucket_id: door_retention
- bucket_id: anti_ejection
- bucket_id: head_impact
- bucket_id: child_restraints
- bucket_id: seat_systems
- bucket_id: steering_control
- bucket_id: glazing_retention
- bucket_id: fuel_system_integrity
- bucket_id: fire_risk
- bucket_id: pedestrian_protection
""",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "compat_active_safety_v1.yaml").write_text(
        "registry_version: v1\nlegacy_domain: active_safety\nfeatures:\n- aeb\n",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "compat_passive_buckets_v1.yaml").write_text(
        "registry_version: v1\nlegacy_domain: passive_crash\nbrowse_buckets:\n- frontal_impact\n",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "crosswalk_v1_to_v2.yaml").write_text(
        "crosswalks:\n- legacy_value: active_safety\n  canonical_phase: pre_crash\n  canonical_functional_domain: crash_avoidance_and_vehicle_control\n",
        encoding="utf-8",
    )
    (project_root / "taxonomy" / "kmvss_signal_lexicon.yaml").write_text(
        "version: 1\nphase_signals:\n  pre_crash: {title: [자율주행], body: [경고]}\n  in_crash: {title: [충돌], body: [안전띠]}\n  post_crash: {title: [구동축전지], body: [고전압]}\n  non_phase_admin: {title: [특례], body: [고시]}\ndomain_signals:\n  crash_avoidance_and_vehicle_control: {title: [자율주행], body: [경고]}\n  other_or_review: {title: [특례], body: [고시]}\ntopic_aliases:\n  automated_driving_assist: [자율주행]\nweak_title_priors:\n  제동장치:\n    phase: {pre_crash: 2, in_crash: 1}\n    domain: {crash_avoidance_and_vehicle_control: 2}\n",
        encoding="utf-8",
    )
    (project_root / "schemas" / "note_frontmatter.schema.json").write_text(
        json.dumps({"type": "object", "required": ["record_layer", "id", "note_type"]}),
        encoding="utf-8",
    )
    (project_root / "schemas" / "regulation_unit.schema.json").write_text(
        json.dumps({"type": "object", "required": ["phase", "functional_domain"]}),
        encoding="utf-8",
    )
    (project_root / "sources" / "authority_registry.yaml").write_text(
        "sources:\n- source_id: demo\n  jurisdiction: US\n  title: Demo\n  source_type: official_web\n  official_status: primary_official\n  original_url: https://example.com\n  snapshot_date: 2026-04-13\n  effective_date:\n  parser_strategy: html\n  checksum: pending\n  notes: demo\n",
        encoding="utf-8",
    )
    (project_root / "sources" / "document_inventory.csv").write_text(
        "source_id,jurisdiction,title,source_type,official_status,original_url,snapshot_date,effective_date,parser_strategy,checksum,notes\n"
        "demo,US,Demo,official_web,primary_official,https://example.com,2026-04-13,,html,pending,demo\n",
        encoding="utf-8",
    )
    for idx, name in enumerate(
        (
            "ADR-0001-classification-model.md",
            "ADR-0002-regulation-unit-granularity.md",
            "ADR-0003-authoritative-source-policy.md",
            "ADR-0004-obsidian-note-contract.md",
        ),
        start=1,
    ):
        (project_root / "docs" / "architecture" / "adr" / name).write_text(
            f"---\nrecord_layer: operations\nid: adr-{idx}\ntitle: {name}\nsummary: x\nstatus: active\ncreated: 2026-04-13\nupdated: 2026-04-13\ntags:\n  - operations\n---\n\n# {name}\n",
            encoding="utf-8",
        )
    (project_root / "docs" / "operations" / "notes" / "generated-surfaces.md").write_text(
        "---\nrecord_layer: operations\nid: generated-surfaces\ntitle: Generated Surfaces\nsummary: x\nstatus: active\ncreated: 2026-04-13\nupdated: 2026-04-13\ntags:\n  - operations\n---\n\n# Generated Surfaces\n",
        encoding="utf-8",
    )
    calibration_csv = [
        "calibration_id,jurisdiction,document_title,source_citation,authority_source,selected_phase,rejected_alternative_phase,expected_functional_domain,expected_primary_topic,confidence,selection_note"
    ]
    calibration_jsonl = []
    unit_csv = [
        "calibration_id,unit_sample_id,unit_label,source_locator,document_selected_phase,selected_phase,rejected_alternative_phase,authority_source,note"
    ]
    unit_jsonl = []
    for idx in range(20):
        calibration_id = f"demo-{idx}"
        calibration_csv.append(
            f"{calibration_id},US,Demo {idx},Demo citation {idx},https://example.com/{idx},pre_crash,cross_phase,crash_avoidance_and_vehicle_control,demo_topic,0.9,demo"
        )
        calibration_jsonl.append(
            json.dumps(
                {
                    "calibration_id": calibration_id,
                    "current_phase": "cross_phase",
                    "selected_phase": "pre_crash",
                    "rejected_alternative_phase": "cross_phase",
                    "selected_phase_rationale": "demo",
                    "rejected_alternative_rationale": "demo",
                }
            )
        )
        for unit_idx in range(3):
            unit_csv.append(
                f"{calibration_id},{calibration_id}-u{unit_idx},Demo unit {unit_idx},clause,pre_crash,pre_crash,cross_phase,https://example.com/{idx},demo"
            )
            unit_jsonl.append(
                json.dumps(
                    {
                        "calibration_id": calibration_id,
                        "unit_sample_id": f"{calibration_id}-u{unit_idx}",
                        "selected_phase": "pre_crash",
                        "rejected_alternative_phase": "cross_phase",
                        "selected_phase_rationale": "demo",
                        "rejected_alternative_rationale": "demo",
                    }
                )
            )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_document_set.csv").write_text(
        "\n".join(calibration_csv) + "\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_document_adjudications.jsonl").write_text(
        "\n".join(calibration_jsonl) + "\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_unit_samples.csv").write_text(
        "\n".join(unit_csv) + "\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_unit_adjudications.jsonl").write_text(
        "\n".join(unit_jsonl) + "\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_decision_table.md").write_text(
        "# Decision Table\n\ndocument-level calibration is for entry classification only; canonical phase stabilization is governed by regulation_unit adjudication.\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_dashboard_delta.md").write_text(
        "# Dashboard Delta\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_unit_vs_document_delta.md").write_text(
        "# Unit vs Document Delta\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "representative_xml_kmvss_subset.csv").write_text(
        "subset_id,collection,raw_file,intended_phase,intended_functional_domain,rationale\ndemo,xml_kmvss,demo.xml,post_crash,fire_electrical_and_energy_storage_safety,demo\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "representative_pdf_ece_subset.csv").write_text(
        "subset_id,collection,raw_file,intended_phase,intended_functional_domain,rationale\ndemo,pdf_ece,demo.pdf,post_crash,fire_electrical_and_energy_storage_safety,demo\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "kmvss_holdout_set.csv").write_text(
        "holdout_id,raw_file,expected_phase,expected_functional_domain,rationale\ndemo,demo.xml,post_crash,other_or_review,demo\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "kmvss_negative_control_set.csv").write_text(
        "control_id,source,expected_phase,expected_functional_domain,rationale\ndemo,Demo,pre_crash,crash_avoidance_and_vehicle_control,demo\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "kmvss_assumptions.md").write_text(
        "# KMVSS Assumptions\n",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "kmvss_classification_consumption_analysis.md").write_text(
        "# KMVSS Analysis\n",
        encoding="utf-8",
    )

    raw_path = project_root / "raw" / "collections" / "demo" / "sample.txt"
    raw_path.write_text("sample source\n", encoding="utf-8")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    (project_root / "artifacts" / "manifests").mkdir(parents=True)
    (project_root / "artifacts" / "manifests" / "raw_manifest_baseline.json").write_text(
        json.dumps([{"path": "raw/collections/demo/sample.txt", "sha256": raw_hash}], indent=2),
        encoding="utf-8",
    )

    page = f"""---
record_layer: knowledge
id: demo-unit
note_type: regulation_unit
title: Demo unit
summary: A valid regulation unit.
status: draft
created: 2026-04-13
updated: 2026-04-13
jurisdiction: US
source_collection: demo
regulatory_layer: technical_requirement
phase: pre_crash
functional_domain:
  - crash_avoidance_and_vehicle_control
primary_topic: pedestrian_aeb
secondary_topics:
  - pedestrian
browse_buckets: []
legacy_domain: active_safety
aliases: []
provenance:
  source_files:
    - raw/collections/demo/sample.txt
  source_hashes:
    raw/collections/demo/sample.txt: "{raw_hash}"
source_url: https://example.com/demo
source_citation: Demo sample
effective_date:
confidence: medium
statement: Demo
basis: Demo basis
document_id: demo-doc
clause_path: s1
---
# Demo unit

## Statement
Demo

## Classification
- x

## Basis
Demo basis

## Authority
- source

## Related Notes
- [[regulation_documents/demo-doc]]
"""
    (project_root / "wiki" / "regulation_units" / "demo-unit.md").write_text(page, encoding="utf-8")
    (project_root / "wiki" / "regulation_documents" / "demo-doc.md").write_text(
        f"""---
record_layer: knowledge
id: demo-doc
note_type: regulation_document
title: Demo document
summary: Supporting regulation document.
status: draft
created: 2026-04-13
updated: 2026-04-13
jurisdiction: US
source_collection: demo
regulatory_layer: technical_requirement
phase: pre_crash
functional_domain:
  - crash_avoidance_and_vehicle_control
primary_topic: pedestrian_aeb
secondary_topics:
  - pedestrian
browse_buckets: []
legacy_domain: active_safety
aliases: []
provenance:
  source_files:
    - raw/collections/demo/sample.txt
  source_hashes:
    raw/collections/demo/sample.txt: "{raw_hash}"
source_url: https://example.com/demo
source_citation: Demo sample
effective_date:
confidence: medium
document_id: demo-doc
---
# Demo document

## Snapshot
- x

## Source Details
- x

## Canonical Classification
- x

## Authority
- x

## Related Units
- [[regulation_units/demo-unit]]
""",
        encoding="utf-8",
    )

    scripts_root = Path(__file__).resolve().parents[1] / "harness" / "scripts"
    for script_name in (
        "check_frontmatter.py",
        "check_wikilinks.py",
        "check_provenance.py",
        "check_layer_boundaries.py",
        "check_note_ids.py",
        "check_raw_immutability.py",
        "build_index.py",
        "build_operations_index.py",
        "check_design_package.py",
    ):
        completed = subprocess.run(
            [sys.executable, str(scripts_root / script_name), "--project-root", str(project_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr


def _load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_graph_layer_browse_index_frontmatter_contract(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    (project_root / "wiki" / "indexes").mkdir(parents=True, exist_ok=True)
    (project_root / "wiki" / "regulation_documents").mkdir(parents=True, exist_ok=True)
    (project_root / "wiki" / "regulation_units").mkdir(parents=True, exist_ok=True)

    tool_module = _load_module(
        Path(__file__).resolve().parents[1] / "tools" / "build_obsidian_graph_layer.py",
        "build_obsidian_graph_layer_test",
    )
    frontmatter_module = _load_module(
        Path(__file__).resolve().parents[1] / "harness" / "scripts" / "check_frontmatter.py",
        "check_frontmatter_test",
    )

    rendered = tool_module.build_current_wiki_visualization(project_root)
    frontmatter, _body = tool_module.parse_frontmatter_text(rendered)

    assert frontmatter["record_layer"] == "knowledge"
    assert frontmatter["note_type"] == "browse_index"
    assert frontmatter["browse_axis"] == "visualization"
    assert frontmatter["status"] in frontmatter_module.STATUS_VALUES
    assert frontmatter["status"] == tool_module.GENERATED_BROWSE_INDEX_STATUS
    assert frontmatter["provenance"]["source_files"] == []
    assert frontmatter["provenance"]["source_hashes"] == {}
    assert isinstance(frontmatter["aliases"], list)
