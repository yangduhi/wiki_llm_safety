from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_jsonl, write_text


SECONDARY_UMBRELLA_LANES = {
    "xml_kmvss-kmvss_art_38_055": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_39_057": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_40_059": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_45_068": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_79_115": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_87_128": "secondary_umbrella_promotable",
    "xml_kmvss-kmvss_art_4_007": "secondary_umbrella_keep_review",
    "xml_kmvss-kmvss_art_23_035": "secondary_umbrella_keep_review",
    "xml_kmvss-kmvss_art_6_009": "secondary_umbrella_needs_policy_decision",
    "xml_kmvss-kmvss_art_108_162": "secondary_umbrella_needs_policy_decision",
    "xml_kmvss-kmvss_art_108_163": "secondary_umbrella_needs_policy_decision",
}

PROMOTION_STATUS_BY_LANE = {
    "secondary_umbrella_promotable": "promotion_candidate",
    "secondary_umbrella_keep_review": "temporary_retain",
    "secondary_umbrella_needs_policy_decision": "needs_policy_decision",
}

PROMOTION_REASON_BY_LANE = {
    "secondary_umbrella_promotable": "family_prior_plus_parent_context_alignment",
    "secondary_umbrella_keep_review": "local_text_too_abstract_for_safe_canonical_lowering",
    "secondary_umbrella_needs_policy_decision": "taxonomy_or_policy_semantics_not_settled",
}

RETAIN_STABILITY_BY_LANE = {
    "secondary_umbrella_promotable": "",
    "secondary_umbrella_keep_review": "temporary_retain",
    "secondary_umbrella_needs_policy_decision": "temporary_retain",
}

CANONICAL_FIT_BY_LANE = {
    "secondary_umbrella_promotable": "strong_family_fit",
    "secondary_umbrella_keep_review": "weak_or_abstract_scope",
    "secondary_umbrella_needs_policy_decision": "policy_unsettled",
}

REFERENCE_PATTERN_BY_LANE = {
    "secondary_umbrella_promotable": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
    "secondary_umbrella_keep_review": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
    "secondary_umbrella_needs_policy_decision": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    run_root = settings.paths.normalized_root / "runs" / args.run_id
    documents = {row["document_id"]: row for row in read_jsonl(run_root / "documents.jsonl")}
    trace_rows = [row for row in read_jsonl(run_root / "classification_trace.jsonl") if row.get("note_kind") == "unit"]
    subjects = _raw_subjects(settings.paths.collections_root / "xml_kmvss")

    register_rows: list[dict[str, object]] = []
    adjudications: list[dict[str, object]] = []
    section_lines: dict[str, list[str]] = {
        "secondary_umbrella_promotable": [],
        "secondary_umbrella_keep_review": [],
        "secondary_umbrella_needs_policy_decision": [],
    }

    for document_id, lane in SECONDARY_UMBRELLA_LANES.items():
        doc = documents[document_id]
        subject = subjects.get(document_id, document_id)
        rows = [row for row in trace_rows if row.get("document_id") == document_id]
        short_clause_share = _share(sum(1 for row in rows if row.get("is_short_clause")), len(rows))
        parent_inheritance_effect = _share(
            sum(
                1
                for row in rows
                if any(str(source).startswith("parent") for source in (row.get("inherited_context_sources") or []))
            ),
            len(rows),
        )
        residual_rows = [
            row
            for row in rows
            if row.get("final_decision", {}).get("phase") == "cross_phase"
            or row.get("final_decision", {}).get("functional_domain") == "other_or_review"
        ]
        current_residual_reason = _mode(residual_rows, "fallback_reason")
        row = {
            "document_id": document_id,
            "subject": subject,
            "current_phase": doc["phase"],
            "current_domain": doc["functional_domain"][0],
            "current_review_lane_type": _mode(rows, "review_lane_type"),
            "title_family": _mode(rows, "umbrella_family") or _mode(rows, "article_bucket"),
            "local_text_weakness": _local_text_weakness(short_clause_share),
            "short_clause_share": f"{short_clause_share:.2%}",
            "parent_inheritance_effect": f"{parent_inheritance_effect:.2%}",
            "canonical_taxonomy_fit": CANONICAL_FIT_BY_LANE[lane],
            "promotion_status": PROMOTION_STATUS_BY_LANE[lane],
            "promotion_reason": PROMOTION_REASON_BY_LANE[lane],
            "retain_stability": RETAIN_STABILITY_BY_LANE[lane],
            "needs_policy_decision": str(lane == "secondary_umbrella_needs_policy_decision"),
            "reference_repo_pattern": REFERENCE_PATTERN_BY_LANE[lane],
            "current_residual_reason": current_residual_reason or "",
            "cross_units": sum(1 for row in rows if row.get("final_decision", {}).get("phase") == "cross_phase"),
            "other_units": sum(1 for row in rows if row.get("final_decision", {}).get("functional_domain") == "other_or_review"),
            "total_units": len(rows),
        }
        register_rows.append(row)
        adjudications.append(row.copy())
        section_lines[lane].extend(
            [
                f"### {subject}",
                f"- document_id: `{document_id}`",
                f"- current phase/domain: `{row['current_phase']} / {row['current_domain']}`",
                f"- current review lane type: `{row['current_review_lane_type']}`",
                f"- current residual reason: `{row['current_residual_reason']}`",
                f"- title family: `{row['title_family']}`",
                f"- local text weakness: `{row['local_text_weakness']}`",
                f"- short clause share: `{row['short_clause_share']}`",
                f"- parent inheritance effect: `{row['parent_inheritance_effect']}`",
                f"- canonical taxonomy fit: `{row['canonical_taxonomy_fit']}`",
                f"- promotion status: `{row['promotion_status']}`",
                f"- promotion reason: `{row['promotion_reason']}`",
                f"- retain stability: `{row['retain_stability'] or 'n/a'}`",
                f"- needs policy decision: `{row['needs_policy_decision']}`",
                f"- why residual: `{_why_residual(subject=subject, lane=lane, current_residual_reason=row['current_residual_reason'])}`",
                f"- reference repo pattern: `{row['reference_repo_pattern']}`",
                "",
            ]
        )

    register_path = settings.paths.operations_pilot_root / "kmvss_round2d_secondary_umbrella_register.csv"
    with register_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "subject",
                "current_phase",
                "current_domain",
                "current_review_lane_type",
                "title_family",
                "local_text_weakness",
                "short_clause_share",
                "parent_inheritance_effect",
                "canonical_taxonomy_fit",
                "promotion_status",
                "promotion_reason",
                "retain_stability",
                "needs_policy_decision",
                "reference_repo_pattern",
                "current_residual_reason",
                "cross_units",
                "other_units",
                "total_units",
            ],
        )
        writer.writeheader()
        writer.writerows(register_rows)

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-round2d-secondary-umbrella-audit",
        "title: KMVSS Round 2D Secondary Umbrella Audit",
        "summary: Baseline audit for secondary umbrella article residuals before round 2D promotion pruning.",
        "status: active",
        "created: 2026-04-14",
        "updated: 2026-04-14",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - round2d",
        "  - audit",
        "---",
        "",
        "# KMVSS Round 2D Secondary Umbrella Audit",
        "",
        f"- run_id: `{args.run_id}`",
        "",
        "## Secondary Umbrella Promotable",
        *section_lines["secondary_umbrella_promotable"],
        "## Secondary Umbrella Keep Review",
        *section_lines["secondary_umbrella_keep_review"],
        "## Secondary Umbrella Needs Policy Decision",
        *section_lines["secondary_umbrella_needs_policy_decision"],
    ]
    write_text(settings.paths.operations_pilot_root / "kmvss_round2d_secondary_umbrella_audit.md", "\n".join(lines))
    (settings.paths.operations_pilot_root / "kmvss_round2d_adjudications.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in adjudications) + "\n",
        encoding="utf-8",
    )


def _why_residual(*, subject: str, lane: str, current_residual_reason: str) -> str:
    if lane == "secondary_umbrella_promotable":
        return f"{subject} is still residual because short article units fall through to `{current_residual_reason}` before family prior promotion is applied."
    if lane == "secondary_umbrella_keep_review":
        return f"{subject} remains residual because the scope is abstract and local text is too weak for safe canonical lowering."
    return f"{subject} remains residual because taxonomy semantics are still unsettled enough that classifier tuning alone should not force a canonical mapping."


def _local_text_weakness(short_clause_share: float) -> str:
    if short_clause_share >= 0.8:
        return "high"
    if short_clause_share >= 0.4:
        return "medium"
    return "low"


def _share(count: int, total: int) -> float:
    return count / total if total else 0.0


def _mode(rows: list[dict[str, object]], key: str) -> object:
    counts = Counter(row.get(key) for row in rows)
    return counts.most_common(1)[0][0] if counts else None


def _raw_subjects(collection_root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in collection_root.rglob("*.xml"):
        if not path.stem.lower().startswith("kmvss_art_"):
            continue
        root = ET.parse(path).getroot()
        out[f"xml_kmvss-{path.stem.lower()}"] = (root.findtext("SUBJECT") or "").strip()
    return out


if __name__ == "__main__":
    main()
