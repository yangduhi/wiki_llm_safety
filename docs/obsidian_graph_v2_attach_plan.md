---
record_layer: operations
id: obsidian-graph-v2-attach-plan
title: Obsidian Graph V2 Attach Plan
summary: Execution plan for the first UNECE attach drill while keeping EU 2019/2144 deferred.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - graph
  - unece
  - plan
---

# Obsidian Graph V2 Attach Plan

## Branch

- Branch A
- Reason: UNECE R137 and R95 already exist as source-grounded `regulation_document` notes, while `EU 2019/2144` does not.

## Attach Scope

- Attach:
  - `regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english`
  - `regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english`
- Keep deferred:
  - `regdoc-eu-2019-2144`
- Do not attach in this phase:
  - `R94`
  - `R127`
  - `concept-general-safety-umbrella`

## Registry Decisions

- Add R137 and R95 as active UNECE documents in `occupant-protection`.
- Add only minimal concept-to-document relations:
  - occupant / frontal / restraint -> R137
  - occupant / side-impact -> R95
- Add only minimal document-to-document relations:
  - `FMVSS 208 <-> R137` as `same_test_family`
  - `FMVSS 214 <-> R95` as `jurisdictional_analog`
- Keep `FMVSS 208 -> EU 2019/2144` as `pending_source_note`.

## Generated Surface Expectations

- Coverage matrix must support `US | KR | UNECE | EU`.
- Occupant hub remains unsplit and absorbs UNECE readability updates.
- Graph home and usage docs must expose UNECE representative entry points.
