#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

EXCLUDE_DIRS = {"_templates"}
EXCLUDE_FILENAMES = {"README.md", ".gitkeep"}


@dataclass(frozen=True)
class PageEntry:
    title: str
    rel: str
    summary: str
    status: str
    frontmatter: dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def load_taxonomy(root: Path) -> list[tuple[str, str, tuple[str, ...], bool]]:
    payload = yaml.safe_load((root / "configs" / "wiki" / "taxonomy.yaml").read_text(encoding="utf-8")) or {}
    ordered: list[tuple[str, str, tuple[str, ...], bool]] = []
    for note_type, config in (payload.get("types") or {}).items():
        ordered.append(
            (
                note_type,
                str(config.get("index_section") or note_type.title()),
                tuple(str(config.get("dir") or "").split("/")),
                bool(config.get("compact")),
            )
        )
    return ordered


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    block = text[4:end]
    try:
        payload = yaml.safe_load(block) or {}
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}


def infer_section(rel: Path, ordered_types: list[tuple[str, str, tuple[str, ...], bool]]) -> str:
    parts = rel.parts
    for _, heading, directory, _ in ordered_types:
        if directory and parts[: len(directory)] == directory:
            return heading
    return "Other"


def collect_pages(root: Path, ordered_types: list[tuple[str, str, tuple[str, ...], bool]]) -> dict[str, list[PageEntry]]:
    wiki_root = root / "wiki"
    grouped: dict[str, list[PageEntry]] = defaultdict(list)
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILENAMES:
            continue
        frontmatter = parse_frontmatter(path)
        if str(frontmatter.get("record_layer") or "") != "knowledge":
            continue
        title = str(frontmatter.get("title") or path.stem.replace("-", " ").title())
        summary = str(frontmatter.get("summary") or "").strip()
        status = str(frontmatter.get("status") or "unknown")
        heading = infer_section(rel, ordered_types)
        grouped[heading].append(PageEntry(title=title, rel=rel.as_posix(), summary=summary, status=status, frontmatter=frontmatter))
    return grouped


def render_compact(lines: list[str], pages: list[PageEntry], label: str) -> None:
    lines.append(f"- page_count: {len(pages)}")
    by_phase = defaultdict(int)
    by_jurisdiction = defaultdict(int)
    for page in pages:
        by_phase[str(page.frontmatter.get("phase") or "unknown")] += 1
        by_jurisdiction[str(page.frontmatter.get("jurisdiction") or "unknown")] += 1
    lines.append(f"- phase_counts: {dict(sorted(by_phase.items()))}")
    lines.append(f"- jurisdiction_counts: {dict(sorted(by_jurisdiction.items()))}")
    for entry in pages[:30]:
        lines.append(f"- [{entry.title}](wiki/{entry.rel}) - {entry.summary or 'No summary.'} (`status: {entry.status}`)")


def render(root: Path) -> str:
    ordered_types = load_taxonomy(root)
    grouped = collect_pages(root, ordered_types)
    ordered_sections = [(heading, compact) for _, heading, _, compact in ordered_types]
    lines = [
        "# Index",
        "",
        "> Auto-generated catalog entrypoint for the Obsidian LLM wiki. Read this file before drilling into individual notes.",
        "",
        "## How to use this file",
        "1. Start here.",
        "2. Identify the smallest relevant note set.",
        "3. Open raw sources only when grounded notes are insufficient.",
    ]
    for heading, compact in ordered_sections:
        lines.extend(["", f"## {heading}", ""])
        pages = grouped.get(heading, [])
        if not pages:
            lines.extend(["_None yet._", ""])
            continue
        if compact:
            render_compact(lines, pages, heading)
            lines.append("")
            continue
        for entry in pages:
            suffix = f" - {entry.summary}" if entry.summary else ""
            lines.append(f"- [{entry.title}](wiki/{entry.rel}){suffix} (`status: {entry.status}`)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    index_path = root / "index.md"
    index_path.write_text(render(root), encoding="utf-8")
    print(f"Wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
