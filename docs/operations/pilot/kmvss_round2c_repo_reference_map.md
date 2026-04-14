---
record_layer: operations
id: operations-kmvss-round2c-repo-reference-map
title: KMVSS Round 2C Repo Reference Map
summary: Records the reference repositories and reusable operating patterns used for KMVSS round 2C.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2c
  - reference
---

# KMVSS Round 2C Repo Reference Map

## 확인한 핵심 파일

- 원격 `wiki_llm_safety`
  - `README.md`
  - `docs/operations/README.md`
  - `docs/operations/pilot/pilot_document_set.csv`
  - `docs/operations/pilot/pilot_mapping_results.jsonl`
  - `harness/scripts/*`
- 로컬 미러 `D:\vscode\4__wiki__obsidian__chatgpt_repo`
  - `docs/operations/README.md`
  - `docs/operations/notes/operating-rules.md`
  - `docs/operations/pilot/pilot_document_set.csv`
  - `docs/operations/pilot/pilot_mapping_results.jsonl`
  - `harness/scripts/*`

## 이번 라운드에 재사용할 패턴

- `docs/operations/notes | plans | dashboards | pilot`를 분리하는 운영 레이아웃
- pilot set CSV와 adjudication/result JSONL을 병행해 evidence와 verdict를 나누는 방식
- public CLI는 유지하고 repo-local helper script만 추가하는 방식
- verify gate를 harness script 모음으로 유지하는 방식
- policy note와 pilot artifact를 같은 `docs/operations/pilot/` 레이어에 두는 방식

## 적용하지 않을 패턴과 이유

- pilot 2파일만으로 끝내는 최소 구조
  - 현재 저장소는 round 1 / 2A / 2B 누적 의사결정과 trace가 있어서 triage, policy, comparable evaluation, fix log를 별도 문서로 남겨야 한다.
- reference 저장소의 의미 체계 재사용
  - `wiki_llm_safety`는 운영 패턴 참고용이고, KMVSS의 canonical phase/domain taxonomy는 현재 저장소 결정을 우선한다.
- review-lane 형식의 무비판적 복붙
  - 현재 저장소 trace 계약을 깨지 않기 위해 review-lane observability는 trace/audit artifact 확장으로만 추가한다.

## 적용 방식

- 현재 저장소의 round 1 / round 2A / round 2B 결정을 우선한다.
- `wiki_llm_safety`의 패턴은 운영 방식만 참고한다.
- helper script, pilot 문서, trace observability만 추가하는 최소 침습 방식을 유지한다.
- 브랜치는 `codex/local-sync-20260414`를 유지하고, `main`에는 직접 적용하지 않는다.
