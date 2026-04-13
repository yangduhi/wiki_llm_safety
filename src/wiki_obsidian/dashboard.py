from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_text
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.ids import build_run_id


def dashboard_refresh(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("dashboard")
    ensure_dir(settings.paths.operations_dashboards_root)

    notes = _load_notes(settings.paths.wiki_root)
    written_files = [
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-jurisdiction.md",
            "Coverage by Jurisdiction",
            _counter_lines("jurisdiction", Counter(_scalar(note, "jurisdiction") for note in notes)),
            'TABLE jurisdiction, count(rows) AS notes\nFROM "wiki/regulation_units"\nGROUP BY jurisdiction\nSORT jurisdiction ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-phase.md",
            "Coverage by Phase",
            _counter_lines("phase", Counter(_scalar(note, "phase") for note in notes)),
            'TABLE phase, count(rows) AS notes\nFROM "wiki/regulation_units"\nGROUP BY phase\nSORT phase ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-functional-domain.md",
            "Coverage by Functional Domain",
            _flatten_counter_lines("functional_domain", _list_counter(notes, "functional_domain")),
            'TABLE value AS functional_domain, length(rows) AS notes\nFROM "wiki/regulation_units"\nFLATTEN functional_domain AS value\nGROUP BY value\nSORT value ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "in-crash-browse-buckets.md",
            "In-crash Browse Buckets",
            _flatten_counter_lines("browse_bucket", _list_counter(notes, "browse_buckets")),
            'TABLE value AS browse_bucket, length(rows) AS notes\nFROM "wiki/regulation_units"\nWHERE phase = "in_crash"\nFLATTEN browse_buckets AS value\nGROUP BY value\nSORT value ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "needs-review-queue.md",
            "Needs Review Queue",
            _review_lines(notes),
            'TABLE file.link, title, legacy_domain, confidence\nFROM "wiki"\nWHERE legacy_domain = "needs_review" OR confidence = "low"\nSORT file.mtime DESC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "missing-provenance.md",
            "Missing Provenance",
            _missing_provenance_lines(notes),
            'TABLE file.link, title\nFROM "wiki"\nWHERE !provenance OR length(provenance.source_files) = 0',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "recently-changed-notes.md",
            "Recently Changed Notes",
            _recent_lines(notes),
            'TABLE file.link, updated, phase, primary_topic\nFROM "wiki/regulation_units"\nSORT updated DESC\nLIMIT 25',
        ),
    ]

    return {
        "run_id": active_run_id,
        "status": "refreshed",
        "written_files": [str(path) for path in written_files],
    }


def _load_notes(wiki_root: Path) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        if str(frontmatter.get("record_layer") or "") != "knowledge":
            continue
        notes.append(frontmatter)
    return notes


def _scalar(frontmatter: dict[str, Any], key: str) -> str:
    value = frontmatter.get(key)
    return str(value or "unknown")


def _list_counter(notes: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for note in notes:
        for value in note.get(key) or []:
            counter[str(value)] += 1
    return counter


def _counter_lines(label: str, counter: Counter[str]) -> list[str]:
    return [f"- {label}: `{key}` -> {value}" for key, value in sorted(counter.items())]


def _flatten_counter_lines(label: str, counter: Counter[str]) -> list[str]:
    return [f"- {label}: `{key}` -> {value}" for key, value in sorted(counter.items())]


def _review_lines(notes: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for note in notes:
        if note.get("legacy_domain") == "needs_review" or note.get("confidence") == "low":
            lines.append(f"- `{note.get('id')}` | {note.get('title')}")
    return lines or ["- None."]


def _missing_provenance_lines(notes: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for note in notes:
        provenance = note.get("provenance") or {}
        if not isinstance(provenance, dict) or not (provenance.get("source_files") or []):
            lines.append(f"- `{note.get('id')}` | {note.get('title')}")
    return lines or ["- None."]


def _recent_lines(notes: list[dict[str, Any]]) -> list[str]:
    sorted_notes = sorted(notes, key=lambda note: str(note.get("updated") or ""), reverse=True)
    return [
        f"- `{note.get('updated')}` | `{note.get('id')}` | {note.get('title')}"
        for note in sorted_notes[:25]
    ] or ["- None."]


def _write_dashboard(path: Path, title: str, bullet_lines: list[str], dataview_query: str) -> Path:
    body = [
        f"# {title}",
        "",
        "## Snapshot",
    ]
    body.extend(bullet_lines or ["- None."])
    body.extend(
        [
            "",
            "## Dataview",
            "```dataview",
            dataview_query,
            "```",
            "",
        ]
    )
    return write_text(path, "\n".join(body))
