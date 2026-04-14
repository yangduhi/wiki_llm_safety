---
record_layer: operations
id: operations-kmvss-round2d-comparable-evaluation
title: KMVSS Round 2D Comparable Evaluation
summary: Before and after comparison for KMVSS secondary umbrella pruning and review-lane promotion separation.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2d
  - evaluation
---

# KMVSS Round 2D Comparable Evaluation

- before_run: `20260414T011841Z__e42c6ca0`
- after_run: `20260414T042351Z__e42c6ca0`

## Overall Raw Before/After
- slice: `all`
- total_units: `4410 -> 4410`
- cross_phase: `648 -> 625` (`14.69% -> 14.17%`)
- other_or_review: `914 -> 912` (`20.73% -> 20.68%`)

## Article-Only Before/After
- slice: `articles`
- total_units: `1056 -> 1056`
- cross_phase: `152 -> 129` (`14.39% -> 12.22%`)
- other_or_review: `260 -> 258` (`24.62% -> 24.43%`)

## Attachment Regression Check
- slice: `attachments`
- total_units: `3354 -> 3354`
- cross_phase: `496 -> 496` (`14.79% -> 14.79%`)
- other_or_review: `654 -> 654` (`19.50% -> 19.50%`)

## Secondary Umbrella Slice
- slice: `secondary_umbrella`
- total_units: `52 -> 52`
- cross_phase: `28 -> 10` (`53.85% -> 19.23%`)
- other_or_review: `39 -> 31` (`75.00% -> 59.62%`)

## Review-Lane Status Transition Summary
- `xml_kmvss-kmvss_art_105_158`: lane `intentional_cross_phase -> stable_retain`, promotion `None -> stable_retain`
- `xml_kmvss-kmvss_art_108_162`: lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision`, promotion `None -> needs_policy_decision`
- `xml_kmvss-kmvss_art_108_163`: lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision`, promotion `None -> needs_policy_decision`
- `xml_kmvss-kmvss_art_113_188`: lane `intentional_other_or_review -> temporary_retain`, promotion `None -> temporary_retain`
- `xml_kmvss-kmvss_art_114_189`: lane `intentional_other_or_review -> stable_retain`, promotion `None -> stable_retain`
- `xml_kmvss-kmvss_art_18_028`: lane `mixed_or_ambiguous_keep_for_review -> mixed_keep_review`, promotion `None -> mixed_keep_review`
- `xml_kmvss-kmvss_art_18_029`: lane `mixed_or_ambiguous_keep_for_review -> mixed_keep_review`, promotion `None -> mixed_keep_review`
- `xml_kmvss-kmvss_art_23_035`: lane `umbrella_adjudication_candidate -> secondary_umbrella_keep_review`, promotion `None -> temporary_retain`
- `xml_kmvss-kmvss_art_28_042`: lane `intentional_other_or_review -> temporary_retain`, promotion `None -> temporary_retain`
- `xml_kmvss-kmvss_art_2_002`: lane `intentional_other_or_review -> stable_retain`, promotion `None -> stable_retain`
- `xml_kmvss-kmvss_art_32_046`: lane `intentional_other_or_review -> temporary_retain`, promotion `None -> temporary_retain`
- `xml_kmvss-kmvss_art_34_048`: lane `intentional_cross_phase -> stable_retain`, promotion `None -> stable_retain`
- `xml_kmvss-kmvss_art_38_055`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`
- `xml_kmvss-kmvss_art_39_057`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`
- `xml_kmvss-kmvss_art_40_059`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`
- `xml_kmvss-kmvss_art_45_068`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`
- `xml_kmvss-kmvss_art_4_007`: lane `umbrella_adjudication_candidate -> secondary_umbrella_keep_review`, promotion `None -> temporary_retain`
- `xml_kmvss-kmvss_art_6_009`: lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision`, promotion `None -> needs_policy_decision`
- `xml_kmvss-kmvss_art_79_115`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`
- `xml_kmvss-kmvss_art_87_128`: lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable`, promotion `None -> promotion_candidate`

## Same-Document Fixed Slice Comparison
- `xml_kmvss-kmvss_art_2_002` / 정의 / lane `intentional_other_or_review -> stable_retain` / promotion ` -> stable_retain` / cross `0 -> 0` / other `83 -> 83`
- `xml_kmvss-kmvss_art_34_048` / 창유리 등 / lane `intentional_cross_phase -> stable_retain` / promotion ` -> stable_retain` / cross `18 -> 18` / other `0 -> 0`
- `xml_kmvss-kmvss_art_114_189` / 기준적용의 특례 / lane `intentional_other_or_review -> stable_retain` / promotion ` -> stable_retain` / cross `0 -> 0` / other `13 -> 13`
- `xml_kmvss-kmvss_art_32_046` / 물품적재장치 / lane `intentional_other_or_review -> temporary_retain` / promotion ` -> temporary_retain` / cross `0 -> 0` / other `11 -> 11`
- `xml_kmvss-kmvss_art_105_158` / 창유리의 안전성 등 / lane `intentional_cross_phase -> stable_retain` / promotion ` -> stable_retain` / cross `10 -> 10` / other `0 -> 0`
- `xml_kmvss-kmvss_art_113_188` / 승차정원 및 최대적재량 / lane `intentional_other_or_review -> temporary_retain` / promotion ` -> temporary_retain` / cross `5 -> 5` / other `5 -> 5`
- `xml_kmvss-kmvss_art_28_042` / 입석 / lane `intentional_other_or_review -> temporary_retain` / promotion ` -> temporary_retain` / cross `5 -> 5` / other `5 -> 5`
- `xml_kmvss-kmvss_art_18_028` / 사이버보안 / lane `mixed_or_ambiguous_keep_for_review -> mixed_keep_review` / promotion ` -> mixed_keep_review` / cross `0 -> 0` / other `9 -> 9`
- `xml_kmvss-kmvss_art_18_029` / 소프트웨어 / lane `mixed_or_ambiguous_keep_for_review -> mixed_keep_review` / promotion ` -> mixed_keep_review` / cross `0 -> 0` / other `9 -> 9`
- `xml_kmvss-kmvss_art_4_007` / 길이ㆍ너비 및 높이 / lane `umbrella_adjudication_candidate -> secondary_umbrella_keep_review` / promotion ` -> temporary_retain` / cross `0 -> 0` / other `8 -> 10`
- `xml_kmvss-kmvss_art_6_009` / 차량총중량등 / lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision` / promotion ` -> needs_policy_decision` / cross `4 -> 4` / other `4 -> 4`
- `xml_kmvss-kmvss_art_108_162` / 에너지소비효율 / lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision` / promotion ` -> needs_policy_decision` / cross `3 -> 3` / other `3 -> 3`
- `xml_kmvss-kmvss_art_108_163` / 1회 충전 후 주행가능거리 / lane `umbrella_adjudication_candidate -> secondary_umbrella_needs_policy_decision` / promotion ` -> needs_policy_decision` / cross `3 -> 3` / other `3 -> 3`
- `xml_kmvss-kmvss_art_16_023` / 완충장치 / lane `umbrella_adjudication_candidate -> promotion_candidate` / promotion ` -> promotion_candidate` / cross `3 -> 3` / other `3 -> 3`
- `xml_kmvss-kmvss_art_38_055` / 주간주행등 / lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable` / promotion ` -> promotion_candidate` / cross `3 -> 0` / other `3 -> 0`
- `xml_kmvss-kmvss_art_38_056` / 코너링조명등 / lane `umbrella_adjudication_candidate -> promotion_candidate` / promotion ` -> promotion_candidate` / cross `3 -> 3` / other `3 -> 3`
- `xml_kmvss-kmvss_art_39_057` / 후퇴등 / lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable` / promotion ` -> promotion_candidate` / cross `3 -> 0` / other `3 -> 0`
- `xml_kmvss-kmvss_art_40_059` / 차폭등 / lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable` / promotion ` -> promotion_candidate` / cross `3 -> 0` / other `3 -> 0`
- `xml_kmvss-kmvss_art_45_068` / 후방추돌경고등 / lane `umbrella_adjudication_candidate -> secondary_umbrella_promotable` / promotion ` -> promotion_candidate` / cross `3 -> 0` / other `3 -> 0`
- `xml_kmvss-kmvss_art_53_076` / 경음기 / lane `umbrella_adjudication_candidate -> promotion_candidate` / promotion ` -> promotion_candidate` / cross `3 -> 3` / other `3 -> 3`

## Residual Decomposition
- stable_retain residual units: `124`
- temporary_retain residual units: `64`
- unresolved_residual units: `99`
- mixed_keep_review residual units: `18`

## Interpretation
- raw `other_or_review` is not used as a standalone fail metric
- secondary umbrella success is accepted when residual drops or promotion separation becomes materially clearer
- stable retain and temporary retain remain policy-grounded review states rather than hidden failure buckets