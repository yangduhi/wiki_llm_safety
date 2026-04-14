from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.parse.service import _attachment_bucket_from_subject
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_jsonl, write_text


EXEMPLARS = [
    "xml_kmvss-kmvss_att_0006_066",
    "xml_kmvss-kmvss_att_0001_001",
    "xml_kmvss-kmvss_att_0024_125",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--before-run", required=True)
    parser.add_argument("--after-run", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    before_units = _load_units(settings.paths.normalized_root / "runs" / args.before_run / "units.jsonl")
    after_units = _load_units(settings.paths.normalized_root / "runs" / args.after_run / "units.jsonl")
    before_trace = _load_trace(settings.paths.normalized_root / "runs" / args.before_run / "classification_trace.jsonl")
    after_trace = _load_trace(settings.paths.normalized_root / "runs" / args.after_run / "classification_trace.jsonl")
    meta = _raw_meta(settings.paths.collections_root / "xml_kmvss")

    before_attachment = [row for row in before_units if row.get("source_collection") == "xml_kmvss" and _is_attachment_row(row)]
    after_attachment = [row for row in after_units if row.get("source_collection") == "xml_kmvss" and _is_attachment_row(row)]
    before_articles = [row for row in before_units if row.get("source_collection") == "xml_kmvss" and not _is_attachment_row(row)]
    after_articles = [row for row in after_units if row.get("source_collection") == "xml_kmvss" and not _is_attachment_row(row)]

    csv_rows = _top20_before_after(before_units, after_units, meta)
    csv_path = settings.paths.operations_pilot_root / "kmvss_attachment_top20_before_after.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "sectno",
                "subject",
                "bucket",
                "before_cross_units",
                "after_cross_units",
                "before_other_units",
                "after_other_units",
                "before_total_units",
                "after_total_units",
                "major_fallback_before",
                "major_fallback_after",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-attachment-comparable-evaluation",
        "title: KMVSS Attachment Comparable Evaluation",
        "summary: Before and after evaluation for KMVSS attachment-aware round 2A.",
        "status: active",
        "created: 2026-04-13",
        "updated: 2026-04-13",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - attachment",
        "  - evaluation",
        "---",
        "",
        "# KMVSS Attachment Comparable Evaluation",
        "",
        f"- before_run: `{args.before_run}`",
        f"- after_run: `{args.after_run}`",
        "",
        "## Raw Full-Corpus Comparison",
    ]
    lines.extend(_render_ratio_block("all", before_units, after_units))
    lines.append("")
    lines.append("## Attachment-Only Comparison")
    lines.extend(_render_ratio_block("attachments", before_attachment, after_attachment))
    lines.append("")
    lines.append("## Non-Attachment Comparison")
    lines.extend(_render_ratio_block("articles", before_articles, after_articles))
    lines.append("")
    lines.append("## Same-Document Top20 Comparison")
    for row in csv_rows:
        lines.append(
            "- "
            f"`{row['document_id']}` / {row['subject']} / bucket=`{row['bucket']}` / "
            f"cross `{row['before_cross_units']} -> {row['after_cross_units']}` / "
            f"other `{row['before_other_units']} -> {row['after_other_units']}` / "
            f"fallback `{row['major_fallback_before']} -> {row['major_fallback_after']}`"
        )
    lines.append("")
    lines.append("## Exemplar Trace Diff")
    for document_id in EXEMPLARS:
        lines.extend(_render_exemplar(document_id, before_trace, after_trace, meta))
        lines.append("")
    write_text(settings.paths.operations_pilot_root / "kmvss_attachment_comparable_evaluation.md", "\n".join(lines))


def _load_units(path: Path) -> list[dict[str, object]]:
    return [row for row in read_jsonl(path) if row.get("source_collection") == "xml_kmvss"]


def _load_trace(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _is_attachment_row(row: dict[str, object]) -> bool:
    return bool(row.get("is_attachment")) or "kmvss_att_" in str(row.get("document_id") or "")


def _ratio(rows: list[dict[str, object]], *, metric: str) -> tuple[int, int, float]:
    total = len(rows)
    if metric == "cross_phase":
        count = sum(1 for row in rows if row.get("phase") == "cross_phase")
    else:
        count = sum(1 for row in rows if (row.get("functional_domain") or [None])[0] == "other_or_review")
    return count, total, (count / total) if total else 0.0


def _render_ratio_block(label: str, before_rows: list[dict[str, object]], after_rows: list[dict[str, object]]) -> list[str]:
    before_cross, before_total, before_cross_ratio = _ratio(before_rows, metric="cross_phase")
    after_cross, after_total, after_cross_ratio = _ratio(after_rows, metric="cross_phase")
    before_other, _, before_other_ratio = _ratio(before_rows, metric="other_or_review")
    after_other, _, after_other_ratio = _ratio(after_rows, metric="other_or_review")
    return [
        f"- slice: `{label}`",
        f"- total_units: `{before_total} -> {after_total}`",
        f"- cross_phase: `{before_cross} -> {after_cross}` (`{before_cross_ratio:.2%} -> {after_cross_ratio:.2%}`)",
        f"- other_or_review: `{before_other} -> {after_other}` (`{before_other_ratio:.2%} -> {after_other_ratio:.2%}`)",
    ]


def _top20_before_after(
    before_units: list[dict[str, object]],
    after_units: list[dict[str, object]],
    meta: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    before = _doc_stats(before_units)
    after = _doc_stats(after_units)
    top_documents = sorted(
        before.keys(),
        key=lambda document_id: before[document_id]["cross_phase"] + before[document_id]["other_or_review"],
        reverse=True,
    )[:20]
    rows: list[dict[str, object]] = []
    for document_id in top_documents:
        before_stats = before.get(document_id, {})
        after_stats = after.get(document_id, {})
        doc_meta = meta.get(document_id, {})
        rows.append(
            {
                "document_id": document_id,
                "sectno": doc_meta.get("sectno", ""),
                "subject": doc_meta.get("subject", ""),
                "bucket": _attachment_bucket_from_subject(str(doc_meta.get("subject") or "")),
                "before_cross_units": before_stats.get("cross_phase", 0),
                "after_cross_units": after_stats.get("cross_phase", 0),
                "before_other_units": before_stats.get("other_or_review", 0),
                "after_other_units": after_stats.get("other_or_review", 0),
                "before_total_units": before_stats.get("total_units", 0),
                "after_total_units": after_stats.get("total_units", 0),
                "major_fallback_before": before_stats.get("major_fallback", "<none>"),
                "major_fallback_after": after_stats.get("major_fallback", "<none>"),
            }
        )
    return rows


def _doc_stats(units: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    stats: dict[str, dict[str, object]] = defaultdict(lambda: {"cross_phase": 0, "other_or_review": 0, "total_units": 0})
    trace_map: dict[str, Counter[str]] = defaultdict(Counter)
    for unit in units:
        document_id = str(unit.get("document_id") or "")
        if "kmvss_att_" not in document_id:
            continue
        stats[document_id]["total_units"] += 1
        if unit.get("phase") == "cross_phase":
            stats[document_id]["cross_phase"] += 1
        if (unit.get("functional_domain") or [None])[0] == "other_or_review":
            stats[document_id]["other_or_review"] += 1
    return stats


def _render_exemplar(
    document_id: str,
    before_trace: list[dict[str, object]],
    after_trace: list[dict[str, object]],
    meta: dict[str, dict[str, str]],
) -> list[str]:
    before_rows = [row for row in before_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    after_rows = [row for row in after_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    doc_meta = meta.get(document_id, {})
    before_fallback = Counter(str(row.get("fallback_reason") or "<none>") for row in before_rows)
    after_fallback = Counter(str(row.get("fallback_reason") or "<none>") for row in after_rows)
    lines = [
        f"### {document_id}",
        f"- subject: {doc_meta.get('subject', '')}",
        f"- before_units: {len(before_rows)} / after_units: {len(after_rows)}",
        f"- before_fallback_top3: {before_fallback.most_common(3)}",
        f"- after_fallback_top3: {after_fallback.most_common(3)}",
    ]
    return lines


def _raw_meta(collection_root: Path) -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    for path in collection_root.rglob("*.xml"):
        root = ET.parse(path).getroot()
        meta[f"xml_kmvss-{path.stem.lower()}"] = {
            "sectno": (root.findtext("SECTNO") or "").strip(),
            "subject": (root.findtext("SUBJECT") or "").strip(),
        }
    return meta


if __name__ == "__main__":
    main()
