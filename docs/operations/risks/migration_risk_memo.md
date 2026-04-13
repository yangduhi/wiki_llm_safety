---
record_layer: operations
id: operations-migration-risk-memo-v1
title: Migration Risk Memo
summary: Summarizes the risks of moving directly to production migration before the regulatory ontology pilot is validated.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - risks
  - migration
---

# Migration Risk Memo

## Major Risks
- `phase`를 문서 전체에 하나만 강제하면 FMVSS 205, 305/305a 같은 문서에서 오분류가 대량 복제될 수 있다.
- 이미지 16개를 global root로 사용하면 AEB, ESC, eCall, EDR, approval framework를 안정적으로 설명하지 못한다.
- KR authoritative source URL이 아직 완전히 고정되지 않은 항목이 있어, bulk ingestion 전에 source authority를 먼저 정리해야 한다.
- retrieval weighting을 검증하지 않은 채 reindex를 하면 `AEB pedestrian` 같은 질의가 passive pedestrian protection 쪽으로 틀어질 위험이 있다.
- legacy taxonomy를 너무 빨리 삭제하면 회귀 비교와 설명 가능성이 떨어진다.

## Go / No-Go
- 현재 단계의 권고는 `NO-GO for production migration`.
- 이유:
  - source authority inventory에 KR canonical URL pending 항목이 남아 있다.
  - pilot mapping은 아직 문서 단위 manual-grade 결과일 뿐 unit-level 확정이 아니다.
  - gold query는 설계되었지만 실제 retrieval scoring 실험은 다음 단계다.

## Go Criteria For Phase 2
- KR authoritative source canonical URL이 확정될 것
- pilot mapping 12~20건에서 `phase`, `functional_domain`, `topic`의 충돌 규칙이 안정될 것
- `gold_queries.yaml` 기준 수동 점검 또는 shadow retrieval 결과가 accept 가능한 수준일 것
- legacy crosswalk를 기준으로 production migration diff를 설명할 수 있을 것
