from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import subprocess
import sys
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_text
from wiki_obsidian.utils.frontmatter import render_frontmatter
from wiki_obsidian.utils.text import slugify


def append_knowledge_log(
    *,
    title: str,
    details: list[str],
    project_root: str | Path | None = None,
    operation: str,
) -> Path:
    settings = load_project_settings(project_root)
    return _append_log(
        log_path=settings.paths.root_log,
        title=title,
        details=details,
        operation=operation,
    )


def append_operations_log(
    *,
    title: str,
    details: list[str],
    project_root: str | Path | None = None,
    operation: str,
) -> Path:
    settings = load_project_settings(project_root)
    return _append_log(
        log_path=settings.paths.operations_log,
        title=title,
        details=details,
        operation=operation,
    )


def write_operation_note(
    *,
    title: str,
    summary: str,
    body_sections: list[str],
    project_root: str | Path | None = None,
    slug: str | None = None,
    note_id: str | None = None,
) -> Path:
    settings = load_project_settings(project_root)
    target = settings.paths.operations_notes_root / f"{slug or slugify(title)}.md"
    frontmatter = {
        "record_layer": "operations",
        "id": note_id or f"operations-{slugify(title)}",
        "title": title,
        "summary": summary,
        "status": "active",
        "created": datetime.now(UTC).strftime("%Y-%m-%d"),
        "updated": datetime.now(UTC).strftime("%Y-%m-%d"),
        "tags": ["operations"],
    }
    content = [render_frontmatter(frontmatter), f"# {title}", ""]
    content.extend(body_sections)
    return write_text(target, "\n".join(content).rstrip() + "\n")


def _append_log(*, log_path: Path, title: str, details: list[str], operation: str) -> Path:
    ensure_dir(log_path.parent)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d")
    existing = log_path.read_text(encoding="utf-8").rstrip() if log_path.exists() else ""
    lines = [existing] if existing else []
    if lines:
        lines.append("")
    lines.append(f"## [{timestamp}] {operation} | {title}")
    lines.extend(details)
    lines.append("")
    return write_text(log_path, "\n".join(lines))


def rebuild_indexes(*, project_root: str | Path | None = None, include_operations: bool = True) -> None:
    settings = load_project_settings(project_root)
    _run_harness_script(settings.paths.project_root, "build_index.py")
    if include_operations:
        _run_harness_script(settings.paths.project_root, "build_operations_index.py")


def _run_harness_script(project_root: Path, script_name: str) -> None:
    script_path = project_root / "harness" / "scripts" / script_name
    if not script_path.exists():
        return
    subprocess.run(
        [sys.executable, str(script_path), "--project-root", str(project_root)],
        check=True,
        cwd=project_root,
    )

