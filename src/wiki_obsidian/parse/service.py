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
from wiki_obsidian.utils.text import normalize_whitespace, slugify


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
    segments = [{"text": normalize_whitespace(line), "page_no": None} for line in content.splitlines() if normalize_whitespace(line)]
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


def _parse_pdf_text_first(*, path: Path, collection: str, profile: dict[str, Any], project_root: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    try:
        source_hash = _sha256_file(path)
        source_relpath = _relpath(path, project_root)
        first_page_lines: list[str] = []
        segments: list[dict[str, Any]] = []
        for page_index in range(doc.page_count):
            page = doc[page_index]
            lines = [normalize_whitespace(line) for line in page.get_text("text").splitlines() if normalize_whitespace(line)]
            if page_index == 0:
                first_page_lines = lines[:20]
            for line in lines:
                segments.append({"text": line, "page_no": page_index + 1})
        title = _pdf_title(path.stem, first_page_lines)
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
) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for segment in segments:
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        marker = _clause_marker(text)
        if marker is not None:
            if current is not None:
                units.append(_finalize_unit(current, title=title, document_id=document_id, collection=collection, source_file=source_file, source_hash=source_hash, source_language=source_language, jurisdiction=jurisdiction, regulatory_layer=regulatory_layer, source_url=source_url))
            current = {
                "marker": marker,
                "lines": [text],
                "page_start": segment.get("page_no"),
                "page_end": segment.get("page_no"),
            }
        elif current is not None:
            current["lines"].append(text)
            if segment.get("page_no"):
                current["page_end"] = segment["page_no"]
        else:
            current = {
                "marker": "document",
                "lines": [text],
                "page_start": segment.get("page_no"),
                "page_end": segment.get("page_no"),
            }
    if current is not None:
        units.append(_finalize_unit(current, title=title, document_id=document_id, collection=collection, source_file=source_file, source_hash=source_hash, source_language=source_language, jurisdiction=jurisdiction, regulatory_layer=regulatory_layer, source_url=source_url))
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
        "statement": statement,
        "basis": basis,
        "page_start": current.get("page_start"),
        "page_end": current.get("page_end"),
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
    }


def _clause_marker(text: str) -> str | None:
    patterns = [
        r"^(S\d+(?:\.\d+)*)\b",
        r"^(제\d+조)",
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
    return slugify(marker.strip().replace("(", "").replace(")", ""))


def _pdf_title(stem: str, first_page_lines: list[str]) -> str:
    for line in first_page_lines:
        if len(line) > 10:
            return line
    return stem.replace("_", " ")


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
