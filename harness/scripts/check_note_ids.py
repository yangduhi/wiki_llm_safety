#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import yaml


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


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in sorted((root / "wiki").rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter = parse_frontmatter(path)
        note_id = str(frontmatter.get("id") or "")
        if note_id:
            grouped[note_id].append(path.relative_to(root).as_posix())

    duplicates = {note_id: paths for note_id, paths in grouped.items() if len(paths) > 1}
    if duplicates:
        print("Note ID check failed:")
        for note_id, paths in sorted(duplicates.items()):
            print(f"  - {note_id}: {paths}")
        return 1

    print("Note ID check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
