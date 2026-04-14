---
record_layer: operations
id: operations-kmvss-round2d-fix-log
title: KMVSS Round 2D Fix Log
summary: Execution log for KMVSS secondary umbrella pruning and review-lane promotion criteria.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2d
  - fix-log
---

# KMVSS Round 2D Fix Log

## Start-of-Run Verification

- current branch:
  - `git branch --show-current` -> `codex/local-sync-20260414`
- upstream / tracking:
  - `git branch -vv` -> current branch tracks `origin/main` and is `behind 2`
- working tree:
  - `git status --short` -> `dirty`
  - note: repository already contains broad unrelated wiki / dashboard / graph changes; round 2D edits are intentionally limited to reviewable KMVSS files
- baseline run artifacts:
  - `artifacts/normalized/runs/20260414T011841Z__e42c6ca0/classification_trace.jsonl` exists
  - `artifacts/normalized/runs/20260414T011841Z__e42c6ca0/units.jsonl` exists
  - `artifacts/normalized/runs/20260414T011841Z__e42c6ca0/documents.jsonl` exists
  - `artifacts/reports/runs/20260414T015931Z__a12dd3a7/verify_report.json` exists
- baseline docs:
  - `kmvss_round2c_repo_reference_map.md` exists
  - `kmvss_round2c_review_lane_policy.md` exists
  - `kmvss_round2c_residual_triage.md` exists
  - `kmvss_round2c_comparable_evaluation.md` exists
  - `kmvss_round2c_fix_log.md` exists

## Commands

- `git branch --show-current`
- `git branch -vv`
- `git status --short`
- `python harness/scripts/kmvss_round2d_secondary_umbrella_audit.py --project-root . --run-id 20260414T011841Z__e42c6ca0`
- targeted replay on fixed 35-doc article slice in a temporary project using `normalize_collection(...)`
- `python -m pytest tests/test_pipeline.py -q -k "kmvss"`
- `python -m wiki_obsidian.cli run --collection xml_kmvss`
  - intermediate round2d run: `20260414T034237Z__e42c6ca0`
  - final round2d run: `20260414T042351Z__e42c6ca0`
- `python -m wiki_obsidian.cli verify`
  - pre-final standalone verify: `20260414T040412Z__a12dd3a7`
  - final standalone verify: `20260414T044358Z__a12dd3a7`
- `python harness/scripts/kmvss_round2d_comparable_eval.py --project-root . --before-run 20260414T011841Z__e42c6ca0 --after-run 20260414T042351Z__e42c6ca0`
- `python -m pytest -q`

## Targeted Replay Outcome

- fixed 35-doc slice summary:
  - article units: `371`
  - article `cross_phase: 48 / 371`
  - article `other_or_review: 166 / 371`
  - secondary umbrella units: `52`
  - secondary umbrella `cross_phase: 10 / 52`
  - secondary umbrella `other_or_review: 29 / 52`
- key promotion candidates:
  - `주간주행등`: `cross 0`, `other 0`
  - `후방추돌경고등`: `cross 0`, `other 0`
  - `가속제어장치`: `cross 0`, `other 0`
- key retain lanes:
  - `정의`: `stable_retain`
  - `에너지소비효율`: `secondary_umbrella_needs_policy_decision`

## Final Before/After Snapshot

- baseline run: `20260414T011841Z__e42c6ca0`
- final run: `20260414T042351Z__e42c6ca0`
- overall raw:
  - `cross_phase: 648 -> 625` (`14.69% -> 14.17%`)
  - `other_or_review: 914 -> 912` (`20.73% -> 20.68%`)
- article-only:
  - `cross_phase: 152 -> 129` (`14.39% -> 12.22%`)
  - `other_or_review: 260 -> 258` (`24.62% -> 24.43%`)
- attachment-only:
  - `cross_phase: 496 -> 496` (`14.79% -> 14.79%`)
  - `other_or_review: 654 -> 654` (`19.50% -> 19.50%`)
- secondary umbrella slice:
  - `cross_phase: 28 -> 10` (`53.85% -> 19.23%`)
  - `other_or_review: 39 -> 31` (`75.00% -> 59.62%`)

## Regression Gates

- representative:
  - core representative anchors remained stable
  - `KMVSS_Art_15_020` remains in `crash_avoidance_and_vehicle_control`; document phase is now `pre_crash`, which is consistent with the weak-prior assumption and does not indicate a regression
- holdout: `12 / 12`
- negative control: `10 / 10`
- attachment regression:
  - `cross_phase` change: `0.00 percentage points`
  - `other_or_review` change: `0.00 percentage points`
- final verify:
  - standalone verify `20260414T044358Z__a12dd3a7` -> `passed`
- full test suite:
  - `27 passed`

## Notes

- round 2D keeps attachment parser/unitization unchanged
- round 2D focuses on secondary umbrella pruning and review-lane promotion observability
- raw `other_or_review` was interpreted together with `stable_retain / temporary_retain / unresolved_residual` decomposition rather than as a standalone failure metric
