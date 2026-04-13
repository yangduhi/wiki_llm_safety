from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any

from wiki_obsidian.operations import append_operations_log, rebuild_indexes, write_operation_note
from wiki_obsidian.profiles import load_collection_profile, profile_path
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json, write_text
from wiki_obsidian.utils.ids import build_run_id


def inspect_collection(
    *,
    collection: str,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("inspect", collection)
    report_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    collection_root = settings.paths.collections_root / collection
    files = [path for path in sorted(collection_root.rglob("*")) if path.is_file() and path.name != ".gitkeep"]
    extension_counts = Counter(path.suffix.lower().lstrip(".") or "no_extension" for path in files)

    xml_root_counts: Counter[str] = Counter()
    malformed_files: list[dict[str, str]] = []
    for path in files:
        if path.suffix.lower() != ".xml":
            continue
        try:
            root_tag = ET.parse(path).getroot().tag
            xml_root_counts[root_tag] += 1
        except Exception as exc:
            malformed_files.append(
                {
                    "path": str(path.relative_to(settings.paths.project_root)).replace("\\", "/"),
                    "error": str(exc),
                }
            )

    profile = load_collection_profile(collection, project_root=settings.paths.project_root)
    payload = {
        "run_id": active_run_id,
        "collection_id": collection,
        "collection_root": str(collection_root),
        "file_count": len(files),
        "extension_counts": dict(sorted(extension_counts.items())),
        "xml_root_counts": dict(sorted(xml_root_counts.items())),
        "malformed_files": malformed_files,
        "profile_path": str(profile_path(collection, project_root=settings.paths.project_root)),
        "parser_mode": profile.get("parser_mode"),
        "language_detected": profile.get("language"),
        "encoding_notes": [
            "KMVSS XML must be treated as UTF-8 canonically even if shell rendering is noisy."
            if collection == "xml_kmvss"
            else "No special encoding issue detected from the collection profile."
        ],
        "inspected_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
    report_path = write_json(report_root / "collection_inspection.json", payload)
    return payload | {"report_path": str(report_path)}


def propose_profile(
    *,
    collection: str,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    inspection = inspect_collection(collection=collection, project_root=settings.paths.project_root, run_id=run_id)
    active_run_id = str(inspection["run_id"])
    report_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    profile = load_collection_profile(collection, project_root=settings.paths.project_root)

    proposal = {
        "run_id": active_run_id,
        "collection_id": collection,
        "inspection_report_path": inspection["report_path"],
        "recommended_profile": profile,
        "notes": _proposal_notes(collection, inspection),
    }
    json_path = write_json(report_root / "collection_profile_proposal.json", proposal)
    md_path = write_text(report_root / "collection_profile_proposal.md", _render_proposal_markdown(proposal))
    return proposal | {"json_path": str(json_path), "markdown_path": str(md_path)}


def apply_profile(
    *,
    collection: str,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("apply-profile", collection)
    profile = load_collection_profile(collection, project_root=settings.paths.project_root)
    note_path = write_operation_note(
        title=f"Applied profile for {collection}",
        summary=f"Collection profile `{collection}` validated and marked active for onboarding.",
        body_sections=[
            "## Collection",
            f"- collection_id: `{collection}`",
            "",
            "## Profile",
            f"- profile_path: `{profile_path(collection, project_root=settings.paths.project_root)}`",
            f"- parser_mode: `{profile.get('parser_mode')}`",
            f"- language: `{profile.get('language')}`",
            "",
            "## Notes",
            "- The profile file is tracked in-repo and acts as the deterministic onboarding contract.",
        ],
        project_root=settings.paths.project_root,
        slug=f"apply-profile-{collection}",
        note_id=f"operations-apply-profile-{collection}",
    )
    append_operations_log(
        title=f"Applied profile for {collection}",
        details=[
            f"- run_id: `{active_run_id}`",
            f"- note_path: `{note_path.relative_to(settings.paths.project_root).as_posix()}`",
            f"- parser_mode: `{profile.get('parser_mode')}`",
        ],
        project_root=settings.paths.project_root,
        operation="apply-profile",
    )
    rebuild_indexes(project_root=settings.paths.project_root, include_operations=True)
    return {
        "run_id": active_run_id,
        "collection_id": collection,
        "profile_path": str(profile_path(collection, project_root=settings.paths.project_root)),
        "operations_note_path": str(note_path),
        "status": "applied",
    }


def _proposal_notes(collection: str, inspection: dict[str, Any]) -> list[str]:
    notes = [f"Collection `{collection}` is modeled as its own parser profile."]
    if inspection.get("malformed_files"):
        notes.append("Malformed source files should be quarantined in reports and never rewritten in raw/.")
    if collection == "xml_fmvss":
        notes.append("Use XML section parsing with clause extraction from S-style identifiers.")
    elif collection == "xml_kmvss":
        notes.append("Use XML record parsing and derive clause boundaries from Korean numbering patterns.")
    elif collection == "pdf_ece":
        notes.append("Use text-first PDF extraction and keep review_required high for derived claims.")
    return notes


def _render_proposal_markdown(proposal: dict[str, Any]) -> str:
    profile = proposal["recommended_profile"]
    lines = [
        f"# Collection Profile Proposal `{proposal['collection_id']}`",
        "",
        f"- run_id: `{proposal['run_id']}`",
        f"- parser_mode: `{profile.get('parser_mode')}`",
        f"- language: `{profile.get('language')}`",
        "",
        "## Notes",
    ]
    lines.extend(f"- {note}" for note in proposal["notes"])
    lines.extend(["", "## Profile Preview", "```yaml"])
    import yaml

    lines.append(yaml.safe_dump(profile, sort_keys=False, allow_unicode=True).rstrip())
    lines.extend(["```", ""])
    return "\n".join(lines)

