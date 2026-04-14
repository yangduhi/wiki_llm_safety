from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from wiki_obsidian.classification import classify_text_with_trace
from wiki_obsidian.parse.service import parse_collection
from wiki_obsidian.profiles import load_collection_profile
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, read_json, read_jsonl, write_json, write_jsonl
from wiki_obsidian.utils.ids import build_run_id


def normalize_collection(
    *,
    collection: str,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("normalize", collection)
    parse_root = settings.paths.parsed_root / "runs" / active_run_id
    if not parse_root.exists():
        parse_collection(collection=collection, project_root=settings.paths.project_root, run_id=active_run_id)

    profile = load_collection_profile(collection, project_root=settings.paths.project_root)
    documents = read_jsonl(parse_root / "documents.jsonl")
    units_raw = read_jsonl(parse_root / "units_raw.jsonl")
    parse_report = read_json(parse_root / "parse_report.json")
    run_root = ensure_dir(settings.paths.normalized_root / "runs" / active_run_id)

    trace_rows: list[dict[str, Any]] = []
    normalized_documents = [_normalize_document(row, profile=profile, run_id=active_run_id, project_root=settings.paths.project_root, trace_rows=trace_rows) for row in documents]
    normalized_units = [_normalize_unit(row, profile=profile, run_id=active_run_id, project_root=settings.paths.project_root, trace_rows=trace_rows) for row in units_raw]
    jurisdiction_rows = _jurisdiction_rows(normalized_units, run_id=active_run_id)
    concept_rows: list[dict[str, Any]] = []
    relation_rows = _build_relations(normalized_documents, normalized_units, jurisdiction_rows)

    documents_path = write_jsonl(run_root / "documents.jsonl", normalized_documents)
    units_path = write_jsonl(run_root / "units.jsonl", normalized_units)
    concepts_path = write_jsonl(run_root / "concepts.jsonl", concept_rows)
    jurisdictions_path = write_jsonl(run_root / "jurisdictions.jsonl", jurisdiction_rows)
    relations_path = write_jsonl(run_root / "relations.jsonl", relation_rows)
    trace_path = write_jsonl(run_root / "classification_trace.jsonl", trace_rows)
    report = {
        "run_id": active_run_id,
        "collection_id": collection,
        "document_count": len(normalized_documents),
        "unit_count": len(normalized_units),
        "malformed_files": parse_report.get("malformed_files", []),
        "documents_path": str(documents_path),
        "units_path": str(units_path),
        "concepts_path": str(concepts_path),
        "jurisdictions_path": str(jurisdictions_path),
        "relations_path": str(relations_path),
        "classification_trace_path": str(trace_path),
    }
    report_path = write_json(run_root / "normalize_report.json", report)
    return report | {"report_path": str(report_path)}


def _normalize_document(row: dict[str, Any], *, profile: dict[str, Any], run_id: str, project_root: str | Path, trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    text = " ".join(
        part
        for part in (
            row["title"],
            row.get("subject"),
            " ".join(row.get("reference_articles") or []),
            row.get("regulatory_layer", ""),
        )
        if part
    )
    classification_result = classify_text_with_trace(
        f"{row['document_id']} {row['source_file']} {text}",
        collection=str(row["collection_id"]),
        jurisdiction=str(row["jurisdiction"]),
        regulatory_layer=str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
        project_root=project_root,
        metadata={
            "note_kind": "document",
            "document_id": row["document_id"],
            "title": row["title"],
            "subject": row.get("subject"),
            "sectno": row.get("sectno"),
            "parent_title": row["title"],
            "document_kind": row.get("document_kind"),
            "is_attachment": row.get("is_attachment"),
            "attachment_bucket": row.get("attachment_bucket"),
            "reference_articles": row.get("reference_articles") or [],
        },
    )
    classification = classification_result["decision"]
    comparison_key = _comparison_key(row["document_id"], row["title"], text)
    trace_rows.append(
        {
            "collection_id": row["collection_id"],
            "note_kind": "document",
            "unit_id": None,
            "document_id": row["document_id"],
            "source_file": row["source_file"],
            "comparison_key": comparison_key,
            "document_kind": row.get("document_kind"),
            "is_attachment": row.get("is_attachment"),
            "attachment_bucket": row.get("attachment_bucket"),
            "reference_articles": row.get("reference_articles") or [],
            **classification_result["trace"],
        }
    )
    source_file = str(row["source_file"])
    source_hash = str(row["source_hash"])
    return {
        "record_layer": "knowledge",
        "id": f"regdoc-{row['document_id']}",
        "note_type": "regulation_document",
        "title": str(row["title"]),
        "summary": f"Document-level source summary for {row['title']}.",
        "status": "draft",
        "created": "2026-04-13",
        "updated": "2026-04-13",
        "jurisdiction": str(row["jurisdiction"]),
        "source_collection": str(row["collection_id"]),
        "document_id": str(row["document_id"]),
        "regulatory_layer": str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
        "phase": classification["phase"],
        "functional_domain": classification["functional_domain"],
        "primary_topic": classification["primary_topic"],
        "secondary_topics": classification["secondary_topics"],
        "browse_buckets": classification["browse_buckets"],
        "legacy_domain": classification["legacy_domain"],
        "aliases": [],
        "provenance": {
            "source_files": [source_file],
            "source_hashes": {source_file: source_hash},
            "source_url": row.get("source_url"),
            "parser_run_id": run_id,
        },
        "effective_date": None,
        "confidence": "medium",
        "review_required": bool(profile.get("review_defaults", {}).get("source_summary", False)),
        "source_url": row.get("source_url"),
        "source_citation": _document_source_citation(row),
        "page_count": row.get("page_count"),
        "source_language": str(row["source_language"]),
        "sectno": row.get("sectno"),
        "subject": row.get("subject"),
        "document_kind": row.get("document_kind"),
        "is_attachment": row.get("is_attachment"),
        "attachment_bucket": row.get("attachment_bucket"),
        "reference_articles": row.get("reference_articles") or [],
        "comparison_key": comparison_key,
    }


def _normalize_unit(row: dict[str, Any], *, profile: dict[str, Any], run_id: str, project_root: str | Path, trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    classifier_text = " ".join(
        part
        for part in (
            row["document_id"],
            row["source_file"],
            row.get("subject"),
            row.get("parent_title"),
            row.get("attachment_section"),
            " ".join(row.get("reference_articles") or []),
            row["title_fragment"],
            row["statement"],
            row["basis"],
        )
        if part
    )
    classification_result = classify_text_with_trace(
        classifier_text,
        collection=str(row["collection_id"]),
        jurisdiction=str(row["jurisdiction"]),
        regulatory_layer=str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
        project_root=project_root,
        metadata={
            "note_kind": "unit",
            "document_id": row["document_id"],
            "unit_id": row["unit_id"],
            "title": row["title_fragment"],
            "subject": row.get("subject"),
            "sectno": row.get("sectno"),
            "parent_title": row.get("parent_title"),
            "raw_marker": row.get("raw_marker"),
            "line_index_start": row.get("line_index_start"),
            "line_index_end": row.get("line_index_end"),
            "document_kind": row.get("document_kind"),
            "is_attachment": row.get("is_attachment"),
            "attachment_bucket": row.get("attachment_bucket"),
            "attachment_section": row.get("attachment_section"),
            "row_group_id": row.get("row_group_id"),
            "is_table_like_row": row.get("is_table_like_row"),
            "inherits_subject_context": row.get("inherits_subject_context"),
            "inherits_section_context": row.get("inherits_section_context"),
            "reference_articles": row.get("reference_articles") or [],
            "statement": row.get("statement"),
            "basis": row.get("basis"),
            "parent_clause_path": row.get("parent_clause_path"),
            "parent_clause_text": row.get("parent_clause_text"),
        },
    )
    classification = classification_result["decision"]
    comparison_key = _comparison_key(row["document_id"], row["title_fragment"], row["statement"])
    trace_rows.append(
        {
            "collection_id": row["collection_id"],
            "note_kind": "unit",
            "unit_id": row["unit_id"],
            "document_id": row["document_id"],
            "source_file": row["source_file"],
            "comparison_key": comparison_key,
            "document_kind": row.get("document_kind"),
            "is_attachment": row.get("is_attachment"),
            "attachment_bucket": row.get("attachment_bucket"),
            "attachment_section": row.get("attachment_section"),
            "row_group_id": row.get("row_group_id"),
            "is_table_like": row.get("is_table_like_row"),
            "reference_articles": row.get("reference_articles") or [],
            **classification_result["trace"],
        }
    )
    source_file = str(row["source_file"])
    source_hash = str(row["source_hash"])
    return {
        "record_layer": "knowledge",
        "id": f"regunit-{row['unit_id']}",
        "note_type": "regulation_unit",
        "title": str(row["title_fragment"]),
        "summary": f"Regulation unit `{row['clause_path']}` from {row['document_id']}.",
        "status": "draft",
        "created": "2026-04-13",
        "updated": "2026-04-13",
        "jurisdiction": str(row["jurisdiction"]),
        "source_collection": str(row["collection_id"]),
        "document_id": str(row["document_id"]),
        "clause_path": str(row["clause_path"]),
        "regulatory_layer": str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
        "phase": classification["phase"],
        "functional_domain": classification["functional_domain"],
        "primary_topic": classification["primary_topic"],
        "secondary_topics": classification["secondary_topics"],
        "browse_buckets": classification["browse_buckets"],
        "legacy_domain": classification["legacy_domain"],
        "aliases": [],
        "provenance": {
            "source_files": [source_file],
            "source_hashes": {source_file: source_hash},
            "source_url": row.get("source_url"),
            "parser_run_id": run_id,
        },
        "effective_date": None,
        "confidence": "medium",
        "review_required": bool(profile.get("review_defaults", {}).get("claim", False)),
        "source_url": row.get("source_url"),
        "source_citation": _unit_source_citation(row),
        "statement": str(row["statement"]),
        "basis": str(row["basis"]),
        "page_start": row.get("page_start"),
        "page_end": row.get("page_end"),
        "sectno": row.get("sectno"),
        "subject": row.get("subject"),
        "parent_title": row.get("parent_title"),
        "raw_marker": row.get("raw_marker"),
        "line_index_start": row.get("line_index_start"),
        "line_index_end": row.get("line_index_end"),
        "document_kind": row.get("document_kind"),
        "is_attachment": row.get("is_attachment"),
        "attachment_bucket": row.get("attachment_bucket"),
        "attachment_section": row.get("attachment_section"),
        "row_group_id": row.get("row_group_id"),
        "is_table_like_row": row.get("is_table_like_row"),
        "inherits_subject_context": row.get("inherits_subject_context"),
        "inherits_section_context": row.get("inherits_section_context"),
        "reference_articles": row.get("reference_articles") or [],
        "comparison_key": comparison_key,
        "parent_clause_path": row.get("parent_clause_path"),
        "parent_clause_text": row.get("parent_clause_text"),
    }


def _comparison_key(document_id: str, title: str, statement: str) -> str:
    payload = f"{document_id}::{title}::{statement}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def _jurisdiction_rows(units: list[dict[str, Any]], *, run_id: str) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for unit in units:
        jurisdiction = str(unit["jurisdiction"])
        if jurisdiction in seen:
            continue
        seen[jurisdiction] = {
            "record_layer": "knowledge",
            "id": f"jurisdiction-{jurisdiction.lower()}",
            "note_type": "jurisdiction_overview",
            "title": jurisdiction,
            "summary": f"Overview note for {jurisdiction} regulation material in the wiki.",
            "status": "draft",
            "created": "2026-04-13",
            "updated": "2026-04-13",
            "aliases": [],
            "provenance": {"source_files": [], "source_hashes": {}, "parser_run_id": run_id},
            "confidence": "medium",
            "phase_coverage": sorted({str(row["phase"]) for row in units if str(row["jurisdiction"]) == jurisdiction}),
            "related_collections": sorted({str(row["source_collection"]) for row in units if str(row["jurisdiction"]) == jurisdiction}),
        }
    return list(seen.values())


def _build_relations(
    documents: list[dict[str, Any]],
    units: list[dict[str, Any]],
    jurisdictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    jurisdiction_lookup = {row["title"]: row["id"] for row in jurisdictions}
    for document in documents:
        jurisdiction_id = jurisdiction_lookup.get(str(document["jurisdiction"]))
        if jurisdiction_id:
            relations.append({"source_id": document["id"], "target_id": jurisdiction_id, "relation_type": "document_in_jurisdiction"})
    for unit in units:
        relations.append({"source_id": unit["id"], "target_id": unit["document_id"], "relation_type": "unit_from_document"})
    return relations


def _document_source_citation(row: dict[str, Any]) -> str:
    title = str(row.get("title") or "").strip()
    if title:
        return title
    return str(row["document_id"])


def _unit_source_citation(row: dict[str, Any]) -> str:
    return f"{row['document_id']} / {row['clause_path']}"
