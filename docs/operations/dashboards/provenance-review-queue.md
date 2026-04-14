---
record_layer: operations
id: dashboard-provenance-review-queue
title: Provenance Review Queue
summary: Visible regulation units with incomplete provenance metadata.
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

# Provenance Review Queue

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- queue_size: 0

## Dataview
```dataview
TABLE file.link, source_collection, document_id, source_url
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document" AND (!provenance OR length(provenance.source_files) = 0)
SORT updated DESC
```
