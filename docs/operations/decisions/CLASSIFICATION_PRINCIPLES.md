---
record_layer: operations
id: operations-classification-principles-v1
title: Classification Principles
summary: Defines the canonical classification principles for the regulatory ontology pilot, including top-level facets, phase rules, and the role of the image-based in-crash browse buckets.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - classification
  - ontology
---

# Classification Principles

## Canonical Facets
- `regulatory_layer`
- `phase`
- `functional_domain`
- `topic/object`

## Phase Rules
- `pre_crash`: sensing, warning, intervention, or control before collision
- `in_crash`: impact, occupant restraint, structural retention, ejection mitigation, or crash test logic
- `post_crash`: eCall, EDR, rescue, post-crash response, post-crash data capture
- `cross_phase`: documents that materially span multiple phases
- `non_phase_admin`: approval, conformity, market surveillance, recall, and other administrative framework material

## Functional Domain Rules
- `crash_avoidance_and_vehicle_control`: AEB, FCW, ESC, lane support, collision avoidance
- `occupant_protection_and_restraints`: occupant impact, restraint performance, seat belt logic
- `vru_protection`: pedestrian and other vulnerable road user passive protection
- `visibility_glazing_and_driver_information`: glazing, visibility, driver information, display context
- `structural_integrity_retention_and_egress`: door retention, egress, structural retention, anti-ejection logic
- `fire_electrical_and_energy_storage_safety`: EV electrical safety, battery, electrical isolation, fire risk
- `post_crash_response_and_data`: eCall, EDR, rescue and post-crash response systems
- `interior_materials_and_fire`: interior flammability and interior materials
- `child_occupant_protection`: CRS and child occupant protection topics
- `other_or_review`: unresolved or out-of-band cases

## Browse Taxonomy Rule
- 이미지 기반 16개 항목은 `in_crash` browse taxonomy이다.
- browse taxonomy는 실무 탐색을 돕기 위한 보조 구조이며, canonical ontology의 최상위 루트가 아니다.
- canonical mapping은 image bucket이 없어도 성립해야 한다.

## Representative Decisions
- `AEB pedestrian`는 passive pedestrian protection 문서가 아니라 `pre_crash + crash_avoidance_and_vehicle_control`로 간다.
- `FMVSS 206`는 `in_crash + structural_integrity_retention_and_egress`가 우선이다.
- `FMVSS 302`는 `interior_materials_and_fire`가 우선이며, phase는 `post_crash` 또는 `cross_phase` 후보를 열어 둔다.
- `FMVSS 305/305a`는 정상 운행과 충돌 중·후를 함께 다루므로 `cross_phase`를 기본 후보로 둔다.

## Legacy Handling
- 기존 taxonomy / concept는 운영 루트가 아니다.
- legacy taxonomy는 `legacy_crosswalk`로만 유지하고 canonical 설계 판단의 보조 근거로만 쓴다.
