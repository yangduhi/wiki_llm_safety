from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from wiki_obsidian.settings import load_project_settings


def load_collection_profile(
    collection_id: str,
    *,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    path = settings.paths.collection_configs_root / collection_id / "profile.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Collection profile not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping at {path}")
    return payload


def profile_path(
    collection_id: str,
    *,
    project_root: str | Path | None = None,
) -> Path:
    settings = load_project_settings(project_root)
    return settings.paths.collection_configs_root / collection_id / "profile.yaml"

