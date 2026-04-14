from __future__ import annotations

from datetime import UTC, datetime
import hashlib
from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET

import fitz

from wiki_obsidian.profiles import load_collection_profile
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json, write_jsonl
from wiki_obsidian.utils.ids import build_run_id
from wiki_obsidian.utils.text import (
    is_attachment_table_like_text,
    normalize_classifier_text,
    normalize_whitespace,
    slugify,
)


def parse_collection(
    *,
    collection: str,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    profile = load_collection_profile(collection, project_root=settings.paths.project_root)
    active_run_id = run_id or build_run_id("parse", collection)
    run_root = ensure_dir(settings.paths.parsed_root / "runs" / active_run_id)
    collection_root = settings.paths.collections_root / collection
    files = [path for path in sorted(collection_root.rglob("*")) if path.is_file() and path.name != ".gitkeep"]

    documents: list[dict[str, Any]] = []
    units: list[dict[str, Any]] = []
    malformed_files: list[dict[str, str]] = []

    for path in files:
        try:
            parsed = _parse_file(path=path, collection=collection, profile=profile, project_root=settings.paths.project_root)
        except Exception as exc:
            malformed_files.append(
                {
                    "path": _relpath(path, settings.paths.project_root),
                    "error": str(exc),
                }
            )
            continue
        documents.append(parsed["document"])
        units.extend(parsed["units"])

    documents_path = write_jsonl(run_root / "documents.jsonl", documents)
    units_path = write_jsonl(run_root / "units_raw.jsonl", units)
    report = {
        "run_id": active_run_id,
        "collection_id": collection,
        "parser_mode": profile["parser_mode"],
        "document_count": len(documents),
        "unit_count": len(units),
        "malformed_files": malformed_files,
        "documents_path": str(documents_path),
        "units_path": str(units_path),
        "parsed_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
    report_path = write_json(run_root / "parse_report.json", report)
    return report | {"report_path": str(report_path)}


def _parse_file(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    parser_mode = str(profile["parser_mode"])
    if parser_mode == "xml_fmvss_section":
        return _parse_xml_fmvss(path=path, collection=collection, profile=profile, project_root=project_root)
    if parser_mode == "xml_kmvss_record":
        return _parse_xml_kmvss(path=path, collection=collection, profile=profile, project_root=project_root)
    if parser_mode == "pdf_text_first":
        return _parse_pdf_text_first(path=path, collection=collection, profile=profile, project_root=project_root)
    if parser_mode == "markdown_clip":
        return _parse_markdown_clip(path=path, collection=collection, profile=profile, project_root=project_root)
    if parser_mode == "official_web_capture":
        return _parse_official_web(path=path, collection=collection, profile=profile, project_root=project_root)
    raise ValueError(f"Unsupported parser mode: {parser_mode}")


def _parse_xml_fmvss(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    title = normalize_whitespace(_text_or_default(root.findtext("HEAD"), path.stem))
    source_hash = _sha256_file(path)
    source_relpath = _relpath(path, project_root)
    segments = []
    for child in root:
        text = normalize_whitespace(" ".join(part.strip() for part in child.itertext() if part and part.strip()))
        if text:
            segments.append({"text": text, "page_no": None})
    document_id = f"{collection}-{slugify(path.stem)}"
    units = _units_from_segments(
        segments=segments,
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
    )
    document = _document_record(
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        parser_mode=str(profile["parser_mode"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
    )
    return {"document": document, "units": units}


def _parse_xml_kmvss(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    sectno = normalize_whitespace(root.findtext("SECTNO") or path.stem)
    subject = normalize_whitespace(root.findtext("SUBJECT") or path.stem)
    content = root.findtext("CONTENT") or ""
    title = normalize_whitespace(f"{sectno} {subject}")
    source_hash = _sha256_file(path)
    source_relpath = _relpath(path, project_root)
    document_id = f"{collection}-{slugify(path.stem)}"
    is_attachment = _is_kmvss_attachment_document(path=path, sectno=sectno, subject=subject)
    reference_articles = _extract_reference_articles(subject)
    attachment_bucket = _attachment_bucket_from_subject(subject) if is_attachment else None
    if is_attachment:
        segments = _build_kmvss_attachment_segments(
            content=content,
            sectno=sectno,
            subject=subject,
            title=title,
            attachment_bucket=attachment_bucket,
            reference_articles=reference_articles,
        )
    else:
        segments = []
        for line_index, line in enumerate(content.splitlines(), start=1):
            normalized_line = normalize_whitespace(line)
            if not normalized_line:
                continue
            segments.append(
                {
                    "text": normalized_line,
                    "page_no": None,
                    "line_index": line_index,
                    "sectno": sectno,
                    "subject": subject,
                    "parent_title": title,
                    "marker_override": _kmvss_segment_marker(normalized_line),
                    "document_kind": "article",
                    "is_attachment": False,
                    "reference_articles": reference_articles,
                    "allow_clause_marker_fallback": True,
                }
            )
    units = _units_from_segments(
        segments=segments,
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
        context={
            "sectno": sectno,
            "subject": subject,
            "parent_title": title,
            "document_kind": "attachment" if is_attachment else "article",
            "is_attachment": is_attachment,
            "attachment_bucket": attachment_bucket,
            "reference_articles": reference_articles,
        },
    )
    document = _document_record(
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        parser_mode=str(profile["parser_mode"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
        sectno=sectno,
        subject=subject,
        document_kind="attachment" if is_attachment else "article",
        is_attachment=is_attachment,
        attachment_bucket=attachment_bucket,
        reference_articles=reference_articles,
    )
    return {"document": document, "units": units}


def _parse_pdf_text_first(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    try:
        source_hash = _sha256_file(path)
        source_relpath = _relpath(path, project_root)
        first_page_lines: list[str] = []
        raw_segments: list[dict[str, Any]] = []
        for page_index in range(doc.page_count):
            page = doc[page_index]
            lines = [normalize_whitespace(line) for line in page.get_text("text").splitlines() if normalize_whitespace(line)]
            if page_index == 0:
                first_page_lines = lines[:20]
            for line in lines:
                raw_segments.append({"text": line, "page_no": page_index + 1})
        title = _pdf_collection_title(collection=collection, stem=path.stem, first_page_lines=first_page_lines)
        document_id = f"{collection}-{slugify(path.stem)}"
        segments = _segment_pdf_ece_lines(raw_segments, title=title) if collection == "pdf_ece" else raw_segments
        units = _units_from_segments(
            segments=segments,
            collection=collection,
            document_id=document_id,
            title=title,
            source_file=source_relpath,
            source_hash=source_hash,
            source_language=str(profile["language"]),
            jurisdiction=str(profile["jurisdiction"]),
            regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
            source_url=profile.get("source_url"),
        )
        document = _document_record(
            collection=collection,
            document_id=document_id,
            title=title,
            source_file=source_relpath,
            source_hash=source_hash,
            source_language=str(profile["language"]),
            jurisdiction=str(profile["jurisdiction"]),
            parser_mode=str(profile["parser_mode"]),
            regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
            source_url=profile.get("source_url"),
            page_count=doc.page_count,
        )
        return {"document": document, "units": units}
    finally:
        doc.close()


def _parse_markdown_clip(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    title = _markdown_title(text, fallback=path.stem)
    source_hash = _sha256_file(path)
    source_relpath = _relpath(path, project_root)
    document_id = f"{collection}-{slugify(path.stem)}"
    unit = _single_unit(
        document_id=document_id,
        collection=collection,
        title=title,
        statement=normalize_whitespace(title),
        basis=normalize_whitespace(text)[:4000] or normalize_whitespace(title),
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
    )
    document = _document_record(
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        parser_mode=str(profile["parser_mode"]),
        regulatory_layer=str(profile.get("regulatory_layer", "technical_requirement")),
        source_url=profile.get("source_url"),
    )
    return {"document": document, "units": [unit]}


def _parse_official_web(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    title = normalize_whitespace(title_match.group(1) if title_match else h1_match.group(1) if h1_match else path.stem)
    source_hash = _sha256_file(path)
    source_relpath = _relpath(path, project_root)
    document_id = f"{collection}-{slugify(path.stem)}"
    basis = normalize_whitespace(re.sub(r"<[^>]+>", " ", text))[:5000]
    unit = _single_unit(
        document_id=document_id,
        collection=collection,
        title=title,
        statement=title,
        basis=basis or title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        regulatory_layer=str(profile.get("regulatory_layer", "framework_admin")),
        source_url=profile.get("source_url"),
    )
    document = _document_record(
        collection=collection,
        document_id=document_id,
        title=title,
        source_file=source_relpath,
        source_hash=source_hash,
        source_language=str(profile["language"]),
        jurisdiction=str(profile["jurisdiction"]),
        parser_mode=str(profile["parser_mode"]),
        regulatory_layer=str(profile.get("regulatory_layer", "framework_admin")),
        source_url=profile.get("source_url"),
    )
    return {"document": document, "units": [unit]}


def _units_from_segments(
    *,
    segments: list[dict[str, Any]],
    collection: str,
    document_id: str,
    title: str,
    source_file: str,
    source_hash: str,
    source_language: str,
    jurisdiction: str,
    regulatory_layer: str,
    source_url: str | None,
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    context = context or {}
    hierarchy: dict[int, tuple[str, str]] = {}
    for segment in segments:
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        marker = segment.get("marker_override")
        if marker is None and segment.get("allow_clause_marker_fallback", True):
            marker = _clause_marker(text)
        if marker is not None:
            if current is not None:
                finalized = _finalize_unit(
                    current,
                    title=title,
                    document_id=document_id,
                    collection=collection,
                    source_file=source_file,
                    source_hash=source_hash,
                    source_language=source_language,
                    jurisdiction=jurisdiction,
                    regulatory_layer=regulatory_layer,
                    source_url=source_url,
                )
                units.append(finalized)
                hierarchy[_kmvss_hierarchy_level(str(finalized.get("raw_marker") or finalized.get("clause_path")))] = (
                    str(finalized.get("clause_path") or ""),
                    str(finalized.get("statement") or ""),
                )
            parent_clause_path, parent_clause_text = _parent_clause_for_marker(
                marker=str(marker),
                hierarchy=hierarchy,
                fallback_title=str(segment.get("parent_title") or context.get("parent_title") or title),
            )
            current = {
                "marker": marker,
                "raw_marker": segment.get("marker_override") or marker,
                "lines": [text],
                "page_start": segment.get("page_no"),
                "page_end": segment.get("page_no"),
                "sectno": segment.get("sectno") or context.get("sectno"),
                "subject": segment.get("subject") or context.get("subject"),
                "parent_title": segment.get("parent_title") or context.get("parent_title") or title,
                "line_index_start": segment.get("line_index"),
                "line_index_end": segment.get("line_index"),
                "document_kind": segment.get("document_kind") or context.get("document_kind"),
                "is_attachment": bool(segment.get("is_attachment") or context.get("is_attachment")),
                "attachment_bucket": segment.get("attachment_bucket") or context.get("attachment_bucket"),
                "attachment_section": segment.get("attachment_section"),
                "row_group_id": segment.get("row_group_id"),
                "is_table_like_row": bool(segment.get("is_table_like_row")),
                "inherits_subject_context": bool(segment.get("inherits_subject_context")),
                "inherits_section_context": bool(segment.get("inherits_section_context")),
                "reference_articles": segment.get("reference_articles") or context.get("reference_articles") or [],
                "parent_clause_path": parent_clause_path,
                "parent_clause_text": parent_clause_text,
            }
        elif current is not None:
            current["lines"].append(text)
            if segment.get("page_no"):
                current["page_end"] = segment["page_no"]
            if segment.get("line_index"):
                current["line_index_end"] = segment["line_index"]
            current["is_table_like_row"] = bool(current.get("is_table_like_row") or segment.get("is_table_like_row"))
            if segment.get("attachment_section") and not current.get("attachment_section"):
                current["attachment_section"] = segment.get("attachment_section")
            if segment.get("row_group_id"):
                current["row_group_id"] = segment.get("row_group_id")
            if segment.get("inherits_subject_context"):
                current["inherits_subject_context"] = True
            if segment.get("inherits_section_context"):
                current["inherits_section_context"] = True
        else:
            current = {
                "marker": "document",
                "raw_marker": "document",
                "lines": [text],
                "page_start": segment.get("page_no"),
                "page_end": segment.get("page_no"),
                "sectno": segment.get("sectno") or context.get("sectno"),
                "subject": segment.get("subject") or context.get("subject"),
                "parent_title": segment.get("parent_title") or context.get("parent_title") or title,
                "line_index_start": segment.get("line_index"),
                "line_index_end": segment.get("line_index"),
                "document_kind": segment.get("document_kind") or context.get("document_kind"),
                "is_attachment": bool(segment.get("is_attachment") or context.get("is_attachment")),
                "attachment_bucket": segment.get("attachment_bucket") or context.get("attachment_bucket"),
                "attachment_section": segment.get("attachment_section"),
                "row_group_id": segment.get("row_group_id"),
                "is_table_like_row": bool(segment.get("is_table_like_row")),
                "inherits_subject_context": bool(segment.get("inherits_subject_context")),
                "inherits_section_context": bool(segment.get("inherits_section_context")),
                "reference_articles": segment.get("reference_articles") or context.get("reference_articles") or [],
                "parent_clause_path": None,
                "parent_clause_text": None,
            }
    if current is not None:
        units.append(
            _finalize_unit(
                current,
                title=title,
                document_id=document_id,
                collection=collection,
                source_file=source_file,
                source_hash=source_hash,
                source_language=source_language,
                jurisdiction=jurisdiction,
                regulatory_layer=regulatory_layer,
                source_url=source_url,
            )
        )
    units = _dedupe_units(units)
    return units or [
        _single_unit(
            document_id=document_id,
            collection=collection,
            title=title,
            statement=title,
            basis=title,
            source_file=source_file,
            source_hash=source_hash,
            source_language=source_language,
            jurisdiction=jurisdiction,
            regulatory_layer=regulatory_layer,
            source_url=source_url,
        )
    ]


def _dedupe_units(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for unit in units:
        clause_path = str(unit["clause_path"])
        seen[clause_path] = seen.get(clause_path, 0) + 1
        if seen[clause_path] > 1:
            suffix = str(seen[clause_path])
            unit = dict(unit)
            unit["clause_path"] = f"{clause_path}-{suffix}"
            unit["unit_id"] = f"{unit['document_id']}-{unit['clause_path']}"
            unit["slug"] = slugify(unit["unit_id"])
        out.append(unit)
    return out


def _finalize_unit(
    current: dict[str, Any],
    *,
    title: str,
    document_id: str,
    collection: str,
    source_file: str,
    source_hash: str,
    source_language: str,
    jurisdiction: str,
    regulatory_layer: str,
    source_url: str | None,
) -> dict[str, Any]:
    lines = [normalize_whitespace(line) for line in current["lines"] if normalize_whitespace(line)]
    statement = lines[0] if lines else title
    basis = "\n".join(lines)
    clause_path = _normalize_marker(str(current["marker"]))
    unit_slug = slugify(f"{document_id}-{clause_path}")
    return {
        "unit_id": f"{document_id}-{clause_path}",
        "document_id": document_id,
        "collection_id": collection,
        "title_fragment": statement[:120],
        "clause_path": clause_path,
        "raw_marker": current.get("raw_marker"),
        "sectno": current.get("sectno"),
        "subject": current.get("subject"),
        "parent_title": current.get("parent_title"),
        "line_index_start": current.get("line_index_start"),
        "line_index_end": current.get("line_index_end"),
        "statement": statement,
        "basis": basis,
        "page_start": current.get("page_start"),
        "page_end": current.get("page_end"),
        "document_kind": current.get("document_kind"),
        "is_attachment": current.get("is_attachment"),
        "attachment_bucket": current.get("attachment_bucket"),
        "attachment_section": current.get("attachment_section"),
        "row_group_id": current.get("row_group_id"),
        "is_table_like_row": current.get("is_table_like_row"),
        "inherits_subject_context": current.get("inherits_subject_context"),
        "inherits_section_context": current.get("inherits_section_context"),
        "reference_articles": current.get("reference_articles") or [],
        "parent_clause_path": current.get("parent_clause_path"),
        "parent_clause_text": current.get("parent_clause_text"),
        "source_file": source_file,
        "source_hash": source_hash,
        "source_language": source_language,
        "jurisdiction": jurisdiction,
        "regulatory_layer": regulatory_layer,
        "source_url": source_url,
        "slug": unit_slug,
    }


def _single_unit(
    *,
    document_id: str,
    collection: str,
    title: str,
    statement: str,
    basis: str,
    source_file: str,
    source_hash: str,
    source_language: str,
    jurisdiction: str,
    regulatory_layer: str,
    source_url: str | None,
) -> dict[str, Any]:
    return {
        "unit_id": f"{document_id}-document",
        "document_id": document_id,
        "collection_id": collection,
        "title_fragment": title,
        "clause_path": "document",
        "raw_marker": "document",
        "sectno": None,
        "subject": None,
        "parent_title": title,
        "line_index_start": None,
        "line_index_end": None,
        "document_kind": "document",
        "is_attachment": False,
        "attachment_bucket": None,
        "attachment_section": None,
        "row_group_id": None,
        "is_table_like_row": False,
        "inherits_subject_context": False,
        "inherits_section_context": False,
        "reference_articles": [],
        "parent_clause_path": None,
        "parent_clause_text": None,
        "statement": statement,
        "basis": basis,
        "page_start": None,
        "page_end": None,
        "source_file": source_file,
        "source_hash": source_hash,
        "source_language": source_language,
        "jurisdiction": jurisdiction,
        "regulatory_layer": regulatory_layer,
        "source_url": source_url,
        "slug": slugify(f"{document_id}-document"),
    }


def _is_kmvss_attachment_document(*, path: Path, sectno: str, subject: str) -> bool:
    if path.stem.lower().startswith("kmvss_att_"):
        return True
    if any(token in sectno for token in ("별표", "별지")):
        return True
    return False


def _kmvss_hierarchy_level(marker: str) -> int:
    raw = str(marker)
    if raw.startswith("paragraph-"):
        return 1
    if raw.startswith("item-"):
        return 2
    if raw.startswith("subitem-"):
        return 3
    if raw.startswith("제") and "조" in raw:
        return 0
    return 0


def _parent_clause_for_marker(
    *,
    marker: str,
    hierarchy: dict[int, tuple[str, str]],
    fallback_title: str,
) -> tuple[str | None, str | None]:
    level = _kmvss_hierarchy_level(marker)
    for candidate_level in range(level - 1, -1, -1):
        if candidate_level in hierarchy:
            return hierarchy[candidate_level]
    return (None, fallback_title if level > 0 else None)


def _extract_reference_articles(subject: str) -> list[str]:
    references = re.findall(r"(제\d+조(?:의\d+)?(?:제\d+항)?(?:제\d+호)?)", normalize_classifier_text(subject))
    return sorted(set(references))


def _attachment_bucket_from_subject(subject: str) -> str:
    normalized = normalize_classifier_text(subject)
    if any(token in normalized for token in ("전자파 적합성", "EMC", "방사", "전도")):
        return "emc_electrical_compatibility"
    if any(token in normalized for token in ("전조등", "안개등", "방향지시등", "후부반사기", "후부반사판", "광원형식", "광도", "반사띠", "등화")):
        return "lighting_photometric_reflector_signaling"
    if any(token in normalized for token in ("제동능력", "제동장치", "브레이크호스", "제동등")):
        return "braking_performance_hardware"
    if any(token in normalized for token in ("표기", "표시", "식별표시")):
        return "labeling_marking_indication"
    if any(token in normalized for token in ("타이어", "휠", "호스")):
        return "tire_wheel_hose_running_gear"
    return "short_value_rows"


def _build_kmvss_attachment_segments(
    *,
    content: str,
    sectno: str,
    subject: str,
    title: str,
    attachment_bucket: str | None,
    reference_articles: list[str],
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    current_section = subject or title
    current_parent = subject or title
    current_row_group = 0
    for line_index, line in enumerate(content.splitlines(), start=1):
        normalized_line = normalize_whitespace(line)
        if not normalized_line or _is_attachment_boilerplate_line(normalized_line):
            continue
        line_kind = _attachment_line_kind(normalized_line)
        if line_kind in {"section_header", "semantic_header"}:
            current_parent = normalized_line
            if line_kind == "section_header":
                current_section = normalized_line
            current_row_group += 1
            segments.append(
                {
                    "text": normalized_line,
                    "page_no": None,
                    "line_index": line_index,
                    "sectno": sectno,
                    "subject": subject,
                    "parent_title": current_parent,
                    "marker_override": _attachment_marker(normalized_line, line_index),
                    "document_kind": "attachment",
                    "is_attachment": True,
                    "attachment_bucket": attachment_bucket,
                    "attachment_section": current_section,
                    "row_group_id": f"group-{current_row_group}",
                    "is_table_like_row": False,
                    "inherits_subject_context": True,
                    "inherits_section_context": line_kind == "semantic_header",
                    "reference_articles": reference_articles,
                    "allow_clause_marker_fallback": False,
                }
            )
            continue
        segments.append(
            {
                "text": normalized_line,
                "page_no": None,
                "line_index": line_index,
                "sectno": sectno,
                "subject": subject,
                "parent_title": current_parent,
                "marker_override": None,
                "document_kind": "attachment",
                "is_attachment": True,
                "attachment_bucket": attachment_bucket,
                "attachment_section": current_section,
                "row_group_id": f"group-{current_row_group or 1}",
                "is_table_like_row": line_kind == "table_like_row",
                "inherits_subject_context": True,
                "inherits_section_context": True,
                "reference_articles": reference_articles,
                "allow_clause_marker_fallback": False,
            }
        )
    return segments


def _is_attachment_boilerplate_line(text: str) -> bool:
    normalized = normalize_classifier_text(text)
    if normalized.startswith("■ 자동차 및 자동차부품의 성능과 기준에 관한 규칙"):
        return True
    return bool(re.fullmatch(r"[■□┯┨┠┷┳┻├┤│─═║╭╮╯╰+\s]+", text))


def _attachment_line_kind(text: str) -> str:
    normalized = normalize_classifier_text(text)
    if re.match(r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩIVX]+\.", normalized):
        return "section_header"
    if re.match(r"^\d+\.\s*[가-힣A-Za-z]", normalized) and not is_attachment_table_like_text(normalized):
        return "semantic_header"
    if re.match(r"^[가나다라마바사아자차카타파하]\.\s*", normalized):
        return "semantic_header"
    if re.match(r"^\d+\)\s*", normalized):
        return "semantic_header"
    if re.match(r"^[가나다라마바사아자차카타파하]\)\s*", normalized):
        return "semantic_header"
    if _looks_like_attachment_descriptive_header(normalized):
        return "semantic_header"
    if is_attachment_table_like_text(normalized):
        return "table_like_row"
    return "body_row"


def _looks_like_attachment_descriptive_header(text: str) -> bool:
    hangul_count = len(re.findall(r"[가-힣]", text))
    digit_count = len(re.findall(r"\d", text))
    if hangul_count < 4 or digit_count > 2:
        return False
    return any(
        keyword in text
        for keyword in (
            "광원",
            "방사기준",
            "전도 내성",
            "표기 기준",
            "설치 기준",
            "성능 기준",
            "반사성능",
            "제동능력 기준",
        )
    )


def _attachment_marker(text: str, line_index: int) -> str:
    marker = slugify(text)[:48]
    return f"{marker or 'attachment'}-{line_index}"


def _document_record(
    *,
    collection: str,
    document_id: str,
    title: str,
    source_file: str,
    source_hash: str,
    source_language: str,
    jurisdiction: str,
    parser_mode: str,
    regulatory_layer: str,
    source_url: str | None,
    page_count: int | None = None,
    sectno: str | None = None,
    subject: str | None = None,
    document_kind: str | None = None,
    is_attachment: bool = False,
    attachment_bucket: str | None = None,
    reference_articles: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "collection_id": collection,
        "title": title,
        "source_file": source_file,
        "source_hash": source_hash,
        "source_language": source_language,
        "jurisdiction": jurisdiction,
        "parser_mode": parser_mode,
        "regulatory_layer": regulatory_layer,
        "source_url": source_url,
        "page_count": page_count,
        "sectno": sectno,
        "subject": subject,
        "document_kind": document_kind,
        "is_attachment": is_attachment,
        "attachment_bucket": attachment_bucket,
        "reference_articles": reference_articles or [],
    }


def _segment_pdf_ece_lines(segments: list[dict[str, Any]], *, title: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    current_annex_marker: str | None = None
    current_annex_heading: str | None = None

    for segment in segments:
        text = normalize_whitespace(str(segment.get("text") or ""))
        if not text or _is_pdf_ece_noise_line(text=text, title=title):
            continue

        annex_marker = _ece_annex_marker(text)
        if annex_marker is not None:
            current_annex_marker = annex_marker
            current_annex_heading = text
            out.append(
                {
                    "text": text,
                    "page_no": segment.get("page_no"),
                    "marker_override": annex_marker,
                    "allow_clause_marker_fallback": False,
                    "document_kind": "annex",
                    "attachment_section": current_annex_heading,
                }
            )
            continue

        clause_marker = _ece_clause_marker(text)
        if clause_marker is not None:
            marker = f"{current_annex_marker}-{clause_marker}" if current_annex_marker else clause_marker
            out.append(
                {
                    "text": text,
                    "page_no": segment.get("page_no"),
                    "marker_override": marker,
                    "allow_clause_marker_fallback": False,
                    "document_kind": "annex_clause" if current_annex_marker else "article",
                    "attachment_section": current_annex_heading,
                }
            )
            continue

        out.append(
            {
                "text": text,
                "page_no": segment.get("page_no"),
                "marker_override": None,
                "allow_clause_marker_fallback": False,
                "document_kind": "annex_clause" if current_annex_marker else "article",
                "attachment_section": current_annex_heading,
            }
        )

    return out


def _is_ece_annex_heading(text: str) -> bool:
    return re.match(r"^(ANNEX|Appendix|APPENDIX|Annex)\s+[A-Z0-9IVX]+(?:\b|[\s:.-])", text, re.IGNORECASE) is not None


def _ece_annex_marker(text: str) -> str | None:
    if not _is_ece_annex_heading(text):
        return None
    match = re.match(r"^(ANNEX|Appendix|APPENDIX|Annex)\s+([A-Z0-9IVX]+)", text, re.IGNORECASE)
    if match is None:
        return None
    prefix = "appendix" if match.group(1).lower().startswith("appendix") else "annex"
    return f"{prefix}-{slugify(match.group(2))}"


def _ece_clause_marker(text: str) -> str | None:
    if match := re.match(r"^(\d+(?:\.\d+){0,4})\.(?:\s*$|\s+[A-Za-z(][^\n]*$)", text):
        return match.group(1)
    if match := re.match(r"^(\(\d+\))", text):
        return match.group(1)
    if match := re.match(r"^(\([a-z]\))", text, re.IGNORECASE):
        return match.group(1)
    return None


def _is_pdf_ece_noise_line(*, text: str, title: str) -> bool:
    if re.fullmatch(r"\d+", text):
        return True
    if title and normalize_whitespace(text).casefold() == normalize_whitespace(title).casefold():
        return False
    return False


def _clause_marker(text: str) -> str | None:
    patterns = [
        r"^(S\d+(?:\.\d+)*)\b",
        r"^(제\d+조(?:의\d+)?)",
        r"^(\d+(?:\.\d+)*)\b",
        r"^(Article\s+\d+(?:-\d+)?)",
        r"^(\(\d+\))",
        r"^(\([a-z]\))",
    ]
    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _normalize_marker(marker: str) -> str:
    return slugify(normalize_classifier_text(marker).replace("(", "").replace(")", ""))


def _kmvss_segment_marker(text: str) -> str | None:
    if match := re.match(r"^(제\d+조(?:의\d+)?)", text):
        return match.group(1)
    if match := re.match(r"^\[([①②③④⑤⑥⑦⑧⑨⑩])\]", text):
        return f"paragraph-{_circled_to_number(match.group(1))}"
    if match := re.match(r"^([①②③④⑤⑥⑦⑧⑨⑩])", text):
        return f"paragraph-{_circled_to_number(match.group(1))}"
    if match := re.match(r"^(\d+)\.\s*(\d+)\.", text):
        return f"item-{match.group(1)}-{match.group(2)}"
    if match := re.match(r"^(\d+)\.", text):
        return f"item-{match.group(1)}"
    if match := re.match(r"^([가나다라마바사아자차카타파하])\.", text):
        return f"subitem-{match.group(1)}"
    return None


def _circled_to_number(value: str) -> str:
    mapping = {
        "①": "1",
        "②": "2",
        "③": "3",
        "④": "4",
        "⑤": "5",
        "⑥": "6",
        "⑦": "7",
        "⑧": "8",
        "⑨": "9",
        "⑩": "10",
    }
    return mapping.get(value, value)


def _pdf_title(stem: str, first_page_lines: list[str]) -> str:
    for line in first_page_lines:
        if len(line) > 10:
            return line
    return stem.replace("_", " ")


def _pdf_collection_title(*, collection: str, stem: str, first_page_lines: list[str]) -> str:
    if collection == "pdf_ece":
        return _pdf_ece_title(stem=stem, first_page_lines=first_page_lines)
    return _pdf_title(stem, first_page_lines)


def _pdf_ece_title(*, stem: str, first_page_lines: list[str]) -> str:
    for line in first_page_lines:
        lowered = line.lower()
        if (
            re.search(r"\b(?:unece|ece)\s+r\d+\b", lowered)
            or "advanced emergency braking" in lowered
            or "accident emergency call" in lowered
            or "collision protection" in lowered
            or "electric power train" in lowered
            or "pedestrian safety" in lowered
            or "door latches and hinges" in lowered
        ):
            return _normalize_pdf_ece_title(line)
    return _normalize_pdf_ece_title(stem.replace("_", " "))


def _normalize_pdf_ece_title(value: str) -> str:
    title = normalize_whitespace(value.replace("_", " "))
    title = re.sub(r"\s*-\s*Rev0 English$", "", title, flags=re.IGNORECASE)
    if regulation_match := re.search(r"Regulation(?:\s+No\.?|\s*:\s*)(\d+)", title, re.IGNORECASE):
        regulation_no = regulation_match.group(1)
        if re.match(rf"^ECE\s+R{regulation_no}\b", title, re.IGNORECASE):
            title = re.sub(rf"^ECE\s+R{regulation_no}\b", f"UNECE R{regulation_no}", title, count=1, flags=re.IGNORECASE)
        elif not re.search(rf"\bR{regulation_no}\b", title, re.IGNORECASE):
            title = f"UNECE R{regulation_no} {title}"
    return title


def _markdown_title(text: str, *, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _text_or_default(value: str | None, fallback: str) -> str:
    return normalize_whitespace(value or fallback)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relpath(path: Path, project_root: Path) -> str:
    return str(path.relative_to(project_root)).replace("\\", "/")
