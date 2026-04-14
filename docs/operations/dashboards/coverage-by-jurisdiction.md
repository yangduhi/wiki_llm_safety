---
record_layer: operations
id: dashboard-coverage-by-jurisdiction
title: Coverage by Jurisdiction
summary: Counts visible regulation units by jurisdiction.
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

# Coverage by Jurisdiction

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- jurisdiction: `KR` -> 4238
- jurisdiction: `UNECE` -> 11554
- jurisdiction: `US` -> 10345

## Dataview
```dataview
TABLE jurisdiction, count(rows) AS notes
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
GROUP BY jurisdiction
SORT jurisdiction ASC
```
