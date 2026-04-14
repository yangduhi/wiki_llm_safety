---
record_layer: operations
id: operations-kmvss-article-taxonomy-policy-round2b
title: KMVSS Article Taxonomy Policy Round 2B
summary: Article-family taxonomy policy used for KMVSS residual reduction round 2B.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - article
  - taxonomy
---

# KMVSS Article Taxonomy Policy Round 2B

## Intentionally Retained Cross-Phase

- `창유리 등`
- `창유리의 안전성 등`

These remain `cross_phase` by policy because the document-level scope spans visibility and crash-retention concerns together.

## Visibility / Signaling Family

- `간접시계장치`
- `경광등 및 사이렌`
- `끝단표시등`
- `후미등`
- `그 밖의 등화의 제한`
- `번호등`
- `옆면표시등`

Policy:

- default `phase = pre_crash`
- default `functional_domain = visibility_glazing_and_driver_information`

## Powertrain / Running Gear Family

- `원동기 및 동력전달장치`
- `원동기 출력`
- `주행장치`
- `접지부분 및 접지압력`
- `최대안전경사각도`
- `도난방지장치`

Policy:

- default `phase = pre_crash`
- default `functional_domain = crash_avoidance_and_vehicle_control`
- if the clause is purely definitional or spec-only, `other_or_review` is allowed

## Definitions and Special Exceptions

- `정의`
- `기준적용의 특례`

Policy:

- default `phase = non_phase_admin`
- default `functional_domain = other_or_review`
- do not force a technical domain only to improve metrics

## Software / Cyber

- `소프트웨어`
- `사이버보안`

Policy:

- default `phase = non_phase_admin`
- default `functional_domain = other_or_review`
- allow `pre_crash + crash_avoidance_and_vehicle_control` only when the local body has strong control or safe-state language such as rollback, safe state, or drive-function deactivation

## Umbrella Titles With Weak Unit Text

- `물품적재장치`
- `승차정원 및 최대적재량`
- `입석`
- `견인장치 및 연결장치`
- `계기판넬`

Policy:

- use weak title priors only when the local clause is short or governance-heavy
- retain `other_or_review` when the clause is still too abstract for a clean canonical mapping
