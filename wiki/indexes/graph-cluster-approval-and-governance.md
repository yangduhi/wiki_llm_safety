---
record_layer: knowledge
id: graph-cluster-approval-and-governance
note_type: browse_index
title: Approval and Governance Cluster
summary: Semantic graph hub for the `approval-and-governance` cluster.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: graph_connectivity
type: hub
graph_group: hub
cluster: approval-and-governance
tags:
- graph-ready
- graph/hub
- cluster/approval-and-governance
graph_ready: true
provenance:
  source_files:
  - taxonomy/regulatory_connectivity.yaml
  source_hashes:
    taxonomy/regulatory_connectivity.yaml: 524131bcbcc3395d4bf03a687936a83a9c4e84b3d983b8fa9f216272d6348ce0
  parser_run_id: graph-layer-2026-04-14
confidence: medium
---

# Approval and Governance Cluster

## Snapshot
- cluster: `approval-and-governance`
- graph_group: hub
- graph_ready: true

## Why This Hub Exists
- This hub gathers graph-ready concepts and selected regulations for the `approval-and-governance` semantic neighborhood.

## Browse View
- Use this note as the cluster entry point for Local Graph exploration.

## Cluster Scope
- cluster: `approval-and-governance`
- planned_concepts_backlog: concept-market-surveillance-recall, concept-general-safety-umbrella

## Seed Concepts
- [[concepts/concept-type-approval-framework|Type Approval Framework]]
- [[concepts/concept-conformity-assessment|Conformity Assessment]]

## Seed Regulations
- [[regulation_documents/xml_kmvss-kmvss_art_114_189|조문 114 기준적용의 특례]]
- [[regulation_documents/xml_kmvss-kmvss_art_114_190|조문 114 장치 기준에 관한 특례]]

## Dataview
```dataview
TABLE file.link, graph_group, cluster
FROM "wiki"
WHERE contains(tags, "graph-ready") AND cluster = "approval-and-governance"
SORT graph_group ASC, file.name ASC
```

<!-- BEGIN GENERATED GRAPH LAYER -->
### Neighbor Clusters
- [[indexes/graph-cluster-occupant-protection|Occupant Protection Cluster]]
- [[indexes/graph-cluster-vru-and-external-protection|VRU and External Protection Cluster]]
- [[indexes/graph-cluster-battery-fire-and-electrical-safety|Battery / Fire / Electrical Safety Cluster]]
<!-- END GENERATED GRAPH LAYER -->
