from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    project_root: Path
    raw_root: Path
    collections_root: Path
    artifacts_root: Path
    reports_root: Path
    manifests_root: Path
    scan_root: Path
    parsed_root: Path
    normalized_root: Path
    docs_root: Path
    architecture_root: Path
    adr_root: Path
    decisions_root: Path
    operations_root: Path
    operations_notes_root: Path
    operations_archive_root: Path
    operations_dashboards_root: Path
    operations_plans_root: Path
    operations_pilot_root: Path
    operations_risks_root: Path
    operations_index: Path
    operations_log: Path
    wiki_root: Path
    wiki_templates_root: Path
    regulation_documents_root: Path
    regulation_units_root: Path
    concepts_root: Path
    jurisdictions_root: Path
    analyses_root: Path
    crosswalks_root: Path
    taxonomy_root: Path
    schemas_root: Path
    sources_root: Path
    authority_registry: Path
    document_inventory: Path
    regulation_unit_schema: Path
    note_frontmatter_schema: Path
    taxonomy_config: Path
    query_config: Path
    lint_config: Path
    collection_configs_root: Path
    obsidian_root: Path
    mcp_config: Path
    tools_config: Path
    root_index: Path
    root_log: Path


@dataclass(frozen=True)
class ProjectSettings:
    paths: ProjectPaths


def load_project_settings(project_root: str | Path | None = None) -> ProjectSettings:
    root = Path(project_root or Path.cwd()).resolve()
    return ProjectSettings(
        paths=ProjectPaths(
            project_root=root,
            raw_root=root / "raw",
            collections_root=root / "raw" / "collections",
            artifacts_root=root / "artifacts",
            reports_root=root / "artifacts" / "reports",
            manifests_root=root / "artifacts" / "manifests",
            scan_root=root / "artifacts" / "scan",
            parsed_root=root / "artifacts" / "parsed",
            normalized_root=root / "artifacts" / "normalized",
            docs_root=root / "docs",
            architecture_root=root / "docs" / "architecture",
            adr_root=root / "docs" / "architecture" / "adr",
            decisions_root=root / "docs" / "decisions",
            operations_root=root / "docs" / "operations",
            operations_notes_root=root / "docs" / "operations" / "notes",
            operations_archive_root=root / "docs" / "operations" / "archive",
            operations_dashboards_root=root / "docs" / "operations" / "dashboards",
            operations_plans_root=root / "docs" / "operations" / "plans",
            operations_pilot_root=root / "docs" / "operations" / "pilot",
            operations_risks_root=root / "docs" / "operations" / "risks",
            operations_index=root / "docs" / "operations" / "INDEX.md",
            operations_log=root / "docs" / "operations" / "LOG.md",
            wiki_root=root / "wiki",
            wiki_templates_root=root / "wiki" / "_templates",
            regulation_documents_root=root / "wiki" / "regulation_documents",
            regulation_units_root=root / "wiki" / "regulation_units",
            concepts_root=root / "wiki" / "concepts",
            jurisdictions_root=root / "wiki" / "jurisdictions",
            analyses_root=root / "wiki" / "analyses",
            crosswalks_root=root / "wiki" / "crosswalks",
            taxonomy_root=root / "taxonomy",
            schemas_root=root / "schemas",
            sources_root=root / "sources",
            authority_registry=root / "sources" / "authority_registry.yaml",
            document_inventory=root / "sources" / "document_inventory.csv",
            regulation_unit_schema=root / "schemas" / "regulation_unit.schema.json",
            note_frontmatter_schema=root / "schemas" / "note_frontmatter.schema.json",
            taxonomy_config=root / "configs" / "wiki" / "taxonomy.yaml",
            query_config=root / "configs" / "wiki" / "query.yaml",
            lint_config=root / "configs" / "wiki" / "lint.yaml",
            collection_configs_root=root / "configs" / "collections",
            obsidian_root=root / ".obsidian",
            mcp_config=root / "configs" / "mcp" / "servers.yaml",
            tools_config=root / "configs" / "tools" / "tooling.yaml",
            root_index=root / "index.md",
            root_log=root / "log.md",
        )
    )
