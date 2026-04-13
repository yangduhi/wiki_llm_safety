from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.ids import build_run_id


def schema_validate(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("schema-validate")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)

    base_schema = json.loads(settings.paths.note_frontmatter_schema.read_text(encoding="utf-8"))
    unit_schema = json.loads(settings.paths.regulation_unit_schema.read_text(encoding="utf-8"))
    base_validator = Draft202012Validator(base_schema)
    unit_validator = Draft202012Validator(unit_schema)

    errors: list[str] = []
    checked_files: list[str] = []
    for path in sorted(settings.paths.wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        rel = str(path.relative_to(settings.paths.project_root)).replace("\\", "/")
        checked_files.append(rel)
        for error in base_validator.iter_errors(frontmatter):
            errors.append(f"{rel}: {error.message}")
        if str(frontmatter.get("note_type") or "") == "regulation_unit":
            for error in unit_validator.iter_errors(frontmatter):
                errors.append(f"{rel}: {error.message}")

    payload = {
        "run_id": active_run_id,
        "status": "passed" if not errors else "failed",
        "checked_files": checked_files,
        "errors": errors,
    }
    report_path = write_json(reports_root / "schema_validate_report.json", payload)
    return payload | {"report_path": str(report_path)}
