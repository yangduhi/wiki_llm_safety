from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from wiki_obsidian.jurisdiction_overviews import refresh_jurisdiction_overviews
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.dashboard import dashboard_refresh
from wiki_obsidian.operations import rebuild_indexes
from wiki_obsidian.schema_service import schema_validate
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
    "generated-surfaces": "check_generated_surfaces.py",
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
    results: list[dict[str, Any]] = []

    jurisdiction_payload = refresh_jurisdiction_overviews(
        project_root=settings.paths.project_root,
        run_id=active_run_id,
    )
    results.append(
        {
            "check": "jurisdiction-overviews-refresh",
            "script": "refresh_jurisdiction_overviews",
            "returncode": 0,
            "passed": True,
            "output": json.dumps(jurisdiction_payload, ensure_ascii=False, sort_keys=True),
        }
    )

    dashboard_refresh(project_root=settings.paths.project_root, run_id=active_run_id)
    results.append(
        {
            "check": "dashboard-refresh",
            "script": "wiki_obsidian.dashboard_refresh",
            "returncode": 0,
            "passed": True,
            "output": "dashboard_refresh completed",
        }
    )

    results.append(_run_graph_refresh(project_root=settings.paths.project_root))
    rebuild_indexes(project_root=settings.paths.project_root, include_operations=True)
    results.append(
        {
            "check": "indexes-refresh",
            "script": "build_index.py + build_operations_index.py",
            "returncode": 0,
            "passed": True,
            "output": "index and operations index rebuilt",
        }
    )
    results.extend(
        run_checks(
        check_names=[
            "frontmatter",
            "links",
            "provenance",
            "boundaries",
            "note-ids",
            "raw-immutability",
            "design-package",
        ],
        project_root=settings.paths.project_root,
        )
    )

    schema_payload = schema_validate(project_root=settings.paths.project_root, run_id=active_run_id)
    results.append(
        {
            "check": "schema-validate",
            "script": "wiki_obsidian.schema_service.schema_validate",
            "returncode": 0 if schema_payload["status"] == "passed" else 1,
            "passed": schema_payload["status"] == "passed",
            "output": json.dumps(
                {
                    "status": schema_payload["status"],
                    "error_count": len(schema_payload["errors"]),
                    "checked_file_count": len(schema_payload["checked_files"]),
                    "report_path": schema_payload["report_path"],
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
    )
    results.extend(
        run_checks(
            check_names=["generated-surfaces"],
            project_root=settings.paths.project_root,
        )
    )
    payload = {
        "run_id": active_run_id,
        "status": "passed" if all(result["passed"] for result in results) else "failed",
        "checks": results,
    }
    report_path = write_json(reports_root / "verify_report.json", payload)
    return payload | {"report_path": str(report_path)}


def _run_graph_refresh(*, project_root: Path) -> dict[str, Any]:
    script_path = project_root / "tools" / "build_obsidian_graph_layer.py"
    command = [sys.executable, str(script_path), "--project-root", str(project_root)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False, cwd=project_root)
    output = "\n".join(
        line.strip()
        for line in (completed.stdout + "\n" + completed.stderr).splitlines()
        if line.strip()
    )
    return {
        "check": "graph-refresh",
        "script": "build_obsidian_graph_layer.py",
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "output": output,
    }
