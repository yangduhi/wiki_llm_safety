#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

CORE_GENERATED_BASELINE_FILES = [
    "docs/operations/INDEX.md",
    "docs/operations/dashboards/coverage-by-jurisdiction.md",
    "docs/operations/dashboards/coverage-by-phase.md",
    "docs/operations/dashboards/calibration-phase-delta.md",
    "docs/operations/dashboards/coverage-by-functional-domain.md",
    "docs/operations/dashboards/in-crash-browse-coverage.md",
    "docs/operations/dashboards/classification-review-queue.md",
    "docs/operations/dashboards/provenance-review-queue.md",
    "docs/operations/dashboards/missing-provenance.md",
    "docs/operations/dashboards/recently-changed-notes.md",
    "docs/operations/dashboards/recent-pilot-mapping-changes.md",
    "docs/operations/dashboards/source-authority-monitor.md",
    "docs/operations/pilot/reclassification_unit_vs_document_delta.md",
    "wiki/indexes/jurisdiction-hub.md",
    "wiki/indexes/phase-hub.md",
    "wiki/indexes/functional-domain-hub.md",
    "wiki/indexes/in-crash-browse-hub.md",
    "wiki/indexes/approval-and-governance-hub.md",
    "index.md",
]

# Builder-owned graph surfaces are committed generated artifacts in the Git
# contract. Human-authored graph docs under docs/obsidian_graph*.md are tracked
# operations docs, but they are checked via discovery coverage rather than the
# freshness baseline below.
GENERATED_GRAPH_SURFACE_FILES = [
    "docs/obsidian_graph_validation.md",
    "docs/obsidian_graph_relation_decisions.md",
    "docs/obsidian_graph_attach_readiness.md",
    "docs/obsidian_graph_coverage_matrix.md",
    "docs/obsidian_graph_review_queue.md",
    "docs/obsidian_graph_v1_2_plan.md",
    "wiki/indexes/graph-home.md",
    "wiki/indexes/graph-cluster-occupant-protection.md",
    "wiki/indexes/graph-cluster-structural-retention-and-egress.md",
    "wiki/indexes/graph-cluster-visibility-and-glazing.md",
    "wiki/indexes/graph-cluster-battery-fire-and-electrical-safety.md",
    "wiki/indexes/graph-cluster-vru-and-external-protection.md",
    "wiki/indexes/graph-cluster-approval-and-governance.md",
    "wiki/indexes/current-wiki-visualization.md",
]
GENERATED_BASELINE_FILES = [*CORE_GENERATED_BASELINE_FILES, *GENERATED_GRAPH_SURFACE_FILES]

LEGACY_FILES = [
    "docs/operations/dashboards/in-crash-browse-buckets.md",
    "docs/operations/dashboards/needs-review-queue.md",
]

REQUIRED_INDEX_LINKS = [
    "wiki/indexes/jurisdiction-hub.md",
    "wiki/indexes/phase-hub.md",
    "wiki/indexes/functional-domain-hub.md",
    "wiki/indexes/in-crash-browse-hub.md",
    "wiki/indexes/approval-and-governance-hub.md",
]


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


def iter_official_graph_docs(root: Path) -> list[Path]:
    return sorted((root / "docs").glob("obsidian_graph*.md"))


def main() -> int:
    root = Path(parse_args().project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in GENERATED_BASELINE_FILES:
        if not (root / rel).exists():
            errors.append(f"missing generated file: {rel}")

    for rel in LEGACY_FILES:
        if (root / rel).exists():
            errors.append(f"legacy generated file should be removed: {rel}")

    index_text = (root / "index.md").read_text(encoding="utf-8") if (root / "index.md").exists() else ""
    for rel in REQUIRED_INDEX_LINKS:
        if rel not in index_text:
            errors.append(f"index.md missing browse hub link: {rel}")

    operations_index_text = (root / "docs" / "operations" / "INDEX.md").read_text(encoding="utf-8") if (root / "docs" / "operations" / "INDEX.md").exists() else ""
    for path in iter_official_graph_docs(root):
        rel = path.relative_to(root).as_posix()
        if rel not in operations_index_text:
            errors.append(f"operations index missing graph doc link: {rel}")

    in_crash_hub = root / "wiki" / "indexes" / "in-crash-browse-hub.md"
    if in_crash_hub.exists():
        body = in_crash_hub.read_text(encoding="utf-8")
        for match in WIKILINK_RE.finditer(body):
            target = match.group(1).strip()
            if not target.startswith(("regulation_documents/", "regulation_units/")):
                continue
            target_path = root / "wiki" / f"{target}.md"
            if not target_path.exists():
                continue
            frontmatter = parse_frontmatter(target_path)
            note_type = str(frontmatter.get("note_type") or "")
            if note_type in {"regulation_document", "regulation_unit"} and str(frontmatter.get("phase") or "") != "in_crash":
                errors.append(f"in-crash browse hub links non-in_crash note: {target}")

    pseudo_units = []
    for path in sorted((root / "wiki" / "regulation_units").glob("*.md")):
        frontmatter = parse_frontmatter(path)
        if str(frontmatter.get("clause_path") or "") == "document" or str(frontmatter.get("id") or "").endswith("-document"):
            pseudo_units.append(path.relative_to(root).as_posix())
    if pseudo_units:
        warnings.append(f"pseudo document units still present: {len(pseudo_units)}")

    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")
    if errors:
        print("Generated surface check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Generated surface check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
