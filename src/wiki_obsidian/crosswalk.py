from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json, write_text
from wiki_obsidian.utils.frontmatter import render_frontmatter
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.ids import build_run_id


def build_crosswalk(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("crosswalk")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    mapping = yaml.safe_load((settings.paths.taxonomy_root / "crosswalk_v1_to_v2.yaml").read_text(encoding="utf-8")) or {}
    notes = _load_regulation_units(settings.paths.regulation_units_root)
    by_legacy = Counter(str(note.get("legacy_domain") or "unknown") for note in notes)
    by_phase = Counter(str(note.get("phase") or "unknown") for note in notes)

    md_path = settings.paths.crosswalks_root / "compatibility-crosswalk.md"
    frontmatter = {
        "record_layer": "knowledge",
        "id": "crosswalk-compatibility-v1-to-v2",
        "note_type": "crosswalk",
        "title": "Compatibility Crosswalk",
        "summary": "Maps legacy compatibility domains to canonical v2 classification and records current note counts.",
        "status": "draft",
        "created": "2026-04-13",
        "updated": "2026-04-13",
        "aliases": [],
        "provenance": {"source_files": [], "source_hashes": {}, "parser_run_id": active_run_id},
        "confidence": "medium",
    }
    write_text(
        md_path,
        "\n".join(
            [
                render_frontmatter(frontmatter),
                "# Compatibility Crosswalk",
                "",
                "## Mapping Rules",
                *[
                    f"- `{row['legacy_value']}` -> `{row['canonical_phase']}` / `{row['canonical_functional_domain']}`"
                    for row in mapping.get("crosswalks") or []
                    if isinstance(row, dict)
                ],
                "",
                "## Current Note Counts By Legacy Domain",
                *[f"- `{key}` -> {value}" for key, value in sorted(by_legacy.items())],
                "",
                "## Current Note Counts By Phase",
                *[f"- `{key}` -> {value}" for key, value in sorted(by_phase.items())],
                "",
            ]
        ),
    )
    payload = {
        "run_id": active_run_id,
        "crosswalk_file": str(md_path),
        "legacy_counts": dict(sorted(by_legacy.items())),
        "phase_counts": dict(sorted(by_phase.items())),
    }
    report_path = write_json(reports_root / "crosswalk_report.json", payload)
    return payload | {"report_path": str(report_path)}


def _load_regulation_units(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*.md")):
        if path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        rows.append(frontmatter)
    return rows
