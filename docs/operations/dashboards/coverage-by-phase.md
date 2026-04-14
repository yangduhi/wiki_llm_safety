---
record_layer: operations
id: dashboard-coverage-by-phase
title: Coverage by Phase
summary: Counts visible regulation units by canonical phase.
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

# Coverage by Phase

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- phase: `cross_phase` -> 14138
- phase: `in_crash` -> 5306
- phase: `non_phase_admin` -> 890
- phase: `post_crash` -> 2256
- phase: `pre_crash` -> 3547

## Dataview
```dataview
TABLE phase, count(rows) AS notes
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
GROUP BY phase
SORT phase ASC
```
