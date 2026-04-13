# Coverage by Functional Domain

## Snapshot
- functional_domain: `child_occupant_protection` -> 214
- functional_domain: `crash_avoidance_and_vehicle_control` -> 497
- functional_domain: `fire_electrical_and_energy_storage_safety` -> 118
- functional_domain: `interior_materials_and_fire` -> 2
- functional_domain: `occupant_protection_and_restraints` -> 316
- functional_domain: `other_or_review` -> 4778
- functional_domain: `structural_integrity_retention_and_egress` -> 171
- functional_domain: `visibility_glazing_and_driver_information` -> 142
- functional_domain: `vru_protection` -> 22

## Dataview
```dataview
TABLE value AS functional_domain, length(rows) AS notes
FROM "wiki/regulation_units"
FLATTEN functional_domain AS value
GROUP BY value
SORT value ASC
```
