from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.utils.files import read_jsonl, write_text


UMBRELLA_CANDIDATES = {
    "xml_kmvss-kmvss_art_88_129",
    "xml_kmvss-kmvss_art_20_032",
    "xml_kmvss-kmvss_art_33_047",
    "xml_kmvss-kmvss_art_37_051",
    "xml_kmvss-kmvss_art_98_147",
    "xml_kmvss-kmvss_art_25_038",
}
INTENTIONAL_RETAIN = {
    "xml_kmvss-kmvss_art_34_048",
    "xml_kmvss-kmvss_art_105_158",
    "xml_kmvss-kmvss_art_2_002",
    "xml_kmvss-kmvss_art_114_189",
    "xml_kmvss-kmvss_art_32_046",
    "xml_kmvss-kmvss_art_28_042",
    "xml_kmvss-kmvss_art_113_188",
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
    before_trace = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.before_run / "classification_trace.jsonl")
    after_trace = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / args.after_run / "classification_trace.jsonl")
    meta = _raw_meta(project_root / "raw" / "collections" / "xml_kmvss")

    csv_rows = _top20(before_units, after_units, meta)
    csv_path = project_root / "docs" / "operations" / "pilot" / "kmvss_round2c_top20_before_after.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "subject",
                "lane",
                "umbrella_family",
                "before_cross",
                "after_cross",
                "before_other",
                "after_other",
                "before_total",
                "after_total",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-round2c-comparable-evaluation",
        "title: KMVSS Round 2C Comparable Evaluation",
        "summary: Before and after comparison for KMVSS umbrella adjudication and intentional review-lane separation.",
        "status: active",
        "created: 2026-04-14",
        "updated: 2026-04-14",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - round2c",
        "  - evaluation",
        "---",
        "",
        "# KMVSS Round 2C Comparable Evaluation",
        "",
        f"- before_run: `{args.before_run}`",
        f"- after_run: `{args.after_run}`",
        "",
        "## Overall Raw Before/After",
    ]
    lines.extend(_ratio_block("all", before_units, after_units))
    lines.extend(["", "## Article-Only Before/After"])
    lines.extend(_ratio_block("articles", _article_rows(before_units), _article_rows(after_units)))
    lines.extend(["", "## Attachment Regression Check"])
    lines.extend(_ratio_block("attachments", _attachment_rows(before_units), _attachment_rows(after_units)))
    lines.extend(["", "## Umbrella Candidate Slice"])
    lines.extend(_ratio_block("umbrella_candidates", _filter_docs(_article_rows(before_units), UMBRELLA_CANDIDATES), _filter_docs(_article_rows(after_units), UMBRELLA_CANDIDATES)))
    lines.extend(["", "## Intentional Retain Slice Stability"])
    lines.extend(_ratio_block("intentional_retain", _filter_docs(_article_rows(before_units), INTENTIONAL_RETAIN), _filter_docs(_article_rows(after_units), INTENTIONAL_RETAIN)))
    lines.extend(["", "## Same-Document Top20"])
    for row in csv_rows:
        lines.append(
            f"- `{row['document_id']}` / {row['subject']} / lane=`{row['lane']}` / family=`{row['umbrella_family']}` / "
            f"cross `{row['before_cross']} -> {row['after_cross']}` / other `{row['before_other']} -> {row['after_other']}`"
        )
    lines.extend(["", "## Trace Diff Summary"])
    for document_id in list(UMBRELLA_CANDIDATES)[:4] + list(INTENTIONAL_RETAIN)[:4]:
        lines.extend(_trace_summary(document_id, before_trace, after_trace, meta))
        lines.append("")
    write_text(project_root / "docs" / "operations" / "pilot" / "kmvss_round2c_comparable_evaluation.md", "\n".join(lines))

    diff_lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-round2c-trace-diff-summary",
        "title: KMVSS Round 2C Trace Diff Summary",
        "summary: Trace-level lane and exemplar summary for KMVSS round 2C.",
        "status: active",
        "created: 2026-04-14",
        "updated: 2026-04-14",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - round2c",
        "  - trace",
        "---",
        "",
        "# KMVSS Round 2C Trace Diff Summary",
        "",
    ]
    for document_id in list(UMBRELLA_CANDIDATES)[:3] + ["xml_kmvss-kmvss_art_34_048", "xml_kmvss-kmvss_art_2_002"]:
        diff_lines.extend(_trace_summary(document_id, before_trace, after_trace, meta))
        diff_lines.append("")
    write_text(project_root / "docs" / "operations" / "pilot" / "kmvss_round2c_trace_diff_summary.md", "\n".join(diff_lines))


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


def _top20(before_units: list[dict[str, object]], after_units: list[dict[str, object]], meta: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    before = _doc_stats(_article_rows(before_units))
    after = _doc_stats(_article_rows(after_units))
    docs = sorted(before, key=lambda doc: before[doc]["cross"] + before[doc]["other"], reverse=True)[:20]
    out: list[dict[str, object]] = []
    for document_id in docs:
        subject = meta.get(document_id, {}).get("subject", "")
        lane, family = _lane_and_family(subject)
        out.append(
            {
                "document_id": document_id,
                "subject": subject,
                "lane": lane,
                "umbrella_family": family,
                "before_cross": before[document_id]["cross"],
                "after_cross": after.get(document_id, {}).get("cross", 0),
                "before_other": before[document_id]["other"],
                "after_other": after.get(document_id, {}).get("other", 0),
                "before_total": before[document_id]["total"],
                "after_total": after.get(document_id, {}).get("total", 0),
            }
        )
    return out


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


def _trace_summary(document_id: str, before_trace: list[dict[str, object]], after_trace: list[dict[str, object]], meta: dict[str, dict[str, str]]) -> list[str]:
    before_rows = [row for row in before_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    after_rows = [row for row in after_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    return [
        f"### {document_id}",
        f"- subject: {meta.get(document_id, {}).get('subject', '')}",
        f"- before_cross: {sum(1 for row in before_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}",
        f"- after_cross: {sum(1 for row in after_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}",
        f"- before_other: {sum(1 for row in before_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}",
        f"- after_other: {sum(1 for row in after_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}",
        f"- after_lane: {_mode(after_rows, 'review_lane_type')}",
        f"- after_family: {_mode(after_rows, 'umbrella_family')}",
        f"- after_retain_reason: {_mode(after_rows, 'retain_reason')}",
    ]


def _mode(rows: list[dict[str, object]], key: str) -> object:
    counts: dict[object, int] = {}
    for row in rows:
        value = row.get(key)
        counts[value] = counts.get(value, 0) + 1
    return max(counts, key=counts.get) if counts else None


def _lane_and_family(subject: str) -> tuple[str, str]:
    if subject in {"창유리 등", "창유리의 안전성 등"}:
        return "intentional_cross_phase", "glazing_cross_phase"
    if subject in {"정의", "기준적용의 특례", "물품적재장치", "입석", "승차정원 및 최대적재량"}:
        return "intentional_other_or_review", "intentional_review_lane"
    if subject in {"사이버보안", "소프트웨어"}:
        return "mixed_or_ambiguous_keep_for_review", "software_cyber"
    family_map = {
        "계기판넬": "umbrella_instrument_panel",
        "견인장치 및 연결장치": "umbrella_towing_connection",
        "가스운송장치": "umbrella_gas_transport",
        "배기관": "umbrella_exhaust",
        "좌석등받이": "umbrella_seat_back",
        "접이식좌석": "umbrella_folding_seat",
    }
    return "umbrella_adjudication_candidate", family_map.get(subject, "umbrella_titles_with_weak_unit_text")


def _raw_meta(collection_root: Path) -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    for path in collection_root.rglob("*.xml"):
        if not path.stem.lower().startswith("kmvss_art_"):
            continue
        root = ET.parse(path).getroot()
        meta[f"xml_kmvss-{path.stem.lower()}"] = {"subject": (root.findtext("SUBJECT") or "").strip()}
    return meta


if __name__ == "__main__":
    main()
