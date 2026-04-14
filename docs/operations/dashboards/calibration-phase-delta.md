---
record_layer: operations
id: dashboard-calibration-phase-delta
title: Calibration Phase Delta
summary: Delta between current and adjudicated phase decisions for the 20-document
  calibration set.
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

# Calibration Phase Delta

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- calibration_items: 20
- changed_items: 5
- cross_phase_to_post_crash: 3
- cross_phase_to_pre_crash: 2
- current_phase_counts: {'cross_phase': 8, 'in_crash': 6, 'non_phase_admin': 2, 'post_crash': 2, 'pre_crash': 2}
- selected_phase_counts: {'cross_phase': 3, 'in_crash': 6, 'non_phase_admin': 2, 'post_crash': 5, 'pre_crash': 4}
- rejected_alternative_counts: {'cross_phase': 11, 'in_crash': 4, 'non_phase_admin': 1, 'post_crash': 2, 'pre_crash': 2}
- document-level calibration is for entry classification only; canonical phase stabilization is governed by regulation_unit adjudication.
- `us-fmvss-111` | current=`cross_phase` -> selected=`pre_crash` | rejected=`cross_phase`
- `us-fmvss-126` | current=`cross_phase` -> selected=`pre_crash` | rejected=`in_crash`
- `unece-r131` | current=`pre_crash` -> selected=`pre_crash` | rejected=`in_crash`
- `unece-r152` | current=`pre_crash` -> selected=`pre_crash` | rejected=`in_crash`
- `us-fmvss-208` | current=`in_crash` -> selected=`in_crash` | rejected=`cross_phase`
- `us-fmvss-206` | current=`in_crash` -> selected=`in_crash` | rejected=`post_crash`
- `us-fmvss-214` | current=`in_crash` -> selected=`in_crash` | rejected=`cross_phase`
- `us-fmvss-226` | current=`in_crash` -> selected=`in_crash` | rejected=`post_crash`
- `unece-r94` | current=`in_crash` -> selected=`in_crash` | rejected=`cross_phase`
- `unece-r95` | current=`in_crash` -> selected=`in_crash` | rejected=`cross_phase`
- `us-fmvss-302` | current=`post_crash` -> selected=`post_crash` | rejected=`cross_phase`
- `us-fmvss-305a` | current=`cross_phase` -> selected=`post_crash` | rejected=`cross_phase`
- `kr-kmvss-art-112-186` | current=`cross_phase` -> selected=`post_crash` | rejected=`cross_phase`
- `unece-r100` | current=`cross_phase` -> selected=`post_crash` | rejected=`cross_phase`
- `unece-r144` | current=`post_crash` -> selected=`post_crash` | rejected=`non_phase_admin`
- `us-fmvss-205` | current=`cross_phase` -> selected=`cross_phase` | rejected=`pre_crash`
- `eu-2019-2144` | current=`cross_phase` -> selected=`cross_phase` | rejected=`pre_crash`
- `kr-performance-rule` | current=`cross_phase` -> selected=`cross_phase` | rejected=`in_crash`
- `eu-2018-858` | current=`non_phase_admin` -> selected=`non_phase_admin` | rejected=`cross_phase`
- `unece-1958` | current=`non_phase_admin` -> selected=`non_phase_admin` | rejected=`cross_phase`
