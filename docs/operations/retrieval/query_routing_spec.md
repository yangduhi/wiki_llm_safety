---
record_layer: operations
id: operations-query-routing-spec-v1
title: Query Routing Spec
summary: Defines the retrieval routing order for the regulatory ontology pilot before any production migration.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - retrieval
  - graphrag
---

# Query Routing Spec

## Routing Order
1. `jurisdiction`
2. `phase`
3. `functional_domain`
4. `primary_topic` and aliases
5. regulation number or citation
6. `in_crash` browse bucket

## Intent Rules
- 문서 번호나 조문 번호가 있는 질의는 citation-first로 본다.
- phase가 직접 언급되면 해당 phase를 강하게 가중한다.
- `AEB`, `FCW`, `ESC`, `lane` 관련 키워드는 `pre_crash + crash_avoidance_and_vehicle_control`을 우선 검토한다.
- `door retention`, `occupant crash protection`, `side impact`, `rollover`는 `in_crash` 중심으로 본다.
- `eCall`, `EDR`, rescue, post-crash response는 `post_crash` 중심으로 본다.
- type approval, framework, market surveillance, recall은 `non_phase_admin`을 우선 검토한다.

## Browse Taxonomy Usage
- 이미지 16개 bucket은 `in_crash` browse layer에서만 사용한다.
- browse bucket은 query expansion의 마지막 단계에서만 사용한다.
- canonical ranking은 browse bucket보다 `phase`와 `functional_domain`이 우선한다.

## Failure Conditions
- `AEB pedestrian`가 passive pedestrian protection 문서만 과도하게 반환되면 실패
- `EU 2018/858`가 억지로 `pre_crash`, `in_crash`, `post_crash` 중 하나에만 들어가면 실패
- `FMVSS 205`가 visibility 축 없이 단일 `in_crash` 문서로만 취급되면 실패
