from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


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
effective_date:
confidence: medium
source_files:
  - raw/collections/demo/sample.txt
source_hashes:
  raw/collections/demo/sample.txt: "{raw_hash}"
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
effective_date:
confidence: medium
source_files:
  - raw/collections/demo/sample.txt
source_hashes:
  raw/collections/demo/sample.txt: "{raw_hash}"
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
