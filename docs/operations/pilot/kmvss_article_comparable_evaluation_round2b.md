---
record_layer: operations
id: operations-kmvss-article-comparable-evaluation-round2b
title: KMVSS Article Comparable Evaluation Round 2B
summary: Before and after comparison for article-only KMVSS residual reduction round 2B.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - article
  - evaluation
---

# KMVSS Article Comparable Evaluation Round 2B

- before_run: `20260413T130606Z__e42c6ca0`
- after_run: `20260413T144219Z__e42c6ca0`

## Overall Raw Before/After
- slice: `all`
- total_units: `4410 -> 4410`
- cross_phase: `756 -> 679` (`17.14% -> 15.40%`)
- other_or_review: `909 -> 907` (`20.61% -> 20.57%`)

## Article-Only Before/After
- slice: `articles`
- total_units: `1056 -> 1056`
- cross_phase: `258 -> 183` (`24.43% -> 17.33%`)
- other_or_review: `290 -> 253` (`27.46% -> 23.96%`)

## Attachment Regression Check
- slice: `attachments`
- total_units: `3354 -> 3354`
- cross_phase: `498 -> 496` (`14.85% -> 14.79%`)
- other_or_review: `619 -> 654` (`18.46% -> 19.50%`)

## Fixed Article Residual Slice
- slice: `target_docs`
- total_units: `195 -> 195`
- cross_phase: `71 -> 29` (`36.41% -> 14.87%`)
- other_or_review: `120 -> 91` (`61.54% -> 46.67%`)

## Same-Document Top20 Comparison
- `xml_kmvss-kmvss_art_2_002` / 정의 / bucket=`definitions` / cross `1 -> 1` / other `55 -> 62`
- `xml_kmvss-kmvss_art_34_048` / 창유리 등 / bucket=`glazing_cross_phase_intentional` / cross `18 -> 18` / other `0 -> 0`
- `xml_kmvss-kmvss_art_18_028` / 사이버보안 / bucket=`software_cyber` / cross `5 -> 0` / other `9 -> 9`
- `xml_kmvss-kmvss_art_114_189` / 기준적용의 특례 / bucket=`special_exceptions` / cross `0 -> 0` / other `12 -> 13`
- `xml_kmvss-kmvss_art_58_085` / 경광등 및 사이렌 / bucket=`body_visibility_signaling` / cross `6 -> 0` / other `6 -> 0`
- `xml_kmvss-kmvss_art_32_046` / 물품적재장치 / bucket=`umbrella_titles_with_weak_unit_text` / cross `0 -> 0` / other `11 -> 11`
- `xml_kmvss-kmvss_art_47_070` / 그 밖의 등화의 제한 / bucket=`body_visibility_signaling` / cross `5 -> 0` / other `6 -> 0`
- `xml_kmvss-kmvss_art_50_073` / 간접시계장치 / bucket=`body_visibility_signaling` / cross `6 -> 0` / other `5 -> 0`
- `xml_kmvss-kmvss_art_105_158` / 창유리의 안전성 등 / bucket=`glazing_cross_phase_intentional` / cross `10 -> 10` / other `0 -> 0`
- `xml_kmvss-kmvss_art_113_188` / 승차정원 및 최대적재량 / bucket=`umbrella_titles_with_weak_unit_text` / cross `5 -> 5` / other `5 -> 5`
- `xml_kmvss-kmvss_art_28_042` / 입석 / bucket=`umbrella_titles_with_weak_unit_text` / cross `5 -> 5` / other `5 -> 5`
- `xml_kmvss-kmvss_art_40_060` / 끝단표시등 / bucket=`body_visibility_signaling` / cross `5 -> 0` / other `5 -> 0`
- `xml_kmvss-kmvss_art_4_007` / 길이ㆍ너비 및 높이 / bucket=`umbrella_titles_with_weak_unit_text` / cross `0 -> 0` / other `10 -> 8`
- `xml_kmvss-kmvss_art_63_092` / 원동기 출력 / bucket=`powertrain_running_gear` / cross `5 -> 0` / other `5 -> 0`
- `xml_kmvss-kmvss_art_77_111` / 후미등 / bucket=`body_visibility_signaling` / cross `5 -> 0` / other `5 -> 0`
- `xml_kmvss-kmvss_art_10_013` / 접지부분 및 접지압력 / bucket=`powertrain_running_gear` / cross `5 -> 0` / other `4 -> 0`
- `xml_kmvss-kmvss_art_18_029` / 소프트웨어 / bucket=`software_cyber` / cross `0 -> 0` / other `9 -> 7`
- `xml_kmvss-kmvss_art_20_032` / 견인장치 및 연결장치 / bucket=`umbrella_titles_with_weak_unit_text` / cross `5 -> 4` / other `4 -> 3`
- `xml_kmvss-kmvss_art_88_129` / 계기판넬 / bucket=`umbrella_titles_with_weak_unit_text` / cross `6 -> 6` / other `3 -> 3`
- `xml_kmvss-kmvss_art_106_159` / 원동기 출력 / bucket=`powertrain_running_gear` / cross `5 -> 0` / other `3 -> 0`

## Exemplar Trace Diff
### xml_kmvss-kmvss_art_34_048
- subject: 창유리 등
- before_units: 18 / after_units: 18
- before_cross: 18
- after_cross: 18
- before_other: 0
- after_other: 0
- before_fallback_top3: [('<none>', 18)]
- after_fallback_top3: [('<none>', 18)]

### xml_kmvss-kmvss_art_105_158
- subject: 창유리의 안전성 등
- before_units: 10 / after_units: 10
- before_cross: 10
- after_cross: 10
- before_other: 0
- after_other: 0
- before_fallback_top3: [('<none>', 10)]
- after_fallback_top3: [('<none>', 10)]

### xml_kmvss-kmvss_art_50_073
- subject: 간접시계장치
- before_units: 8 / after_units: 8
- before_cross: 6
- after_cross: 0
- before_other: 5
- after_other: 0
- before_fallback_top3: [('no_phase_signal;low_domain_signal', 5), ('<none>', 2), ('no_phase_signal', 1)]
- after_fallback_top3: [('<none>', 8)]

### xml_kmvss-kmvss_art_58_085
- subject: 경광등 및 사이렌
- before_units: 7 / after_units: 7
- before_cross: 6
- after_cross: 0
- before_other: 6
- after_other: 0
- before_fallback_top3: [('no_phase_signal;low_domain_signal', 6), ('<none>', 1)]
- after_fallback_top3: [('<none>', 7)]

### xml_kmvss-kmvss_art_40_060
- subject: 끝단표시등
- before_units: 6 / after_units: 6
- before_cross: 5
- after_cross: 0
- before_other: 5
- after_other: 0
- before_fallback_top3: [('no_phase_signal;low_domain_signal', 5), ('<none>', 1)]
- after_fallback_top3: [('<none>', 6)]

### xml_kmvss-kmvss_art_47_070
- subject: 그 밖의 등화의 제한
- before_units: 8 / after_units: 8
- before_cross: 5
- after_cross: 0
- before_other: 6
- after_other: 0
- before_fallback_top3: [('no_phase_signal;low_domain_signal', 5), ('<none>', 2), ('low_domain_signal', 1)]
- after_fallback_top3: [('<none>', 8)]

### xml_kmvss-kmvss_art_77_111
- subject: 후미등
- before_units: 5 / after_units: 5
- before_cross: 5
- after_cross: 0
- before_other: 5
- after_other: 0
- before_fallback_top3: [('no_phase_signal;low_domain_signal', 5)]
- after_fallback_top3: [('<none>', 5)]

### xml_kmvss-kmvss_art_2_002
- subject: 정의
- before_units: 83 / after_units: 83
- before_cross: 1
- after_cross: 1
- before_other: 55
- after_other: 62
- before_fallback_top3: [('low_domain_signal', 55), ('<none>', 28)]
- after_fallback_top3: [('<none>', 60), ('low_domain_signal', 22), ('article_inherited_context', 1)]
