from __future__ import annotations

from pathlib import Path
from typing import Any

from wiki_obsidian.classification import classify_text
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

    normalized_documents = [_normalize_document(row, profile=profile, run_id=active_run_id) for row in documents]
    normalized_units = [_normalize_unit(row, profile=profile, run_id=active_run_id) for row in units_raw]
    jurisdiction_rows = _jurisdiction_rows(normalized_units, run_id=active_run_id)
    concept_rows: list[dict[str, Any]] = []
    relation_rows = _build_relations(normalized_documents, normalized_units, jurisdiction_rows)

    documents_path = write_jsonl(run_root / "documents.jsonl", normalized_documents)
    units_path = write_jsonl(run_root / "units.jsonl", normalized_units)
    concepts_path = write_jsonl(run_root / "concepts.jsonl", concept_rows)
    jurisdictions_path = write_jsonl(run_root / "jurisdictions.jsonl", jurisdiction_rows)
    relations_path = write_jsonl(run_root / "relations.jsonl", relation_rows)
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
    }
    report_path = write_json(run_root / "normalize_report.json", report)
    return report | {"report_path": str(report_path)}


def _normalize_document(row: dict[str, Any], *, profile: dict[str, Any], run_id: str) -> dict[str, Any]:
    text = f"{row['title']} {row.get('regulatory_layer', '')}"
    classification = classify_text(
        text,
        collection=str(row["collection_id"]),
        jurisdiction=str(row["jurisdiction"]),
        regulatory_layer=str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
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
        "source_files": [source_file],
        "source_hashes": {source_file: source_hash},
        "source_url": row.get("source_url"),
        "document_id": str(row["document_id"]),
        "page_count": row.get("page_count"),
        "source_language": str(row["source_language"]),
    }


def _normalize_unit(row: dict[str, Any], *, profile: dict[str, Any], run_id: str) -> dict[str, Any]:
    classification = classify_text(
        f"{row['title_fragment']} {row['statement']} {row['basis']}",
        collection=str(row["collection_id"]),
        jurisdiction=str(row["jurisdiction"]),
        regulatory_layer=str(row.get("regulatory_layer") or profile.get("regulatory_layer") or "technical_requirement"),
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
        "source_files": [source_file],
        "source_hashes": {source_file: source_hash},
        "source_url": row.get("source_url"),
        "document_id": str(row["document_id"]),
        "clause_path": str(row["clause_path"]),
        "statement": str(row["statement"]),
        "basis": str(row["basis"]),
        "page_start": row.get("page_start"),
        "page_end": row.get("page_end"),
    }


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
