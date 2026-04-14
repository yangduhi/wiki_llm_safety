---
record_layer: operations
id: operations-kmvss-round2b-fix-log
title: KMVSS Round 2B Fix Log
summary: Execution log for article-only residual reduction round 2B.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - article
  - fix-log
---

# KMVSS Round 2B Fix Log

## Commands

- `python -m pytest -q`
- targeted replay on fixed 14-doc article set in a temporary project
- `python -m wiki_obsidian.cli run --collection xml_kmvss`
  - final round2b run: `20260413T144219Z__e42c6ca0`
- `python harness/scripts/kmvss_article_residual_audit.py --project-root ... --run-id 20260413T130606Z__e42c6ca0`
- `python harness/scripts/kmvss_article_comparable_eval.py --project-root ... --before-run 20260413T130606Z__e42c6ca0 --after-run 20260413T144219Z__e42c6ca0`
- final verify status is taken from the round2b run verify payload:
  - `artifacts/reports/runs/20260413T144219Z__e42c6ca0/verify_report.json`

## Targeted Replay Outcome

- fixed article set:
  - `창유리 등`
  - `창유리의 안전성 등`
  - `간접시계장치`
  - `경광등 및 사이렌`
  - `끝단표시등`
  - `그 밖의 등화의 제한`
  - `후미등`
  - `정의`
  - `기준적용의 특례`
  - `사이버보안`
  - `소프트웨어`
  - `원동기 및 동력전달장치`
  - `원동기 출력`
  - `주행장치`
- targeted replay article totals:
  - `cross_phase = 29 / 195` (`14.87%`)
  - `other_or_review = 93 / 195` (`47.69%`)

## Final Before/After Snapshot

- baseline run: `20260413T130606Z__e42c6ca0`
- final run: `20260413T144219Z__e42c6ca0`
- article-only:
  - `cross_phase: 258 -> 183` (`24.43% -> 17.33%`)
  - `other_or_review: 290 -> 253` (`27.46% -> 23.96%`)
- attachment-only regression check:
  - `cross_phase: 498 -> 496` (`14.85% -> 14.79%`)
  - `other_or_review: 619 -> 654` (`18.46% -> 19.50%`)
- holdout and controls:
  - holdout: `12/12`
  - negative control: `10/10`

## Notes

- article-only `cross_phase` hit the requested threshold `<= 18%`
- article-only `other_or_review` also improved further
- attachment-only metrics stayed within the allowed regression band
- remaining article residuals are concentrated in:
  - intentionally retained glazing docs
  - umbrella titles with weak local text
  - `정의` and `기준적용의 특례`
  - software/cyber governance docs
