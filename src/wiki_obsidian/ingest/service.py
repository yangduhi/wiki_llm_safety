from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wiki_obsidian.jurisdiction_overviews import refresh_jurisdiction_overviews
from wiki_obsidian.normalize.service import normalize_collection
from wiki_obsidian.operations import append_knowledge_log, rebuild_indexes
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_jsonl, write_text
from wiki_obsidian.utils.frontmatter import render_frontmatter
from wiki_obsidian.utils.text import slugify


def ingest_wiki(
    *,
    project_root: str | Path | None = None,
    collection: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if not collection:
        raise ValueError("ingest requires --collection")
    settings = load_project_settings(project_root)
    normalize_report = normalize_collection(collection=collection, project_root=settings.paths.project_root, run_id=run_id)
    active_run_id = str(normalize_report["run_id"])
    run_root = settings.paths.normalized_root / "runs" / active_run_id

    documents = read_jsonl(run_root / "documents.jsonl")
    units = read_jsonl(run_root / "units.jsonl")
    concepts = read_jsonl(run_root / "concepts.jsonl")

    doc_to_units: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        doc_to_units.setdefault(str(unit["document_id"]), []).append(unit)

    written_files: list[str] = []
    for document in documents:
        path = settings.paths.regulation_documents_root / f"{slugify(str(document['document_id']))}.md"
        write_text(path, _render_regulation_document(document, doc_to_units.get(str(document["document_id"]), [])))
        written_files.append(path.relative_to(settings.paths.project_root).as_posix())

    for unit in units:
        path = settings.paths.regulation_units_root / f"{slugify(str(unit['id']))}.md"
        write_text(path, _render_regulation_unit(unit))
        written_files.append(path.relative_to(settings.paths.project_root).as_posix())

    for concept in concepts:
        path = settings.paths.concepts_root / f"{slugify(str(concept['id']))}.md"
        write_text(path, _render_concept(concept))
        written_files.append(path.relative_to(settings.paths.project_root).as_posix())

    jurisdiction_refresh = refresh_jurisdiction_overviews(
        project_root=settings.paths.project_root,
        run_id=active_run_id,
    )
    written_files.extend(jurisdiction_refresh["written_files"])

    append_knowledge_log(
        title=f"Ingested collection {collection}",
        details=[
            f"- run_id: `{active_run_id}`",
            f"- collection_id: `{collection}`",
            f"- document_notes_written: {len(documents)}",
            f"- regulation_units_written: {len(units)}",
            f"- jurisdiction_notes_written: {jurisdiction_refresh['jurisdiction_count']}",
        ],
        project_root=settings.paths.project_root,
        operation="ingest",
    )
    rebuild_indexes(project_root=settings.paths.project_root, include_operations=True)

    return {
        "run_id": active_run_id,
        "collection": collection,
        "status": "ingested",
        "pages_written": len(written_files),
        "written_files": written_files,
    }


def write_analysis_page(
    *,
    question: str,
    answer: str,
    matched_pages: list[str],
    source_files: list[str],
    source_hashes: dict[str, str],
    run_id: str,
    project_root: str | Path | None = None,
) -> Path:
    settings = load_project_settings(project_root)
    title_slug = slugify(question)[:100]
    path = settings.paths.analyses_root / f"{title_slug}.md"
    frontmatter = {
        "record_layer": "knowledge",
        "id": f"analysis-{title_slug}",
        "note_type": "analysis",
        "title": question,
        "summary": answer[:140] if answer else question,
        "status": "draft",
        "created": _today(),
        "updated": _today(),
        "aliases": [],
        "provenance": {
            "source_files": source_files,
            "source_hashes": source_hashes,
            "parser_run_id": run_id,
        },
        "confidence": "medium",
        "derived_from": matched_pages,
    }
    body = [
        render_frontmatter(frontmatter),
        f"# {question}",
        "",
        "## Question",
        question,
        "",
        "## Answer",
        answer,
        "",
        "## Evidence",
    ]
    if matched_pages:
        body.extend(f"- supporting_page: [[{page}]]" for page in matched_pages)
    else:
        body.append("- No matched knowledge pages were available.")
    body.extend(["", "## Counterarguments or Alternatives", "- Review before treating as settled.", ""])
    write_text(path, "\n".join(body))
    append_knowledge_log(
        title=question,
        details=[
            f"- run_id: `{run_id}`",
            f"- analysis_path: `{path.relative_to(settings.paths.project_root).as_posix()}`",
        ],
        project_root=settings.paths.project_root,
        operation="query-writeback",
    )
    rebuild_indexes(project_root=settings.paths.project_root, include_operations=True)
    return path


def _render_regulation_document(document: dict[str, Any], units: list[dict[str, Any]]) -> str:
    provenance = document.get("provenance") or {}
    source_files = provenance.get("source_files") or []
    lines = [
        render_frontmatter(document),
        f"# {document['title']}",
        "",
        "## Snapshot",
        f"- jurisdiction: {document['jurisdiction']}",
        f"- source_collection: {document['source_collection']}",
        f"- phase: {document['phase']}",
        "",
        "## Source Details",
        f"- document_id: {document['document_id']}",
        f"- source_file: {source_files[0] if source_files else 'n/a'}",
        f"- source_citation: {document.get('source_citation') or 'n/a'}",
        f"- source_language: {document.get('source_language', 'n/a')}",
        f"- page_count: {document.get('page_count') or 'n/a'}",
        "",
        "## Canonical Classification",
        f"- regulatory_layer: {document['regulatory_layer']}",
        f"- functional_domain: {', '.join(document.get('functional_domain') or [])}",
        f"- primary_topic: {document['primary_topic']}",
        f"- legacy_domain: {document['legacy_domain']}",
        "",
        "## Authority",
        f"- source_url: {document.get('source_url') or 'n/a'}",
        f"- confidence: {document['confidence']}",
        "",
        "## Related Units",
    ]
    visible_units = [unit for unit in units if not _is_pseudo_document_unit(unit)]
    for unit in visible_units[:40]:
        lines.append(f"- [[regulation_units/{slugify(str(unit['id']))}]]")
    if not visible_units:
        lines.append("- None yet.")
    lines.append("")
    return "\n".join(lines)


def _render_regulation_unit(unit: dict[str, Any]) -> str:
    provenance = unit.get("provenance") or {}
    source_files = provenance.get("source_files") or []
    lines = [
        render_frontmatter(unit),
        f"# {unit['title']}",
        "",
        "## Statement",
        unit["statement"],
        "",
        "## Classification",
        f"- jurisdiction: {unit['jurisdiction']}",
        f"- source_collection: {unit['source_collection']}",
        f"- regulatory_layer: {unit['regulatory_layer']}",
        f"- phase: {unit['phase']}",
        f"- functional_domain: {', '.join(unit.get('functional_domain') or [])}",
        f"- primary_topic: {unit['primary_topic']}",
        f"- secondary_topics: {', '.join(unit.get('secondary_topics') or []) or 'n/a'}",
        f"- browse_buckets: {', '.join(unit.get('browse_buckets') or []) or 'n/a'}",
        f"- legacy_domain: {unit['legacy_domain']}",
        "",
        "## Basis",
        unit["basis"],
        "",
        "## Authority",
        f"- clause_path: {unit['clause_path']}",
        f"- source_file: {source_files[0] if source_files else 'n/a'}",
        f"- source_citation: {unit.get('source_citation') or 'n/a'}",
        f"- source_url: {unit.get('source_url') or 'n/a'}",
        f"- confidence: {unit['confidence']}",
        "",
        "## Related Notes",
        f"- [[regulation_documents/{slugify(str(unit['document_id']))}]]",
        f"- [[jurisdictions/jurisdiction-{str(unit['jurisdiction']).lower()}]]",
        "",
    ]
    return "\n".join(lines)


def _render_jurisdiction(jurisdiction: dict[str, Any]) -> str:
    lines = [
        render_frontmatter(jurisdiction),
        f"# {jurisdiction['title']}",
        "",
        "## Snapshot",
        f"- id: {jurisdiction['id']}",
        "",
        "## Source Landscape",
        f"- related_collections: {', '.join(jurisdiction.get('related_collections') or []) or 'n/a'}",
        "",
        "## Phase Coverage",
        f"- phases: {', '.join(jurisdiction.get('phase_coverage') or []) or 'n/a'}",
        "",
        "## Related Notes",
        "- See regulation documents and units for this jurisdiction.",
        "",
    ]
    return "\n".join(lines)


def _render_concept(concept: dict[str, Any]) -> str:
    lines = [
        render_frontmatter(concept),
        f"# {concept['title']}",
        "",
        "## Definition",
        concept.get("definition", concept["summary"]),
        "",
        "## Classification Role",
        concept["summary"],
        "",
        "## Evidence",
        "- Derived from normalized corpus patterns.",
        "",
        "## Related Notes",
        "- None yet.",
        "",
    ]
    return "\n".join(lines)


def _today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _is_pseudo_document_unit(unit: dict[str, Any]) -> bool:
    return str(unit.get("note_type") or "") == "regulation_unit" and (
        str(unit.get("clause_path") or "") == "document" or str(unit.get("id") or "").endswith("-document")
    )
