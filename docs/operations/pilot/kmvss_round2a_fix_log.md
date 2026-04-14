---
record_layer: operations
id: operations-kmvss-round2a-fix-log
title: KMVSS Round 2A Fix Log
summary: Execution log for attachment-aware KMVSS residual reduction round 2A.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - attachment
  - fix-log
---

# KMVSS Round 2A Fix Log

## Commands

- `python -m pytest -q`
- targeted replay on exemplar/top attachment subset in a temporary project created from `tests.test_pipeline._write_common_project_layout`
- `python -m wiki_obsidian.cli run --collection xml_kmvss`
  - intermediate runs:
    - `20260413T122121Z__e42c6ca0`
    - `20260413T123723Z__e42c6ca0`
    - final run: `20260413T130606Z__e42c6ca0`
- `python harness/scripts/kmvss_attachment_residual_audit.py --project-root ... --run-id 20260413T105702Z__e42c6ca0`
- `python harness/scripts/kmvss_attachment_comparable_eval.py --project-root ... --before-run 20260413T105702Z__e42c6ca0 --after-run 20260413T130606Z__e42c6ca0`
- `python -m wiki_obsidian.cli verify`
  - final verify run: `20260413T132123Z__a12dd3a7`

## Targeted Replay Outcome

- subset documents:
  - `KMVSS_Att_0006_066`
  - `KMVSS_Att_0001_001`
  - `KMVSS_Att_0024_125`
  - plus 7 additional top residual attachments
- targeted replay attachment totals:
  - `attachment_cross_phase = 0`
  - `attachment_other_or_review = 118`
- exemplar observations:
  - `KMVSS_Att_0006_066`: grouped into `5` units and no residual `cross_phase`
  - `KMVSS_Att_0001_001`: `cross_phase` removed, `other_or_review` intentionally retained for marking/spec rows
  - `KMVSS_Att_0024_125`: `cross_phase` removed, `other_or_review` retained as EMC policy

## Final Before/After Snapshot

- baseline run: `20260413T105702Z__e42c6ca0`
- final run: `20260413T130606Z__e42c6ca0`
- full KMVSS raw:
  - `cross_phase: 2363 -> 756` (`46.13% -> 17.14%`)
  - `other_or_review: 2614 -> 909` (`51.03% -> 20.61%`)
- attachment-only:
  - `cross_phase: 2237 -> 498` (`55.02% -> 14.85%`)
  - `other_or_review: 2148 -> 619` (`52.83% -> 18.46%`)
- article-only:
  - `cross_phase: 126 -> 258` (`11.93% -> 24.43%`)
  - `other_or_review: 466 -> 290` (`44.13% -> 27.46%`)

## Verification Status

- `pytest`: `17 passed`
- final repository verify: `passed`
- verify report path:
  - `artifacts/reports/runs/20260413T132123Z__a12dd3a7/verify_report.json`

## Notes

- attachment goals were achieved strongly
- article-only `other_or_review` improved, but article-only `cross_phase` remained above the baseline due the removal of the old degenerate `문` signal and incomplete replacement priors
- this remaining article-side drift is documented as a residual risk for the next round
