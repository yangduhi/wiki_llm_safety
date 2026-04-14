---
record_layer: operations
id: dashboard-missing-provenance
title: Missing Provenance
summary: All visible source-grounded knowledge notes missing provenance.
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

# Missing Provenance

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- total_missing: 0

## Dataview
```dataview
TABLE file.link, note_type, title
FROM "wiki"
WHERE note_type != "browse_index" AND note_type != "jurisdiction_overview" AND (!provenance OR length(provenance.source_files) = 0)
SORT file.name ASC
```
