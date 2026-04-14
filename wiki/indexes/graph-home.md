---
record_layer: knowledge
id: graph-home
note_type: browse_index
title: Graph Home
summary: Human entrypoint for using the graph-ready semantic layer.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: graph_home
type: hub
graph_group: operator
cluster: graph-home
tags:
  - operator-entry
graph_ready: false
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: graph-home-v1-2
confidence: medium
---

# Graph Home

## Snapshot
- purpose: primary human entrypoint for the graph-ready semantic layer
- role: official tracked operator hub
- git_contract: committed generated artifact
- graph_ready: false
- freshness_protected_by_verify: true
- live_wiki_snapshot: [[indexes/current-wiki-visualization|Current Wiki Visualization]]

## Why This Hub Exists
- Start here when you want to use the graph layer as an operator rather than as a graph node.
- This hub is a builder-owned official graph surface rather than a hand-maintained note.
- `.\scripts\wiki.ps1 verify` now rebuilds graph-generated surfaces before baseline checks, so graph-view operations follow the same freshness contract as dashboards and indexes.
- Manual docs under `docs/obsidian_graph*.md` remain official tracked operations docs even when they are not generated.

## Browse View
- Global Graph: filter by `tag:#graph-ready`.
- Local Graph: hub depth 1, concept/document depth 2.
- Keep `graph-home.md` itself out of the Global Graph; it is an operator landing page, not a graph node.

## Cluster Scope
- [[indexes/graph-cluster-occupant-protection|Occupant Protection Cluster]]
- [[indexes/graph-cluster-structural-retention-and-egress|Structural Retention and Egress Cluster]]
- [[indexes/graph-cluster-visibility-and-glazing|Visibility and Glazing Cluster]]
- [[indexes/graph-cluster-battery-fire-and-electrical-safety|Battery / Fire / Electrical Safety Cluster]]
- [[indexes/graph-cluster-vru-and-external-protection|VRU and External Protection Cluster]]
- [[indexes/graph-cluster-approval-and-governance|Approval and Governance Cluster]]

## Seed Concepts
- [[concepts/concept-occupant-protection|Occupant Protection]]
- [[concepts/concept-door-retention|Door Retention]]
- [[concepts/concept-glazing-materials|Glazing Materials]]
- [[concepts/concept-ev-electrical-safety|EV Electrical Safety]]
- [[concepts/concept-pedestrian-protection|Pedestrian Protection]]

## Seed Regulations
- [[regulation_documents/xml_fmvss-571-205|FMVSS 205]]
- [[regulation_documents/xml_fmvss-571-206|FMVSS 206]]
- [[regulation_documents/xml_fmvss-571-208|FMVSS 208]]
- [[regulation_documents/xml_fmvss-571-214|FMVSS 214]]
- [[regulation_documents/xml_fmvss-571-226|FMVSS 226]]
- [[regulation_documents/xml_fmvss-571-305a|FMVSS 305a]]
- [[regulation_documents/xml_kmvss-kmvss_art_102_151|조문 102 충돌 시의 승객보호]]
- [[regulation_documents/xml_kmvss-kmvss_art_112_186|조문 112 전기자동차 등에 사용되는 구동축전지]]
- [[regulation_documents/pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english|ECE R137 UN Regulation No. 137 - Rev.1 - Frontal impact with focus on restraint systems Rev0 English]]
- [[regulation_documents/pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english|ECE R95 UN Regulation No. 95 - Rev.2 - Lateral collision protection Rev0 English]]

## Dataview
```dataview
TABLE file.link, graph_group, cluster
FROM "wiki"
WHERE contains(tags, "graph-ready")
SORT graph_group ASC, file.name ASC
```

## Review and Operations Links
- [docs/operations/INDEX.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/operations/INDEX.md)
- [docs/obsidian_graph_usage.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_usage.md)
- [docs/obsidian_graph_validation.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_validation.md)
- [docs/obsidian_graph_review_queue.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_review_queue.md)
- [docs/obsidian_graph_coverage_matrix.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_coverage_matrix.md)
- [docs/obsidian_graph_relation_decisions.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_relation_decisions.md)
- [docs/obsidian_graph_attach_readiness.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_attach_readiness.md)
- [docs/obsidian_graph_v1_2_plan.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_v1_2_plan.md)
- [docs/obsidian_graph_reference_alignment.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_reference_alignment.md)
- [docs/obsidian_graph_v2_attach_plan.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_v2_attach_plan.md)

## Commands
- refresh graph surfaces: `.\scripts\wiki.ps1 graph-refresh`
- graph-refresh regenerates builder-owned graph surfaces in this contract; it does not define a separate graph-only local markdown path
- rebuild directly: `python tools/build_obsidian_graph_layer.py --project-root .`
- verify: `.\scripts\wiki.ps1 verify`
