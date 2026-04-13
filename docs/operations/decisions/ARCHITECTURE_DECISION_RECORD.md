---
record_layer: operations
id: operations-adr-regulatory-ontology-v1
title: Regulatory Ontology Pilot ADR
summary: Fixes the first-stage design decision to use a faceted ontology for regulatory classification and to treat the 16 image buckets as an in-crash browse taxonomy only.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - architecture
  - adr
  - classification
---

# Regulatory Ontology Pilot ADR

## Decision
- 전역 분류는 단일 taxonomy가 아니라 faceted ontology로 설계한다.
- 최상위 축은 최소 `regulatory_layer`, `phase`, `functional_domain`, `topic/object`를 가진다.
- `phase` 허용값은 `pre_crash`, `in_crash`, `post_crash`, `cross_phase`, `non_phase_admin`로 고정한다.
- 이미지 기반 16개 항목은 전역 루트가 아니라 `in_crash` browse taxonomy로만 사용한다.
- 기존 taxonomy는 즉시 삭제하지 않고 `legacy_crosswalk`로만 유지한다.

## Why
- FMVSS 205, 305/305a처럼 하나의 문서 안에 visibility, ejection mitigation, 정상 주행, 충돌 중·후 전기적 위험이 함께 들어가는 경우가 있어 단일 phase 또는 단일 component taxonomy로는 안정적으로 설명되지 않는다.
- EU 2018/858 같은 승인·시장감시 프레임 문서는 `pre/in/post` 어느 하나에도 깔끔하게 들어가지 않으므로 `non_phase_admin`이 필요하다.
- 이미지 16개 bucket은 충돌 중 탐색에는 강하지만, AEB, ESC, eCall, EDR, type approval framework를 전역적으로 설명하기에는 부족하다.

## Locked Outcomes
- `AEB for pedestrian`는 `phase = pre_crash`, `functional_domain = crash_avoidance_and_vehicle_control`이다.
- `FMVSS 205`는 `phase = cross_phase` 후보이며, `functional_domain = visibility_glazing_and_driver_information`으로 본다.
- `EU 2018/858`은 `regulatory_layer = framework_admin`, `phase = non_phase_admin`으로 본다.
- `Pedestrian Protection`은 전역 root가 아니라 `in_crash` browse taxonomy의 one bucket이거나, canonical ontology에서는 `topic/object` 수준에서 다룬다.
- 이미지 16개는 canonical source of truth가 아니라 browse layer에 위치한다.

## Non-Goals For This Phase
- production runtime overwrite
- full reindex
- live wiki classification 교체
- legacy taxonomy physical delete
- image 16개를 global root로 승격

## Go/No-Go Gate
- 이번 단계의 산출물은 설계 패키지와 파일럿 검증이다.
- 파일럿 매핑과 gold query 검증이 끝난 뒤에만 2차 production migration 여부를 결정한다.
