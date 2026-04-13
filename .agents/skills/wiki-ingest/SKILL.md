---
name: wiki-ingest
description: Ingest raw sources into `regulation_document` and `regulation_unit` notes, refresh indexes, and run repository-local verification.
---

# Wiki ingest

- Read ADRs, operations notes, and the relevant collection profile first.
- Keep `raw/` immutable.
- Prefer updating an existing durable note over creating near-duplicates.
- Materialize `regulation_unit` notes as the default durable output.
- Run `.\scripts\wiki.ps1 verify` before stopping.
