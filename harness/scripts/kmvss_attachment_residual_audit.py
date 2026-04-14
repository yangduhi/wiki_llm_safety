from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.parse.service import _attachment_bucket_from_subject
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import write_text


BUCKET_NOTES = {
    "lighting_photometric_reflector_signaling": {
        "cross_phase": "등화/광도 표 문서가 broad title 또는 약한 visibility 신호만 가진 채 table row로 쪼개지면 cross_phase로 잔존한다.",
        "other_or_review": "광원형식·광도·반사기 row가 section context를 잃으면 domain이 비어 other_or_review로 떨어진다.",
        "root_cause": "주원인은 parse와 selector다. row가 semantic header와 분리되고, subject prior보다 row text가 먼저 평가된다.",
    },
    "braking_performance_hardware": {
        "cross_phase": "제동능력/브레이크호스 표는 pre/in 신호가 약하게 섞여 multi-phase처럼 보일 수 있다.",
        "other_or_review": "숫자/시험 조건 row가 단독 unit가 되면 braking domain이 약해진다.",
        "root_cause": "parse와 selector가 주원인이고, braking subject prior가 부족하면 residual이 커진다.",
    },
    "tire_wheel_hose_running_gear": {
        "cross_phase": "타이어/휠 문서는 구조·성능 단어가 broad하게 소비되면 cross_phase 노이즈를 만든다.",
        "other_or_review": "표기/구조/성능 spec는 taxonomy상 intentionally retained other_or_review가 일부 맞다.",
        "root_cause": "normalize와 taxonomy가 함께 얽힌다. marking/specification과 safety domain을 분리해야 한다.",
    },
    "emc_electrical_compatibility": {
        "cross_phase": "적합성·유지 같은 약한 단어가 attachment 기술표에서 admin/in-crash를 동시에 흔든다.",
        "other_or_review": "EMC는 canonical domain에 억지 매핑하지 않는 편이 안전해 other_or_review가 정책적으로 남을 수 있다.",
        "root_cause": "selector와 taxonomy가 주원인이다. EMC는 admin-like지만 domain은 intentionally conservative해야 한다.",
    },
    "labeling_marking_indication": {
        "cross_phase": "표기/표시 문서 루트가 broad override에 끌리면 cross_phase가 생긴다.",
        "other_or_review": "표시 기준/식별표시는 admin-like로 읽히지만 canonical domain으로는 억지 매핑하지 않는 편이 안전하다.",
        "root_cause": "lexicon과 selector가 주원인이다. 표시/표기 문맥을 non_phase_admin 쪽으로 묶어야 한다.",
    },
    "short_value_rows": {
        "cross_phase": "숫자/단위 row가 독립 unit가 되면 no_phase_signal fallback으로 cross_phase가 누적된다.",
        "other_or_review": "domain도 함께 비어 other_or_review가 대량 발생한다.",
        "root_cause": "parse가 핵심이다. row merge와 section inheritance가 없으면 residual이 계속 남는다.",
    },
    "admin_like_exception_rows": {
        "cross_phase": "적용 제외/특례가 table 조건 안에 숨어 있으면 low-phase cross_phase가 남을 수 있다.",
        "other_or_review": "admin row는 phase는 잡혀도 domain은 intentionally other_or_review가 많다.",
        "root_cause": "selector와 taxonomy가 주원인이다. admin signal은 강화하되 domain은 보수적으로 둔다.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    trace_path = settings.paths.normalized_root / "runs" / args.run_id / "classification_trace.jsonl"
    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    unit_rows = [row for row in rows if row.get("note_kind") == "unit" and row.get("collection_id") == "xml_kmvss"]
    meta = _raw_meta(settings.paths.collections_root / "xml_kmvss")

    bucket_counts: Counter[str] = Counter()
    fallback_counts: dict[str, Counter[str]] = {"cross_phase": Counter(), "other_or_review": Counter()}
    attachment_rows: list[dict[str, object]] = []
    for row in unit_rows:
        document_id = str(row.get("document_id") or "")
        if "kmvss_att_" not in document_id:
            continue
        doc_meta = meta.get(document_id, {})
        bucket = _attachment_bucket_from_subject(str(doc_meta.get("subject") or ""))
        fallback = str(row.get("fallback_reason") or "<none>")
        decision = row.get("final_decision") or {}
        if decision.get("phase") == "cross_phase":
            fallback_counts["cross_phase"][fallback] += 1
            bucket_counts[bucket] += 1
        if decision.get("functional_domain") == "other_or_review":
            fallback_counts["other_or_review"][fallback] += 1
            bucket_counts[bucket] += 1
        attachment_rows.append(
            {
                "document_id": document_id,
                "bucket": bucket,
                "phase": decision.get("phase"),
                "domain": decision.get("functional_domain"),
                "fallback_reason": fallback,
            }
        )

    top_docs = _top_attachment_docs(unit_rows, meta)
    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-attachment-residual-buckets",
        "title: KMVSS Attachment Residual Buckets",
        "summary: Baseline attachment residual buckets for KMVSS round 2A.",
        "status: active",
        "created: 2026-04-13",
        "updated: 2026-04-13",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - attachment",
        "  - residual",
        "---",
        "",
        "# KMVSS Attachment Residual Buckets",
        "",
        f"- baseline_run: `{args.run_id}`",
        f"- attachment_cross_phase_units: {sum(1 for row in attachment_rows if row['phase'] == 'cross_phase')}",
        f"- attachment_other_or_review_units: {sum(1 for row in attachment_rows if row['domain'] == 'other_or_review')}",
        "",
        "## Bucket Summary",
    ]
    for bucket, count in bucket_counts.most_common():
        notes = BUCKET_NOTES.get(bucket, {})
        lines.extend(
            [
                f"### {bucket}",
                f"- residual_units: {count}",
                f"- why_cross_phase: {notes.get('cross_phase', 'n/a')}",
                f"- why_other_or_review: {notes.get('other_or_review', 'n/a')}",
                f"- main_cause: {notes.get('root_cause', 'n/a')}",
                "",
            ]
        )
    lines.append("## Major Fallback Reasons")
    for label, counter in fallback_counts.items():
        lines.append(f"### {label}")
        for reason, count in counter.most_common(10):
            lines.append(f"- {reason}: {count}")
        lines.append("")
    lines.append("## Top Attachment Residual Documents")
    for row in top_docs:
        lines.append(
            "- "
            f"`{row['document_id']}` / `{row['sectno']}` / {row['subject']} / "
            f"bucket=`{row['bucket']}` / cross={row['cross_phase']} / other={row['other_or_review']}"
        )
    lines.append("")
    write_text(settings.paths.operations_pilot_root / "kmvss_attachment_residual_buckets.md", "\n".join(lines))


def _raw_meta(collection_root: Path) -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    for path in collection_root.rglob("*.xml"):
        root = ET.parse(path).getroot()
        doc_id = f"xml_kmvss-{path.stem.lower()}"
        meta[doc_id] = {
            "sectno": (root.findtext("SECTNO") or "").strip(),
            "subject": (root.findtext("SUBJECT") or "").strip(),
            "raw_file": path.name,
        }
    return meta


def _top_attachment_docs(unit_rows: list[dict[str, object]], meta: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    per_doc = defaultdict(lambda: {"cross_phase": 0, "other_or_review": 0, "total_units": 0})
    for row in unit_rows:
        document_id = str(row.get("document_id") or "")
        if "kmvss_att_" not in document_id:
            continue
        per_doc[document_id]["total_units"] += 1
        decision = row.get("final_decision") or {}
        if decision.get("phase") == "cross_phase":
            per_doc[document_id]["cross_phase"] += 1
        if decision.get("functional_domain") == "other_or_review":
            per_doc[document_id]["other_or_review"] += 1
    ordered = sorted(
        per_doc.items(),
        key=lambda item: (item[1]["cross_phase"] + item[1]["other_or_review"], item[1]["cross_phase"]),
        reverse=True,
    )[:20]
    out: list[dict[str, object]] = []
    for document_id, stats in ordered:
        doc_meta = meta.get(document_id, {})
        out.append(
            {
                "document_id": document_id,
                "sectno": doc_meta.get("sectno", ""),
                "subject": doc_meta.get("subject", ""),
                "bucket": _attachment_bucket_from_subject(str(doc_meta.get("subject") or "")),
                **stats,
            }
        )
    return out


if __name__ == "__main__":
    main()
