---
record_layer: operations
id: operations-kmvss-round2c-fix-log
title: KMVSS Round 2C Fix Log
summary: Execution log for KMVSS umbrella article adjudication and intentional review-lane separation.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2c
  - fix-log
---

# KMVSS Round 2C Fix Log

## Commands

- `python -m pytest -q`
- targeted replay on fixed 15-doc article set in a temporary project
- `python -m wiki_obsidian.cli run --collection xml_kmvss`
  - final round2c run: `20260414T011841Z__e42c6ca0`
- `python harness/scripts/kmvss_round2c_triage.py --project-root ... --run-id 20260414T011841Z__e42c6ca0`
- `python harness/scripts/kmvss_round2c_comparable_eval.py --project-root ... --before-run 20260413T144219Z__e42c6ca0 --after-run 20260414T011841Z__e42c6ca0`
- standalone verify after docs/index refresh:
  - `python -m wiki_obsidian.cli verify`
  - final verify run: `20260414T014141Z__a12dd3a7`

## Targeted Replay Outcome

- fixed 15-doc set summary:
  - umbrella candidates: `33` units
  - `cross_phase: 0 / 33`
  - `other_or_review: 1 / 33`
- intentional cross retain docs stayed `100% cross_phase`
- intentional other retain docs stayed review-lane 중심
- mixed docs stayed review-lane 중심

## Final Before/After Snapshot

- baseline run: `20260413T144219Z__e42c6ca0`
- final run: `20260414T011841Z__e42c6ca0`
- article-only:
  - `cross_phase: 183 -> 152` (`17.33% -> 14.39%`)
  - `other_or_review: 253 -> 260` (`23.96% -> 24.62%`)
- attachment-only:
  - `cross_phase: 496 -> 496` (`14.79% -> 14.79%`)
  - `other_or_review: 654 -> 654` (`19.50% -> 19.50%`)
- umbrella candidate slice:
  - `cross_phase: 28 -> 0` (`84.85% -> 0.00%`)
  - `other_or_review: 14 -> 1` (`42.42% -> 3.03%`)

## Regression Gates

- representative: maintained
- holdout: `12 / 12`
- negative control: `10 / 10`
- attachment regression: within allowed band
- final verify: `passed`

## Notes

- round 2C improved umbrella candidates strongly without touching attachment parser logic
- intentional retain documents stayed stable and became explicitly observable through trace fields
- article-only `other_or_review` rose slightly because intentional retain policy was made explicit rather than silently forcing canonical mapping
