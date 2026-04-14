---
record_layer: operations
id: obsidian-graph-reference-alignment-v2-1
title: Obsidian Graph Reference Alignment
summary: Records which canonical repository patterns were reused for the UNECE attach and EU attach-gate phases.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - graph
  - reference
---

# Obsidian Graph Reference Alignment

## Reference Surface Used

- Separate local `wiki_llm_safety` clone was not found.
- The current workspace itself is the canonical repository because `origin` points to `https://github.com/yangduhi/wiki_llm_safety.git`.
- Inspected reference files:
  - `src/wiki_obsidian/ingest/service.py`
  - `src/wiki_obsidian/dashboard.py`
  - `harness/scripts/check_generated_surfaces.py`
  - `docs/operations/notes/generated-surfaces.md`
  - current graph layer files under `taxonomy/`, `tools/`, and `docs/obsidian_graph_*`

## Phase Context

- The first UNECE attach drill is already completed in the current repository.
- The current phase is the first EU attach gate for `EU 2019/2144`.
- This phase does not attach EU yet because no repository-local source-grounded EU note exists.

## Adopted Patterns

- Source-grounded notes are materialized first, then generated graph surfaces project them.
- Registry-first generation remains the source of truth for graph nodes and edges.
- Verify treats generated markdown surfaces as baseline files rather than optional artifacts.
- Operator-facing docs such as validation, coverage, review, and graph-home remain builder-generated.
- Attach gates are decided from repository-local source availability, not from authority rows or URLs alone.
- When a source package is missing, the repo prefers blocker/source-map documentation over simulated attach completion.

## Rejected Patterns

- No ingest-phase graph edge writing:
  - graph attach remains a post-ingest registry decision, not an ingest side effect.
- No browse hub promotion to ontology foundation:
  - browse hubs remain UI surfaces, not canonical graph roots.
- No placeholder or stub documents:
  - deferred EU attach remains deferred until a real source-grounded note exists.
- No authority-row-only attach:
  - `sources/document_inventory.csv` and `sources/authority_registry.yaml` can justify a target, but not a source-grounded graph note.
- No umbrella concept activation for symmetry:
  - governance or umbrella concepts stay excluded unless the ingested note itself clearly supports that role.

## Fit With Current Foundation

- The adopted patterns fit because the current repository already separates:
  - source-grounded note identity
  - registry decisions
  - generated operator surfaces
- The rejected patterns do not fit because they would blur provenance or introduce graph noise without source-grounded evidence.

## EU 2019/2144 Gate Alignment

- Reused from the current repository:
  - source-grounded ingest lifecycle from `src/wiki_obsidian/ingest/service.py`
  - generated-surface freshness + verify baseline from `scripts/wiki.ps1`, `harness/scripts/check_generated_surfaces.py`, and `docs/operations/notes/generated-surfaces.md`
  - registry-first graph attach contract from `tools/build_obsidian_graph_layer.py`
- Not reused:
  - no custom one-off EU note bootstrap
  - no bypass around `raw/collections/*`
  - no direct graph write that skips registry and builder
- Resulting decision:
  - `EU 2019/2144` remains `pending_source_note`
  - the correct next step is an ingest blocker package, not a partial attach
