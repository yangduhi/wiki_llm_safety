#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml

EXCLUDE_DIRS = {"_templates"}
EXCLUDE_FILENAMES = {"README.md", ".gitkeep"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def iter_pages(root: Path):
    wiki_root = root / "wiki"
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILENAMES:
            continue
        yield path


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    errors: list[str] = []

    for path in iter_pages(root):
        frontmatter = parse_frontmatter(path)
        rel = path.relative_to(root).as_posix()
        provenance = frontmatter.get("provenance") or {}
        source_files = provenance.get("source_files", frontmatter.get("source_files", []))
        source_hashes = provenance.get("source_hashes", frontmatter.get("source_hashes", {}))
        note_type = str(frontmatter.get("note_type") or "")

        if note_type in {"regulation_document", "regulation_unit"} and not provenance:
            errors.append(f"{rel}: canonical note is missing provenance")
            continue

        if source_files and not isinstance(source_files, list):
            errors.append(f"{rel}: `source_files` must be a list")
            continue
        if source_hashes and not isinstance(source_hashes, dict):
            errors.append(f"{rel}: `source_hashes` must be a mapping")
            continue

        for raw_path in source_files or []:
            if not isinstance(raw_path, str):
                errors.append(f"{rel}: `source_files` entries must be strings")
                continue
            candidate = Path(raw_path)
            if candidate.is_absolute():
                errors.append(f"{rel}: `source_files` must use repository-relative paths")
                continue
            absolute = root / candidate
            if not absolute.exists():
                errors.append(f"{rel}: missing source file `{raw_path}`")
                continue
            expected_hash = source_hashes.get(raw_path)
            if expected_hash is None:
                errors.append(f"{rel}: missing source hash for `{raw_path}`")
                continue
            actual_hash = sha256_file(absolute)
            if str(expected_hash).lower() != actual_hash.lower():
                errors.append(f"{rel}: source hash mismatch for `{raw_path}`")

    if errors:
        print("Provenance check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Provenance check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
