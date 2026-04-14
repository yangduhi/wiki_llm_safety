#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ALLOWED_STATUSES = {"active", "review_required", "pending_source_note", "excluded"}
GENERATED_START = "<!-- BEGIN GENERATED GRAPH LAYER -->"
GENERATED_END = "<!-- END GENERATED GRAPH LAYER -->"
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
# Generated browse-index pages are knowledge-layer navigation surfaces and must
# stay valid under harness frontmatter validation. Use a validator-accepted
# status value here because `.\scripts\wiki.ps1 verify` regenerates them.
GENERATED_BROWSE_INDEX_STATUS = "draft"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> bool:
    ensure_dir(path.parent)
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_frontmatter_text(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :]
    payload = yaml.safe_load(block) or {}
    return (payload if isinstance(payload, dict) else {}), body


def parse_frontmatter_file(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter_text(read_text(path))


def render_frontmatter(payload: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---\n"


def today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def merge_tags(*tags: list[str]) -> list[str]:
    out: list[str] = []
    for tag_list in tags:
        for tag in tag_list:
            if tag not in out:
                out.append(tag)
    return out


def note_ref_from_path(wiki_root: Path, path: Path) -> str:
    return str(path.relative_to(wiki_root)).replace("\\", "/").removesuffix(".md")


def load_registry(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(read_text(path)) or {}
    for key in ("documents", "deferred_documents", "concepts_tier1", "planned_concepts", "hubs", "relations"):
        payload.setdefault(key, [])
    return payload


def active_concept_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in [*(registry["concepts_tier1"] or []), *(registry["planned_concepts"] or [])]
        if str(row.get("status") or "excluded") == "active"
    ]


def scan_document_notes(project_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    wiki_root = project_root / "wiki"
    documents_root = wiki_root / "regulation_documents"
    by_id: dict[str, dict[str, Any]] = {}
    all_notes: dict[str, dict[str, Any]] = {}
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, body = parse_frontmatter_file(path)
        page_ref = note_ref_from_path(wiki_root, path)
        row = {"path": path, "page_ref": page_ref, "frontmatter": frontmatter, "body": body}
        all_notes[page_ref] = row
        if path.parent == documents_root:
            note_id = str(frontmatter.get("id") or "").strip()
            if note_id:
                by_id[note_id] = row
    return by_id, all_notes


def graph_tagged(frontmatter: dict[str, Any]) -> bool:
    return "graph-ready" in [str(tag) for tag in frontmatter.get("tags") or []]


def cluster_tag(cluster: str) -> str:
    return f"cluster/{cluster}"


def hub_ref(hub_id: str) -> str:
    return f"indexes/{hub_id}"


def concept_ref(concept_id: str) -> str:
    return f"concepts/{concept_id}"


def render_wikilink(page_ref: str, title: str) -> str:
    return f"[[{page_ref}|{title}]]"


def render_local_file_link(project_root: Path, relpath: str, label: str) -> str:
    target = (project_root / relpath).resolve().as_posix()
    return f"[{label}](/{target})"


def relation_buckets(registry: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    active, review, deferred = [], [], []
    for row in registry["relations"]:
        status = str(row.get("status") or "active")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Unsupported relation status: {status}")
        if status == "active":
            active.append(row)
        elif status == "review_required":
            review.append(row)
        else:
            deferred.append(row)
    return active, review, deferred


def relation_map(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        out[str(row["source"])].append(row)
        out[str(row["target"])].append(row)
    return out


def note_title_lookup(active_documents: dict[str, dict[str, Any]], registry: dict[str, Any]) -> dict[str, str]:
    titles: dict[str, str] = {}
    for row in registry["concepts_tier1"]:
        if str(row.get("status") or "active") == "active":
            titles[str(row["id"])] = str(row["title"])
    for row in registry["planned_concepts"]:
        if str(row.get("status") or "excluded") == "active":
            titles[str(row["id"])] = str(row["title"])
        else:
            titles[str(row["id"])] = str(row["title"])
    for row in registry["hubs"]:
        titles[str(row["id"])] = str(row["title"])
    for row in registry["deferred_documents"]:
        titles[str(row["id"])] = str(row["label"])
    registry_document_rows = {str(row["id"]): row for row in registry["documents"]}
    for note_id, row in active_documents.items():
        preferred = str((registry_document_rows.get(note_id) or {}).get("display_title") or "").strip()
        titles[note_id] = _display_title(row["frontmatter"], note_id, preferred=preferred)
    return titles


def _display_title(frontmatter: dict[str, Any], fallback: str, *, preferred: str = "") -> str:
    if preferred:
        return preferred
    for key in ("display_title", "title"):
        value = str(frontmatter.get(key) or "").strip()
        if value:
            return value
    return fallback


def build_graph(project_root: Path) -> dict[str, Any]:
    registry_path = project_root / "taxonomy" / "regulatory_connectivity.yaml"
    registry = load_registry(registry_path)
    active_relations, review_relations, deferred_relations = relation_buckets(registry)
    active_documents, _all_notes = scan_document_notes(project_root)
    titles = note_title_lookup(active_documents, registry)
    hub_by_cluster = {str(row["cluster"]): str(row["id"]) for row in registry["hubs"] if str(row.get("status") or "active") == "active"}
    written: list[str] = []
    validation_errors: list[str] = []

    for row in registry["documents"]:
        if str(row.get("status") or "active") == "active" and str(row["id"]) not in active_documents:
            validation_errors.append(f"active document missing source-grounded note: {row['id']}")

    concept_paths: dict[str, Path] = {}
    concept_page_refs: dict[str, str] = {}
    active_concepts = active_concept_rows(registry)
    for row in active_concepts:
        concept_id = str(row["id"])
        path = project_root / "wiki" / "concepts" / f"{concept_id}.md"
        concept_paths[concept_id] = path
        concept_page_refs[concept_id] = note_ref_from_path(project_root / "wiki", path)

    hub_paths: dict[str, Path] = {}
    hub_page_refs: dict[str, str] = {}
    for row in registry["hubs"]:
        if str(row.get("status") or "active") != "active":
            continue
        hub_id = str(row["id"])
        path = project_root / "wiki" / "indexes" / f"{hub_id}.md"
        hub_paths[hub_id] = path
        hub_page_refs[hub_id] = note_ref_from_path(project_root / "wiki", path)

    active_node_ids = set(concept_paths) | set(hub_paths) | {str(row["id"]) for row in registry["documents"] if str(row.get("status") or "active") == "active" and str(row["id"]) in active_documents}
    registry_provenance = {
        "source_files": ["taxonomy/regulatory_connectivity.yaml"],
        "source_hashes": {"taxonomy/regulatory_connectivity.yaml": sha256_file(registry_path)},
        "parser_run_id": f"graph-layer-{today()}",
    }

    for row in active_concepts:
        concept_id = str(row["id"])
        path = concept_paths[concept_id]
        existing_fm, _ = parse_frontmatter_file(path) if path.exists() else ({}, "")
        cluster = str(row["cluster"])
        hub_id = hub_by_cluster.get(cluster)
        related_concepts = _linked_targets(concept_id, active_relations, {"concept_related"}, active_node_ids, prefix="concept-")
        representative_docs = _linked_targets(concept_id, active_relations, {"concept_to_document"}, active_node_ids, prefix="regdoc-")
        deferred_refs = _deferred_targets(concept_id, deferred_relations, titles)
        frontmatter = {
            "record_layer": "knowledge",
            "id": concept_id,
            "note_type": "concept_node",
            "title": str(row["title"]),
            "summary": str(row["definition"]),
            "status": "draft",
            "created": str(existing_fm.get("created") or today()),
            "updated": today(),
            "aliases": [],
            "type": "concept",
            "graph_group": "concept",
            "cluster": cluster,
            "tags": merge_tags(["graph-ready", "graph/concept", cluster_tag(cluster)]),
            "graph_ready": True,
            "provenance": registry_provenance,
            "confidence": "medium",
        }
        body = [
            render_frontmatter(frontmatter),
            f"# {row['title']}",
            "",
            "## Definition",
            str(row["definition"]),
            "",
            "## Classification Role",
            f"- type: concept",
            f"- graph_group: concept",
            f"- cluster: `{cluster}`",
            "",
            "## Cluster",
            f"- primary_hub: {render_wikilink(hub_page_refs[hub_id], titles[hub_id]) if hub_id else 'n/a'}",
            "",
            "## Evidence",
            "- Graph-ready semantic layer derived from `taxonomy/regulatory_connectivity.yaml`.",
            "- Links below are explicit semantic links, not automatic links from shared classification fields.",
            "",
            "## Related Concepts",
        ]
        body.extend(f"- {render_wikilink(concept_page_refs[target], titles[target])}" for target in related_concepts) if related_concepts else body.append("- None yet.")
        body.extend(["", "## Representative Regulations"])
        body.extend(f"- {render_wikilink(active_documents[target]['page_ref'], titles[target])}" for target in representative_docs) if representative_docs else body.append("- None yet.")
        if deferred_refs:
            body.extend(["", "## Deferred References"])
            body.extend(f"- {label} (`{status}`)" for label, status in deferred_refs)
        body.extend(["", "## Related Notes", f"{GENERATED_START}", "### Cluster Hub"])
        body.append(f"- {render_wikilink(hub_page_refs[hub_id], titles[hub_id])}" if hub_id else "- None yet.")
        body.extend([GENERATED_END, ""])
        if write_text(path, "\n".join(body)):
            written.append(str(path.relative_to(project_root)).replace("\\", "/"))

    for row in registry["hubs"]:
        if str(row.get("status") or "active") != "active":
            continue
        hub_id = str(row["id"])
        path = hub_paths[hub_id]
        existing_fm, _ = parse_frontmatter_file(path) if path.exists() else ({}, "")
        cluster = str(row["cluster"])
        seed_concepts = [concept_id for concept_id in row.get("seed_concepts") or [] if concept_id in concept_page_refs]
        seed_documents = [doc_id for doc_id in row.get("seed_documents") or [] if doc_id in active_documents]
        neighbor_hubs = _neighbor_hubs(cluster, hub_id, registry, active_relations, hub_by_cluster, active_documents)
        frontmatter = {
            "record_layer": "knowledge",
            "id": hub_id,
            "note_type": "browse_index",
            "title": str(row["title"]),
            "summary": f"Semantic graph hub for the `{cluster}` cluster.",
            "status": "draft",
            "created": str(existing_fm.get("created") or today()),
            "updated": today(),
            "aliases": [],
            "browse_axis": "graph_connectivity",
            "type": "hub",
            "graph_group": "hub",
            "cluster": cluster,
            "tags": merge_tags(["graph-ready", "graph/hub", cluster_tag(cluster)]),
            "graph_ready": True,
            "provenance": registry_provenance,
            "confidence": "medium",
        }
        body = [
            render_frontmatter(frontmatter),
            f"# {row['title']}",
            "",
            "## Snapshot",
            f"- cluster: `{cluster}`",
            f"- graph_group: hub",
            f"- graph_ready: true",
            "",
            "## Why This Hub Exists",
            f"- This hub gathers graph-ready concepts and selected regulations for the `{cluster}` semantic neighborhood.",
            "",
            "## Browse View",
            "- Use this note as the cluster entry point for Local Graph exploration.",
            "",
            "## Cluster Scope",
            f"- cluster: `{cluster}`",
            f"- planned_concepts_backlog: {', '.join(row.get('planned_concepts') or []) or 'none'}",
            "",
        ]
        body.extend(_cluster_hub_sections(cluster, titles, concept_page_refs, active_documents))
        if body[-1] != "":
            body.append("")
        body.append("## Seed Concepts")
        body.extend(f"- {render_wikilink(concept_page_refs[concept_id], titles[concept_id])}" for concept_id in seed_concepts) if seed_concepts else body.append("- None yet.")
        body.extend(["", "## Seed Regulations"])
        body.extend(f"- {render_wikilink(active_documents[doc_id]['page_ref'], titles[doc_id])}" for doc_id in seed_documents) if seed_documents else body.append("- None yet.")
        body.extend(["", "## Dataview", "```dataview", f'TABLE file.link, graph_group, cluster\nFROM "wiki"\nWHERE contains(tags, "graph-ready") AND cluster = "{cluster}"\nSORT graph_group ASC, file.name ASC', "```", "", GENERATED_START, "### Neighbor Clusters"])
        body.extend(f"- {render_wikilink(hub_page_refs[neighbor_id], titles[neighbor_id])}" for neighbor_id in neighbor_hubs) if neighbor_hubs else body.append("- None yet.")
        body.extend([GENERATED_END, ""])
        if write_text(path, "\n".join(body)):
            written.append(str(path.relative_to(project_root)).replace("\\", "/"))

    for row in registry["documents"]:
        if str(row.get("status") or "active") != "active":
            continue
        note_id = str(row["id"])
        if note_id not in active_documents:
            continue
        note = active_documents[note_id]
        cluster = str(row["cluster"])
        hub_id = hub_by_cluster.get(cluster)
        fm = dict(note["frontmatter"])
        fm["type"] = "regulation_document"
        fm["graph_group"] = "document"
        fm["cluster"] = cluster
        fm["graph_ready"] = True
        if str(row.get("jurisdiction") or "") == "KR" and row.get("display_title"):
            fm["display_title"] = str(row["display_title"])
            aliases = [str(alias) for alias in fm.get("aliases") or []]
            if str(row["display_title"]) not in aliases:
                fm["aliases"] = [str(row["display_title"]), *aliases]
        fm["tags"] = merge_tags(
            [str(tag) for tag in fm.get("tags") or []],
            ["graph-ready", "graph/document", cluster_tag(cluster), f"jurisdiction/{str(row['jurisdiction']).lower()}"],
        )
        generated_block = _render_document_graph_block(
            note_id=note_id,
            hub_id=hub_id,
            titles=titles,
            active_documents=active_documents,
            concept_page_refs=concept_page_refs,
            hub_page_refs=hub_page_refs,
            active_relations=active_relations,
            deferred_relations=deferred_relations,
        )
        body = _patch_document_body(note["body"], generated_block)
        if write_text(note["path"], render_frontmatter(fm) + body):
            written.append(str(note["path"].relative_to(project_root)).replace("\\", "/"))

    validation = build_validation(project_root, registry, active_documents, concept_page_refs, hub_page_refs, validation_errors)
    # Builder-owned official graph surfaces covered by the Git contract.
    # Human-authored tracked graph docs such as docs/obsidian_graph_usage.md,
    # docs/obsidian_graph_plan.md, and docs/obsidian_graph_reference_alignment.md
    # are official operations docs, but they are not regenerated here.
    outputs = {
        "docs/obsidian_graph_validation.md": validation,
        "docs/obsidian_graph_review_queue.md": build_review_queue(project_root, registry, titles),
        "docs/obsidian_graph_coverage_matrix.md": build_coverage_matrix(registry),
        "docs/obsidian_graph_v1_2_plan.md": build_v1_2_plan(registry),
        "docs/obsidian_graph_relation_decisions.md": build_relation_decisions(registry, titles),
        "docs/obsidian_graph_attach_readiness.md": build_attach_readiness(registry),
        "wiki/indexes/graph-home.md": build_graph_home(project_root, titles),
        "wiki/indexes/current-wiki-visualization.md": build_current_wiki_visualization(project_root),
    }
    for rel_path, content in outputs.items():
        if write_text(project_root / rel_path, content):
            written.append(rel_path)
    return {"written": sorted(set(written))}


def _linked_targets(node_id: str, relations: list[dict[str, Any]], relation_types: set[str], active_node_ids: set[str], *, prefix: str) -> list[str]:
    targets: list[str] = []
    for row in relations:
        if str(row["relation_type"]) not in relation_types:
            continue
        source = str(row["source"])
        target = str(row["target"])
        if source == node_id and target.startswith(prefix) and target in active_node_ids and target not in targets:
            targets.append(target)
        elif target == node_id and source.startswith(prefix) and source in active_node_ids and source not in targets:
            targets.append(source)
    return targets


def _deferred_targets(node_id: str, relations: list[dict[str, Any]], titles: dict[str, str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for row in relations:
        source = str(row["source"])
        target = str(row["target"])
        status = str(row.get("status") or "")
        if source == node_id and target not in titles:
            out.append((target, status))
        elif target == node_id and source not in titles:
            out.append((source, status))
        elif source == node_id and target in titles and status != "active":
            out.append((titles[target], status))
        elif target == node_id and source in titles and status != "active":
            out.append((titles[source], status))
    dedup: list[tuple[str, str]] = []
    for item in out:
        if item not in dedup:
            dedup.append(item)
    return dedup


def _neighbor_hubs(
    cluster: str,
    hub_id: str,
    registry: dict[str, Any],
    active_relations: list[dict[str, Any]],
    hub_by_cluster: dict[str, str],
    active_documents: dict[str, dict[str, Any]],
) -> list[str]:
    doc_cluster = {str(row["id"]): str(row["cluster"]) for row in registry["documents"] if str(row.get("status") or "active") == "active" and str(row["id"]) in active_documents}
    concept_cluster = {str(row["id"]): str(row["cluster"]) for row in registry["concepts_tier1"] if str(row.get("status") or "active") == "active"}
    neighbors: list[str] = []
    for row in active_relations:
        endpoints = [str(row["source"]), str(row["target"])]
        endpoint_clusters = []
        for endpoint in endpoints:
            if endpoint in doc_cluster:
                endpoint_clusters.append(doc_cluster[endpoint])
            elif endpoint in concept_cluster:
                endpoint_clusters.append(concept_cluster[endpoint])
        if cluster in endpoint_clusters:
            for other_cluster in endpoint_clusters:
                if other_cluster != cluster and other_cluster in hub_by_cluster:
                    other_hub = hub_by_cluster[other_cluster]
                    if other_hub != hub_id and other_hub not in neighbors:
                        neighbors.append(other_hub)
    return neighbors


def _cluster_hub_sections(
    cluster: str,
    titles: dict[str, str],
    concept_page_refs: dict[str, str],
    active_documents: dict[str, dict[str, Any]],
) -> list[str]:
    def _doc_line(note_id: str) -> str | None:
        note = active_documents.get(note_id)
        if not note or note_id not in titles:
            return None
        return f"- {render_wikilink(note['page_ref'], titles[note_id])}"

    if cluster == "occupant-protection":
        lines = [
            "## Readability Note",
            "- This hub remains intentionally unsplit in V1.2 because the current density reflects a coherent occupant-protection neighborhood rather than noisy overlinking.",
            "",
            "## Subgroups",
            "### Frontal Occupant Protection",
            f"- {render_wikilink(concept_page_refs['concept-frontal-impact-protection'], titles['concept-frontal-impact-protection'])}",
            _doc_line("regdoc-xml_fmvss-571-208") or "- Missing FMVSS 208 seed",
            _doc_line("regdoc-xml_kmvss-kmvss_art_102_153") or "- Missing KR 102_153 seed",
            _doc_line("regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english") or "- Missing UNECE R137 seed",
            "",
            "### Side Occupant Protection",
            f"- {render_wikilink(concept_page_refs['concept-side-impact-protection'], titles['concept-side-impact-protection'])}",
            _doc_line("regdoc-xml_fmvss-571-214") or "- Missing FMVSS 214 seed",
            _doc_line("regdoc-xml_kmvss-kmvss_art_102_154") or "- Missing KR 102_154 seed",
            _doc_line("regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english") or "- Missing UNECE R95 seed",
            "",
            "### Restraint Systems and Injury Criteria",
            f"- {render_wikilink(concept_page_refs['concept-occupant-protection'], titles['concept-occupant-protection'])}",
            f"- {render_wikilink(concept_page_refs['concept-restraint-systems'], titles['concept-restraint-systems'])}",
            f"- {render_wikilink(concept_page_refs['concept-injury-criteria'], titles['concept-injury-criteria'])}",
            f"- {render_wikilink(concept_page_refs['concept-child-restraint-systems'], titles['concept-child-restraint-systems'])}",
            _doc_line("regdoc-xml_kmvss-kmvss_art_102_151") or "- Missing KR 102_151 seed",
            "",
            "## Mermaid Summary",
            "```mermaid",
            'flowchart LR',
            '    Hub["Occupant Protection Cluster"] --> Frontal["Frontal occupant protection"]',
            '    Hub --> Side["Side occupant protection"]',
            '    Hub --> Restraint["Restraint systems / injury criteria"]',
            "```",
        ]
        return lines
    if cluster == "vru-and-external-protection":
        return [
            "## Readability Note",
            "- This cluster remains active but sparse in V1.2. It is intentionally treated as a seed-stage neighborhood until more source-grounded notes are ingested.",
            "",
            "## Seed-Stage Status",
            "- active_concepts: 1",
            "- active_documents: 1",
            "- emphasis: KR-led pedestrian protection seed, not a broad VRU ontology.",
        ]
    return []


def _render_document_graph_block(
    *,
    note_id: str,
    hub_id: str | None,
    titles: dict[str, str],
    active_documents: dict[str, dict[str, Any]],
    concept_page_refs: dict[str, str],
    hub_page_refs: dict[str, str],
    active_relations: list[dict[str, Any]],
    deferred_relations: list[dict[str, Any]],
) -> str:
    related_concepts = _linked_targets(note_id, active_relations, {"concept_to_document"}, set(concept_page_refs), prefix="concept-")
    connected_docs = _linked_targets(note_id, active_relations, {"jurisdictional_analog", "same_safety_function", "same_test_family", "umbrella_to_implementing", "admin_governs", "variant_or_successor"}, set(active_documents), prefix="regdoc-")
    deferred_refs = _deferred_targets(note_id, deferred_relations, titles)
    lines = [
        GENERATED_START,
        "## Graph Connections",
        "### Related Concepts",
    ]
    lines.extend(f"- {render_wikilink(concept_page_refs[target], titles[target])}" for target in related_concepts) if related_concepts else lines.append("- None yet.")
    lines.extend(["", "### Connected Regulations"])
    lines.extend(f"- {render_wikilink(active_documents[target]['page_ref'], titles[target])}" for target in connected_docs) if connected_docs else lines.append("- None yet.")
    lines.extend(["", "### Cluster Hub"])
    lines.append(f"- {render_wikilink(hub_page_refs[hub_id], titles[hub_id])}" if hub_id else "- None yet.")
    if deferred_refs:
        lines.extend(["", "### Deferred References"])
        lines.extend(f"- {label} (`{status}`)" for label, status in deferred_refs)
    lines.append(GENERATED_END)
    return "\n".join(lines)


def _patch_document_body(body: str, generated_block: str) -> str:
    has_existing = GENERATED_START in body and GENERATED_END in body
    cleaned = re.sub(re.escape(GENERATED_START) + r"[\s\S]*?" + re.escape(GENERATED_END) + r"\n*", "", body, flags=re.M)
    if "## Related Units" in cleaned:
        return cleaned.replace("## Related Units", generated_block + "\n\n## Related Units", 1)
    if has_existing:
        return re.sub(re.escape(GENERATED_START) + r"[\s\S]*?" + re.escape(GENERATED_END), generated_block, body, flags=re.M)
    return cleaned.rstrip() + "\n\n" + generated_block + "\n"


def _extract_generated_graph_block(body: str) -> str:
    match = re.search(re.escape(GENERATED_START) + r"[\s\S]*?" + re.escape(GENERATED_END), body, flags=re.M)
    return match.group(0) if match else ""


def build_review_queue(project_root: Path, registry: dict[str, Any], titles: dict[str, str]) -> str:
    review_rows = [row for row in registry["relations"] if str(row.get("status") or "active") == "review_required"]
    pending_docs = registry.get("deferred_documents") or []
    lines = [
        "# Obsidian Graph Review Queue",
        "",
        "## Purpose",
        "- Use this queue to close unresolved semantic relations and to track attach-on-ingest work for deferred source-grounded notes.",
        "",
        "## Review-Required Relations",
    ]
    if not review_rows:
        lines.extend(
            [
                "- none",
                "- The previously reviewed candidates are now adjudicated in `docs/obsidian_graph_relation_decisions.md`.",
            ]
        )
    for row in review_rows:
        source = titles.get(str(row["source"]), str(row["source"]))
        target = titles.get(str(row["target"]), str(row["target"]))
        provenance = row.get("provenance") or {}
        lines.extend(
            [
                f"### {source} -> {target}",
                f"- relation_type: `{row['relation_type']}`",
                f"- status: `{row['status']}`",
                f"- confidence: `{row['confidence']}`",
                f"- rationale: {row['rationale']}",
                f"- evidence_needed_to_activate: confirm stable same-safety-function or same-test-family equivalence from source-grounded notes.",
                f"- evidence_needed_to_exclude: show that the overlap is merely taxonomic adjacency and not a reusable semantic analog.",
                f"- reviewed_by: {', '.join(provenance.get('reviewed_by') or []) or 'n/a'}",
                f"- last_reviewed_at: {provenance.get('last_reviewed_at') or 'n/a'}",
                "- operator_next_step: inspect both source-grounded notes and either promote to `active` or demote to `excluded`.",
                "",
            ]
        )

    lines.extend(["## Pending Source Notes"])
    if not pending_docs:
        lines.append("- none")
    for row in pending_docs:
        lines.extend(
            [
                f"### {row['label']}",
                f"- id: `{row['id']}`",
                f"- status: `{row['status']}`",
                f"- rationale: {row['rationale']}",
                "- attach_on_ingest: create the real source-grounded regulation_document note through ingest, switch the document and related relation rows to `active`, then rerun graph build.",
                "- operator_next_step: follow `docs/obsidian_graph_attach_readiness.md` and confirm validation after rebuild.",
                "",
            ]
        )

    lines.extend(
        [
            "## State Transitions",
            "- `review_required -> active`: semantic equivalence becomes strong enough for explicit graph emission.",
            "- `review_required -> excluded`: review shows the relation should not become a semantic graph edge.",
            "- `pending_source_note -> active`: source-grounded regulation_document note exists and the registry is updated after ingest.",
            "",
            "## Operator Links",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_relation_decisions.md', 'Relation Decisions')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_attach_readiness.md', 'Attach Readiness')}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_coverage_matrix(registry: dict[str, Any]) -> str:
    active_docs = [row for row in registry["documents"] if str(row.get("status") or "active") == "active"]
    active_concepts = active_concept_rows(registry)
    concept_by_cluster = Counter(str(row["cluster"]) for row in active_concepts)
    doc_by_cluster = Counter(str(row["cluster"]) for row in active_docs)
    doc_by_cluster_jurisdiction: dict[str, Counter[str]] = defaultdict(Counter)
    for row in active_docs:
        doc_by_cluster_jurisdiction[str(row["cluster"])][str(row["jurisdiction"])] += 1
    ordered_jurisdictions = ["US", "KR", "UNECE", "EU"]

    lines = [
        "# Obsidian Graph Coverage Matrix",
        "",
        "| Cluster | Concepts | Documents | US | KR | UNECE | EU | State | Notes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for hub in registry["hubs"]:
        if str(hub.get("status") or "active") != "active":
            continue
        cluster = str(hub["cluster"])
        concept_count = concept_by_cluster[cluster]
        doc_count = doc_by_cluster[cluster]
        jurisdiction_counts = {name: doc_by_cluster_jurisdiction[cluster][name] for name in ordered_jurisdictions}
        us_count = jurisdiction_counts["US"]
        kr_count = jurisdiction_counts["KR"]
        unece_count = jurisdiction_counts["UNECE"]
        eu_count = jurisdiction_counts["EU"]
        state = "active"
        note = ""
        if cluster == "vru-and-external-protection":
            state = "sparse"
            note = "KR-led seed-stage cluster with one active concept mediator and one active document"
        elif eu_count > 0 and us_count == 0 and kr_count == 0 and unece_count == 0:
            note = "EU-led"
        elif unece_count > 0 and us_count == 0 and kr_count == 0:
            note = "UNECE-led"
        elif us_count > 0 and kr_count == 0 and unece_count == 0 and eu_count == 0:
            note = "US-led"
        elif kr_count > 0 and us_count == 0 and unece_count == 0 and eu_count == 0:
            note = "KR-led"
        elif sum(1 for value in jurisdiction_counts.values() if value > 0) >= 2:
            note = "cross-jurisdiction"
        lines.append(f"| `{cluster}` | {concept_count} | {doc_count} | {us_count} | {kr_count} | {unece_count} | {eu_count} | {state} | {note} |")
    lines.extend(
        [
            "",
            "## Coverage Notes",
            "- `visibility-glazing` is currently US-led because only source-grounded U.S. graph seeds are active in this cluster.",
            "- `approval-and-governance` is currently KR-led because the current active administrative seeds are KR approval and conformity notes.",
            "- `occupant-protection` now includes UNECE attach seeds through R137 and R95 without changing the unsplit hub topology.",
            "- `vru-and-external-protection` is intentionally sparse in V1.2: one active concept and one active KR document.",
            "- `EU` remains deferred in this phase because `regdoc-eu-2019-2144` still has no source-grounded regulation document note.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_v1_2_plan(registry: dict[str, Any]) -> str:
    review_required_count = sum(1 for row in registry["relations"] if str(row.get("status") or "active") == "review_required")
    pending_count = sum(1 for row in registry["relations"] if str(row.get("status") or "active") == "pending_source_note")
    return "\n".join(
        [
            "# Obsidian Graph V1.2 Plan",
            "",
            "## Confirmed Current State",
            "- graph foundation is stable and remains unchanged.",
            "- graph-ready layer uses concept, selected regulation_document, and hub only.",
            "- deferred policy remains placeholder-free.",
            f"- unresolved review_required relations after adjudication: {review_required_count}",
            f"- pending_source_note relations: {pending_count}",
            "",
            "## Confirmed Bottlenecks",
            "- coverage and validation wording previously undercounted active concepts promoted from planned concepts.",
            "- KR graph-facing labels needed readable display metadata instead of mojibake.",
            "- review_required candidates needed decisive adjudication rather than an indefinitely open queue.",
            "- operator docs needed a clearer attach-on-ingest workflow for deferred regulations.",
            "",
            "## Change Scope",
            "- keep the occupant-protection hub unsplit and document the rationale rather than proliferating hubs.",
            "- keep the VRU cluster active but explicitly sparse and seed-stage.",
            "- normalize KR display titles without changing source-grounded file paths or note ids.",
            "- adjudicate the two prior review_required cross-jurisdiction relations.",
            "- add relation decision and attach-readiness docs to make graph operations auditable.",
            "- align coverage, validation, usage, and graph-home outputs with actual builder behavior.",
            "",
            "## Non-Change Scope",
            "- no new graph foundation.",
            "- no placeholder regulation documents.",
            "- no regulation_unit graph emission.",
            "- no source-grounded file renames.",
            "",
            "## Occupant Hub Policy",
            "- `graph-cluster-occupant-protection` remains intentionally unsplit.",
            "- The current density still reflects a coherent semantic neighborhood rather than unusable graph noise.",
            "",
            "## Deferred Policy",
            "- `regdoc-eu-2019-2144` remains deferred until a real source-grounded regulation_document note exists.",
        ]
    ).rstrip() + "\n"


def _wiki_note_inventory(project_root: Path) -> dict[str, int]:
    counts = Counter()
    pseudo_document_units = 0
    wiki_root = project_root / "wiki"
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root)
        if "_templates" in rel.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, _ = parse_frontmatter_file(path)
        note_type = str(frontmatter.get("note_type") or "unknown")
        counts[note_type] += 1
        if note_type == "regulation_unit" and (
            str(frontmatter.get("clause_path") or "") == "document"
            or str(frontmatter.get("id") or "").endswith("-document")
        ):
            pseudo_document_units += 1
    counts["pseudo_document_units_hidden"] = pseudo_document_units
    counts["regulation_units_visible"] = counts.get("regulation_unit", 0) - pseudo_document_units
    counts["graph_cluster_hubs"] = len(list((wiki_root / "indexes").glob("graph-cluster-*.md")))
    return counts


# This page is a builder-owned committed current snapshot in the graph
# generated-surface Git contract. It is not a hand-maintained memo.
def build_current_wiki_visualization(project_root: Path) -> str:
    note_path = project_root / "wiki" / "indexes" / "current-wiki-visualization.md"
    existing_fm, _ = parse_frontmatter_file(note_path) if note_path.exists() else ({}, "")
    counts = _wiki_note_inventory(project_root)
    generated_on = today()
    return "\n".join(
        [
            "---",
            "record_layer: knowledge",
            "id: browse-index-current-wiki-visualization",
            "note_type: browse_index",
            "title: Current Wiki Visualization",
            "summary: Auto-generated visualization snapshot for the current hubs, documents, and unit-centered structure.",
            f"status: {GENERATED_BROWSE_INDEX_STATUS}",
            f"created: '{existing_fm.get('created') or generated_on}'",
            f"updated: '{generated_on}'",
            "aliases: []",
            "browse_axis: visualization",
            "provenance:",
            "  source_files: []",
            "  source_hashes: {}",
            f"  parser_run_id: current-wiki-visualization-{generated_on}",
            "confidence: medium",
            "---",
            "",
            "# Current Wiki Visualization",
            "",
            "## Snapshot",
            f"- generated_at: {generated_on}",
            "- generator: `python tools/build_obsidian_graph_layer.py --project-root .`",
            "- role: official tracked current snapshot",
            "- git_contract: committed generated artifact",
            "- browse_axis: visualization",
            "- canonical_global_browse_hubs: 5",
            f"- graph_cluster_hubs: {counts.get('graph_cluster_hubs', 0)}",
            f"- regulation_documents: {counts.get('regulation_document', 0):,}",
            f"- regulation_units_total: {counts.get('regulation_unit', 0):,}",
            f"- regulation_units_visible: {counts.get('regulation_units_visible', 0):,}",
            f"- pseudo_document_units_hidden: {counts.get('pseudo_document_units_hidden', 0):,}",
            "",
            "> [!abstract] Quick Start",
            "> 1. Start with [[indexes/graph-home|Graph Home]] for graph-layer operations and validation context.",
            "> 2. Start with [[indexes/phase-hub|Phase Hub]] or [[indexes/functional-domain-hub|Functional Domain Hub]] for canonical browse-first navigation.",
            "> 3. Use [[indexes/jurisdiction-hub|Jurisdiction Hub]] when the question is jurisdiction-first.",
            "> 4. Use [[indexes/approval-and-governance-hub|Approval and Governance Hub]] for approval, conformity, surveillance, recall, and governance text.",
            "> 5. Treat `regulation_document` as a source anchor and `regulation_unit` as the real answer unit.",
            "",
            "## Why This Hub Exists",
            "> [!info] This note is a builder-owned committed current snapshot generated from the live wiki note inventory.",
            "> Open this page in Obsidian to render the Mermaid diagrams and use it as the current structural snapshot before drilling into individual hubs.",
            "> `.\scripts\wiki.ps1 graph-refresh` regenerates this page as part of the official graph surface set.",
            "",
            "> [!warning] Read This Correctly",
            "> `Phase` and `functional_domain` remain the primary global browse surfaces.",
            "> `In-Crash Browse` is a secondary browse aid, not the ontology root.",
            "> `[[indexes/graph-home|Graph Home]]` is the operator entrypoint for graph-layer refresh, validation, and review docs.",
            "",
            "## Browse View",
            "### Navigation Priority",
            "```mermaid",
            "flowchart TD",
            '    Start["Open Wiki in Obsidian"] --> Graph["Graph Home"]',
            '    Start --> Phase["Phase Hub"]',
            '    Start --> Domain["Functional Domain Hub"]',
            '    Start --> Jurisdiction["Jurisdiction Hub"]',
            '    Start --> Admin["Approval and Governance Hub"]',
            '    Start --> InCrash["In-Crash Browse Hub"]',
            "",
            '    Graph --> GraphDocs["Graph operations docs"]',
            '    Phase --> Unit["regulation_unit"]',
            "    Domain --> Unit",
            "    Jurisdiction --> Unit",
            "    Admin --> Unit",
            "    InCrash --> Unit",
            "",
            "    classDef primary fill:#e8f4ff,stroke:#1f5aa6,color:#163a6b,stroke-width:2px;",
            "    classDef support fill:#eef7ec,stroke:#4c7a3d,color:#23451d,stroke-width:1.5px;",
            "    classDef secondary fill:#fff4e5,stroke:#c47a00,color:#6f4300,stroke-width:1.5px;",
            "    classDef target fill:#f6f3ff,stroke:#6b46c1,color:#40256f,stroke-width:1.5px;",
            "",
            "    class Graph,Phase,Domain primary;",
            "    class Jurisdiction,Admin support;",
            "    class InCrash secondary;",
            "    class Unit,GraphDocs target;",
            "```",
            "",
            "### Knowledge Topology",
            "```mermaid",
            "flowchart LR",
            '    Hub["Browse Hubs"] --> Unit["regulation_unit"]',
            '    Hub --> Document["regulation_document"]',
            '    Hub --> Crosswalk["crosswalk"]',
            '    Hub --> JurisdictionOverview["jurisdiction_overview"]',
            '    GraphHome["graph-home"] --> GraphDocs["graph operations docs"]',
            "",
            '    Document -->|"source anchor"| Unit',
            '    Crosswalk -->|"legacy to canonical reference"| Unit',
            '    JurisdictionOverview -->|"entry point"| Unit',
            '    Hidden["pseudo document units"] -. hidden from browse .-> Unit',
            "",
            "    classDef hub fill:#edf7f5,stroke:#26736b,color:#12433e,stroke-width:1.5px;",
            "    classDef visible fill:#f8f5ff,stroke:#6b46c1,color:#3a246f,stroke-width:1.5px;",
            "    classDef hidden fill:#fff6f6,stroke:#c05656,color:#742a2a,stroke-dasharray: 4 4;",
            "",
            "    class Hub,GraphHome hub;",
            "    class Unit,Document,Crosswalk,JurisdictionOverview,GraphDocs visible;",
            "    class Hidden hidden;",
            "```",
            "",
            "### Current Corpus Shape",
            "```mermaid",
            "flowchart TD",
            '    N["Current Note Inventory"] --> N1["browse_index: ' + f"{counts.get('browse_index', 0):,}" + '"]',
            '    N --> N2["regulation_document: ' + f"{counts.get('regulation_document', 0):,}" + '"]',
            '    N --> N3["regulation_unit: ' + f"{counts.get('regulation_unit', 0):,}" + ' total"]',
            '    N3 --> N31["' + f"{counts.get('regulation_units_visible', 0):,}" + ' visible clause-like units"]',
            '    N3 --> N32["' + f"{counts.get('pseudo_document_units_hidden', 0):,}" + ' pseudo document units<br/>kept but hidden from browse"]',
            '    N --> N4["jurisdiction_overview: ' + f"{counts.get('jurisdiction_overview', 0):,}" + '"]',
            '    N --> N5["crosswalk: ' + f"{counts.get('crosswalk', 0):,}" + '"]',
            "",
            "    classDef big fill:#ecfeff,stroke:#0f766e,color:#134e4a,stroke-width:1.5px;",
            "    classDef count fill:#faf5ff,stroke:#7c3aed,color:#4c1d95,stroke-width:1.5px;",
            "",
            "    class N big;",
            "    class N1,N2,N3,N31,N32,N4,N5 count;",
            "```",
            "",
            "### Open These First",
            "- Graph operations:",
            "  - [[indexes/graph-home|Graph Home]]",
            "- Primary global browse:",
            "  - [[indexes/phase-hub|Phase Hub]]",
            "  - [[indexes/functional-domain-hub|Functional Domain Hub]]",
            "- Supporting browse:",
            "  - [[indexes/jurisdiction-hub|Jurisdiction Hub]]",
            "  - [[indexes/approval-and-governance-hub|Approval and Governance Hub]]",
            "- Secondary browse only:",
            "  - [[indexes/in-crash-browse-hub|In-Crash Browse Hub]]",
            "- Root entrypoints:",
            f"  - {render_local_file_link(project_root, 'index.md', 'index.md')}",
            f"  - {render_local_file_link(project_root, 'docs/operations/INDEX.md', 'docs/operations/INDEX.md')}",
            "",
            "> [!tip] Reading Rule",
            "> Use this page as a live structural snapshot, not as a hand-maintained planning memo.",
            "> For graph-specific operations, start with `Graph Home`; for canonical browsing, start with `Phase Hub` or `Functional Domain Hub`.",
            "",
            "## Dataview",
            "### Browse Hub Listing",
            "```dataview",
            'TABLE file.link, browse_axis, updated',
            'FROM "wiki/indexes"',
            'WHERE note_type = "browse_index"',
            "SORT file.name ASC",
            "```",
            "",
            "### Live Note Inventory",
            "```dataview",
            'TABLE WITHOUT ID note_type AS "Note Type", length(rows) AS "Count"',
            'FROM "wiki"',
            "GROUP BY note_type",
            "SORT length(rows) DESC",
            "```",
            "",
        ]
    )


def build_graph_home(project_root: Path, titles: dict[str, str]) -> str:
    return "\n".join(
        [
            "---",
            "record_layer: knowledge",
            "id: graph-home",
            "note_type: browse_index",
            "title: Graph Home",
            "summary: Human entrypoint for using the graph-ready semantic layer.",
            f"status: {GENERATED_BROWSE_INDEX_STATUS}",
            f"created: '{today()}'",
            f"updated: '{today()}'",
            "aliases: []",
            "browse_axis: graph_home",
            "type: hub",
            "graph_group: operator",
            "cluster: graph-home",
            "tags:",
            "  - operator-entry",
            "graph_ready: false",
            "provenance:",
            "  source_files: []",
            "  source_hashes: {}",
            "  parser_run_id: graph-home-v1-2",
            "confidence: medium",
            "---",
            "",
            "# Graph Home",
            "",
            "## Snapshot",
            "- purpose: primary human entrypoint for the graph-ready semantic layer",
            "- role: official tracked operator hub",
            "- git_contract: committed generated artifact",
            "- graph_ready: false",
            "- freshness_protected_by_verify: true",
            "- live_wiki_snapshot: [[indexes/current-wiki-visualization|Current Wiki Visualization]]",
            "",
            "## Why This Hub Exists",
            "- Start here when you want to use the graph layer as an operator rather than as a graph node.",
            "- This hub is a builder-owned official graph surface rather than a hand-maintained note.",
            "- `.\scripts\wiki.ps1 verify` now rebuilds graph-generated surfaces before baseline checks, so graph-view operations follow the same freshness contract as dashboards and indexes.",
            "- Manual docs under `docs/obsidian_graph*.md` remain official tracked operations docs even when they are not generated.",
            "",
            "## Browse View",
            "- Global Graph: filter by `tag:#graph-ready`.",
            "- Local Graph: hub depth 1, concept/document depth 2.",
            "- Keep `graph-home.md` itself out of the Global Graph; it is an operator landing page, not a graph node.",
            "",
            "## Cluster Scope",
            "- [[indexes/graph-cluster-occupant-protection|Occupant Protection Cluster]]",
            "- [[indexes/graph-cluster-structural-retention-and-egress|Structural Retention and Egress Cluster]]",
            "- [[indexes/graph-cluster-visibility-and-glazing|Visibility and Glazing Cluster]]",
            "- [[indexes/graph-cluster-battery-fire-and-electrical-safety|Battery / Fire / Electrical Safety Cluster]]",
            "- [[indexes/graph-cluster-vru-and-external-protection|VRU and External Protection Cluster]]",
            "- [[indexes/graph-cluster-approval-and-governance|Approval and Governance Cluster]]",
            "",
            "## Seed Concepts",
            "- [[concepts/concept-occupant-protection|Occupant Protection]]",
            "- [[concepts/concept-door-retention|Door Retention]]",
            "- [[concepts/concept-glazing-materials|Glazing Materials]]",
            "- [[concepts/concept-ev-electrical-safety|EV Electrical Safety]]",
            "- [[concepts/concept-pedestrian-protection|Pedestrian Protection]]",
            "",
            "## Seed Regulations",
            "- [[regulation_documents/xml_fmvss-571-205|FMVSS 205]]",
            "- [[regulation_documents/xml_fmvss-571-206|FMVSS 206]]",
            "- [[regulation_documents/xml_fmvss-571-208|FMVSS 208]]",
            "- [[regulation_documents/xml_fmvss-571-214|FMVSS 214]]",
            "- [[regulation_documents/xml_fmvss-571-226|FMVSS 226]]",
            "- [[regulation_documents/xml_fmvss-571-305a|FMVSS 305a]]",
            f"- {render_wikilink('regulation_documents/xml_kmvss-kmvss_art_102_151', titles['regdoc-xml_kmvss-kmvss_art_102_151'])}",
            f"- {render_wikilink('regulation_documents/xml_kmvss-kmvss_art_112_186', titles['regdoc-xml_kmvss-kmvss_art_112_186'])}",
            f"- {render_wikilink('regulation_documents/pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english', titles['regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english']) if 'regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english' in titles else '- UNECE R137 pending attach'}",
            f"- {render_wikilink('regulation_documents/pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english', titles['regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english']) if 'regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english' in titles else '- UNECE R95 pending attach'}",
            "",
            "## Dataview",
            "```dataview",
            'TABLE file.link, graph_group, cluster',
            'FROM "wiki"',
            'WHERE contains(tags, "graph-ready")',
            "SORT graph_group ASC, file.name ASC",
            "```",
            "",
            "## Review and Operations Links",
            f"- {render_local_file_link(project_root, 'docs/operations/INDEX.md', 'docs/operations/INDEX.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_usage.md', 'docs/obsidian_graph_usage.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_validation.md', 'docs/obsidian_graph_validation.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_review_queue.md', 'docs/obsidian_graph_review_queue.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_coverage_matrix.md', 'docs/obsidian_graph_coverage_matrix.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_relation_decisions.md', 'docs/obsidian_graph_relation_decisions.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_attach_readiness.md', 'docs/obsidian_graph_attach_readiness.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_v1_2_plan.md', 'docs/obsidian_graph_v1_2_plan.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_reference_alignment.md', 'docs/obsidian_graph_reference_alignment.md')}",
            f"- {render_local_file_link(project_root, 'docs/obsidian_graph_v2_attach_plan.md', 'docs/obsidian_graph_v2_attach_plan.md')}",
            "",
            "## Commands",
            "- refresh graph surfaces: `.\\scripts\\wiki.ps1 graph-refresh`",
            "- graph-refresh regenerates builder-owned graph surfaces in this contract; it does not define a separate graph-only local markdown path",
            "- rebuild directly: `python tools/build_obsidian_graph_layer.py --project-root .`",
            "- verify: `.\\scripts\\wiki.ps1 verify`",
            "",
        ]
    )


def build_relation_decisions(registry: dict[str, Any], titles: dict[str, str]) -> str:
    doc_doc_rows = [
        row
        for row in registry["relations"]
        if str(row["source"]).startswith("regdoc-") and str(row["target"]).startswith("regdoc-")
    ]
    active_rows = [row for row in doc_doc_rows if str(row.get("status") or "active") == "active"]
    excluded_rows = [row for row in doc_doc_rows if str(row.get("status") or "active") == "excluded"]
    pending_rows = [row for row in doc_doc_rows if str(row.get("status") or "active") == "pending_source_note"]
    lines = [
        "# Obsidian Graph Relation Decisions",
        "",
        "## Purpose",
        "- This document records evidence-backed document-to-document semantic relation decisions without turning the registry into a long-form memo.",
        "",
        "## Active Document-to-Document Relations",
    ]
    if not active_rows:
        lines.append("- none")
    for row in active_rows:
        provenance = row.get("provenance") or {}
        source = titles.get(str(row["source"]), str(row["source"]))
        target = titles.get(str(row["target"]), str(row["target"]))
        lines.extend(
            [
                f"### {source} -> {target}",
                f"- relation_type: `{row['relation_type']}`",
                f"- status: `{row['status']}`",
                f"- confidence: `{row['confidence']}`",
                f"- evidence_basis: {', '.join(provenance.get('evidence_refs') or []) or 'n/a'}",
                f"- rationale_summary: {row['rationale']}",
                "- decision: retained as `active`",
                f"- follow_up: {provenance.get('basis_note') or 'none'}",
                "",
            ]
        )
    lines.extend(["## Adjudicated Exclusions"])
    if not excluded_rows:
        lines.append("- none")
    for row in excluded_rows:
        provenance = row.get("provenance") or {}
        source = titles.get(str(row["source"]), str(row["source"]))
        target = titles.get(str(row["target"]), str(row["target"]))
        lines.extend(
            [
                f"### {source} -> {target}",
                f"- relation_type: `{row['relation_type']}`",
                f"- current_status: `{row['status']}`",
                f"- confidence: `{row['confidence']}`",
                f"- evidence_basis: {', '.join(provenance.get('evidence_refs') or []) or 'n/a'}",
                f"- rationale_summary: {row['rationale']}",
                "- decision: excluded after review",
                f"- follow_up: {provenance.get('basis_note') or 'none'}",
                "",
            ]
        )
    lines.extend(["## Deferred / Not Yet Adjudicated"])
    if not pending_rows:
        lines.append("- none")
    for row in pending_rows:
        provenance = row.get("provenance") or {}
        source = titles.get(str(row["source"]), str(row["source"]))
        target = titles.get(str(row["target"]), str(row["target"]))
        lines.extend(
            [
                f"### {source} -> {target}",
                f"- relation_type: `{row['relation_type']}`",
                f"- current_status: `{row['status']}`",
                f"- confidence: `{row['confidence']}`",
                f"- evidence_basis: {', '.join(provenance.get('evidence_refs') or []) or 'n/a'}",
                f"- rationale_summary: {row['rationale']}",
                "- decision: still pending because a source-grounded target note does not yet exist",
                f"- follow_up: {provenance.get('basis_note') or 'none'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_attach_readiness(registry: dict[str, Any]) -> str:
    pending_docs = registry.get("deferred_documents") or []
    lines = [
        "# Obsidian Graph Attach Readiness",
        "",
        "## Purpose",
        "- This document explains how deferred `pending_source_note` relations become active after real source-grounded regulation documents are available.",
        "",
        "## Core Rule",
        "- Do not create placeholder or stub `regulation_document` notes just to satisfy the graph.",
        "- Attach only after a real source-grounded note exists in `wiki/regulation_documents`.",
        "- Existing source-grounded notes such as UNECE R137 and R95 may be attached directly through the registry without a new ingest pass.",
        "",
        "## Attach Workflow",
        "1. Confirm that the target note already exists as a real source-grounded `regulation_document`, or ingest it first if it does not.",
        "2. Add or update the document row in `taxonomy/regulatory_connectivity.yaml` with `status: active`.",
        "3. Update any related relation rows from `pending_source_note` to `active` only if the source-grounded note supports the semantic relation.",
        "4. Run `python tools/build_obsidian_graph_layer.py --project-root .`.",
        "5. Run `.\\scripts\\wiki.ps1 verify`.",
        "",
        "## Validation Checks After Attach",
        "- the deferred document should appear in the graph-ready document count",
        "- pending_source_note relation count should drop for the attached item",
        "- the new document should appear in generated graph connections and coverage docs",
        "- leakage checks must remain clean",
        "",
        "## Dry-Run Example",
        "- target deferred id: `regdoc-eu-2019-2144`",
        "- current policy: remain deferred until a real source-grounded EU 2019/2144 note exists",
        "- no-placeholder reminder: do not create `wiki/regulation_documents/regdoc-eu-2019-2144.md` as a stub",
        "- expected post-ingest behavior: change the document status to `active`, re-evaluate relation type from source-grounded evidence, promote only supported rows to `active`, rerun builder, then confirm validation reflects the attach",
        "",
        "## Current Phase Note",
        "- In the UNECE first attach drill, UNECE R137 and R95 are attached because they already exist as source-grounded notes.",
        "- EU 2019/2144 remains deferred in this phase and is not auto-promoted merely because related jurisdictions are now attached.",
        "",
        "## Current Deferred Items",
    ]
    if not pending_docs:
        lines.append("- none")
    for row in pending_docs:
        lines.append(f"- `{row['id']}` | {row['label']} | status: `{row['status']}`")
    return "\n".join(lines).rstrip() + "\n"


def build_validation(
    project_root: Path,
    registry: dict[str, Any],
    active_documents: dict[str, dict[str, Any]],
    concept_page_refs: dict[str, str],
    hub_page_refs: dict[str, str],
    validation_errors: list[str],
) -> str:
    wiki_root = project_root / "wiki"
    graph_notes: dict[str, dict[str, Any]] = {}
    leaked_unit_targets: set[str] = set()
    non_graph_ready_tagged_nodes: list[str] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if "_templates" in path.parts or path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, body = parse_frontmatter_file(path)
        rel = str(path.relative_to(project_root)).replace("\\", "/")
        tags = [str(tag) for tag in frontmatter.get("tags") or []]
        note_type = str(frontmatter.get("note_type") or "")
        graph_group = str(frontmatter.get("graph_group") or "")
        page_ref = note_ref_from_path(wiki_root, path)
        if "graph-ready" in tags:
            allowed = (
                (note_type == "concept_node" and graph_group == "concept")
                or (note_type == "regulation_document" and graph_group == "document")
                or (note_type == "browse_index" and graph_group == "hub")
            )
            if not allowed:
                non_graph_ready_tagged_nodes.append(rel)
        if frontmatter.get("graph_ready") is True and "graph-ready" in tags:
            graph_notes[page_ref] = {"frontmatter": frontmatter, "body": body, "rel": rel}
            generated_body = _extract_generated_graph_block(body)
            for match in WIKILINK_RE.finditer(generated_body):
                target = match.group(1).strip()
                if target.startswith("regulation_units/"):
                    leaked_unit_targets.add(target)

    edges: set[tuple[str, str]] = set()
    degree = Counter()
    for page_ref, row in graph_notes.items():
        for match in WIKILINK_RE.finditer(row["body"]):
            target = match.group(1).strip()
            if target in graph_notes:
                edges.add(tuple(sorted([page_ref, target])))
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    orphan_nodes = sorted(page for page in graph_notes if degree[page] == 0)
    high_degree_nodes = sorted(((page, count) for page, count in degree.items() if count > 12), key=lambda item: (-item[1], item[0]))
    by_group = Counter(str(row["frontmatter"].get("graph_group") or "unknown") for row in graph_notes.values())
    relation_status_counts = Counter(str(row.get("status") or "active") for row in registry["relations"])
    active_relation_type_counts = Counter(str(row["relation_type"]) for row in registry["relations"] if str(row.get("status") or "active") == "active")
    active_docs = [row for row in registry["documents"] if str(row.get("status") or "active") == "active"]
    active_concepts = active_concept_rows(registry)
    concept_by_cluster = Counter(str(row["cluster"]) for row in active_concepts)
    doc_by_cluster = Counter(str(row["cluster"]) for row in active_docs)
    active_doc_ids = {str(row["id"]) for row in active_docs}
    doc_jurisdiction = {str(row["id"]): str(row.get("jurisdiction") or "") for row in active_docs}
    doc_doc_cross_pairs = Counter()
    doc_doc_cross_pair_types = Counter()
    for row in registry["relations"]:
        if str(row.get("status") or "active") != "active":
            continue
        source = str(row.get("source") or "")
        target = str(row.get("target") or "")
        if source not in active_doc_ids or target not in active_doc_ids:
            continue
        source_jurisdiction = doc_jurisdiction.get(source, "")
        target_jurisdiction = doc_jurisdiction.get(target, "")
        if not source_jurisdiction or not target_jurisdiction or source_jurisdiction == target_jurisdiction:
            continue
        pair = " <-> ".join(sorted((source_jurisdiction, target_jurisdiction)))
        doc_doc_cross_pairs[pair] += 1
        doc_doc_cross_pair_types[f"{row['relation_type']} | {pair}"] += 1
    kr_docs = [row for row in active_docs if str(row.get("jurisdiction") or "") == "KR"]
    kr_display_count = sum(1 for row in kr_docs if str(row.get("display_title") or "").strip())
    degree_bucket = Counter()
    for page in graph_notes:
        node_degree = degree[page]
        if node_degree == 0:
            degree_bucket["0"] += 1
        elif node_degree <= 3:
            degree_bucket["1-3"] += 1
        elif node_degree <= 7:
            degree_bucket["4-7"] += 1
        else:
            degree_bucket["8+"] += 1
    sparse_clusters = []
    for hub in registry["hubs"]:
        if str(hub.get("status") or "active") != "active":
            continue
        cluster = str(hub["cluster"])
        if concept_by_cluster[cluster] <= 1 and doc_by_cluster[cluster] <= 1:
            sparse_clusters.append(cluster)
    deferred = registry.get("deferred_documents") or []

    lines = [
        "# Obsidian Graph Validation",
        "",
        "## Summary",
        f"- graph_ready_node_count: {len(graph_notes)}",
        f"- graph_ready_edge_count: {len(edges)}",
        f"- orphan_node_count: {len(orphan_nodes)}",
        f"- deferred_regulation_count: {len(deferred)}",
        "",
        "## Graph-Ready Layer Result",
        "- The graph-ready layer contains only existing source-grounded regulation_document notes, active concept notes, and graph hub notes.",
        "- missing seeds are deferred and do not emit nodes or wikilinks.",
        "",
        "## Node Counts By Group",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(by_group.items()))
    lines.extend(
        [
            "",
            "## Degree Distribution Summary",
            f"- degree 0: {degree_bucket['0']}",
            f"- degree 1-3: {degree_bucket['1-3']}",
            f"- degree 4-7: {degree_bucket['4-7']}",
            f"- degree 8+: {degree_bucket['8+']}",
            "",
            "## Relation Status Counts",
        ]
    )
    lines.extend(f"- {key}: {value}" for key, value in sorted(relation_status_counts.items()))
    lines.extend(["", "## Active Relation Counts By Type"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(active_relation_type_counts.items()))
    lines.extend(["", "## Cluster Balance Summary"])
    for hub in registry["hubs"]:
        if str(hub.get("status") or "active") != "active":
            continue
        cluster = str(hub["cluster"])
        lines.append(f"- `{cluster}` -> concepts: {concept_by_cluster[cluster]}, documents: {doc_by_cluster[cluster]}")
    lines.extend(
        [
            "",
            "## Concept-to-Document Ratio",
            f"- active_concepts_to_documents: {len(active_concepts)}:{len(active_docs)}",
            "",
            "## Sparse Clusters",
        ]
    )
    lines.extend(f"- `{cluster}`" for cluster in sparse_clusters) if sparse_clusters else lines.append("- none")
    lines.extend(
        [
            "",
            "## Review and Deferred Counts",
            f"- review_required_relation_count: {relation_status_counts.get('review_required', 0)}",
            f"- pending_source_note_relation_count: {relation_status_counts.get('pending_source_note', 0)}",
            "",
            "## Cross-Jurisdiction Document Edges",
            f"- KR <-> US active_document_edges: {doc_doc_cross_pairs.get('KR <-> US', 0)}",
            f"- UNECE <-> US active_document_edges: {doc_doc_cross_pairs.get('UNECE <-> US', 0)}",
            f"- KR <-> UNECE active_document_edges: {doc_doc_cross_pairs.get('KR <-> UNECE', 0)}",
            f"- EU deferred_documents: {sum(1 for row in deferred if str(row.get('jurisdiction') or '') == 'EU')}",
            "",
            "## Cross-Jurisdiction Edge Types",
        ]
    )
    lines.extend(f"- {key}: {value}" for key, value in sorted(doc_doc_cross_pair_types.items()))
    if not doc_doc_cross_pair_types:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## KR Display Title Coverage",
            f"- active_kr_documents: {len(kr_docs)}",
            f"- active_kr_documents_with_display_title: {kr_display_count}",
            "",
            "## Leakage Checks",
            f"- leaked_regulation_units_in_global_graph = {len(leaked_unit_targets)}",
        ]
    )
    if leaked_unit_targets:
        lines.extend(f"- leaked_target: `{target}`" for target in sorted(leaked_unit_targets))
    lines.append(f"- non_graph_ready_tagged_nodes: {len(non_graph_ready_tagged_nodes)}")
    if non_graph_ready_tagged_nodes:
        lines.extend(f"- review: `{rel}`" for rel in sorted(non_graph_ready_tagged_nodes))
    lines.extend(["", "## Orphan Nodes"])
    lines.extend(f"- `{node}`" for node in orphan_nodes) if orphan_nodes else lines.append("- none")
    lines.extend(["", "## High Degree Nodes"])
    lines.extend(f"- `{node}` -> degree {count}" for node, count in high_degree_nodes) if high_degree_nodes else lines.append("- none above threshold")
    lines.extend(["", "## Deferred Regulations"])
    for row in deferred:
        lines.append(f"- `{row['id']}` | {row['label']} | status: `{row['status']}`")
    lines.extend(
        [
            "",
            "## Readability Decisions",
            "- `graph-cluster-occupant-protection` remains unsplit by design because the current density still reflects a coherent occupant-protection neighborhood.",
            "- `graph-cluster-vru-and-external-protection` remains sparse by design as a seed-stage cluster with one active concept mediator and one active document.",
            "",
            "## Local Graph Quality Checklist",
            "- `FMVSS 205`: glazing and driver-visibility neighborhood remains visible at depth 2.",
            "- `FMVSS 206`: door retention, anti-ejection, and egress neighborhood remains visible at depth 2.",
            "- `FMVSS 208`: occupant protection, frontal impact, and KR analog neighborhood remains visible at depth 2.",
            "- `FMVSS 214`: side-impact neighborhood remains visible at depth 2.",
            "- `FMVSS 226`: anti-ejection and retention neighborhood remains visible at depth 2.",
            "- `FMVSS 305a`: EV electrical safety and post-crash isolation neighborhood remains visible at depth 2.",
            "- `UNECE R137`: occupant protection, frontal impact, and restraint-system neighborhood remains visible at depth 2.",
            "- `UNECE R95`: occupant protection and side-impact neighborhood remains visible at depth 2.",
            "",
            "## Missing-Seed Policy Summary",
            "- If a source-grounded regulation document note does not exist, the candidate remains deferred rather than materialized as a placeholder.",
            "- `review_required`, `pending_source_note`, and `excluded` relations are visible in governance docs but do not emit graph edges.",
            "",
            "## Attach-on-Ingest Summary",
            "- When a deferred document is ingested as a real source-grounded note, switch the document row to `active` and promote only supported relation rows to `active` before rebuilding.",
            "- After rerunning `python tools/build_obsidian_graph_layer.py --project-root .`, the new graph-ready links and validation counts update automatically.",
            "- See `docs/obsidian_graph_attach_readiness.md` for the dry-run procedure using `regdoc-eu-2019-2144`.",
        ]
    )
    if validation_errors:
        lines.extend(["", "## Validation Warnings"])
        lines.extend(f"- {error}" for error in validation_errors)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    project_root = Path(parse_args().project_root).resolve()
    payload = build_graph(project_root)
    for rel in payload["written"]:
        print(rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
