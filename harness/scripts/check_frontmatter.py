#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

EXCLUDE_DIRS = {"_templates"}
EXCLUDE_FILENAMES = {"README.md", ".gitkeep"}
BASE_REQUIRED = [
    "record_layer",
    "id",
    "note_type",
    "title",
    "summary",
    "status",
    "created",
    "updated",
    "aliases",
    "provenance",
    "confidence",
]
CANONICAL_REQUIRED = [
    "jurisdiction",
    "source_collection",
    "regulatory_layer",
    "phase",
    "functional_domain",
    "primary_topic",
    "secondary_topics",
    "browse_buckets",
    "legacy_domain",
    "effective_date",
]
STATUS_VALUES = {"draft", "reviewed", "superseded", "archived"}
CONFIDENCE_VALUES = {"low", "medium", "high"}
CANONICAL_NOTE_TYPES = {"regulation_document", "regulation_unit"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def load_taxonomy(root: Path) -> dict[str, list[str]]:
    payload = yaml.safe_load((root / "configs" / "wiki" / "taxonomy.yaml").read_text(encoding="utf-8")) or {}
    types = payload.get("types", {})
    return {
        note_type: [str(item) for item in config.get("required_headings", [])]
        for note_type, config in types.items()
    }


def load_registry_ids(root: Path, relpath: str, key: str) -> set[str]:
    payload = yaml.safe_load((root / relpath).read_text(encoding="utf-8")) or {}
    return {str(row.get(key)) for row in payload.get(key + "s", payload.get("browse_buckets", payload.get("functional_domains", []))) if isinstance(row, dict)}


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


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    note_headings = load_taxonomy(root)
    phase_ids = {row["id"] for row in (yaml.safe_load((root / "taxonomy" / "phase_registry.yaml").read_text(encoding="utf-8")) or {}).get("phases", [])}
    functional_domain_ids = {row["id"] for row in (yaml.safe_load((root / "taxonomy" / "functional_domains.yaml").read_text(encoding="utf-8")) or {}).get("functional_domains", [])}
    browse_bucket_ids = {row["bucket_id"] for row in (yaml.safe_load((root / "taxonomy" / "in_crash_browse_buckets.yaml").read_text(encoding="utf-8")) or {}).get("browse_buckets", [])}
    errors: list[str] = []

    for path in iter_pages(root):
        frontmatter, body = parse_frontmatter(path)
        rel = path.relative_to(root).as_posix()
        if not frontmatter:
            errors.append(f"{rel}: missing or invalid frontmatter")
            continue

        for key in BASE_REQUIRED:
            if key not in frontmatter:
                errors.append(f"{rel}: missing frontmatter key `{key}`")

        if str(frontmatter.get("record_layer") or "") != "knowledge":
            errors.append(f"{rel}: `record_layer` must be `knowledge` for wiki pages")

        status = str(frontmatter.get("status") or "")
        if status and status not in STATUS_VALUES:
            errors.append(f"{rel}: invalid status `{status}`")

        confidence = str(frontmatter.get("confidence") or "")
        if confidence and confidence not in CONFIDENCE_VALUES:
            errors.append(f"{rel}: invalid confidence `{confidence}`")

        note_type = str(frontmatter.get("note_type") or "")
        if note_type not in note_headings:
            errors.append(f"{rel}: unknown note_type `{note_type}`")
            continue

        if note_type in CANONICAL_NOTE_TYPES:
            for key in CANONICAL_REQUIRED:
                if key not in frontmatter:
                    errors.append(f"{rel}: missing canonical frontmatter key `{key}`")
            if str(frontmatter.get("phase") or "") not in phase_ids:
                errors.append(f"{rel}: invalid phase `{frontmatter.get('phase')}`")
            domains = frontmatter.get("functional_domain") or []
            if not isinstance(domains, list) or not domains:
                errors.append(f"{rel}: `functional_domain` must be a non-empty list")
            else:
                for domain in domains:
                    if str(domain) not in functional_domain_ids:
                        errors.append(f"{rel}: invalid functional_domain `{domain}`")
            browse_buckets = frontmatter.get("browse_buckets") or []
            if not isinstance(browse_buckets, list):
                errors.append(f"{rel}: `browse_buckets` must be a list")
            else:
                for bucket in browse_buckets:
                    if str(bucket) not in browse_bucket_ids:
                        errors.append(f"{rel}: invalid browse_bucket `{bucket}`")
            provenance = frontmatter.get("provenance")
            if not isinstance(provenance, dict):
                errors.append(f"{rel}: `provenance` must be a mapping")
            else:
                if not isinstance(provenance.get("source_files", []), list) or not provenance.get("source_files"):
                    errors.append(f"{rel}: provenance must include source_files")
                if not isinstance(provenance.get("source_hashes", {}), dict) or not provenance.get("source_hashes"):
                    errors.append(f"{rel}: provenance must include source_hashes")

        for heading in note_headings[note_type]:
            if heading not in body:
                errors.append(f"{rel}: missing heading `{heading}`")

    if errors:
        print("Frontmatter check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Frontmatter check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
