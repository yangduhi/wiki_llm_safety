from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from wiki_obsidian.ingest.service import write_analysis_page
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.ids import build_run_id


def query_writeback(
    *,
    question: str,
    project_root: str | Path | None = None,
    collection: str | None = None,
    run_id: str | None = None,
    writeback: bool = False,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("query", collection or "all")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)

    pages = _load_knowledge_pages(settings.paths.wiki_root)
    matches = _search_pages(question, pages, collection=collection)
    answer = _build_answer(question, matches)
    analysis_path = None
    if writeback:
        source_files, source_hashes = _collect_sources(matches)
        analysis_path = str(
            write_analysis_page(
                question=question,
                answer=answer,
                matched_pages=[match["page_ref"] for match in matches],
                source_files=source_files,
                source_hashes=source_hashes,
                run_id=active_run_id,
                project_root=settings.paths.project_root,
            )
        )

    payload = {
        "run_id": active_run_id,
        "collection": collection,
        "question": question,
        "writeback_requested": writeback,
        "status": "answered",
        "matched_pages": [match["page_ref"] for match in matches],
        "analysis_written": bool(analysis_path),
        "analysis_path": analysis_path,
        "answer": answer,
    }
    report_path = write_json(reports_root / "query_writeback_report.json", payload)
    return payload | {"report_path": str(report_path)}


def _load_knowledge_pages(wiki_root: Path) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, body = parse_frontmatter_file(path)
        if str(frontmatter.get("record_layer") or "knowledge") != "knowledge":
            continue
        page_ref = str(path.relative_to(wiki_root)).replace("\\", "/").removesuffix(".md")
        pages.append(
            {
                "path": path,
                "page_ref": page_ref,
                "title": str(frontmatter.get("title") or path.stem),
                "summary": str(frontmatter.get("summary") or ""),
                "body": body,
                "frontmatter": frontmatter,
            }
        )
    return pages


def _search_pages(question: str, pages: list[dict[str, Any]], *, collection: str | None) -> list[dict[str, Any]]:
    tokens = {token.lower() for token in re.findall(r"[A-Za-z0-9_]+", question)}
    scored: list[tuple[int, dict[str, Any]]] = []
    for page in pages:
        if collection and str(page["frontmatter"].get("source_collection") or "") not in {"", collection}:
            continue
        haystack = " ".join([page["title"], page["summary"], page["body"]]).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score > 0:
            scored.append((score, page))
    scored.sort(key=lambda item: (-item[0], item[1]["page_ref"]))
    return [page for _, page in scored[:8]]


def _build_answer(question: str, matches: list[dict[str, Any]]) -> str:
    if not matches:
        return f"No directly grounded wiki notes were found for `{question}`."
    lines = [f"Grounded answer draft for `{question}` based on the current wiki notes.", ""]
    for match in matches[:5]:
        lines.append(f"- `{match['title']}`: {match['summary'] or 'No summary available.'}")
    return "\n".join(lines)


def _collect_sources(matches: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    source_files: list[str] = []
    source_hashes: dict[str, str] = {}
    for match in matches:
        for source_file in match["frontmatter"].get("source_files") or []:
            if source_file not in source_files:
                source_files.append(source_file)
        for key, value in (match["frontmatter"].get("source_hashes") or {}).items():
            source_hashes[str(key)] = str(value)
    return source_files, source_hashes
