---
record_layer: operations
id: operations-kmvss-round2d-repo-reference-delta
title: KMVSS Round 2D Repo Reference Delta
summary: Records the actual wiki_llm_safety reference basis and selective operating-pattern reuse for KMVSS round 2D.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2d
  - reference
---

# KMVSS Round 2D Repo Reference Delta

## Reviewed Inputs

- prior map reused:
  - [kmvss_round2c_repo_reference_map.md](/D:/vscode/4__wiki__obsidian/docs/operations/pilot/kmvss_round2c_repo_reference_map.md)
- remote `wiki_llm_safety` reference basis:
  - `README.md`
  - `docs/operations/README.md`
  - `docs/operations/notes/operating-rules.md`
  - `docs/operations/pilot/pilot_document_set.csv`
  - `docs/operations/pilot/pilot_mapping_results.jsonl`
- local pattern witness:
  - [README.md](/D:/vscode/4__wiki__obsidian__autosync/README.md)
  - [docs/operations/README.md](/D:/vscode/4__wiki__obsidian__autosync/docs/operations/README.md)
  - [docs/operations/pilot/pilot_document_set.csv](/D:/vscode/4__wiki__obsidian__autosync/docs/operations/pilot/pilot_document_set.csv)
  - [docs/operations/pilot/pilot_mapping_results.jsonl](/D:/vscode/4__wiki__obsidian__autosync/docs/operations/pilot/pilot_mapping_results.jsonl)
  - [docs/operations/notes/operating-rules.md](/D:/vscode/3__wiki_universal/docs/operations/notes/operating-rules.md)

## Reused Patterns This Round

- `docs/operations/` scoped document layout for policy, audit, evaluation, and fix-log separation
- pilot CSV + JSONL dual artifacts for register and adjudication evidence
- public CLI unchanged, with repo-local helper scripts under `harness/scripts/`
- harness-based verify gate and run-scoped artifact usage
- fixed-slice replay and comparable evaluation discipline
- policy note + pilot artifact dual tracking
- trace diff / adjudication register style when compatible with current trace contract

## Rejected or Narrowed Patterns

- round 2C note pointing to `D:\vscode\4__wiki__obsidian__chatgpt_repo`
  - rejected because the path does not exist in the current workspace
- foreign review-lane names or meaning system
  - rejected because KMVSS round 1 / 2A / 2B / 2C decisions already define the canonical semantics
- minimal pilot-two-file convention
  - rejected because KMVSS round work already relies on separate triage, policy, comparable evaluation, trace diff, and fix log artifacts

## Minimal Adaptation for This Repository

- remote `wiki_llm_safety` is used only as an operating-pattern reference, not as a classification ontology source
- local witness repos are used only to confirm document layout and pilot artifact conventions
- all review-lane states, promotion criteria, and taxonomy decisions stay anchored to KMVSS-specific round 2C baseline and current repository contracts
- round 2D reuse is intentionally limited to helper scripts, pilot docs, and trace observability; attachment parsing and public CLI remain unchanged
