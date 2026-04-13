# In-crash Browse Buckets

## Snapshot
- browse_bucket: `anti_ejection` -> 27
- browse_bucket: `child_restraints` -> 248
- browse_bucket: `door_retention` -> 123
- browse_bucket: `fire_risk` -> 31
- browse_bucket: `frontal_impact` -> 25
- browse_bucket: `fuel_system_integrity` -> 110
- browse_bucket: `glazing_retention` -> 82
- browse_bucket: `head_impact` -> 465
- browse_bucket: `occupant_compartment_integrity` -> 109
- browse_bucket: `occupant_restraints` -> 250
- browse_bucket: `pedestrian_protection` -> 25
- browse_bucket: `rear_impact` -> 305
- browse_bucket: `rollover` -> 40
- browse_bucket: `seat_systems` -> 527
- browse_bucket: `side_impact` -> 347
- browse_bucket: `steering_control` -> 66

## Dataview
```dataview
TABLE value AS browse_bucket, length(rows) AS notes
FROM "wiki/regulation_units"
WHERE phase = "in_crash"
FLATTEN browse_buckets AS value
GROUP BY value
SORT value ASC
```
