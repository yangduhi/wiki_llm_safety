---
record_layer: operations
id: operations-kmvss-full-before-after-phase-distribution
title: KMVSS Full Before After Phase Distribution
summary: Quantitative before/after comparison of KMVSS phase distribution after improving classification consumption logic.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - distribution
---

# KMVSS Full Before After Phase Distribution

## Runs

- before: `20260413T071241Z__e42c6ca0`
- after: `20260413T105702Z__e42c6ca0`

## Counts

- before phase counts:
  - `cross_phase`: 3852
  - `post_crash`: 32
  - `pre_crash`: 2
- after phase counts:
  - `cross_phase`: 2363
  - `in_crash`: 817
  - `non_phase_admin`: 150
  - `post_crash`: 354
  - `pre_crash`: 1438

## Threshold Check

- `cross_phase` reduction: `38.66%`
- threshold: `>= 20%`
- result: pass

## Interpretation

- the largest gain came from converting title-rich KMVSS articles out of `cross_phase`
- `pre_crash`, `in_crash`, and `post_crash` now all appear at meaningful scale
