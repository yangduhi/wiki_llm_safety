---
record_layer: operations
id: operations-reclassification-unit-vs-document-delta
title: Reclassification Unit vs Document Delta
summary: Generated summary of where unit-level adjudication diverges from document-level
  calibration.
status: active
created: '2026-04-13'
updated: '2026-04-14'
generated_at: '2026-04-14'
data_as_of: '2026-04-14'
refresh_run_id: 20260414T073313Z__a12dd3a7
tags:
- operations
- dashboard
---

# Reclassification Unit vs Document Delta

document-level calibration은 entry classification용이며, canonical phase 안정화는 regulation_unit adjudication이 우선한다.

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- documents_covered: 20
- unit_samples: 60
- documents_with_mixed_units: 3
- documents_where_unit_differs: 3
- selected_unit_phase_counts: {'cross_phase': 1, 'in_crash': 21, 'non_phase_admin': 6, 'post_crash': 17, 'pre_crash': 15}

## Per Document
- `eu-2018-858` | document=`non_phase_admin` | unit_phases=`non_phase_admin` | differing_units=0
- `eu-2019-2144` | document=`cross_phase` | unit_phases=`in_crash, post_crash, pre_crash` | differing_units=3
- `kr-kmvss-art-112-186` | document=`post_crash` | unit_phases=`post_crash` | differing_units=0
- `kr-performance-rule` | document=`cross_phase` | unit_phases=`in_crash, post_crash, pre_crash` | differing_units=3
- `unece-1958` | document=`non_phase_admin` | unit_phases=`non_phase_admin` | differing_units=0
- `unece-r100` | document=`post_crash` | unit_phases=`post_crash` | differing_units=0
- `unece-r131` | document=`pre_crash` | unit_phases=`pre_crash` | differing_units=0
- `unece-r144` | document=`post_crash` | unit_phases=`post_crash` | differing_units=0
- `unece-r152` | document=`pre_crash` | unit_phases=`pre_crash` | differing_units=0
- `unece-r94` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `unece-r95` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `us-fmvss-111` | document=`pre_crash` | unit_phases=`pre_crash` | differing_units=0
- `us-fmvss-126` | document=`pre_crash` | unit_phases=`pre_crash` | differing_units=0
- `us-fmvss-205` | document=`cross_phase` | unit_phases=`cross_phase, in_crash, pre_crash` | differing_units=2
- `us-fmvss-206` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `us-fmvss-208` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `us-fmvss-214` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `us-fmvss-226` | document=`in_crash` | unit_phases=`in_crash` | differing_units=0
- `us-fmvss-302` | document=`post_crash` | unit_phases=`post_crash` | differing_units=0
- `us-fmvss-305a` | document=`post_crash` | unit_phases=`post_crash` | differing_units=0
