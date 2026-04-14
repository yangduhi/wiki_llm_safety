---
record_layer: operations
id: dashboard-coverage-by-functional-domain
title: Coverage by Functional Domain
summary: Counts visible regulation units by functional domain.
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

# Coverage by Functional Domain

## Snapshot
- generated_at: 2026-04-14
- data_as_of: 2026-04-14
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- functional_domain: `child_occupant_protection` -> 21
- functional_domain: `crash_avoidance_and_vehicle_control` -> 2738
- functional_domain: `fire_electrical_and_energy_storage_safety` -> 1375
- functional_domain: `interior_materials_and_fire` -> 28
- functional_domain: `occupant_protection_and_restraints` -> 7250
- functional_domain: `other_or_review` -> 10905
- functional_domain: `post_crash_response_and_data` -> 930
- functional_domain: `structural_integrity_retention_and_egress` -> 1023
- functional_domain: `visibility_glazing_and_driver_information` -> 1775
- functional_domain: `vru_protection` -> 92

## Dataview
```dataview
TABLE value AS functional_domain, length(rows) AS notes
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
FLATTEN functional_domain AS value
GROUP BY value
SORT value ASC
```
