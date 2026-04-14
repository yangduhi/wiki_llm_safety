# Obsidian Graph Plan

## Current Structure Diagnosis
- The repository is an Obsidian vault, Git repo, and Codex workspace with the canonical knowledge layer under `wiki/`.
- The current wiki is optimized for `regulation_unit` grounding, not graph-native semantic browsing.
- Current note reality before graph-ready generation:
  - `regulation_document` is the right abstraction for graph entry
  - `regulation_unit` is too granular for global graph use
  - `wiki/concepts/` is effectively empty
  - existing `wiki/indexes/` notes are browse hubs, not semantic graph hubs
- Document-to-document semantic wikilinks are currently sparse, while document-to-unit links are dense.

## Why Raw Graph Becomes a Hairball
- Global Graph over the whole vault would primarily visualize:
  - `regulation_document -> regulation_unit` containment
  - generated browse note link clusters
  - imported or low-signal edge noise
- It would not reliably show:
  - cross-jurisdiction analogs
  - same safety function neighborhoods
  - administrative governance over technical regulations
- Therefore raw corpus graphing is prohibited in V1.

## Graph-Ready Layer Design
- V1 introduces a graph-ready layer whose source of truth is `taxonomy/regulatory_connectivity.yaml`.
- Only three node classes participate in the global graph:
  1. concept notes
  2. selected source-grounded `regulation_document` notes
  3. semantic graph hubs
- `regulation_unit`, raw, evidence, attachment, pasted image, import log, and dashboards are excluded from the global graph.
- The semantic graph is built from explicit relations only. No relation may be inferred from shared `phase` or shared `functional_domain` alone.

## Node Types
- concept
  - implemented as `note_type: concept_node`
  - frontmatter includes `type`, `graph_group`, `cluster`, `tags`, `graph_ready`
- regulation_document
  - implemented as existing source-grounded `note_type: regulation_document`
  - only selected active documents become graph-ready
- hub
  - implemented as `note_type: browse_index`
  - uses dedicated semantic hub notes under `wiki/indexes/graph-cluster-*.md`

## Relation Types
- `concept_related`
- `concept_to_document`
- `jurisdictional_analog`
- `same_safety_function`
- `same_test_family`
- `umbrella_to_implementing`
- `admin_governs`
- `variant_or_successor`

## Missing-Seed Policy
- If a source-grounded `regulation_document` note does not exist in `wiki/regulation_documents`, the seed is deferred.
- No placeholder note is created.
- Deferred items stay visible in:
  - `assumptions.md`
  - `docs/obsidian_graph_plan.md`
  - `docs/obsidian_graph_validation.md`
- Registry rows may still exist with:
  - `status: pending_source_note`
  - or `status: excluded`
- Builder behavior:
  - emit graph wikilinks and edges only for `status: active`
  - show `review_required` in validation only
  - do not emit `pending_source_note`
  - do not emit `excluded`

## Deferred Regulation List
- `EU 2019/2144 General Safety Regulation`
  - desired future ID: `regdoc-eu-2019-2144`
  - current status: `pending_source_note`
  - reason: no existing source-grounded `regulation_document` note in the current wiki

## Active Seed Scope
- US:
  - `FMVSS 205`
  - `FMVSS 206`
  - `FMVSS 208`
  - `FMVSS 214`
  - `FMVSS 226`
  - `FMVSS 305a`
- KR:
  - `KMVSS 102_151`
  - `KMVSS 102_152`
  - `KMVSS 102_153`
  - `KMVSS 102_154`
  - `KMVSS 112_186`
  - `KMVSS 114_189`
  - `KMVSS 114_190`

## Hub Strategy
- Existing generated browse hubs such as `phase-hub` and `functional-domain-hub` remain browse/navigation entrypoints.
- Semantic graph hubs are separate notes:
  - `graph-cluster-occupant-protection.md`
  - `graph-cluster-structural-retention-and-egress.md`
  - `graph-cluster-visibility-and-glazing.md`
  - `graph-cluster-battery-fire-and-electrical-safety.md`
  - `graph-cluster-vru-and-external-protection.md`
  - `graph-cluster-approval-and-governance.md`
- This prevents the dashboard/browse generator from overwriting the semantic graph layer.

## Global Graph vs Local Graph Policy
- Global Graph:
  - filtered by `tag:#graph-ready`
  - used for cluster overview only
- Local Graph:
  - used for semantic neighborhood reading
  - hub depth: 1
  - concept depth: 2
  - selected document depth: 2
- `FMVSS 205`, `206`, `208`, `214`, `226`, and `305a` are the core Local Graph examples for V1.
