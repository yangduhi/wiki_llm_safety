---
record_layer: operations
id: dashboard-recently-changed-notes
title: Recently Changed Notes
summary: Most recently updated visible knowledge notes.
status: active
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
data_as_of: '2026-04-14'
refresh_run_id: 20260414T073313Z__a12dd3a7
tags:
- operations
- dashboard
---

# Recently Changed Notes

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- `2026-04-14` | `jurisdiction_overview` | [[jurisdictions/jurisdiction-us|US]]
- `2026-04-14` | `jurisdiction_overview` | [[jurisdictions/jurisdiction-unece|UNECE]]
- `2026-04-14` | `concept_node` | [[concepts/concept-type-approval-framework|Type Approval Framework]]
- `2026-04-14` | `concept_node` | [[concepts/concept-side-impact-protection|Side Impact Protection]]
- `2026-04-14` | `concept_node` | [[concepts/concept-restraint-systems|Restraint Systems]]
- `2026-04-14` | `concept_node` | [[concepts/concept-post-crash-isolation|Post-Crash Isolation]]
- `2026-04-14` | `concept_node` | [[concepts/concept-pedestrian-protection|Pedestrian Protection]]
- `2026-04-14` | `concept_node` | [[concepts/concept-occupant-protection|Occupant Protection]]
- `2026-04-14` | `jurisdiction_overview` | [[jurisdictions/jurisdiction-kr|KR]]
- `2026-04-14` | `concept_node` | [[concepts/concept-injury-criteria|Injury Criteria]]
- `2026-04-14` | `concept_node` | [[concepts/concept-glazing-materials|Glazing Materials]]
- `2026-04-14` | `concept_node` | [[concepts/concept-frontal-impact-protection|Frontal Impact Protection]]
- `2026-04-14` | `concept_node` | [[concepts/concept-emergency-egress|Emergency Egress]]
- `2026-04-14` | `concept_node` | [[concepts/concept-electrical-shock-protection|Electrical Shock Protection]]
- `2026-04-14` | `concept_node` | [[concepts/concept-ev-electrical-safety|EV Electrical Safety]]
- `2026-04-14` | `concept_node` | [[concepts/concept-driver-visibility|Driver Visibility]]
- `2026-04-14` | `concept_node` | [[concepts/concept-door-retention|Door Retention]]
- `2026-04-14` | `concept_node` | [[concepts/concept-conformity-assessment|Conformity Assessment]]
- `2026-04-14` | `concept_node` | [[concepts/concept-child-restraint-systems|Child Restraint Systems]]
- `2026-04-14` | `concept_node` | [[concepts/concept-anti-ejection|Anti-Ejection]]
- `2026-04-13` | `regulation_unit` | [[regulation_units/regunit-xml_kmvss-kmvss_att_0006_048-item-189|필라멘트 광원 할로겐, 발광소자 광원]]
- `2026-04-13` | `regulation_unit` | [[regulation_units/regunit-xml_kmvss-kmvss_att_0006_066-item-11|필라멘트 광원]]
- `2026-04-13` | `regulation_unit` | [[regulation_units/regunit-xml_kmvss-kmvss_att_0005_035-item-73|파. 휠체어 사용자 공간(휠체어 사용자만을 위해 별도로 제공되는 공간을 포함한다)]]
- `2026-04-13` | `regulation_unit` | [[regulation_units/regunit-xml_kmvss-kmvss_att_0007_087-item-195|파. 비상자동제동장치는 다음의 고장감지 기준에 적합할 것]]
- `2026-04-13` | `regulation_unit` | [[regulation_units/regunit-xml_kmvss-kmvss_att_0007_080-item-1353|태의 자동차를 주제동조종장치의 작동으로 이 호 나목 “제동능력 기준”]]

## Dataview
```dataview
TABLE file.link, updated, note_type, phase, primary_topic
FROM "wiki"
WHERE note_type != "browse_index"
SORT updated DESC
LIMIT 25
```
