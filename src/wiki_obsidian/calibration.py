from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from wiki_obsidian.utils.files import read_jsonl


def load_document_adjudications(path: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(path)


def load_unit_adjudications(path: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(path)


def summarize_document_calibration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    current_counts = Counter(str(row.get("current_phase") or "unknown") for row in rows)
    selected_counts = Counter(str(row.get("selected_phase") or "unknown") for row in rows)
    rejected_counts = Counter(str(row.get("rejected_alternative_phase") or "unknown") for row in rows)
    changed_rows = [row for row in rows if str(row.get("current_phase")) != str(row.get("selected_phase"))]
    cross_to_post = [
        row
        for row in rows
        if str(row.get("current_phase")) == "cross_phase" and str(row.get("selected_phase")) == "post_crash"
    ]
    cross_to_pre = [
        row
        for row in rows
        if str(row.get("current_phase")) == "cross_phase" and str(row.get("selected_phase")) == "pre_crash"
    ]
    return {
        "calibration_items": len(rows),
        "changed_items": len(changed_rows),
        "cross_phase_to_post_crash": len(cross_to_post),
        "cross_phase_to_pre_crash": len(cross_to_pre),
        "current_phase_counts": dict(sorted(current_counts.items())),
        "selected_phase_counts": dict(sorted(selected_counts.items())),
        "rejected_alternative_counts": dict(sorted(rejected_counts.items())),
        "changed_rows": changed_rows,
    }


def summarize_unit_vs_document(
    document_rows: list[dict[str, Any]],
    unit_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    document_by_id = {str(row.get("calibration_id")): row for row in document_rows}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in unit_rows:
        grouped[str(row.get("calibration_id"))].append(row)

    documents_with_mixed_units = 0
    documents_where_unit_differs = 0
    selected_unit_counts = Counter(str(row.get("selected_phase") or "unknown") for row in unit_rows)
    rows_out: list[dict[str, Any]] = []

    for calibration_id, rows in sorted(grouped.items()):
        document_row = document_by_id.get(calibration_id, {})
        document_phase = str(document_row.get("selected_phase") or "unknown")
        unit_phases = {str(row.get("selected_phase") or "unknown") for row in rows}
        differing_rows = [row for row in rows if str(row.get("selected_phase") or "unknown") != document_phase]
        if len(unit_phases) > 1:
            documents_with_mixed_units += 1
        if differing_rows:
            documents_where_unit_differs += 1
        rows_out.append(
            {
                "calibration_id": calibration_id,
                "document_phase": document_phase,
                "unit_count": len(rows),
                "unit_phases": sorted(unit_phases),
                "differing_unit_count": len(differing_rows),
            }
        )

    return {
        "documents_covered": len(grouped),
        "unit_samples": len(unit_rows),
        "documents_with_mixed_units": documents_with_mixed_units,
        "documents_where_unit_differs": documents_where_unit_differs,
        "selected_unit_phase_counts": dict(sorted(selected_unit_counts.items())),
        "rows": rows_out,
    }
