from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.utils.files import read_jsonl, write_text


SECONDARY_DOCS = {
    "xml_kmvss-kmvss_art_6_009",
    "xml_kmvss-kmvss_art_38_055",
    "xml_kmvss-kmvss_art_39_057",
    "xml_kmvss-kmvss_art_40_059",
    "xml_kmvss-kmvss_art_45_068",
    "xml_kmvss-kmvss_art_79_115",
    "xml_kmvss-kmvss_art_87_128",
    "xml_kmvss-kmvss_art_108_162",
    "xml_kmvss-kmvss_art_108_163",
    "xml_kmvss-kmvss_art_4_007",
    "xml_kmvss-kmvss_art_23_035",
}

STABLE_RETAIN_DOCS = {
    "xml_kmvss-kmvss_art_34_048",
    "xml_kmvss-kmvss_art_105_158",
    "xml_kmvss-kmvss_art_2_002",
    "xml_kmvss-kmvss_art_114_189",
}

TEMPORARY_RETAIN_DOCS = {
    "xml_kmvss-kmvss_art_32_046",
    "xml_kmvss-kmvss_art_28_042",
    "xml_kmvss-kmvss_art_113_188",
}

MIXED_DOCS = {
    "xml_kmvss-kmvss_art_18_028",
    "xml_kmvss-kmvss_art_18_029",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--before-run", required=True)
    parser.add_argument("--after-run", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root)
    before_units = [row for row in read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.before_run / "units.jsonl") if row.get("source_collection") == "xml_kmvss"]
    after_units = [row for row in read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.after_run / "units.jsonl") if row.get("source_collection") == "xml_kmvss"]
    before_trace = [row for row in read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.before_run / "classification_trace.jsonl") if row.get("note_kind") == "unit"]
    after_trace = [row for row in read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.after_run / "classification_trace.jsonl") if row.get("note_kind") == "unit"]
    subjects = _raw_subjects(project_root / "raw" / "collections" / "xml_kmvss")

    fixed_slice = SECONDARY_DOCS | STABLE_RETAIN_DOCS | TEMPORARY_RETAIN_DOCS | MIXED_DOCS
    top20_rows = _top20(before_units, after_units, before_trace, after_trace, subjects)

    csv_path = project_root / "docs" / "operations" / "pilot" / "kmvss_round2d_top20_before_after.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "subject",
                "before_lane",
                "after_lane",
                "before_promotion_status",
                "after_promotion_status",
                "before_cross",
                "after_cross",
                "before_other",
                "after_other",
                "before_total",
                "after_total",
            ],
        )
        writer.writeheader()
        writer.writerows(top20_rows)

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-round2d-comparable-evaluation",
        "title: KMVSS Round 2D Comparable Evaluation",
        "summary: Before and after comparison for KMVSS secondary umbrella pruning and review-lane promotion separation.",
        "status: active",
        "created: 2026-04-14",
        "updated: 2026-04-14",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - round2d",
        "  - evaluation",
        "---",
        "",
        "# KMVSS Round 2D Comparable Evaluation",
        "",
        f"- before_run: `{args.before_run}`",
        f"- after_run: `{args.after_run}`",
        "",
        "## Overall Raw Before/After",
        *_ratio_block("all", before_units, after_units),
        "",
        "## Article-Only Before/After",
        *_ratio_block("articles", _article_rows(before_units), _article_rows(after_units)),
        "",
        "## Attachment Regression Check",
        *_ratio_block("attachments", _attachment_rows(before_units), _attachment_rows(after_units)),
        "",
        "## Secondary Umbrella Slice",
        *_ratio_block("secondary_umbrella", _filter_docs(_article_rows(before_units), SECONDARY_DOCS), _filter_docs(_article_rows(after_units), SECONDARY_DOCS)),
        "",
        "## Review-Lane Status Transition Summary",
        *_lane_transition_block(before_trace, after_trace, fixed_slice),
        "",
        "## Same-Document Fixed Slice Comparison",
    ]
    for row in top20_rows:
        lines.append(
            f"- `{row['document_id']}` / {row['subject']} / lane `{row['before_lane']} -> {row['after_lane']}` / "
            f"promotion `{row['before_promotion_status']} -> {row['after_promotion_status']}` / "
            f"cross `{row['before_cross']} -> {row['after_cross']}` / other `{row['before_other']} -> {row['after_other']}`"
        )
    lines.extend(
        [
            "",
            "## Residual Decomposition",
            *_decomposition_block(after_trace),
            "",
            "## Interpretation",
            "- raw `other_or_review` is not used as a standalone fail metric",
            "- secondary umbrella success is accepted when residual drops or promotion separation becomes materially clearer",
            "- stable retain and temporary retain remain policy-grounded review states rather than hidden failure buckets",
        ]
    )
    write_text(project_root / "docs" / "operations" / "pilot" / "kmvss_round2d_comparable_evaluation.md", "\n".join(lines))

    diff_lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-round2d-trace-diff-summary",
        "title: KMVSS Round 2D Trace Diff Summary",
        "summary: Trace-level comparison for promotion candidates and stable retain exemplars in round 2D.",
        "status: active",
        "created: 2026-04-14",
        "updated: 2026-04-14",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - round2d",
        "  - trace",
        "---",
        "",
        "# KMVSS Round 2D Trace Diff Summary",
        "",
        *_trace_summary("xml_kmvss-kmvss_art_38_055", before_trace, after_trace, subjects),
        "",
        *_trace_summary("xml_kmvss-kmvss_art_2_002", before_trace, after_trace, subjects),
    ]
    write_text(project_root / "docs" / "operations" / "pilot" / "kmvss_round2d_trace_diff_summary.md", "\n".join(diff_lines))


def _article_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if "kmvss_art_" in str(row.get("document_id") or "")]


def _attachment_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if row.get("is_attachment") or "kmvss_att_" in str(row.get("document_id") or "")]


def _filter_docs(rows: list[dict[str, object]], docs: set[str]) -> list[dict[str, object]]:
    return [row for row in rows if str(row.get("document_id") or "") in docs]


def _ratio_block(label: str, before_rows: list[dict[str, object]], after_rows: list[dict[str, object]]) -> list[str]:
    return [
        f"- slice: `{label}`",
        f"- total_units: `{len(before_rows)} -> {len(after_rows)}`",
        f"- cross_phase: `{_count(before_rows, 'cross')} -> {_count(after_rows, 'cross')}` (`{_ratio(before_rows, 'cross'):.2%} -> {_ratio(after_rows, 'cross'):.2%}`)",
        f"- other_or_review: `{_count(before_rows, 'other')} -> {_count(after_rows, 'other')}` (`{_ratio(before_rows, 'other'):.2%} -> {_ratio(after_rows, 'other'):.2%}`)",
    ]


def _count(rows: list[dict[str, object]], metric: str) -> int:
    if metric == "cross":
        return sum(1 for row in rows if row.get("phase") == "cross_phase")
    return sum(1 for row in rows if (row.get("functional_domain") or [None])[0] == "other_or_review")


def _ratio(rows: list[dict[str, object]], metric: str) -> float:
    return _count(rows, metric) / len(rows) if rows else 0.0


def _top20(
    before_units: list[dict[str, object]],
    after_units: list[dict[str, object]],
    before_trace: list[dict[str, object]],
    after_trace: list[dict[str, object]],
    subjects: dict[str, str],
) -> list[dict[str, object]]:
    before_stats = _doc_stats(_article_rows(before_units))
    after_stats = _doc_stats(_article_rows(after_units))
    docs = sorted(before_stats, key=lambda doc_id: before_stats[doc_id]["cross"] + before_stats[doc_id]["other"], reverse=True)[:20]
    rows: list[dict[str, object]] = []
    for document_id in docs:
        before_doc_trace = [row for row in before_trace if row.get("document_id") == document_id]
        after_doc_trace = [row for row in after_trace if row.get("document_id") == document_id]
        rows.append(
            {
                "document_id": document_id,
                "subject": subjects.get(document_id, document_id),
                "before_lane": _mode(before_doc_trace, "review_lane_type") or "",
                "after_lane": _mode(after_doc_trace, "review_lane_type") or "",
                "before_promotion_status": _mode(before_doc_trace, "promotion_status") or "",
                "after_promotion_status": _mode(after_doc_trace, "promotion_status") or "",
                "before_cross": before_stats[document_id]["cross"],
                "after_cross": after_stats.get(document_id, {}).get("cross", 0),
                "before_other": before_stats[document_id]["other"],
                "after_other": after_stats.get(document_id, {}).get("other", 0),
                "before_total": before_stats[document_id]["total"],
                "after_total": after_stats.get(document_id, {}).get("total", 0),
            }
        )
    return rows


def _doc_stats(rows: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for row in rows:
        document_id = str(row.get("document_id") or "")
        stats.setdefault(document_id, {"cross": 0, "other": 0, "total": 0})
        stats[document_id]["total"] += 1
        if row.get("phase") == "cross_phase":
            stats[document_id]["cross"] += 1
        if (row.get("functional_domain") or [None])[0] == "other_or_review":
            stats[document_id]["other"] += 1
    return stats


def _lane_transition_block(before_trace: list[dict[str, object]], after_trace: list[dict[str, object]], docs: set[str]) -> list[str]:
    lines: list[str] = []
    for document_id in sorted(docs):
        before_rows = [row for row in before_trace if row.get("document_id") == document_id]
        after_rows = [row for row in after_trace if row.get("document_id") == document_id]
        lines.append(
            f"- `{document_id}`: lane `{_mode(before_rows, 'review_lane_type')} -> {_mode(after_rows, 'review_lane_type')}`, "
            f"promotion `{_mode(before_rows, 'promotion_status')} -> {_mode(after_rows, 'promotion_status')}`"
        )
    return lines


def _decomposition_block(after_trace: list[dict[str, object]]) -> list[str]:
    article_residual = [
        row
        for row in after_trace
        if "kmvss_art_" in str(row.get("document_id") or "")
        and (
            row.get("final_decision", {}).get("phase") == "cross_phase"
            or row.get("final_decision", {}).get("functional_domain") == "other_or_review"
        )
    ]
    stable = [row for row in article_residual if row.get("review_lane_type") == "stable_retain"]
    temporary = [row for row in article_residual if row.get("review_lane_type") in {"temporary_retain", "secondary_umbrella_keep_review", "secondary_umbrella_needs_policy_decision"}]
    unresolved = [
        row
        for row in article_residual
        if row.get("review_lane_type") not in {"stable_retain", "temporary_retain", "secondary_umbrella_keep_review", "secondary_umbrella_needs_policy_decision", "mixed_keep_review"}
    ]
    return [
        f"- stable_retain residual units: `{len(stable)}`",
        f"- temporary_retain residual units: `{len(temporary)}`",
        f"- unresolved_residual units: `{len(unresolved)}`",
        f"- mixed_keep_review residual units: `{sum(1 for row in article_residual if row.get('review_lane_type') == 'mixed_keep_review')}`",
    ]


def _trace_summary(document_id: str, before_trace: list[dict[str, object]], after_trace: list[dict[str, object]], subjects: dict[str, str]) -> list[str]:
    before_rows = [row for row in before_trace if row.get("document_id") == document_id]
    after_rows = [row for row in after_trace if row.get("document_id") == document_id]
    return [
        f"## {subjects.get(document_id, document_id)}",
        f"- document_id: `{document_id}`",
        f"- before lane: `{_mode(before_rows, 'review_lane_type')}`",
        f"- after lane: `{_mode(after_rows, 'review_lane_type')}`",
        f"- before promotion status: `{_mode(before_rows, 'promotion_status')}`",
        f"- after promotion status: `{_mode(after_rows, 'promotion_status')}`",
        f"- before cross: `{sum(1 for row in before_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}`",
        f"- after cross: `{sum(1 for row in after_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}`",
        f"- before other: `{sum(1 for row in before_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}`",
        f"- after other: `{sum(1 for row in after_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}`",
        f"- explanation: `{_trace_explanation(after_rows)}`",
    ]


def _trace_explanation(rows: list[dict[str, object]]) -> str:
    lane = _mode(rows, "review_lane_type")
    if lane == "secondary_umbrella_promotable":
        return "family prior and short-clause inheritance aligned strongly enough to justify canonical lowering"
    if lane == "stable_retain":
        return "policy-grounded retain remains in place because canonical lowering would overstate precision"
    return "review-lane status is now explicit in trace and audit artifacts"


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
