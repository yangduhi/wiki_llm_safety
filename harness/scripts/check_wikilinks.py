#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

EXCLUDE_DIRS = {"_templates"}
EXCLUDE_FILENAMES = {"README.md", ".gitkeep"}
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :]
    try:
        payload = yaml.safe_load(block) or {}
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}, body


def iter_pages(root: Path):
    wiki_root = root / "wiki"
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILENAMES:
            continue
        yield path


def target_key(path: Path, root: Path) -> str:
    rel = path.relative_to(root / "wiki").as_posix()
    return rel.removesuffix(".md")


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    pages = list(iter_pages(root))
    known_targets = {target_key(path, root) for path in pages}
    errors: list[str] = []

    for path in pages:
        _, body = parse_frontmatter(path)
        rel = path.relative_to(root).as_posix()
        for match in WIKILINK_RE.finditer(body):
            target = match.group(1).strip()
            if target and target not in known_targets:
                errors.append(f"{rel}: broken wikilink `[[{target}]]`")

    if errors:
        print("Wikilink check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Wikilink check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
