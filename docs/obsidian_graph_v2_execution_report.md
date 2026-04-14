---
record_layer: operations
id: obsidian-graph-v2-execution-report
title: Obsidian Graph V2 Execution Report
summary: Records the first UNECE attach drill while keeping EU 2019/2144 deferred.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - graph
  - unece
  - execution-report
---

# Obsidian Graph V2 Execution Report

## Branch Selected

- Branch A
- reason: existing source-grounded UNECE notes for R137 and R95 were already present and usable

## Reference Alignment

- `wiki_llm_safety` was treated as the canonical reference through the current repository remote and implementation surface.
- alignment record: `docs/obsidian_graph_reference_alignment.md`

## Attach Candidates Confirmed

- attached:
  - `regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english`
  - `regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english`
- kept deferred:
  - `regdoc-eu-2019-2144`
- not attached in this phase:
  - `R94`
  - `R127`
  - `concept-general-safety-umbrella`

## Actions Taken

- added R137 and R95 as active UNECE graph documents in `occupant-protection`
- added five minimal concept-to-document relations for R137 and R95
- added two minimal document-to-document relations:
  - `FMVSS 208 <-> R137` as `same_test_family`
  - `FMVSS 214 <-> R95` as `jurisdictional_analog`
- kept `FMVSS 208 -> EU 2019/2144` as `pending_source_note`
- updated builder to render coverage across `US | KR | UNECE | EU`
- updated occupant hub readability without splitting topology
- updated graph-home, validation, coverage matrix, usage, relation decisions, attach readiness
- updated generated-surface baseline to include graph governance surfaces

## Relation Decisions

- retained pending:
  - `FMVSS 208 -> EU 2019/2144`
- newly active:
  - `FMVSS 208 <-> R137` as `same_test_family`
  - `FMVSS 214 <-> R95` as `jurisdictional_analog`
- deliberately not added:
  - `R137 <-> KR 102_153`
  - `R95 <-> KR 102_154`
  - `R127 <-> KR 102_152`

## Validation Deltas

- active concept count: `17`
- active document count: `13 -> 15`
- graph_ready_node_count: `36 -> 38`
- graph_ready_edge_count: `91 -> 100`
- review_required_relation_count: `0`
- pending_source_note_relation_count: `1`
- excluded_relation_count: `2`
- orphan_node_count: `0`
- regulation_unit leakage: `0`
- non-graph-ready tagged nodes: `0`

## Verify Result

- `python tools/build_obsidian_graph_layer.py --project-root .` completed
- `.\scripts\wiki.ps1 verify` passed

## Remaining Risks

- `EU 2019/2144` still has no source-grounded regulation document note, so EU attach remains blocked
- occupant-protection hub is now denser, but it remains intentionally unsplit
- UNECE attach remains intentionally conservative and does not yet include UNECE-to-KR dense linking

## Next Trigger

- the next expansion trigger should be one of:
  - a real source-grounded EU 2019/2144 note is ingested
  - additional UNECE notes need attach and are justified by source-grounded evidence
  - cross-jurisdiction evidence becomes strong enough to re-open broader UNECE-to-KR relation decisions
