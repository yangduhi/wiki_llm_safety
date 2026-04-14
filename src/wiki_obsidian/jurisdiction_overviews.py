from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import write_text
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file, render_frontmatter

EXCLUDE_FILENAMES = {"README.md", ".gitkeep"}


def refresh_jurisdiction_overviews(
    *,
    project_root: str | Path | None = None,
    run_id: str,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    documents = _load_notes(settings.paths.regulation_documents_root, note_type="regulation_document")
    visible_units = [
        row
        for row in _load_notes(settings.paths.regulation_units_root, note_type="regulation_unit")
        if not _is_pseudo_document_unit(row["frontmatter"])
    ]

    jurisdictions = sorted(
        {
            str(row["frontmatter"].get("jurisdiction") or "").strip()
            for row in [*documents, *visible_units]
            if str(row["frontmatter"].get("jurisdiction") or "").strip()
        }
    )

    expected_paths: set[Path] = set()
    written_files: list[str] = []
    removed_files: list[str] = []
    generated_on = _today()

    for jurisdiction in jurisdictions:
        documents_for_jurisdiction = [
            row for row in documents if str(row["frontmatter"].get("jurisdiction") or "") == jurisdiction
        ]
        units_for_jurisdiction = [
            row for row in visible_units if str(row["frontmatter"].get("jurisdiction") or "") == jurisdiction
        ]
        related_collections = sorted(
            {
                str(row["frontmatter"].get("source_collection") or "").strip()
                for row in [*documents_for_jurisdiction, *units_for_jurisdiction]
                if str(row["frontmatter"].get("source_collection") or "").strip()
            }
        )
        phase_coverage = sorted(
            {
                str(row["frontmatter"].get("phase") or "").strip()
                for row in [*documents_for_jurisdiction, *units_for_jurisdiction]
                if str(row["frontmatter"].get("phase") or "").strip()
            }
        )
        representative_documents = sorted(
            documents_for_jurisdiction,
            key=lambda row: (
                str(row["frontmatter"].get("primary_topic") or ""),
                str(row["frontmatter"].get("title") or row["path"].stem),
            ),
        )[:5]

        note_id = f"jurisdiction-{jurisdiction.lower()}"
        target = settings.paths.jurisdictions_root / f"{note_id}.md"
        expected_paths.add(target)
        existing_frontmatter, _ = parse_frontmatter_file(target) if target.exists() else ({}, "")
        frontmatter = {
            "record_layer": "knowledge",
            "id": note_id,
            "note_type": "jurisdiction_overview",
            "title": jurisdiction,
            "summary": f"Overview note for {jurisdiction} regulation material in the wiki.",
            "status": "draft",
            "created": str(existing_frontmatter.get("created") or generated_on),
            "updated": generated_on,
            "aliases": [],
            "provenance": {"source_files": [], "source_hashes": {}, "parser_run_id": run_id},
            "confidence": "medium",
            "phase_coverage": phase_coverage,
            "related_collections": related_collections,
            "regulation_document_count": len(documents_for_jurisdiction),
            "visible_regulation_unit_count": len(units_for_jurisdiction),
        }
        body = [
            render_frontmatter(frontmatter),
            f"# {jurisdiction}",
            "",
            "## Snapshot",
            f"- id: {note_id}",
            f"- regulation_document_count: {len(documents_for_jurisdiction)}",
            f"- visible_regulation_unit_count: {len(units_for_jurisdiction)}",
            "",
            "## Source Landscape",
            f"- related_collections: {', '.join(related_collections) or 'n/a'}",
        ]
        if representative_documents:
            for row in representative_documents:
                body.append(f"- representative_document: {_document_link(row)}")
        else:
            body.append("- representative_document: n/a")
        body.extend(
            [
                "",
                "## Phase Coverage",
                f"- phases: {', '.join(phase_coverage) or 'n/a'}",
                "",
                "## Related Notes",
                "- [[indexes/jurisdiction-hub|Jurisdiction Hub]]",
            ]
        )
        for row in representative_documents:
            body.append(f"- {_document_link(row)}")
        if not representative_documents:
            body.append("- See regulation documents and units for this jurisdiction.")
        body.append("")
        write_text(target, "\n".join(body))
        written_files.append(target.relative_to(settings.paths.project_root).as_posix())

    for path in sorted(settings.paths.jurisdictions_root.glob("*.md")):
        if path.name in EXCLUDE_FILENAMES:
            continue
        if path not in expected_paths:
            path.unlink()
            removed_files.append(path.relative_to(settings.paths.project_root).as_posix())

    return {
        "status": "refreshed",
        "jurisdiction_count": len(jurisdictions),
        "written_files": written_files,
        "removed_files": removed_files,
    }


def _load_notes(root: Path, *, note_type: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.glob("*.md")):
        if path.name in EXCLUDE_FILENAMES:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        if str(frontmatter.get("note_type") or "") != note_type:
            continue
        rows.append({"path": path, "frontmatter": frontmatter})
    return rows


def _document_link(row: dict[str, Any]) -> str:
    path = row["path"]
    title = str(row["frontmatter"].get("title") or path.stem)
    return f"[[regulation_documents/{path.stem}|{title}]]"


def _is_pseudo_document_unit(frontmatter: dict[str, Any]) -> bool:
    return str(frontmatter.get("note_type") or "") == "regulation_unit" and (
        str(frontmatter.get("clause_path") or "") == "document"
        or str(frontmatter.get("id") or "").endswith("-document")
    )


def _today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")
