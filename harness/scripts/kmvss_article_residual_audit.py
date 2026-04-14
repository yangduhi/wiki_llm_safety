from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import write_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    trace_path = settings.paths.normalized_root / "runs" / args.run_id / "classification_trace.jsonl"
    trace_rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    article_rows = [
        row
        for row in trace_rows
        if row.get("collection_id") == "xml_kmvss"
        and row.get("note_kind") == "unit"
        and "kmvss_art_" in str(row.get("document_id") or "")
    ]
    meta = _raw_meta(settings.paths.collections_root / "xml_kmvss")

    lines = [
        "---",
        "record_layer: operations",
        "id: operations-kmvss-article-residual-buckets-round2b",
        "title: KMVSS Article Residual Buckets Round 2B",
        "summary: Article-only residual audit used for KMVSS round 2B.",
        "status: active",
        "created: 2026-04-13",
        "updated: 2026-04-13",
        "tags:",
        "  - operations",
        "  - kmvss",
        "  - article",
        "  - residual",
        "---",
        "",
        "# KMVSS Article Residual Buckets Round 2B",
        "",
        f"- baseline_run: `{args.run_id}`",
        "",
        "## Cross Phase Top20",
    ]
    for document_id, count in _top_docs(article_rows, kind="cross_phase"):
        subject = meta.get(document_id, {}).get("subject", "")
        lines.append(f"- `{document_id}` / {subject} / count={count} / bucket=`{_article_bucket(subject)}`")
    lines.extend(["", "## Other Or Review Top20"])
    for document_id, count in _top_docs(article_rows, kind="other_or_review"):
        subject = meta.get(document_id, {}).get("subject", "")
        lines.append(f"- `{document_id}` / {subject} / count={count} / bucket=`{_article_bucket(subject)}`")

    bucket_counts = Counter()
    for row in article_rows:
        decision = row.get("final_decision") or {}
        if decision.get("phase") != "cross_phase" and decision.get("functional_domain") != "other_or_review":
            continue
        bucket_counts[_article_bucket(meta.get(str(row.get("document_id") or ""), {}).get("subject", ""))] += 1

    lines.extend(["", "## Bucket Analysis"])
    for bucket, count in bucket_counts.most_common():
        lines.extend(_bucket_note(bucket=bucket, count=count))
    write_text(settings.paths.operations_pilot_root / "kmvss_article_residual_buckets_round2b.md", "\n".join(lines))


def _top_docs(article_rows: list[dict[str, object]], *, kind: str) -> list[tuple[str, int]]:
    counter = Counter()
    for row in article_rows:
        decision = row.get("final_decision") or {}
        if kind == "cross_phase" and decision.get("phase") == "cross_phase":
            counter[str(row["document_id"])] += 1
        if kind == "other_or_review" and decision.get("functional_domain") == "other_or_review":
            counter[str(row["document_id"])] += 1
    return counter.most_common(20)


def _bucket_note(*, bucket: str, count: int) -> list[str]:
    notes = {
        "body_visibility_signaling": (
            "title prior 부족 때문에 `간접시계장치`, `경광등 및 사이렌`, `끝단표시등` 같은 visibility family가 short clause에서 `cross_phase`로 떨어졌다.",
            "해결 포인트는 phrase-level title prior와 short clause inheritance다.",
        ),
        "glazing_cross_phase_intentional": (
            "`창유리 등`과 `창유리의 안전성 등`은 문서 성격상 intentional cross-phase 유지 대상이다.",
            "이 bucket은 줄이는 대상이 아니라 유지 대상이다.",
        ),
        "powertrain_running_gear": (
            "`원동기 및 동력전달장치`, `원동기 출력`, `주행장치` 계열은 title family prior가 약하면 `cross_phase`나 `other_or_review`로 남는다.",
            "해결 포인트는 pre-crash family policy와 short-clause inheritance다.",
        ),
        "braking": (
            "`제동장치` 계열은 umbrella title이 unit에 충분히 내려오지 않으면 multi-signal로 흔들린다.",
            "해결 포인트는 braking family prior와 local evidence 우선 규칙이다.",
        ),
        "software_cyber": (
            "`소프트웨어`, `사이버보안`은 admin/governance family지만 일부 clause는 safe-state/control phrase를 포함한다.",
            "해결 포인트는 default admin + local override 규칙이다.",
        ),
        "definitions": (
            "`정의` 조문은 phase는 잡혀도 domain이 약해 other_or_review가 유지된다.",
            "해결 포인트는 definition phrase 강화와 intentional other_or_review 유지 정책이다.",
        ),
        "special_exceptions": (
            "`기준적용의 특례`는 안정적으로 non_phase_admin이어야 하며 domain은 보수적으로 other_or_review가 맞다.",
            "해결 포인트는 phrase-level admin governance 유지다.",
        ),
        "short_procedural": (
            "짧은 조항은 local text만으로는 signal이 약해 fallback에 취약하다.",
            "해결 포인트는 capped inheritance와 selector margin 조정이다.",
        ),
        "umbrella_titles_with_weak_unit_text": (
            "umbrella 제목이 강하지만 unit text는 짧거나 참조 위주라 title coverage가 부족하면 잔존 residual이 된다.",
            "해결 포인트는 article family prior다.",
        ),
        "mixed_technical_admin": (
            "technical/admin phrase가 함께 있는 조항은 broad token 없이 phrase combo로만 판정해야 한다.",
            "해결 포인트는 admin combo governance와 local-body 우선 규칙이다.",
        ),
    }
    why, fix = notes.get(bucket, ("기본 residual bucket", "custom follow-up needed"))
    return [f"### {bucket}", f"- residual_units: {count}", f"- diagnosis: {why}", f"- general fix: {fix}", ""]


def _article_bucket(subject: str) -> str:
    normalized = subject.strip()
    if normalized in {"창유리 등", "창유리의 안전성 등"}:
        return "glazing_cross_phase_intentional"
    if any(token in normalized for token in ("간접시계장치", "경광등", "끝단표시등", "후미등", "등화", "번호등", "옆면표시등")):
        return "body_visibility_signaling"
    if any(token in normalized for token in ("원동기", "주행장치", "접지부분", "접지압력", "최대안전경사각도", "도난방지장치", "원동기 출력")):
        return "powertrain_running_gear"
    if "제동장치" in normalized:
        return "braking"
    if normalized == "정의":
        return "definitions"
    if "특례" in normalized:
        return "special_exceptions"
    if any(token in normalized for token in ("소프트웨어", "사이버보안")):
        return "software_cyber"
    return "umbrella_titles_with_weak_unit_text"


def _raw_meta(collection_root: Path) -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = defaultdict(dict)
    for path in collection_root.rglob("*.xml"):
        if not path.stem.lower().startswith("kmvss_art_"):
            continue
        root = ET.parse(path).getroot()
        meta[f"xml_kmvss-{path.stem.lower()}"] = {
            "subject": (root.findtext("SUBJECT") or "").strip(),
        }
    return meta


if __name__ == "__main__":
    main()
