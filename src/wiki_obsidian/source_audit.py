from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

import yaml

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.ids import build_run_id


def source_audit(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
    write_baseline: bool = False,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("source-audit")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    manifests_root = ensure_dir(settings.paths.manifests_root)

    registry_payload = yaml.safe_load(settings.paths.authority_registry.read_text(encoding="utf-8")) or {}
    registry_rows = registry_payload.get("sources") or []
    with settings.paths.document_inventory.open("r", encoding="utf-8", newline="") as handle:
        inventory_rows = list(csv.DictReader(handle))

    registry_ids = {str(row.get("source_id")) for row in registry_rows if isinstance(row, dict)}
    inventory_ids = {str(row.get("source_id")) for row in inventory_rows}
    raw_manifest = _raw_manifest(settings.paths.collections_root)

    payload = {
        "run_id": active_run_id,
        "registry_count": len(registry_rows),
        "inventory_count": len(inventory_rows),
        "registry_only_ids": sorted(registry_ids - inventory_ids),
        "inventory_only_ids": sorted(inventory_ids - registry_ids),
        "raw_file_count": len(raw_manifest),
        "baseline_written": False,
    }
    current_manifest_path = write_json(manifests_root / "raw_manifest_current.json", raw_manifest)

    baseline_path = None
    if write_baseline:
        baseline_path = write_json(manifests_root / "raw_manifest_baseline.json", raw_manifest)
        payload["baseline_written"] = True

    report_path = write_json(reports_root / "source_audit_report.json", payload)

    return payload | {
        "report_path": str(report_path),
        "current_manifest_path": str(current_manifest_path),
        "baseline_path": str(baseline_path) if baseline_path else None,
    }


def build_raw_manifest(project_root: str | Path | None = None) -> list[dict[str, str]]:
    settings = load_project_settings(project_root)
    return _raw_manifest(settings.paths.collections_root)


def _raw_manifest(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        rows.append(
            {
                "path": str(path.relative_to(root.parents[1])).replace("\\", "/"),
                "sha256": _sha256_file(path),
            }
        )
    return rows


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
