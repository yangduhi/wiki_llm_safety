from __future__ import annotations

import argparse
import json

from wiki_obsidian.classification import classify_phase_from_notes
from wiki_obsidian.crosswalk import build_crosswalk
from wiki_obsidian.dashboard import dashboard_refresh
from wiki_obsidian.ingest.service import ingest_wiki
from wiki_obsidian.lint.service import lint_reflect
from wiki_obsidian.normalize.service import normalize_collection
from wiki_obsidian.onboarding import apply_profile, inspect_collection, propose_profile
from wiki_obsidian.parse.service import parse_collection
from wiki_obsidian.query.service import query_writeback
from wiki_obsidian.scan.service import scan_sources
from wiki_obsidian.schema_service import schema_validate
from wiki_obsidian.source_audit import source_audit
from wiki_obsidian.verify.service import verify_repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="wiki-obsidian")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect-collection")
    inspect_parser.add_argument("--collection", required=True)
    inspect_parser.add_argument("--run-id")

    propose_parser = subparsers.add_parser("propose-profile")
    propose_parser.add_argument("--collection", required=True)
    propose_parser.add_argument("--run-id")

    apply_parser = subparsers.add_parser("apply-profile")
    apply_parser.add_argument("--collection", required=True)
    apply_parser.add_argument("--run-id")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--collection")
    scan_parser.add_argument("--run-id")

    parse_parser = subparsers.add_parser("parse")
    parse_parser.add_argument("--collection", required=True)
    parse_parser.add_argument("--run-id")

    normalize_parser = subparsers.add_parser("normalize")
    normalize_parser.add_argument("--collection", required=True)
    normalize_parser.add_argument("--run-id")

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--collection", required=True)
    ingest_parser.add_argument("--run-id")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--collection", required=True)
    run_parser.add_argument("--run-id")

    query_parser = subparsers.add_parser("query-writeback")
    query_parser.add_argument("question")
    query_parser.add_argument("--collection")
    query_parser.add_argument("--run-id")
    query_parser.add_argument("--writeback", action="store_true")

    lint_parser = subparsers.add_parser("lint-reflect")
    lint_parser.add_argument("--collection")
    lint_parser.add_argument("--run-id")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--run-id")

    schema_parser = subparsers.add_parser("schema-validate")
    schema_parser.add_argument("--run-id")

    classify_parser = subparsers.add_parser("classify-phase")
    classify_parser.add_argument("text")

    crosswalk_parser = subparsers.add_parser("build-crosswalk")
    crosswalk_parser.add_argument("--run-id")

    dashboard_parser = subparsers.add_parser("dashboard-refresh")
    dashboard_parser.add_argument("--run-id")

    source_audit_parser = subparsers.add_parser("source-audit")
    source_audit_parser.add_argument("--run-id")
    source_audit_parser.add_argument("--write-baseline", action="store_true")

    args = parser.parse_args()

    if args.command == "inspect-collection":
        payload = inspect_collection(collection=args.collection, run_id=args.run_id)
    elif args.command == "propose-profile":
        payload = propose_profile(collection=args.collection, run_id=args.run_id)
    elif args.command == "apply-profile":
        payload = apply_profile(collection=args.collection, run_id=args.run_id)
    elif args.command == "scan":
        payload = scan_sources(collection=args.collection, run_id=args.run_id)
    elif args.command == "parse":
        payload = parse_collection(collection=args.collection, run_id=args.run_id)
    elif args.command == "normalize":
        payload = normalize_collection(collection=args.collection, run_id=args.run_id)
    elif args.command == "ingest":
        payload = ingest_wiki(collection=args.collection, run_id=args.run_id)
    elif args.command == "run":
        payload = _run_collection(collection=args.collection, run_id=args.run_id)
    elif args.command == "query-writeback":
        payload = query_writeback(
            question=args.question,
            collection=args.collection,
            run_id=args.run_id,
            writeback=args.writeback,
        )
    elif args.command == "lint-reflect":
        payload = lint_reflect(collection=args.collection, run_id=args.run_id)
    elif args.command == "verify":
        payload = verify_repository(run_id=args.run_id)
    elif args.command == "schema-validate":
        payload = schema_validate(run_id=args.run_id)
    elif args.command == "classify-phase":
        payload = classify_phase_from_notes(args.text)
    elif args.command == "build-crosswalk":
        payload = build_crosswalk(run_id=args.run_id)
    elif args.command == "dashboard-refresh":
        payload = dashboard_refresh(run_id=args.run_id)
    elif args.command == "source-audit":
        payload = source_audit(run_id=args.run_id, write_baseline=args.write_baseline)
    else:
        raise ValueError(f"Unsupported command: {args.command}")

    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _run_collection(*, collection: str, run_id: str | None) -> dict[str, object]:
    scan_payload = scan_sources(collection=collection, run_id=run_id)
    active_run_id = str(scan_payload["run_id"])
    parse_payload = parse_collection(collection=collection, run_id=active_run_id)
    normalize_payload = normalize_collection(collection=collection, run_id=active_run_id)
    ingest_payload = ingest_wiki(collection=collection, run_id=active_run_id)
    verify_payload = verify_repository(run_id=active_run_id)
    return {
        "collection": collection,
        "run_id": active_run_id,
        "scan": scan_payload,
        "parse": parse_payload,
        "normalize": normalize_payload,
        "ingest": ingest_payload,
        "verify": verify_payload,
    }


if __name__ == "__main__":
    main()
