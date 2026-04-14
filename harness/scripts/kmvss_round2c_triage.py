from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_jsonl, write_text


CANDIDATE_DOCS = [
    "xml_kmvss-kmvss_art_34_048",
    "xml_kmvss-kmvss_art_105_158",
    "xml_kmvss-kmvss_art_2_002",
    "xml_kmvss-kmvss_art_114_189",
    "xml_kmvss-kmvss_art_32_046",
    "xml_kmvss-kmvss_art_28_042",
    "xml_kmvss-kmvss_art_113_188",
    "xml_kmvss-kmvss_art_18_028",
    "xml_kmvss-kmvss_art_18_029",
    "xml_kmvss-kmvss_art_88_129",
    "xml_kmvss-kmvss_art_20_032",
    "xml_kmvss-kmvss_art_33_047",
    "xml_kmvss-kmvss_art_37_051",
    "xml_kmvss-kmvss_art_98_147",
    "xml_kmvss-kmvss_art_25_038",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    settings = load_project_settings(args.project_root)
    documents = {row["document_id"]: row for row in read_jsonl(settings.paths.normalized_root / "runs" / args.run_id / "documents.jsonl")}
    trace_rows = [row for row in read_jsonl(settings.paths.normalized_root / "runs" / args.run_id / "classification_trace.jsonl") if row.get("note_kind") == "unit"]
    meta = _raw_meta(settings.paths.collections_root / "xml_kmvss")

    register_path = settings.paths.operations_pilot_root / "kmvss_round2c_review_lane_register.csv"
    with register_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "subject",
                "current_phase",
                "current_domain",
                "lane",
                "umbrella_family",
                "intentional_retain",
                "retain_reason",
                "policy_basis",
                "reference_repo_pattern",
                "decision_kind",
                "local_text_weakness",
                "taxonomy_fit",
                "risk_note",
            ],
        )
        writer.writeheader()
        triage_lines = [
            "---",
            "record_layer: operations",
            "id: operations-kmvss-round2c-residual-triage",
            "title: KMVSS Round 2C Residual Triage",
            "summary: Lane-based triage for KMVSS article residuals in round 2C.",
            "status: active",
            "created: 2026-04-14",
            "updated: 2026-04-14",
            "tags:",
            "  - operations",
            "  - kmvss",
            "  - round2c",
            "  - triage",
            "---",
            "",
            "# KMVSS Round 2C Residual Triage",
            "",
            f"- run_id: `{args.run_id}`",
            "",
        ]
        adjudications: list[dict[str, object]] = []
        for document_id in CANDIDATE_DOCS:
            doc = documents[document_id]
            subject = meta.get(document_id, {}).get("subject", "")
            rows = [row for row in trace_rows if row.get("document_id") == document_id]
            lane = _mode(rows, "review_lane_type")
            umbrella_family = _mode(rows, "umbrella_family")
            intentional = bool(_mode(rows, "intentional_retain"))
            retain_reason = _mode(rows, "retain_reason")
            policy_basis = _mode(rows, "policy_basis")
            repo_pattern = _mode(rows, "reference_repo_pattern")
            cross_count = sum(1 for row in rows if row.get("final_decision", {}).get("phase") == "cross_phase")
            other_count = sum(1 for row in rows if row.get("final_decision", {}).get("functional_domain") == "other_or_review")
            decision_kind = "policy retain" if intentional else "classification improvement target"
            local_text_weakness = "high" if any(bool(row.get("is_short_clause")) for row in rows) else "medium"
            taxonomy_fit = _taxonomy_fit(lane)
            risk_note = _risk_note(lane, subject)
            writer.writerow(
                {
                    "document_id": document_id,
                    "subject": subject,
                    "current_phase": doc["phase"],
                    "current_domain": doc["functional_domain"][0],
                    "lane": lane,
                    "umbrella_family": umbrella_family,
                    "intentional_retain": intentional,
                    "retain_reason": retain_reason,
                    "policy_basis": policy_basis,
                    "reference_repo_pattern": repo_pattern,
                    "decision_kind": decision_kind,
                    "local_text_weakness": local_text_weakness,
                    "taxonomy_fit": taxonomy_fit,
                    "risk_note": risk_note,
                }
            )
            adjudications.append(
                {
                    "document_id": document_id,
                    "subject": subject,
                    "lane": lane,
                    "umbrella_family": umbrella_family,
                    "intentional_retain": intentional,
                    "retain_reason": retain_reason,
                    "policy_basis": policy_basis,
                    "reference_repo_pattern": repo_pattern,
                    "current_phase": doc["phase"],
                    "current_domain": doc["functional_domain"][0],
                    "cross_units": cross_count,
                    "other_units": other_count,
                }
            )
            triage_lines.extend(
                [
                    f"## {subject}",
                    f"- document_id: `{document_id}`",
                    f"- current_phase: `{doc['phase']}`",
                    f"- current_domain: `{doc['functional_domain'][0]}`",
                    f"- lane: `{lane}`",
                    f"- umbrella_family: `{umbrella_family}`",
                    f"- intentional_retain: `{intentional}`",
                    f"- retain_reason: `{retain_reason}`",
                    f"- policy_basis: `{policy_basis}`",
                    f"- reference_repo_pattern: `{repo_pattern}`",
                    f"- residual_summary: cross=`{cross_count}` / other=`{other_count}`",
                    f"- local_text_weakness: `{local_text_weakness}`",
                    f"- taxonomy_fit: {taxonomy_fit}",
                    f"- risk_note: {risk_note}",
                    f"- final_decision_kind: `{decision_kind}`",
                    "",
                ]
            )

    write_text(settings.paths.operations_pilot_root / "kmvss_round2c_residual_triage.md", "\n".join(triage_lines))
    (settings.paths.operations_pilot_root / "kmvss_round2c_adjudications.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in adjudications) + "\n",
        encoding="utf-8",
    )


def _mode(rows: list[dict[str, object]], key: str) -> object:
    counts: dict[object, int] = {}
    for row in rows:
        value = row.get(key)
        counts[value] = counts.get(value, 0) + 1
    return max(counts, key=counts.get) if counts else None


def _taxonomy_fit(lane: str | None) -> str:
    if lane == "intentional_cross_phase":
        return "true multi-phase"
    if lane == "intentional_other_or_review":
        return "taxonomy gap or governance scope"
    if lane == "mixed_or_ambiguous_keep_for_review":
        return "mixed technical/admin"
    return "umbrella title needs adjudication"


def _risk_note(lane: str | None, subject: str) -> str:
    if lane == "intentional_cross_phase":
        return "forcing a single phase would discard genuine visibility-retention overlap"
    if lane == "intentional_other_or_review":
        return "forcing a canonical domain would create artificial precision"
    if lane == "mixed_or_ambiguous_keep_for_review":
        return "technical and admin phrases coexist, so over-committing is risky"
    return f"`{subject}` still looks like an umbrella family that can be pushed further with family priors"


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
