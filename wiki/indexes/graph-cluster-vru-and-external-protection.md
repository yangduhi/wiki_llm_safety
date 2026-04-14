---
record_layer: knowledge
id: graph-cluster-vru-and-external-protection
note_type: browse_index
title: VRU and External Protection Cluster
summary: Semantic graph hub for the `vru-and-external-protection` cluster.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: graph_connectivity
type: hub
graph_group: hub
cluster: vru-and-external-protection
tags:
- graph-ready
- graph/hub
- cluster/vru-and-external-protection
graph_ready: true
provenance:
  source_files:
  - taxonomy/regulatory_connectivity.yaml
  source_hashes:
    taxonomy/regulatory_connectivity.yaml: 524131bcbcc3395d4bf03a687936a83a9c4e84b3d983b8fa9f216272d6348ce0
  parser_run_id: graph-layer-2026-04-14
confidence: medium
---

# VRU and External Protection Cluster

## Snapshot
- cluster: `vru-and-external-protection`
- graph_group: hub
- graph_ready: true

## Why This Hub Exists
- This hub gathers graph-ready concepts and selected regulations for the `vru-and-external-protection` semantic neighborhood.

## Browse View
- Use this note as the cluster entry point for Local Graph exploration.

## Cluster Scope
- cluster: `vru-and-external-protection`
- planned_concepts_backlog: concept-vru-protection

## Readability Note
- This cluster remains active but sparse in V1.2. It is intentionally treated as a seed-stage neighborhood until more source-grounded notes are ingested.

## Seed-Stage Status
- active_concepts: 1
- active_documents: 1
- emphasis: KR-led pedestrian protection seed, not a broad VRU ontology.

## Seed Concepts
- [[concepts/concept-pedestrian-protection|Pedestrian Protection]]

## Seed Regulations
- [[regulation_documents/xml_kmvss-kmvss_art_102_152|조문 102 보행자 보호]]

## Dataview
```dataview
TABLE file.link, graph_group, cluster
FROM "wiki"
WHERE contains(tags, "graph-ready") AND cluster = "vru-and-external-protection"
SORT graph_group ASC, file.name ASC
```

<!-- BEGIN GENERATED GRAPH LAYER -->
### Neighbor Clusters
- [[indexes/graph-cluster-approval-and-governance|Approval and Governance Cluster]]
<!-- END GENERATED GRAPH LAYER -->
