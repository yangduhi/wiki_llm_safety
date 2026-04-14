---
record_layer: operations
id: operations-reclassification-20-decision-table
title: Reclassification 20 Decision Table
summary: Boundary-case calibration table for sharpening pre/in/post phase decisions across 20 representative documents.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - pilot
  - classification
---

# Reclassification 20 Decision Table

document-level calibration은 entry classification용이며, canonical phase 안정화는 regulation_unit adjudication이 우선한다.

## Calibration Principles

- `FMVSS 302 = post_crash`
- 충돌 후 화재 안정성 문서군은 기본적으로 `post_crash`
- 충돌 후 고전압 전기 안정성, 전기충격 방지, 전해액 유출, 절연 유지 문서군은 기본적으로 `post_crash`
- 한국과 유럽의 유사 문서도 같은 원칙으로 `post_crash`
- `cross_phase`는 unit-level split으로도 단일 phase화가 어렵다고 입증된 경우에만 유지

## Selected 20

- `pre_crash`: FMVSS 111, FMVSS 126, UNECE R131, UNECE R152
- `in_crash`: FMVSS 208, FMVSS 206, FMVSS 214, FMVSS 226, UNECE R94, UNECE R95
- `post_crash`: FMVSS 302, FMVSS 305a, KMVSS_Art_112_186, UNECE R100, UNECE R144
- `cross_phase`: FMVSS 205, EU 2019/2144, KR umbrella performance rule
- `non_phase_admin`: EU 2018/858, 1958 Agreement

## Reserve Set

- UNECE R160
- UNECE R34
- KR certification rule
- KR implementation detail
- UNECE regulations index

## Acceptance Notes

- each calibration item records a selected phase
- each calibration item records a rejected alternative phase
- each calibration item records short rationale for the selected phase
- each calibration item records short rationale for the rejected alternative phase
