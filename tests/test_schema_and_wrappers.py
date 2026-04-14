from __future__ import annotations

from pathlib import Path

import yaml

from wiki_obsidian.schema_service import schema_validate


def test_schema_validate_fails_on_missing_provenance(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    for rel in (
        "wiki/regulation_units",
        "schemas",
        "artifacts/reports/runs",
    ):
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[1]
    for rel in ("schemas/note_frontmatter.schema.json", "schemas/regulation_unit.schema.json"):
        (project_root / rel).write_text((repo_root / rel).read_text(encoding="utf-8"), encoding="utf-8")

    (project_root / "wiki" / "regulation_units" / "bad.md").write_text(
        """---
record_layer: knowledge
id: bad-unit
note_type: regulation_unit
title: Bad Unit
summary: Missing provenance.
status: draft
created: 2026-04-13
updated: 2026-04-13
jurisdiction: US
source_collection: xml_fmvss
regulatory_layer: technical_requirement
phase: pre_crash
functional_domain:
  - crash_avoidance_and_vehicle_control
primary_topic: pedestrian_aeb
secondary_topics: []
browse_buckets: []
legacy_domain: active_safety
aliases: []
effective_date:
confidence: medium
---
# Bad Unit
""",
        encoding="utf-8",
    )

    payload = schema_validate(project_root=project_root, run_id="schema-1")
    assert payload["status"] == "failed"
    assert payload["errors"]


def test_tooling_fallback_messages_are_documented() -> None:
    tooling = yaml.safe_load((Path(__file__).resolve().parents[1] / "configs" / "tools" / "tooling.yaml").read_text(encoding="utf-8"))
    assert "fallback_message" in tooling["tools"]["qmd"]
    assert "fallback_message" in tooling["tools"]["marp"]


def test_verify_wrapper_delegates_to_cli_verify() -> None:
    wrapper = (Path(__file__).resolve().parents[1] / "scripts" / "wiki.ps1").read_text(encoding="utf-8")
    assert '& $VenvPython -m wiki_obsidian.cli verify | Out-Host' in wrapper
    assert '"graph-refresh"' in wrapper
