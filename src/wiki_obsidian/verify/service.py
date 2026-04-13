from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import ensure_dir, write_json
from wiki_obsidian.utils.ids import build_run_id

SCRIPT_MAP = {
    "frontmatter": "check_frontmatter.py",
    "links": "check_wikilinks.py",
    "provenance": "check_provenance.py",
    "boundaries": "check_layer_boundaries.py",
    "note-ids": "check_note_ids.py",
    "raw-immutability": "check_raw_immutability.py",
    "design-package": "check_design_package.py",
    "index": "build_index.py",
    "operations-index": "build_operations_index.py",
}


def run_checks(
    *,
    check_names: list[str],
    project_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    settings = load_project_settings(project_root)
    results: list[dict[str, Any]] = []
    for name in check_names:
        script_name = SCRIPT_MAP[name]
        script_path = settings.paths.project_root / "harness" / "scripts" / script_name
        command = [sys.executable, str(script_path), "--project-root", str(settings.paths.project_root)]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        output = "\n".join(
            line.strip()
            for line in (completed.stdout + "\n" + completed.stderr).splitlines()
            if line.strip()
        )
        results.append(
            {
                "check": name,
                "script": script_name,
                "returncode": completed.returncode,
                "passed": completed.returncode == 0,
                "output": output,
            }
        )
    return results


def verify_repository(
    *,
    project_root: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    active_run_id = run_id or build_run_id("verify")
    reports_root = ensure_dir(settings.paths.reports_root / "runs" / active_run_id)
    results = run_checks(
        check_names=[
            "frontmatter",
            "links",
            "provenance",
            "boundaries",
            "note-ids",
            "raw-immutability",
            "design-package",
            "index",
            "operations-index",
        ],
        project_root=settings.paths.project_root,
    )
    payload = {
        "run_id": active_run_id,
        "status": "passed" if all(result["passed"] for result in results) else "failed",
        "checks": results,
    }
    report_path = write_json(reports_root / "verify_report.json", payload)
    return payload | {"report_path": str(report_path)}
