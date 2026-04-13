#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml


REQUIRED_FILES = [
    "docs/architecture/adr/ADR-0001-classification-model.md",
    "docs/architecture/adr/ADR-0002-regulation-unit-granularity.md",
    "docs/architecture/adr/ADR-0003-authoritative-source-policy.md",
    "docs/architecture/adr/ADR-0004-obsidian-note-contract.md",
    "taxonomy/phase_registry.yaml",
    "taxonomy/functional_domains.yaml",
    "taxonomy/in_crash_browse_buckets.yaml",
    "taxonomy/compat_active_safety_v1.yaml",
    "taxonomy/compat_passive_buckets_v1.yaml",
    "taxonomy/crosswalk_v1_to_v2.yaml",
    "schemas/regulation_unit.schema.json",
    "schemas/note_frontmatter.schema.json",
    "sources/authority_registry.yaml",
    "sources/document_inventory.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def main() -> int:
    root = Path(parse_args().project_root).resolve()
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    if errors:
        print("Design package check failed.")
        for error in errors:
            print(f"- {error}")
        return 1

    authority_registry = yaml.safe_load((root / "sources" / "authority_registry.yaml").read_text(encoding="utf-8")) or {}
    if not isinstance(authority_registry.get("sources"), list):
        errors.append("authority_registry.yaml must define a `sources` list")
    else:
        for row in authority_registry["sources"]:
            for field in (
                "jurisdiction",
                "title",
                "source_type",
                "official_status",
                "original_url",
                "snapshot_date",
                "parser_strategy",
                "checksum",
                "notes",
            ):
                if not str(row.get(field) or "").strip():
                    errors.append(f"authority_registry.yaml missing `{field}` for `{row.get('source_id')}`")

    with (root / "sources" / "document_inventory.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        errors.append("document_inventory.csv must contain at least one row")
    else:
        for field in (
            "jurisdiction",
            "title",
            "source_type",
            "official_status",
            "original_url",
            "snapshot_date",
            "parser_strategy",
            "checksum",
            "notes",
        ):
            if field not in rows[0]:
                errors.append(f"document_inventory.csv missing required column `{field}`")

    regulation_unit = json.loads((root / "schemas" / "regulation_unit.schema.json").read_text(encoding="utf-8"))
    note_frontmatter = json.loads((root / "schemas" / "note_frontmatter.schema.json").read_text(encoding="utf-8"))
    if "phase" not in regulation_unit.get("required", []):
        errors.append("regulation_unit.schema.json must require `phase`")
    if "note_type" not in note_frontmatter.get("required", []):
        errors.append("note_frontmatter.schema.json must require `note_type`")

    phase_registry = yaml.safe_load((root / "taxonomy" / "phase_registry.yaml").read_text(encoding="utf-8")) or {}
    phases = {row.get("id") for row in phase_registry.get("phases") or [] if isinstance(row, dict)}
    expected_phases = {"pre_crash", "in_crash", "post_crash", "cross_phase", "non_phase_admin"}
    if phases != expected_phases:
        errors.append(f"phase_registry.yaml mismatch: {sorted(phases)}")

    browse_registry = yaml.safe_load((root / "taxonomy" / "in_crash_browse_buckets.yaml").read_text(encoding="utf-8")) or {}
    browse_ids = {row.get("bucket_id") for row in browse_registry.get("browse_buckets") or [] if isinstance(row, dict)}
    if len(browse_ids) != 16:
        errors.append(f"in_crash_browse_buckets.yaml must define exactly 16 buckets, found {len(browse_ids)}")

    if errors:
        print("Design package check failed.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Design package check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
