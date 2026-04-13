from __future__ import annotations

from pathlib import Path
import tomllib

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_codex_environment_and_agents_exist() -> None:
    env_payload = _load_toml(PROJECT_ROOT / ".codex" / "environments" / "environment.toml")
    assert env_payload["runtime"]["preferred_python"] == ".\\.venv\\Scripts\\python.exe"

    agent_files = sorted((PROJECT_ROOT / ".codex" / "agents").glob("*.toml"))
    assert any(path.name == "regulatory-curator.toml" for path in agent_files)
    for path in agent_files:
        payload = _load_toml(path)
        assert "classification impact" in payload["developer_instructions"]


def test_skill_and_obsidian_assets_exist() -> None:
    expected_skills = {
        "classification-governance",
        "source-authority-audit",
        "regulation-unit-splitting",
        "web-clip-intake",
        "obsidian-dashboard",
        "marp-publish",
    }
    actual_skills = {path.name for path in (PROJECT_ROOT / ".agents" / "skills").iterdir() if path.is_dir()}
    assert expected_skills <= actual_skills

    community_plugins = yaml.safe_load((PROJECT_ROOT / ".obsidian" / "community-plugins.json").read_text(encoding="utf-8"))
    assert "dataview" in community_plugins


def test_taxonomy_and_schema_assets_exist() -> None:
    for rel in (
        "taxonomy/phase_registry.yaml",
        "taxonomy/functional_domains.yaml",
        "taxonomy/in_crash_browse_buckets.yaml",
        "taxonomy/compat_active_safety_v1.yaml",
        "taxonomy/compat_passive_buckets_v1.yaml",
        "taxonomy/crosswalk_v1_to_v2.yaml",
        "schemas/regulation_unit.schema.json",
        "schemas/note_frontmatter.schema.json",
        "sources/authority_registry.yaml",
        "sources/document_inventory.csv",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel
