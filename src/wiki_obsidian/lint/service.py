from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.ids import build_run_id
from wiki_obsidian.verify.service import run_checks


def lint_reflect(
    *,
    project_root: str | Path | None = None,
    collection: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("lint", collection or "all")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    results = run_checks(
        check_names=["frontmatter", "links", "provenance", "boundaries", "note-ids"],
        project_root=settings.paths.project_root,
    )
    pages = _load_knowledge_pages(settings.paths.wiki_root, collection=collection)
    duplicate_titles = _duplicate_titles(pages)
    orphan_units = _orphan_units(pages)
    phase_counts = Counter(str(page["frontmatter"].get("phase") or "unknown") for page in pages if page["frontmatter"].get("phase"))
    payload = {
        "run_id": active_run_id,
        "collection": collection,
        "status": "passed" if all(result["passed"] for result in results) else "failed",
        "checks": results,
        "duplicate_titles": duplicate_titles,
        "orphan_units": orphan_units,
        "phase_counts": dict(sorted(phase_counts.items())),
        "open_risks": _open_risks(duplicate_titles, orphan_units),
    }
    report_path = write_json(reports_root / "lint_reflect_report.json", payload)
    return payload | {"report_path": str(report_path)}


def _load_knowledge_pages(wiki_root: Path, *, collection: str | None) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, body = parse_frontmatter_file(path)
        if str(frontmatter.get("record_layer") or "knowledge") != "knowledge":
            continue
        if collection and str(frontmatter.get("source_collection") or "") not in {"", collection}:
            continue
        pages.append({"path": path, "frontmatter": frontmatter, "body": body})
    return pages


def _duplicate_titles(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        grouped[str(page["frontmatter"].get("title") or page["path"].stem)].append(str(page["path"]))
    return [{"title": title, "paths": paths} for title, paths in grouped.items() if len(paths) > 1]


def _orphan_units(pages: list[dict[str, Any]]) -> list[str]:
    unit_refs = {
        str(page["path"].relative_to(page["path"].parents[2]).as_posix()).removeprefix("wiki/").removesuffix(".md")
        for page in pages
        if str(page["frontmatter"].get("note_type") or "") == "regulation_unit"
    }
    inbound = Counter()
    for page in pages:
        for ref in unit_refs:
            if f"[[{ref}]]" in page["body"]:
                inbound[ref] += 1
    return sorted(ref for ref in unit_refs if inbound[ref] == 0)


def _open_risks(duplicate_titles: list[dict[str, Any]], orphan_units: list[str]) -> list[str]:
    risks: list[str] = []
    if duplicate_titles:
        risks.append(f"duplicate_title_groups={len(duplicate_titles)}")
    if orphan_units:
        risks.append(f"orphan_units={len(orphan_units)}")
    return risks
