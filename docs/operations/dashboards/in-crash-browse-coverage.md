---
record_layer: operations
id: dashboard-in-crash-browse-coverage
title: In-Crash Browse Coverage
summary: Operational coverage view for the in-crash browse taxonomy.
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

# In-Crash Browse Coverage

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- visible_in_crash_units: 5306
- units_without_browse_bucket: 528
- browse_bucket: `anti_ejection` -> 127
- browse_bucket: `child_restraints` -> 462
- browse_bucket: `door_retention` -> 930
- browse_bucket: `fire_risk` -> 5
- browse_bucket: `frontal_impact` -> 973
- browse_bucket: `fuel_system_integrity` -> 51
- browse_bucket: `glazing_retention` -> 31
- browse_bucket: `head_impact` -> 338
- browse_bucket: `occupant_compartment_integrity` -> 87
- browse_bucket: `occupant_restraints` -> 1832
- browse_bucket: `pedestrian_protection` -> 10
- browse_bucket: `rear_impact` -> 405
- browse_bucket: `rollover` -> 35
- browse_bucket: `seat_systems` -> 1228
- browse_bucket: `side_impact` -> 1250
- browse_bucket: `steering_control` -> 90

## Dataview
```dataview
TABLE value AS browse_bucket, length(rows) AS notes
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document" AND phase = "in_crash"
FLATTEN browse_buckets AS value
GROUP BY value
SORT value ASC
```
