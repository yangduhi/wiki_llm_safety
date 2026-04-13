from __future__ import annotations

import subprocess
import sys


def test_cli_help_runs() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "wiki_obsidian.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "wiki-obsidian" in completed.stdout
    assert "classify-phase" in completed.stdout
    assert "build-crosswalk" in completed.stdout
    assert "dashboard-refresh" in completed.stdout
    assert "source-audit" in completed.stdout
