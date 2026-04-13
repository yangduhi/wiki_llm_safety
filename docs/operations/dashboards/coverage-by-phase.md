# Coverage by Phase

## Snapshot
- phase: `cross_phase` -> 4955
- phase: `in_crash` -> 796
- phase: `non_phase_admin` -> 23
- phase: `post_crash` -> 8
- phase: `pre_crash` -> 478
- phase: `unknown` -> 1

## Dataview
```dataview
TABLE phase, count(rows) AS notes
FROM "wiki/regulation_units"
GROUP BY phase
SORT phase ASC
```
