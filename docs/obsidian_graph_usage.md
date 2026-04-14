# Obsidian Graph Usage

## Goal

- Use Obsidian Global Graph for cluster overview.
- Use Local Graph for semantic neighborhood reading around concepts and selected regulations.

## Global Graph Filter Recipe

- Open Obsidian Global Graph.
- Apply filter: `tag:#graph-ready`
- This should leave only:
  - graph-ready concept notes
  - selected graph-ready regulation documents
  - graph-ready semantic hubs

## Recommended Exclusions

- Exclude or ignore these paths for graph reading:
  - `wiki/regulation_units`
  - `raw`
  - `artifacts`
  - `docs`
  - `_templates`
- Do not manually tag excluded notes with `graph-ready`.

## Color Group Recommendation

- `graph/concept` -> green
- `graph/document` -> blue
- `graph/hub` -> orange
- cluster tags such as `cluster/occupant-protection` can be used as a secondary grouping
- jurisdiction tags:
  - `jurisdiction/us`
  - `jurisdiction/kr`
  - `jurisdiction/unece`
  - `jurisdiction/eu`

## Local Graph Recommendation

- hub notes: depth 1
- concept notes: depth 2
- selected regulation documents: depth 2
- do not use depth > 2 for the current graph-ready layer

## Where To Start

- First open:
  - `wiki/indexes/graph-home.md`
- Then choose one of:
  - `graph-cluster-occupant-protection`
  - `graph-cluster-structural-retention-and-egress`
  - `graph-cluster-visibility-and-glazing`
  - `graph-cluster-battery-fire-and-electrical-safety`
  - `graph-cluster-vru-and-external-protection`
  - `graph-cluster-approval-and-governance`

## Core Local Graph Examples

- `FMVSS 205`
  - should reveal glazing and driver-visibility neighborhood
- `FMVSS 206`
  - should reveal door retention, anti-ejection, emergency egress neighborhood
- `FMVSS 208`
  - should reveal occupant protection, frontal impact, restraint systems, and KR analogs
- `FMVSS 214`
  - should reveal side impact neighborhood
- `FMVSS 226`
  - should reveal anti-ejection and retention neighborhood
- `FMVSS 305a`
  - should reveal battery / electrical / post-crash isolation neighborhood
- `UNECE R137`
  - should reveal occupant protection, frontal impact, restraint systems, and the FMVSS 208 test-family link
- `UNECE R95`
  - should reveal occupant protection, side-impact protection, and the FMVSS 214 analog link

## KR Display Policy

- Keep source-grounded file paths and canonical ids unchanged.
- For graph-facing rendering, prefer:
  1. `display_title`
  2. `title`
  3. note id
- This keeps repository identity stable while improving graph readability.

## When The Graph Looks Wrong

- Check 1: Did you filter by `tag:#graph-ready`?
- Check 2: Did a non-graph note accidentally receive the `graph-ready` tag?
- Check 3: Did a deferred or review-required relation get promoted incorrectly in the registry?
- Check 4: Did the graph layer need regeneration?
- Check 5: Did `.\scripts\wiki.ps1 verify` or `.\scripts\wiki.ps1 graph-refresh` complete cleanly?
- Check 6: Does `docs/obsidian_graph_validation.md` report leakage or sparse-cluster issues?

## Commands

- refresh graph surfaces:
  - `.\scripts\wiki.ps1 graph-refresh`
  - this is the canonical regeneration path for builder-owned official graph surfaces only
- rebuild graph layer directly:
  - `python tools/build_obsidian_graph_layer.py --project-root .`
- verify repository:
  - `.\scripts\wiki.ps1 verify`
- canonical verify now rebuilds graph surfaces and checks that graph-generated outputs remain in the repository baseline

## Supporting Docs

- relation decisions:
  - `docs/obsidian_graph_relation_decisions.md`
- review queue:
  - `docs/obsidian_graph_review_queue.md`
- attach readiness:
  - `docs/obsidian_graph_attach_readiness.md`
- phase attach plan / execution log:
  - `docs/obsidian_graph_v2_attach_plan.md`
  - `docs/obsidian_graph_v2_execution_report.md`

## Git Contract

- `wiki/indexes/graph-home.md` is the official tracked operator hub and a committed generated artifact.
- `wiki/indexes/current-wiki-visualization.md` is the official tracked current snapshot and a committed generated artifact.
- `wiki/indexes/graph-cluster-*.md` are official tracked generated graph cluster hubs.
- `docs/obsidian_graph*.md` remain official tracked graph operations docs even when they are not generated.
- The manual tracked graph docs include planning, reference-alignment, and execution-record pages such as `docs/obsidian_graph_plan.md`, `docs/obsidian_graph_reference_alignment.md`, and `docs/obsidian_graph_v2_execution_report.md`.
- The committed generated graph docs are the builder-owned status surfaces such as validation, review queue, coverage matrix, relation decisions, attach readiness, and `docs/obsidian_graph_v1_2_plan.md`.
- Builder-touched concept notes and injected graph blocks inside selected regulation documents remain tracked notes, but they are outside the generated-surface freshness baseline for this contract.
- There is no separate graph-only local markdown output path under `docs/` or `wiki/indexes/`.
- Purely local inspection output should stay under already ignored locations such as `artifacts/` or private Obsidian workspace state.

## Operating Rules

- Add or revise relations in `taxonomy/regulatory_connectivity.yaml` first.
- Then rerun `.\scripts\wiki.ps1 graph-refresh`.
- Never add graph links manually to selected documents unless the registry is also updated.
- If a desired regulation note does not yet exist as a source-grounded `regulation_document`, defer it instead of creating a stub.
