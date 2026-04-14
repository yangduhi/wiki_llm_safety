# Obsidian Graph Review Queue

## Purpose
- Use this queue to close unresolved semantic relations and to track attach-on-ingest work for deferred source-grounded notes.

## Review-Required Relations
- none
- The previously reviewed candidates are now adjudicated in `docs/obsidian_graph_relation_decisions.md`.
## Pending Source Notes
### EU 2019/2144 General Safety Regulation
- id: `regdoc-eu-2019-2144`
- status: `pending_source_note`
- rationale: Deferred in graph v1 because no source-grounded regulation_document note exists in wiki/regulation_documents.
- attach_on_ingest: create the real source-grounded regulation_document note through ingest, switch the document and related relation rows to `active`, then rerun graph build.
- operator_next_step: follow `docs/obsidian_graph_attach_readiness.md` and confirm validation after rebuild.

## State Transitions
- `review_required -> active`: semantic equivalence becomes strong enough for explicit graph emission.
- `review_required -> excluded`: review shows the relation should not become a semantic graph edge.
- `pending_source_note -> active`: source-grounded regulation_document note exists and the registry is updated after ingest.

## Operator Links
- [Relation Decisions](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_relation_decisions.md)
- [Attach Readiness](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/obsidian_graph_attach_readiness.md)
