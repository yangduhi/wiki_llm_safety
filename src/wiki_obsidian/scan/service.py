from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any

from wiki_obsidian.profiles import load_collection_profile
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.ids import build_run_id


def scan_sources(
    *,
    project_root: str | Path | None = None,
    collection: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    profile = load_collection_profile(collection, project_root=settings.paths.project_root) if collection else None
    active_run_id = run_id or build_run_id("scan", collection or "all")
    run_root = ensure_dir(settings.paths.scan_root / "runs" / active_run_id)
    ensure_dir(settings.paths.manifests_root / "runs")

    source_root = settings.paths.collections_root / collection if collection else settings.paths.collections_root
    files = [path for path in sorted(source_root.rglob("*")) if path.is_file() and path.name != ".gitkeep"]
    extension_counts = Counter(path.suffix.lower().lstrip(".") or "no_extension" for path in files)
    xml_root_counts: Counter[str] = Counter()
    malformed_files: list[dict[str, str]] = []

    for path in files:
        if path.suffix.lower() != ".xml":
            continue
        try:
            xml_root_counts[ET.parse(path).getroot().tag] += 1
        except Exception as exc:
            malformed_files.append(
                {
                    "path": str(path.relative_to(settings.paths.project_root)).replace("\\", "/"),
                    "error": str(exc),
                }
            )

    payload = {
        "run_id": active_run_id,
        "collection_id": collection,
        "source_root": str(source_root),
        "file_count": len(files),
        "format_counts": dict(sorted(extension_counts.items())),
        "xml_root_counts": dict(sorted(xml_root_counts.items())),
        "malformed_files": malformed_files,
        "input_files": [str(path.relative_to(settings.paths.project_root)).replace("\\", "/") for path in files],
        "language_detected": profile.get("language") if profile else None,
        "parser_mode": profile.get("parser_mode") if profile else None,
        "collection_kind": profile.get("collection_kind") if profile else None,
        "scanned_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "status": "scanned",
    }
    report_path = write_json(run_root / "scan_report.json", payload)
    manifest_path = write_json(settings.paths.manifests_root / "runs" / f"{active_run_id}.json", payload)
    return payload | {"report_path": str(report_path), "manifest_path": str(manifest_path)}
