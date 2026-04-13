#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from wiki_obsidian.source_audit import build_raw_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    baseline_path = root / "artifacts" / "manifests" / "raw_manifest_baseline.json"
    if not baseline_path.exists():
        print("Raw immutability baseline not found. Skipping strict comparison.")
        return 0

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = build_raw_manifest(root)
    if baseline != current:
        print("Raw immutability check failed.")
        return 1

    print("Raw immutability check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
