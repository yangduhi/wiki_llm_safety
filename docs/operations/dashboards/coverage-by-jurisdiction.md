# Coverage by Jurisdiction

## Snapshot
- jurisdiction: `US` -> 6260
- jurisdiction: `unknown` -> 1

## Dataview
```dataview
TABLE jurisdiction, count(rows) AS notes
FROM "wiki/regulation_units"
GROUP BY jurisdiction
SORT jurisdiction ASC
```
