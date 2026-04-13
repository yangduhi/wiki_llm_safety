#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

EXCLUDE_FILENAMES = {"README.md", "INDEX.md", "LOG.md", ".gitkeep"}
MANAGEMENT_ROOTS = [("docs", "operations"), ("docs", "architecture"), ("docs", "decisions")]


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
    errors: list[str] = []

    for path in sorted((root / "wiki").rglob("*.md")):
        if path.name in EXCLUDE_FILENAMES or "_templates" in path.parts:
            continue
        frontmatter = parse_frontmatter(path)
        rel = path.relative_to(root).as_posix()
        if str(frontmatter.get("record_layer") or "") != "knowledge":
            errors.append(f"{rel}: non-knowledge page must not live under wiki/")

    for base in MANAGEMENT_ROOTS:
        management_root = root.joinpath(*base)
        if not management_root.exists():
            continue
        for path in sorted(management_root.rglob("*.md")):
            if path.name in EXCLUDE_FILENAMES:
                continue
            frontmatter = parse_frontmatter(path)
            rel = path.relative_to(root).as_posix()
            if frontmatter and str(frontmatter.get("record_layer") or "") != "operations":
                errors.append(f"{rel}: management document should declare `record_layer: operations`")

    index_text = (root / "index.md").read_text(encoding="utf-8") if (root / "index.md").exists() else ""
    if "docs/operations/" in index_text or "docs/architecture/" in index_text:
        errors.append("index.md: management path leakage detected")

    if errors:
        print("Layer boundary check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Layer boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
