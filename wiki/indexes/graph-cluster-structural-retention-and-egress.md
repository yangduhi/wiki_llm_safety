---
record_layer: knowledge
id: graph-cluster-structural-retention-and-egress
note_type: browse_index
title: Structural Retention and Egress Cluster
summary: Semantic graph hub for the `structural-retention-and-egress` cluster.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: graph_connectivity
type: hub
graph_group: hub
cluster: structural-retention-and-egress
tags:
- graph-ready
- graph/hub
- cluster/structural-retention-and-egress
graph_ready: true
provenance:
  source_files:
  - taxonomy/regulatory_connectivity.yaml
  source_hashes:
    taxonomy/regulatory_connectivity.yaml: 524131bcbcc3395d4bf03a687936a83a9c4e84b3d983b8fa9f216272d6348ce0
  parser_run_id: graph-layer-2026-04-14
confidence: medium
---

# Structural Retention and Egress Cluster

## Snapshot
- cluster: `structural-retention-and-egress`
- graph_group: hub
- graph_ready: true

## Why This Hub Exists
- This hub gathers graph-ready concepts and selected regulations for the `structural-retention-and-egress` semantic neighborhood.

## Browse View
- Use this note as the cluster entry point for Local Graph exploration.

## Cluster Scope
- cluster: `structural-retention-and-egress`
- planned_concepts_backlog: none

## Seed Concepts
- [[concepts/concept-door-retention|Door Retention]]
- [[concepts/concept-anti-ejection|Anti-Ejection]]
- [[concepts/concept-emergency-egress|Emergency Egress]]

## Seed Regulations
- [[regulation_documents/xml_fmvss-571-206|§ 571.206 Standard No. 206; Door locks and door retention components.]]
- [[regulation_documents/xml_fmvss-571-226|§ 571.226 Standard No. 226; Ejection Mitigation.]]

## Dataview
```dataview
TABLE file.link, graph_group, cluster
FROM "wiki"
WHERE contains(tags, "graph-ready") AND cluster = "structural-retention-and-egress"
SORT graph_group ASC, file.name ASC
```

<!-- BEGIN GENERATED GRAPH LAYER -->
### Neighbor Clusters
- [[indexes/graph-cluster-occupant-protection|Occupant Protection Cluster]]
<!-- END GENERATED GRAPH LAYER -->
