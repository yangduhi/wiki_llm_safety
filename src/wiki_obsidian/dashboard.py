from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import csv
from pathlib import Path
from typing import Any

import yaml

from wiki_obsidian.calibration import (
    load_document_adjudications,
    load_unit_adjudications,
    summarize_document_calibration,
    summarize_unit_vs_document,
)
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, read_jsonl, write_text
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file, render_frontmatter
from wiki_obsidian.utils.ids import build_run_id

ADMIN_LAYERS = {"framework_admin", "conformity_assessment", "market_surveillance_recall"}
SCENARIO_BUCKETS = ["frontal_impact", "side_impact", "rear_impact", "rollover"]
PROTECTION_TARGET_BUCKETS = ["pedestrian_protection"]
LEGACY_DASHBOARD_FILES = [
    "in-crash-browse-buckets.md",
    "needs-review-queue.md",
]


def dashboard_refresh(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("dashboard")
    generated_on = _today()

    ensure_dir(settings.paths.operations_dashboards_root)
    ensure_dir(settings.paths.indexes_root)
    ensure_dir(settings.paths.operations_pilot_root)

    notes = _load_notes(settings.paths.wiki_root)
    visible_notes = [note for note in notes if _is_visible_knowledge_note(note)]
    visible_units = [note for note in visible_notes if _note_type(note) == "regulation_unit"]
    visible_documents = [note for note in visible_notes if _note_type(note) == "regulation_document"]

    written_operations = [
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-jurisdiction.md",
            note_id="dashboard-coverage-by-jurisdiction",
            title="Coverage by Jurisdiction",
            summary="Counts visible regulation units by jurisdiction.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_counter_lines("jurisdiction", Counter(_scalar(note, "jurisdiction") for note in visible_units)),
            dataview_query='TABLE jurisdiction, count(rows) AS notes\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nGROUP BY jurisdiction\nSORT jurisdiction ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-phase.md",
            note_id="dashboard-coverage-by-phase",
            title="Coverage by Phase",
            summary="Counts visible regulation units by canonical phase.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_counter_lines("phase", Counter(_scalar(note, "phase") for note in visible_units)),
            dataview_query='TABLE phase, count(rows) AS notes\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nGROUP BY phase\nSORT phase ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "calibration-phase-delta.md",
            note_id="dashboard-calibration-phase-delta",
            title="Calibration Phase Delta",
            summary="Delta between current and adjudicated phase decisions for the 20-document calibration set.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_calibration_delta_lines(settings.paths.operations_pilot_root / "reclassification_20_document_adjudications.jsonl"),
            dataview_query=None,
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "coverage-by-functional-domain.md",
            note_id="dashboard-coverage-by-functional-domain",
            title="Coverage by Functional Domain",
            summary="Counts visible regulation units by functional domain.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_flatten_counter_lines("functional_domain", _list_counter(visible_units, "functional_domain")),
            dataview_query='TABLE value AS functional_domain, length(rows) AS notes\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nFLATTEN functional_domain AS value\nGROUP BY value\nSORT value ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "in-crash-browse-coverage.md",
            note_id="dashboard-in-crash-browse-coverage",
            title="In-Crash Browse Coverage",
            summary="Operational coverage view for the in-crash browse taxonomy.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_browse_coverage_lines(visible_units),
            dataview_query='TABLE value AS browse_bucket, length(rows) AS notes\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document" AND phase = "in_crash"\nFLATTEN browse_buckets AS value\nGROUP BY value\nSORT value ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "classification-review-queue.md",
            note_id="dashboard-classification-review-queue",
            title="Classification Review Queue",
            summary="Regulation units needing classification review.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_classification_review_lines(visible_units),
            dataview_query='TABLE file.link, phase, functional_domain, legacy_domain, confidence\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document" AND (legacy_domain = "needs_review" OR contains(functional_domain, "other_or_review") OR confidence = "low" OR review_required = true)\nSORT updated DESC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "provenance-review-queue.md",
            note_id="dashboard-provenance-review-queue",
            title="Provenance Review Queue",
            summary="Visible regulation units with incomplete provenance metadata.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_provenance_review_lines(visible_units),
            dataview_query='TABLE file.link, source_collection, document_id, source_url\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document" AND (!provenance OR length(provenance.source_files) = 0)\nSORT updated DESC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "missing-provenance.md",
            note_id="dashboard-missing-provenance",
            title="Missing Provenance",
            summary="All visible source-grounded knowledge notes missing provenance.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_missing_provenance_lines(visible_notes),
            dataview_query='TABLE file.link, note_type, title\nFROM "wiki"\nWHERE note_type != "browse_index" AND note_type != "jurisdiction_overview" AND (!provenance OR length(provenance.source_files) = 0)\nSORT file.name ASC',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "recently-changed-notes.md",
            note_id="dashboard-recently-changed-notes",
            title="Recently Changed Notes",
            summary="Most recently updated visible knowledge notes.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_recent_lines(visible_notes),
            dataview_query='TABLE file.link, updated, note_type, phase, primary_topic\nFROM "wiki"\nWHERE note_type != "browse_index"\nSORT updated DESC\nLIMIT 25',
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "recent-pilot-mapping-changes.md",
            note_id="dashboard-recent-pilot-mapping-changes",
            title="Recent Pilot Mapping Changes",
            summary="Generated snapshot of the latest pilot mapping entries.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_recent_pilot_mapping_lines(settings.paths.operations_pilot_root / "pilot_mapping_results.jsonl"),
            dataview_query=None,
        ),
        _write_dashboard(
            settings.paths.operations_dashboards_root / "source-authority-monitor.md",
            note_id="dashboard-source-authority-monitor",
            title="Source Authority Monitor",
            summary="Generated monitor for authority registry and document inventory health.",
            run_id=active_run_id,
            data_as_of=generated_on,
            snapshot_lines=_source_authority_monitor_lines(settings.paths.authority_registry, settings.paths.document_inventory),
            dataview_query=None,
        ),
    ]

    written_hubs = [
        _write_browse_hub(
            settings.paths.indexes_root / "functional-domain-hub.md",
            note_id="browse-index-functional-domain",
            title="Functional Domain Hub",
            summary="Primary browse hub for functional_domain across visible regulation units.",
            browse_axis="functional_domain",
            run_id=active_run_id,
            snapshot_lines=[
                "- browse_role: primary",
                "- canonical_axis: functional_domain",
                f"- visible_regulation_units: {len(visible_units)}",
                f"- domains: {len(_list_counter(visible_units, 'functional_domain'))}",
            ],
            purpose_lines=[
                "> [!important] Functional domain is a primary global browse axis.",
                "> Use this hub before in-crash browse buckets when the question is about safety function or subsystem intent.",
            ],
            browse_lines=_functional_domain_browse_lines(visible_units, visible_documents),
            dataview_blocks=[("Live Listing", '```dataview\nTABLE file.link, phase, jurisdiction, primary_topic\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nFLATTEN functional_domain AS value\nGROUP BY value\nSORT value ASC\n```')],
        ),
        _write_browse_hub(
            settings.paths.indexes_root / "phase-hub.md",
            note_id="browse-index-phase",
            title="Phase Hub",
            summary="Primary browse hub for canonical phase across visible regulation units.",
            browse_axis="phase",
            run_id=active_run_id,
            snapshot_lines=[
                "- browse_role: primary",
                "- canonical_axis: phase",
                f"- visible_regulation_units: {len(visible_units)}",
                f"- phases_present: {len(Counter(_scalar(note, 'phase') for note in visible_units))}",
            ],
            purpose_lines=[
                "> [!important] Phase is the canonical global root facet.",
                "> Use this hub before any compatibility or browse-only taxonomy.",
            ],
            browse_lines=_phase_browse_lines(visible_units, visible_documents),
            dataview_blocks=[("Live Listing", '```dataview\nTABLE file.link, jurisdiction, functional_domain, primary_topic\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nGROUP BY phase\nSORT phase ASC\n```')],
        ),
        _write_browse_hub(
            settings.paths.indexes_root / "jurisdiction-hub.md",
            note_id="browse-index-jurisdiction",
            title="Jurisdiction Hub",
            summary="Browse hub for jurisdiction-specific entry into the visible regulation corpus.",
            browse_axis="jurisdiction",
            run_id=active_run_id,
            snapshot_lines=[
                "- browse_role: supporting",
                "- canonical_axis: jurisdiction",
                f"- visible_regulation_units: {len(visible_units)}",
                f"- jurisdictions_present: {len(Counter(_scalar(note, 'jurisdiction') for note in visible_units))}",
            ],
            purpose_lines=[
                "> [!info] Jurisdiction is a practical entry surface for comparative law work.",
                "> Use it alongside Phase Hub and Functional Domain Hub, not instead of them.",
            ],
            browse_lines=_jurisdiction_browse_lines(visible_units, visible_documents),
            dataview_blocks=[("Live Listing", '```dataview\nTABLE file.link, phase, functional_domain, primary_topic\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document"\nGROUP BY jurisdiction\nSORT jurisdiction ASC\n```')],
        ),
        _write_browse_hub(
            settings.paths.indexes_root / "approval-and-governance-hub.md",
            note_id="browse-index-approval-governance",
            title="Approval and Governance Hub",
            summary="Browse hub for non_phase_admin and administrative framework material.",
            browse_axis="approval_and_governance",
            run_id=active_run_id,
            snapshot_lines=[
                "- browse_role: supporting",
                "- canonical_axis: non_phase_admin + administrative regulatory layers",
                f"- visible_notes: {len(visible_notes)}",
                f"- admin_candidates: {len(_approval_governance_notes(visible_notes))}",
            ],
            purpose_lines=[
                "> [!info] This hub is for approval, conformity, surveillance, recall, and governance texts.",
                "> It prevents administrative material from being buried inside phase-oriented technical browsing.",
            ],
            browse_lines=_approval_governance_lines(visible_notes),
            dataview_blocks=[("Live Listing", '```dataview\nTABLE file.link, phase, regulatory_layer, jurisdiction\nFROM "wiki"\nWHERE note_type != "browse_index" AND (phase = "non_phase_admin" OR regulatory_layer = "framework_admin" OR regulatory_layer = "conformity_assessment" OR regulatory_layer = "market_surveillance_recall")\nSORT jurisdiction ASC, file.name ASC\n```')],
        ),
        _write_browse_hub(
            settings.paths.indexes_root / "in-crash-browse-hub.md",
            note_id="browse-index-in-crash-browse",
            title="In-Crash Browse Hub",
            summary="Secondary browse hub for the in-crash browse taxonomy only.",
            browse_axis="in_crash_browse",
            run_id=active_run_id,
            snapshot_lines=[
                "- browse_role: secondary",
                "- browse_scope: in_crash only",
                f"- visible_in_crash_units: {len([note for note in visible_units if _scalar(note, 'phase') == 'in_crash'])}",
                f"- buckets_present: {len(_list_counter([note for note in visible_units if _scalar(note, 'phase') == 'in_crash'], 'browse_buckets'))}",
            ],
            purpose_lines=[
                "> [!warning] Browse buckets are in-crash browse aids, not canonical ontology roots.",
                "> Start with Phase Hub or Functional Domain Hub when the task is not specifically in-crash browsing.",
            ],
            browse_lines=_in_crash_browse_lines(visible_units, visible_documents),
            dataview_blocks=[("Live Listing", '```dataview\nTABLE file.link, primary_topic, functional_domain, browse_buckets\nFROM "wiki/regulation_units"\nWHERE note_type = "regulation_unit" AND clause_path != "document" AND phase = "in_crash"\nSORT primary_topic ASC\nLIMIT 25\n```')],
        ),
    ]

    written_pilot_files = [
        _write_unit_document_delta_note(
            settings.paths.operations_pilot_root / "reclassification_unit_vs_document_delta.md",
            note_id="operations-reclassification-unit-vs-document-delta",
            title="Reclassification Unit vs Document Delta",
            summary="Generated summary of where unit-level adjudication diverges from document-level calibration.",
            run_id=active_run_id,
            data_as_of=generated_on,
            document_rows=load_document_adjudications(settings.paths.operations_pilot_root / "reclassification_20_document_adjudications.jsonl"),
            unit_rows=load_unit_adjudications(settings.paths.operations_pilot_root / "reclassification_20_unit_adjudications.jsonl"),
        )
    ]

    removed_legacy_files: list[str] = []
    for filename in LEGACY_DASHBOARD_FILES:
        path = settings.paths.operations_dashboards_root / filename
        if path.exists():
            path.unlink()
            removed_legacy_files.append(str(path))

    return {
        "run_id": active_run_id,
        "status": "refreshed",
        "written_operations_files": [str(path) for path in written_operations],
        "written_hub_files": [str(path) for path in written_hubs],
        "written_pilot_files": [str(path) for path in written_pilot_files],
        "removed_legacy_files": removed_legacy_files,
        "written_files": [str(path) for path in [*written_operations, *written_hubs, *written_pilot_files]],
    }


def _load_notes(wiki_root: Path) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        if str(frontmatter.get("record_layer") or "") != "knowledge":
            continue
        notes.append(
            {
                "path": path,
                "page_ref": str(path.relative_to(wiki_root)).replace("\\", "/").removesuffix(".md"),
                "frontmatter": frontmatter,
            }
        )
    return notes


def _scalar(note: dict[str, Any], key: str) -> str:
    return str(note["frontmatter"].get(key) or "unknown")


def _note_type(note: dict[str, Any]) -> str:
    return _scalar(note, "note_type")


def _title(note: dict[str, Any]) -> str:
    title = str(note["frontmatter"].get("title") or "").strip()
    return title or note["path"].stem


def _note_link(note: dict[str, Any]) -> str:
    return f"[[{note['page_ref']}|{_title(note)}]]"


def _is_pseudo_document_unit(note: dict[str, Any]) -> bool:
    return _note_type(note) == "regulation_unit" and (
        str(note["frontmatter"].get("clause_path") or "") == "document"
        or str(note["frontmatter"].get("id") or "").endswith("-document")
    )


def _is_visible_knowledge_note(note: dict[str, Any]) -> bool:
    if _note_type(note) == "browse_index":
        return False
    if _is_pseudo_document_unit(note):
        return False
    return True


def _list_counter(notes: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for note in notes:
        for value in note["frontmatter"].get(key) or []:
            counter[str(value)] += 1
    return counter


def _counter_lines(label: str, counter: Counter[str]) -> list[str]:
    return [f"- {label}: `{key}` -> {value}" for key, value in sorted(counter.items())]


def _flatten_counter_lines(label: str, counter: Counter[str]) -> list[str]:
    return [f"- {label}: `{key}` -> {value}" for key, value in sorted(counter.items())]


def _classification_review_lines(notes: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    trigger_counts = Counter()
    queued: list[dict[str, Any]] = []
    for note in notes:
        triggers: list[str] = []
        if _scalar(note, "legacy_domain") == "needs_review":
            triggers.append("legacy_domain")
        if "other_or_review" in [str(value) for value in note["frontmatter"].get("functional_domain") or []]:
            triggers.append("functional_domain")
        if _scalar(note, "confidence") == "low":
            triggers.append("confidence")
        if note["frontmatter"].get("review_required") is True:
            triggers.append("review_required")
        if not triggers:
            continue
        queued.append(note)
        trigger_counts.update(triggers)
        lines.append(f"- {_note_link(note)} | triggers: {', '.join(triggers)}")
    summary = [f"- queue_size: {len(queued)}"]
    summary.extend(f"- trigger_count[{key}]: {value}" for key, value in sorted(trigger_counts.items()))
    summary.extend(lines[:40] or ["- None."])
    return summary


def _provenance_review_lines(notes: list[dict[str, Any]]) -> list[str]:
    queued = [note for note in notes if _needs_provenance_review(note)]
    lines = [f"- queue_size: {len(queued)}"]
    for note in queued[:40]:
        lines.append(f"- {_note_link(note)} | source_collection: `{_scalar(note, 'source_collection')}`")
    return lines


def _missing_provenance_lines(notes: list[dict[str, Any]]) -> list[str]:
    candidates = [note for note in notes if _requires_source_provenance(note)]
    queued = [note for note in candidates if _needs_provenance_review(note)]
    by_type = Counter(_note_type(note) for note in queued)
    lines = [f"- total_missing: {len(queued)}"]
    lines.extend(f"- note_type[{key}]: {value}" for key, value in sorted(by_type.items()))
    for note in queued[:40]:
        lines.append(f"- {_note_link(note)}")
    return lines


def _recent_lines(notes: list[dict[str, Any]]) -> list[str]:
    sorted_notes = sorted(notes, key=lambda note: (_scalar(note, "updated"), _title(note)), reverse=True)
    return [
        f"- `{_scalar(note, 'updated')}` | `{_note_type(note)}` | {_note_link(note)}"
        for note in sorted_notes[:25]
    ] or ["- None."]


def _calibration_delta_lines(path: Path) -> list[str]:
    if not path.exists():
        return ["- No calibration adjudications found yet."]
    rows = load_document_adjudications(path)
    if not rows:
        return ["- No calibration adjudications found yet."]

    summary = summarize_document_calibration(rows)
    lines = [
        f"- calibration_items: {summary['calibration_items']}",
        f"- changed_items: {summary['changed_items']}",
        f"- cross_phase_to_post_crash: {summary['cross_phase_to_post_crash']}",
        f"- cross_phase_to_pre_crash: {summary['cross_phase_to_pre_crash']}",
        f"- current_phase_counts: {summary['current_phase_counts']}",
        f"- selected_phase_counts: {summary['selected_phase_counts']}",
        f"- rejected_alternative_counts: {summary['rejected_alternative_counts']}",
        "- document-level calibration is for entry classification only; canonical phase stabilization is governed by regulation_unit adjudication.",
    ]
    for row in rows:
        lines.append(
            "- "
            f"`{row.get('calibration_id')}` | current=`{row.get('current_phase')}` -> selected=`{row.get('selected_phase')}` | "
            f"rejected=`{row.get('rejected_alternative_phase')}`"
        )
    return lines


def _write_unit_document_delta_note(
    path: Path,
    *,
    note_id: str,
    title: str,
    summary: str,
    run_id: str,
    data_as_of: str,
    document_rows: list[dict[str, Any]],
    unit_rows: list[dict[str, Any]],
) -> Path:
    unit_summary = summarize_unit_vs_document(document_rows, unit_rows)
    frontmatter = _operations_frontmatter(path, note_id=note_id, title=title, summary=summary, run_id=run_id, data_as_of=data_as_of)
    body = [
        render_frontmatter(frontmatter),
        f"# {title}",
        "",
        "document-level calibration은 entry classification용이며, canonical phase 안정화는 regulation_unit adjudication이 우선한다.",
        "",
        "## Snapshot",
        f"- generated_at: {frontmatter['generated_at']}",
        f"- data_as_of: {frontmatter['data_as_of']}",
        f"- refresh_run_id: `{run_id}`",
        f"- documents_covered: {unit_summary['documents_covered']}",
        f"- unit_samples: {unit_summary['unit_samples']}",
        f"- documents_with_mixed_units: {unit_summary['documents_with_mixed_units']}",
        f"- documents_where_unit_differs: {unit_summary['documents_where_unit_differs']}",
        f"- selected_unit_phase_counts: {unit_summary['selected_unit_phase_counts']}",
        "",
        "## Per Document",
    ]
    for row in unit_summary["rows"]:
        body.append(
            "- "
            f"`{row['calibration_id']}` | document=`{row['document_phase']}` | "
            f"unit_phases=`{', '.join(row['unit_phases'])}` | differing_units={row['differing_unit_count']}"
        )
    body.append("")
    return write_text(path, "\n".join(body))


def _browse_coverage_lines(notes: list[dict[str, Any]]) -> list[str]:
    in_crash_notes = [note for note in notes if _scalar(note, "phase") == "in_crash"]
    counter = _list_counter(in_crash_notes, "browse_buckets")
    lines = [
        f"- visible_in_crash_units: {len(in_crash_notes)}",
        f"- units_without_browse_bucket: {sum(1 for note in in_crash_notes if not (note['frontmatter'].get('browse_buckets') or []))}",
    ]
    lines.extend(f"- browse_bucket: `{key}` -> {value}" for key, value in sorted(counter.items()))
    return lines


def _write_dashboard(
    path: Path,
    *,
    note_id: str,
    title: str,
    summary: str,
    run_id: str,
    data_as_of: str,
    snapshot_lines: list[str],
    dataview_query: str | None,
) -> Path:
    frontmatter = _operations_frontmatter(path, note_id=note_id, title=title, summary=summary, run_id=run_id, data_as_of=data_as_of)
    body = [
        render_frontmatter(frontmatter),
        f"# {title}",
        "",
        "## Snapshot",
        f"- generated_at: {frontmatter['generated_at']}",
        f"- data_as_of: {frontmatter['data_as_of']}",
        f"- refresh_run_id: `{run_id}`",
    ]
    body.extend(snapshot_lines or ["- None."])
    if dataview_query:
        body.extend(["", "## Dataview", "```dataview", dataview_query, "```"])
    return write_text(path, "\n".join(body).rstrip() + "\n")


def _write_browse_hub(
    path: Path,
    *,
    note_id: str,
    title: str,
    summary: str,
    browse_axis: str,
    run_id: str,
    snapshot_lines: list[str],
    purpose_lines: list[str],
    browse_lines: list[str],
    dataview_blocks: list[tuple[str, str]],
) -> Path:
    frontmatter = _browse_frontmatter(path, note_id=note_id, title=title, summary=summary, browse_axis=browse_axis, run_id=run_id)
    body = [
        render_frontmatter(frontmatter),
        f"# {title}",
        "",
        "## Snapshot",
        f"- generated_at: {frontmatter['generated_at']}",
        f"- browse_axis: {browse_axis}",
        f"- refresh_run_id: `{run_id}`",
    ]
    body.extend(snapshot_lines or ["- None."])
    body.extend(["", "## Why This Hub Exists"])
    body.extend(purpose_lines)
    body.extend(["", "## Browse View"])
    body.extend(browse_lines or ["- None."])
    body.extend(["", "## Dataview"])
    if dataview_blocks:
        for heading, block in dataview_blocks:
            body.extend([f"### {heading}", block.rstrip(), ""])
    else:
        body.append("_No live Dataview block for this hub._")
    return write_text(path, "\n".join(body).rstrip() + "\n")


def _operations_frontmatter(path: Path, *, note_id: str, title: str, summary: str, run_id: str, data_as_of: str) -> dict[str, Any]:
    created = _existing_created(path) or data_as_of
    return {
        "record_layer": "operations",
        "id": note_id,
        "title": title,
        "summary": summary,
        "status": "active",
        "created": created,
        "updated": data_as_of,
        "generated_at": data_as_of,
        "data_as_of": data_as_of,
        "refresh_run_id": run_id,
        "tags": ["operations", "dashboard"],
    }


def _browse_frontmatter(
    path: Path,
    *,
    note_id: str,
    title: str,
    summary: str,
    browse_axis: str,
    run_id: str,
) -> dict[str, Any]:
    today = _today()
    created = _existing_created(path) or today
    return {
        "record_layer": "knowledge",
        "id": note_id,
        "note_type": "browse_index",
        "title": title,
        "summary": summary,
        "status": "draft",
        "created": created,
        "updated": today,
        "generated_at": today,
        "aliases": [],
        "browse_axis": browse_axis,
        "provenance": {
            "source_files": [],
            "source_hashes": {},
            "parser_run_id": run_id,
        },
        "confidence": "medium",
    }


def _existing_created(path: Path) -> str | None:
    if not path.exists():
        return None
    frontmatter, _ = parse_frontmatter_file(path)
    created = str(frontmatter.get("created") or "").strip()
    return created or None


def _recent_pilot_mapping_lines(path: Path) -> list[str]:
    rows = read_jsonl(path)
    if not rows:
        return ["- No pilot mapping rows found."]
    phase_counts = Counter(str(row.get("phase") or "unknown") for row in rows)
    domain_counts = Counter(str(row.get("functional_domain") or "unknown") for row in rows)
    lines = [f"- pilot_rows: {len(rows)}"]
    lines.extend(f"- phase[{key}]: {value}" for key, value in sorted(phase_counts.items()))
    lines.extend(f"- functional_domain[{key}]: {value}" for key, value in sorted(domain_counts.items()))
    lines.append("- recent_entries:")
    for row in rows[-12:]:
        lines.append(f"  - `{row.get('pilot_id')}` | `{row.get('jurisdiction')}` | `{row.get('phase')}` | `{row.get('functional_domain')}`")
    return lines


def _source_authority_monitor_lines(authority_registry: Path, document_inventory: Path) -> list[str]:
    authority_payload = yaml.safe_load(authority_registry.read_text(encoding="utf-8")) or {}
    authority_rows = authority_payload.get("sources") or []
    with document_inventory.open("r", encoding="utf-8", newline="") as handle:
        inventory_rows = list(csv.DictReader(handle))

    authority_count = len(authority_rows)
    inventory_count = len(inventory_rows)
    authority_by_jurisdiction = Counter(str(row.get("jurisdiction") or "unknown") for row in authority_rows)
    pending_checksum = sum(1 for row in authority_rows if str(row.get("checksum") or "").strip() == "pending_snapshot")
    missing_effective_date = sum(1 for row in authority_rows if not str(row.get("effective_date") or "").strip())
    inventory_ids = {str(row.get("source_id") or "").strip() for row in inventory_rows}
    authority_ids = {str(row.get("source_id") or "").strip() for row in authority_rows}
    authority_only = sorted(source_id for source_id in authority_ids - inventory_ids if source_id)
    inventory_only = sorted(source_id for source_id in inventory_ids - authority_ids if source_id)

    lines = [
        f"- authority_registry_rows: {authority_count}",
        f"- document_inventory_rows: {inventory_count}",
        f"- pending_snapshot_checksums: {pending_checksum}",
        f"- missing_effective_date: {missing_effective_date}",
    ]
    lines.extend(f"- jurisdiction[{key}]: {value}" for key, value in sorted(authority_by_jurisdiction.items()))
    lines.append(f"- authority_only_ids: {authority_only[:10] if authority_only else '[]'}")
    lines.append(f"- inventory_only_ids: {inventory_only[:10] if inventory_only else '[]'}")
    return lines


def _functional_domain_browse_lines(units: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[str]:
    counter = _list_counter(units, "functional_domain")
    lines: list[str] = []
    for domain, count in sorted(counter.items()):
        lines.append(f"### `{domain}`")
        lines.append(f"- unit_count: {count}")
        lines.append(f"- representative_documents: {_representative_documents(documents, 'functional_domain', domain)}")
    return lines


def _phase_browse_lines(units: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[str]:
    counter = Counter(_scalar(note, "phase") for note in units)
    lines: list[str] = []
    for phase, count in sorted(counter.items()):
        lines.append(f"### `{phase}`")
        lines.append(f"- unit_count: {count}")
        lines.append(f"- representative_documents: {_representative_documents(documents, 'phase', phase)}")
    return lines


def _jurisdiction_browse_lines(units: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[str]:
    counter = Counter(_scalar(note, "jurisdiction") for note in units)
    lines: list[str] = []
    for jurisdiction, count in sorted(counter.items()):
        lines.append(f"### `{jurisdiction}`")
        lines.append(f"- unit_count: {count}")
        lines.append(f"- representative_documents: {_representative_documents(documents, 'jurisdiction', jurisdiction)}")
    return lines


def _approval_governance_lines(notes: list[dict[str, Any]]) -> list[str]:
    candidates = _approval_governance_notes(notes)
    lines = [f"- visible_admin_notes: {len(candidates)}"]
    by_jurisdiction = Counter(_scalar(note, "jurisdiction") for note in candidates)
    by_layer = Counter(_scalar(note, "regulatory_layer") for note in candidates)
    lines.extend(f"- jurisdiction[{key}]: {value}" for key, value in sorted(by_jurisdiction.items()))
    lines.extend(f"- regulatory_layer[{key}]: {value}" for key, value in sorted(by_layer.items()))
    for note in candidates[:20]:
        lines.append(f"- {_note_link(note)}")
    return lines


def _in_crash_browse_lines(units: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[str]:
    in_crash_units = [note for note in units if _scalar(note, "phase") == "in_crash"]
    bucket_counter = _list_counter(in_crash_units, "browse_buckets")
    all_buckets = sorted(bucket_counter)
    component_buckets = [bucket for bucket in all_buckets if bucket not in SCENARIO_BUCKETS and bucket not in PROTECTION_TARGET_BUCKETS]

    lines = [
        "### Scenario Browse",
        *[f"- `{bucket}` -> {bucket_counter[bucket]} | documents: {_representative_documents(documents, 'browse_buckets', bucket, phase='in_crash')}" for bucket in SCENARIO_BUCKETS if bucket in bucket_counter],
        "",
        "### Component Browse",
        *[f"- `{bucket}` -> {bucket_counter[bucket]} | documents: {_representative_documents(documents, 'browse_buckets', bucket, phase='in_crash')}" for bucket in component_buckets],
        "",
        "### Protection Target Browse",
        *[f"- `{bucket}` -> {bucket_counter[bucket]} | documents: {_representative_documents(documents, 'browse_buckets', bucket, phase='in_crash')}" for bucket in PROTECTION_TARGET_BUCKETS if bucket in bucket_counter],
        "",
        "### Fallback / Review-Prone Cases",
    ]
    fallback_notes = [
        note
        for note in in_crash_units
        if not (note["frontmatter"].get("browse_buckets") or [])
        or "other_or_review" in [str(value) for value in note["frontmatter"].get("functional_domain") or []]
    ]
    lines.append(f"- units_needing_bucket_review: {len(fallback_notes)}")
    lines.append("- note: the current committed browse registry does not define an explicit `interior` fallback bucket, so unbucketed or weakly bucketed in-crash units are treated as review-prone here.")
    return lines


def _approval_governance_notes(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        note
        for note in notes
        if _scalar(note, "phase") == "non_phase_admin" or _scalar(note, "regulatory_layer") in ADMIN_LAYERS
    ]
    return sorted(candidates, key=lambda note: (_scalar(note, "jurisdiction"), _title(note)))


def _representative_documents(
    documents: list[dict[str, Any]],
    key: str,
    value: str,
    *,
    phase: str | None = None,
) -> str:
    matches: list[str] = []
    for note in documents:
        frontmatter = note["frontmatter"]
        if phase and str(frontmatter.get("phase") or "") != phase:
            continue
        candidate = frontmatter.get(key)
        if isinstance(candidate, list):
            if value not in {str(item) for item in candidate}:
                continue
        elif str(candidate or "") != value:
            continue
        matches.append(_note_link(note))
    if not matches:
        return "n/a"
    return ", ".join(matches[:3])


def _requires_source_provenance(note: dict[str, Any]) -> bool:
    return _note_type(note) in {"regulation_document", "regulation_unit", "analysis", "concept_node"}


def _needs_provenance_review(note: dict[str, Any]) -> bool:
    if not _requires_source_provenance(note):
        return False
    provenance = note["frontmatter"].get("provenance") or {}
    if not isinstance(provenance, dict):
        return True
    source_files = provenance.get("source_files") or []
    source_hashes = provenance.get("source_hashes") or {}
    return not source_files or not source_hashes


def _today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")
