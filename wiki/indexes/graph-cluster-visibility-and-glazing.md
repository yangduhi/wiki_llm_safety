---
record_layer: knowledge
id: graph-cluster-visibility-and-glazing
note_type: browse_index
title: Visibility and Glazing Cluster
summary: Semantic graph hub for the `visibility-glazing` cluster.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: graph_connectivity
type: hub
graph_group: hub
cluster: visibility-glazing
tags:
- graph-ready
- graph/hub
- cluster/visibility-glazing
graph_ready: true
provenance:
  source_files:
  - taxonomy/regulatory_connectivity.yaml
  source_hashes:
    taxonomy/regulatory_connectivity.yaml: 524131bcbcc3395d4bf03a687936a83a9c4e84b3d983b8fa9f216272d6348ce0
  parser_run_id: graph-layer-2026-04-14
confidence: medium
---

# Visibility and Glazing Cluster

## Snapshot
- cluster: `visibility-glazing`
- graph_group: hub
- graph_ready: true

## Why This Hub Exists
- This hub gathers graph-ready concepts and selected regulations for the `visibility-glazing` semantic neighborhood.

## Browse View
- Use this note as the cluster entry point for Local Graph exploration.

## Cluster Scope
- cluster: `visibility-glazing`
- planned_concepts_backlog: none

## Seed Concepts
- [[concepts/concept-glazing-materials|Glazing Materials]]
- [[concepts/concept-driver-visibility|Driver Visibility]]

## Seed Regulations
- [[regulation_documents/xml_fmvss-571-205|§ 571.205 Standard No. 205, Glazing materials.]]

## Dataview
```dataview
TABLE file.link, graph_group, cluster
FROM "wiki"
WHERE contains(tags, "graph-ready") AND cluster = "visibility-glazing"
SORT graph_group ASC, file.name ASC
```

<!-- BEGIN GENERATED GRAPH LAYER -->
### Neighbor Clusters
- None yet.
<!-- END GENERATED GRAPH LAYER -->
