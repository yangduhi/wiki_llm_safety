---
record_layer: knowledge
id: browse-index-approval-governance
note_type: browse_index
title: Approval and Governance Hub
summary: Browse hub for non_phase_admin and administrative framework material.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
aliases: []
browse_axis: approval_and_governance
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: 20260414T073313Z__a12dd3a7
confidence: medium
---

# Approval and Governance Hub

## Snapshot
- generated_at: 2026-04-14
- browse_axis: approval_and_governance
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- browse_role: supporting
- canonical_axis: non_phase_admin + administrative regulatory layers
- visible_notes: 26621
- admin_candidates: 918

## Why This Hub Exists
> [!info] This hub is for approval, conformity, surveillance, recall, and governance texts.
> It prevents administrative material from being buried inside phase-oriented technical browsing.

## Browse View
- visible_admin_notes: 918
- jurisdiction[KR]: 430
- jurisdiction[UNECE]: 463
- jurisdiction[US]: 25
- regulatory_layer[framework_admin]: 1
- regulatory_layer[technical_requirement]: 917
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0024_125-1-ac-455|1) 교류(AC) 전력선]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0032_145-1-27|1) 두 줄로 표시하는 경우]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0032_145-1-300-100-15|1) 두 줄로 표시하는 경우 표지크기는 가로 300밀리미터 이상, 세로 100밀리미터]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0002_002-1-563|1) 발생한 순서에 따라 자동으로 반복하여 표시]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0024_125-1-16-a-207|1) 상당 입력 전류 16 A 이하]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-130-1017|1) 시속 130 킬로미터 이하 속도에서 사용할 수 있도록 제작된 타이어의 경우,]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-493|1) 응급용 타이어]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0005_011-1-49|1) 정지표시장치는 어린이가 승하차 중임을 알리는 표시부와 이를 차체에]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-23|1) 제작사명 또는 제작사를 표시하는 기호]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-897|1) 제작사명 또는 제작사를 표시하는 기호]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0034_147-1-10-30-1-229|1) 창닦이기를 최대속도로 10회 작동시키는 동안 별표30의 제1호에서 정]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0034_147-1-25-215|1) 최저작동주기는 매분 당 25회 이상일 것]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-1167|1) 타이어의 단면 너비는 다음의 식에 따라 구할 것]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0001_001-1-577|1) 트레드 강도(파괴에너지) 최소 기준]]
- [[regulation_units/regunit-xml_kmvss-kmvss_att_0034_147-1-240-80-267|1) 표지는 가로 240밀리미터 이상, 세로 80밀리미터 이상으로 할 것]]
- [[regulation_units/regunit-xml_kmvss-kmvss_art_2_002-item-1-1|1. 1. "공차상태"란 자동차에 사람이 승차하지 않고 물품(예비부분품 및 공구, 그 밖의 휴대물품을 포함한다)을 적재하지 않은 상태로서 연료ㆍ냉각수 및 윤활유를 가득 채우고 예비타이어(예비타이어를 장착한 자동차만]]
- [[regulation_units/regunit-xml_kmvss-kmvss_art_4_007-item-1-1-2|1. 1. 공차상태일 것]]
- [[regulation_units/regunit-xml_kmvss-kmvss_art_4_007-item-1-1|1. 1. 길이 : 13미터(연결자동차의 경우에는 16.7미터를 말한다)]]
- [[regulation_units/regunit-xml_kmvss-kmvss_art_32_046-item-1-1-2|1. 1. 덮개는 방수기능을 갖춘 재질로서 쉽게 파손되지 않는 구조일 것]]
- [[regulation_units/regunit-xml_kmvss-kmvss_art_23_035-item-1-1|1. 1. 승강구 계단 부위에는 국토교통부장관이 정하여 고시하는 보호시설을 갖출 것]]

## Dataview
### Live Listing
```dataview
TABLE file.link, phase, regulatory_layer, jurisdiction
FROM "wiki"
WHERE note_type != "browse_index" AND (phase = "non_phase_admin" OR regulatory_layer = "framework_admin" OR regulatory_layer = "conformity_assessment" OR regulatory_layer = "market_surveillance_recall")
SORT jurisdiction ASC, file.name ASC
```
