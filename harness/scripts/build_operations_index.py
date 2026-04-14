#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

EXCLUDE_FILENAMES = {".gitkeep"}
BUCKETS = {
    "Architecture ADRs": ("docs", "architecture", "adr"),
    "Plans": ("docs", "operations", "plans"),
    "Dashboards": ("docs", "operations", "dashboards"),
    "Notes": ("docs", "operations", "notes"),
    "Graph Operations": ("docs",),
    "Pilot": ("docs", "operations", "pilot"),
    "Risks": ("docs", "operations", "risks"),
    "Archive": ("docs", "operations", "archive"),
}


@dataclass(frozen=True)
class Entry:
    title: str
    rel: str
    summary: str
    status: str


def fallback_title(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


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


def collect_entries(root: Path) -> dict[str, list[Entry]]:
    grouped: dict[str, list[Entry]] = defaultdict(list)
    for bucket, parts in BUCKETS.items():
        if bucket == "Graph Operations":
            paths = sorted((root / "docs").glob("obsidian_graph*.md"))
        else:
            bucket_root = root.joinpath(*parts)
            if not bucket_root.exists():
                continue
            paths = sorted(bucket_root.rglob("*.md"))
        for path in paths:
            if path.name in EXCLUDE_FILENAMES:
                continue
            frontmatter = parse_frontmatter(path)
            title = str(frontmatter.get("title") or fallback_title(path))
            summary = str(frontmatter.get("summary") or "").strip()
            status = str(frontmatter.get("status") or "active")
            grouped[bucket].append(Entry(title=title, rel=path.relative_to(root).as_posix(), summary=summary, status=status))
    return grouped


def render(root: Path) -> str:
    grouped = collect_entries(root)
    lines = [
        "# Operations Index",
        "",
        "> Auto-generated catalog of management and governance records. These pages are excluded from live knowledge grounding.",
    ]
    for heading in BUCKETS:
        lines.extend(["", f"## {heading}", ""])
        entries = grouped.get(heading, [])
        if not entries:
            lines.extend(["_None yet._", ""])
            continue
        for entry in entries:
            suffix = f" - {entry.summary}" if entry.summary else ""
            lines.append(f"- [{entry.title}]({entry.rel}){suffix} (`status: {entry.status}`)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    out = root / "docs" / "operations" / "INDEX.md"
    out.write_text(render(root), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
