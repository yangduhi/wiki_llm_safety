# Missing Provenance

## Snapshot
- `jurisdiction-us` | US

## Dataview
```dataview
TABLE file.link, title
FROM "wiki"
WHERE !provenance OR length(provenance.source_files) = 0
```
