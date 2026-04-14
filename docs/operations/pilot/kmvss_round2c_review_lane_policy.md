---
record_layer: operations
id: operations-kmvss-round2c-review-lane-policy
title: KMVSS Round 2C Review Lane Policy
summary: Defines intentional retain criteria and umbrella adjudication targets for KMVSS round 2C.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2c
  - policy
---

# KMVSS Round 2C Review Lane Policy

## Intentional Cross Phase

Intentional retain으로 인정하는 경우:

- 문서 수준에서 둘 이상의 canonical phase 요구가 실제로 공존한다.
- unit-level local text를 더 내려도 단일 phase로 안전하게 접히지 않는다.
- 현재 KMVSS에서는 아래만 이 lane에 둔다.
  - `창유리 등`
  - `창유리의 안전성 등`

## Intentional Other Or Review

Intentional retain으로 인정하는 경우:

- canonical domain에 억지로 매핑하는 것이 더 위험하다.
- 정의, 특례, 정원, 입석, abstract structural scope가 중심이다.
- 현재 KMVSS에서는 아래를 이 lane에 둔다.
  - `정의`
  - `기준적용의 특례`
  - `물품적재장치`
  - `입석`
  - `승차정원 및 최대적재량`

## Mixed Or Ambiguous Keep For Review

이 lane은 technical/admin 혼합 조항용이다.

- local text가 기술적 제어와 행정적 요구를 함께 가진다.
- 더 밀면 canonical 분류가 오히려 불안정해질 수 있다.
- 현재 KMVSS에서는 아래를 둔다.
  - `사이버보안`
  - `소프트웨어`

## Umbrella Adjudication Candidate

계속 더 분류해야 하는 경우:

- 제목은 umbrella지만 local text와 short-clause inheritance로 canonical phase/domain에 더 안전하게 내릴 수 있다.
- 현재 KMVSS에서는 아래를 umbrella adjudication 대상으로 둔다.
  - `계기판넬`
  - `견인장치 및 연결장치`
  - `가스운송장치`
  - `배기관`
  - `좌석등받이`
  - `접이식좌석`

## 운영 원칙

- review lane은 분류 실패 은닉이 아니다.
- intentional retain은 반드시 근거가 있어야 한다.
- taxonomy를 바꾸지 않고도 설명 가능한 경우만 intentional retain으로 남긴다.
- umbrella adjudication 대상은 weak prior, phrase normalization, parent inheritance, selector tuning으로 먼저 해결한다.
