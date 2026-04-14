from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_jsonl, write_text


TARGET_DOCS = [
    "xml_kmvss-kmvss_art_34_048",
    "xml_kmvss-kmvss_art_105_158",
    "xml_kmvss-kmvss_art_50_073",
    "xml_kmvss-kmvss_art_58_085",
    "xml_kmvss-kmvss_art_40_060",
    "xml_kmvss-kmvss_art_47_070",
    "xml_kmvss-kmvss_art_77_111",
    "xml_kmvss-kmvss_art_2_002",
    "xml_kmvss-kmvss_art_114_189",
    "xml_kmvss-kmvss_art_18_028",
    "xml_kmvss-kmvss_art_18_029",
    "xml_kmvss-kmvss_art_11_014",
    "xml_kmvss-kmvss_art_63_092",
    "xml_kmvss-kmvss_art_106_159",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--before-run", required=True)
    parser.add_argument("--after-run", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    before_units = [row for row in read_jsonl(settings.paths.normalized_root / "runs" / args.before_run / "units.jsonl") if row.get("source_collection") == "xml_kmvss"]
    after_units = [row for row in read_jsonl(settings.paths.normalized_root / "runs" / args.after_run / "units.jsonl") if row.get("source_collection") == "xml_kmvss"]
    before_trace = _load_trace(settings.paths.normalized_root / "runs" / args.before_run / "classification_trace.jsonl")
    after_trace = _load_trace(settings.paths.normalized_root / "runs" / args.after_run / "classification_trace.jsonl")
    meta = _raw_meta(settings.paths.collections_root / "xml_kmvss")

    csv_rows = _top20_before_after(before_units, after_units, meta)
    csv_path = settings.paths.operations_pilot_root / "kmvss_article_top20_before_after_round2b.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "subject",
                "bucket",
                "before_cross_units",
                "after_cross_units",
                "before_other_units",
                "after_other_units",
                "before_total_units",
                "after_total_units",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-article-comparable-evaluation-round2b",
        "title: KMVSS Article Comparable Evaluation Round 2B",
        "summary: Before and after comparison for article-only KMVSS residual reduction round 2B.",
        "status: active",
        "created: 2026-04-13",
        "updated: 2026-04-13",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - article",
        "  - evaluation",
        "---",
        "",
        "# KMVSS Article Comparable Evaluation Round 2B",
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
    lines.extend(["", "## Fixed Article Residual Slice"])
    lines.extend(_ratio_block("target_docs", _filter_docs(_article_rows(before_units), TARGET_DOCS), _filter_docs(_article_rows(after_units), TARGET_DOCS)))
    lines.extend(["", "## Same-Document Top20 Comparison"])
    for row in csv_rows:
        lines.append(
            f"- `{row['document_id']}` / {row['subject']} / bucket=`{row['bucket']}` / "
            f"cross `{row['before_cross_units']} -> {row['after_cross_units']}` / "
            f"other `{row['before_other_units']} -> {row['after_other_units']}`"
        )
    lines.extend(["", "## Exemplar Trace Diff"])
    for document_id in TARGET_DOCS[:8]:
        lines.extend(_render_trace_summary(document_id, before_trace, after_trace, meta))
        lines.append("")
    write_text(settings.paths.operations_pilot_root / "kmvss_article_comparable_evaluation_round2b.md", "\n".join(lines))


def _load_trace(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _article_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if "kmvss_art_" in str(row.get("document_id") or "")]


def _attachment_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if row.get("is_attachment") or "kmvss_att_" in str(row.get("document_id") or "")]


def _filter_docs(rows: list[dict[str, object]], docs: list[str]) -> list[dict[str, object]]:
    doc_set = set(docs)
    return [row for row in rows if str(row.get("document_id") or "") in doc_set]


def _ratio_block(label: str, before_rows: list[dict[str, object]], after_rows: list[dict[str, object]]) -> list[str]:
    return [
        f"- slice: `{label}`",
        f"- total_units: `{len(before_rows)} -> {len(after_rows)}`",
        f"- cross_phase: `{_count(before_rows, 'cross_phase')} -> {_count(after_rows, 'cross_phase')}` (`{_ratio(before_rows, 'cross_phase'):.2%} -> {_ratio(after_rows, 'cross_phase'):.2%}`)",
        f"- other_or_review: `{_count(before_rows, 'other_or_review')} -> {_count(after_rows, 'other_or_review')}` (`{_ratio(before_rows, 'other_or_review'):.2%} -> {_ratio(after_rows, 'other_or_review'):.2%}`)",
    ]


def _count(rows: list[dict[str, object]], metric: str) -> int:
    if metric == "cross_phase":
        return sum(1 for row in rows if row.get("phase") == "cross_phase")
    return sum(1 for row in rows if (row.get("functional_domain") or [None])[0] == "other_or_review")


def _ratio(rows: list[dict[str, object]], metric: str) -> float:
    return _count(rows, metric) / len(rows) if rows else 0.0


def _top20_before_after(
    before_units: list[dict[str, object]],
    after_units: list[dict[str, object]],
    meta: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    before = _doc_stats(_article_rows(before_units))
    after = _doc_stats(_article_rows(after_units))
    docs = sorted(before, key=lambda doc: before[doc]["cross"] + before[doc]["other"], reverse=True)[:20]
    out: list[dict[str, object]] = []
    for document_id in docs:
        subject = meta.get(document_id, {}).get("subject", "")
        out.append(
            {
                "document_id": document_id,
                "subject": subject,
                "bucket": _article_bucket(subject),
                "before_cross_units": before[document_id]["cross"],
                "after_cross_units": after.get(document_id, {}).get("cross", 0),
                "before_other_units": before[document_id]["other"],
                "after_other_units": after.get(document_id, {}).get("other", 0),
                "before_total_units": before[document_id]["total"],
                "after_total_units": after.get(document_id, {}).get("total", 0),
            }
        )
    return out


def _doc_stats(rows: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = defaultdict(lambda: {"cross": 0, "other": 0, "total": 0})
    for row in rows:
        document_id = str(row.get("document_id") or "")
        stats[document_id]["total"] += 1
        if row.get("phase") == "cross_phase":
            stats[document_id]["cross"] += 1
        if (row.get("functional_domain") or [None])[0] == "other_or_review":
            stats[document_id]["other"] += 1
    return stats


def _render_trace_summary(
    document_id: str,
    before_trace: list[dict[str, object]],
    after_trace: list[dict[str, object]],
    meta: dict[str, dict[str, str]],
) -> list[str]:
    before_rows = [row for row in before_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    after_rows = [row for row in after_trace if row.get("document_id") == document_id and row.get("note_kind") == "unit"]
    before_fallback = Counter(str(row.get("fallback_reason") or "<none>") for row in before_rows)
    after_fallback = Counter(str(row.get("fallback_reason") or "<none>") for row in after_rows)
    return [
        f"### {document_id}",
        f"- subject: {meta.get(document_id, {}).get('subject', '')}",
        f"- before_units: {len(before_rows)} / after_units: {len(after_rows)}",
        f"- before_cross: {sum(1 for row in before_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}",
        f"- after_cross: {sum(1 for row in after_rows if row.get('final_decision', {}).get('phase') == 'cross_phase')}",
        f"- before_other: {sum(1 for row in before_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}",
        f"- after_other: {sum(1 for row in after_rows if row.get('final_decision', {}).get('functional_domain') == 'other_or_review')}",
        f"- before_fallback_top3: {before_fallback.most_common(3)}",
        f"- after_fallback_top3: {after_fallback.most_common(3)}",
    ]


def _article_bucket(subject: str) -> str:
    normalized = subject.strip()
    if normalized in {"창유리 등", "창유리의 안전성 등"}:
        return "glazing_cross_phase_intentional"
    if any(token in normalized for token in ("간접시계장치", "경광등", "사이렌", "끝단표시등", "후미등", "그 밖의 등화", "번호등", "옆면표시등")):
        return "body_visibility_signaling"
    if any(token in normalized for token in ("원동기", "원동기 출력", "주행장치", "접지부분", "접지압력", "최대안전경사각도", "도난방지장치")):
        return "powertrain_running_gear"
    if "제동장치" in normalized:
        return "braking"
    if normalized == "정의":
        return "definitions"
    if "특례" in normalized:
        return "special_exceptions"
    if any(token in normalized for token in ("소프트웨어", "사이버보안")):
        return "software_cyber"
    if any(token in normalized for token in ("다음 각 호", "다만", "해당")):
        return "short_procedural"
    return "umbrella_titles_with_weak_unit_text"


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
