# Obsidian Graph Validation

## Summary
- graph_ready_node_count: 38
- graph_ready_edge_count: 100
- orphan_node_count: 0
- deferred_regulation_count: 1

## Graph-Ready Layer Result
- The graph-ready layer contains only existing source-grounded regulation_document notes, active concept notes, and graph hub notes.
- missing seeds are deferred and do not emit nodes or wikilinks.

## Node Counts By Group
- concept: 17
- document: 15
- hub: 6

## Degree Distribution Summary
- degree 0: 0
- degree 1-3: 12
- degree 4-7: 22
- degree 8+: 4

## Relation Status Counts
- active: 64
- excluded: 2
- pending_source_note: 1

## Active Relation Counts By Type
- admin_governs: 4
- concept_related: 15
- concept_to_document: 37
- jurisdictional_analog: 1
- same_safety_function: 5
- same_test_family: 2

## Cluster Balance Summary
- `occupant-protection` -> concepts: 6, documents: 7
- `structural-retention-and-egress` -> concepts: 3, documents: 2
- `visibility-glazing` -> concepts: 2, documents: 1
- `battery-fire-and-electrical-safety` -> concepts: 3, documents: 2
- `vru-and-external-protection` -> concepts: 1, documents: 1
- `approval-and-governance` -> concepts: 2, documents: 2

## Concept-to-Document Ratio
- active_concepts_to_documents: 17:15

## Sparse Clusters
- `vru-and-external-protection`

## Review and Deferred Counts
- review_required_relation_count: 0
- pending_source_note_relation_count: 1

## Cross-Jurisdiction Document Edges
- KR <-> US active_document_edges: 4
- UNECE <-> US active_document_edges: 2
- KR <-> UNECE active_document_edges: 0
- EU deferred_documents: 1

## Cross-Jurisdiction Edge Types
- jurisdictional_analog | UNECE <-> US: 1
- same_safety_function | KR <-> US: 3
- same_test_family | KR <-> US: 1
- same_test_family | UNECE <-> US: 1

## KR Display Title Coverage
- active_kr_documents: 7
- active_kr_documents_with_display_title: 7

## Leakage Checks
- leaked_regulation_units_in_global_graph = 0
- non_graph_ready_tagged_nodes: 0

## Orphan Nodes
- none

## High Degree Nodes
- `indexes/graph-cluster-occupant-protection` -> degree 15

## Deferred Regulations
- `regdoc-eu-2019-2144` | EU 2019/2144 General Safety Regulation | status: `pending_source_note`

## Readability Decisions
- `graph-cluster-occupant-protection` remains unsplit by design because the current density still reflects a coherent occupant-protection neighborhood.
- `graph-cluster-vru-and-external-protection` remains sparse by design as a seed-stage cluster with one active concept mediator and one active document.

## Local Graph Quality Checklist
- `FMVSS 205`: glazing and driver-visibility neighborhood remains visible at depth 2.
- `FMVSS 206`: door retention, anti-ejection, and egress neighborhood remains visible at depth 2.
- `FMVSS 208`: occupant protection, frontal impact, and KR analog neighborhood remains visible at depth 2.
- `FMVSS 214`: side-impact neighborhood remains visible at depth 2.
- `FMVSS 226`: anti-ejection and retention neighborhood remains visible at depth 2.
- `FMVSS 305a`: EV electrical safety and post-crash isolation neighborhood remains visible at depth 2.
- `UNECE R137`: occupant protection, frontal impact, and restraint-system neighborhood remains visible at depth 2.
- `UNECE R95`: occupant protection and side-impact neighborhood remains visible at depth 2.

## Missing-Seed Policy Summary
- If a source-grounded regulation document note does not exist, the candidate remains deferred rather than materialized as a placeholder.
- `review_required`, `pending_source_note`, and `excluded` relations are visible in governance docs but do not emit graph edges.

## Attach-on-Ingest Summary
- When a deferred document is ingested as a real source-grounded note, switch the document row to `active` and promote only supported relation rows to `active` before rebuilding.
- After rerunning `python tools/build_obsidian_graph_layer.py --project-root .`, the new graph-ready links and validation counts update automatically.
- See `docs/obsidian_graph_attach_readiness.md` for the dry-run procedure using `regdoc-eu-2019-2144`.
