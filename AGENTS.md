# Obsidian LLM Wiki Repository Contract

## Mission

Turn raw regulatory sources into a durable Obsidian-centered knowledge base that compounds over time.

This repository is optimized for:

- source-grounded regulatory understanding
- `regulation_unit` level note materialization
- cross-jurisdiction comparison
- human + LLM collaboration inside a shared Obsidian vault

## Read Order

1. `AGENTS.md`
2. `README.md`
3. `docs/architecture/adr/ADR-0001-classification-model.md`
4. `docs/architecture/adr/ADR-0004-obsidian-note-contract.md`
5. `docs/operations/notes/architecture.md`
6. `docs/operations/notes/operating-rules.md`
7. relevant pages in `wiki/`
8. only then the minimum necessary files under `raw/`

## Hard Invariants

1. `raw/` is immutable.
   - Humans may add source files and snapshots.
   - Agents may read files under `raw/`.
   - Agents must not edit, rename, move, or delete files under `raw/`.

2. `wiki/` is the durable knowledge layer.
   - Canonical durable note work belongs here.
   - `regulation_unit` is the default atomic note type.
   - `wiki/analyses/` is for reusable synthesis, not project chatter.

3. `docs/` is the management and governance layer.
   - Architecture, ADRs, plans, pilot memos, dashboards, audits, risks, and operational notes live here.
   - Do not store management records under `wiki/`.

4. `taxonomy/`, `schemas/`, and `sources/` are canonical support layers.
   - `taxonomy/` defines registries and compatibility mappings.
   - `schemas/` defines validation contracts.
   - `sources/` defines authoritative source inventory and policy inputs.

5. Provenance is mandatory.
   - Every durable wiki note must carry `provenance`.
   - Notes tied to raw material must keep `source_files` and `source_hashes` accurate.

6. `phase` is canonical.
   - Do not treat active/passive as the global root classification.
   - Keep `active_safety`, `passive_crash`, and `needs_review` as compatibility layers only.

7. The image-based 16 buckets are browse aids, not canonical ontology roots.
   - Use them as `in_crash` browse taxonomy only.

8. `AEB pedestrian` remains `pre_crash + active_safety`.
   - Do not force it into passive pedestrian protection as the primary bucket.

9. Prefer merge over duplication.
   - Update stable pages when they already cover the same note identity.

10. Run verification before stopping on write tasks.
   - `.\scripts\wiki.ps1 verify`

## Default Note Contract

Canonical wiki notes should use:

- `note_type`
- `jurisdiction`
- `source_collection`
- `regulatory_layer`
- `phase`
- `functional_domain`
- `primary_topic`
- `secondary_topics`
- `browse_buckets`
- `legacy_domain`
- `aliases`
- `provenance`
- `effective_date`
- `confidence`

`regulation_unit` is the primary durable note type. `regulation_document` remains a supporting note type.

## Workflow Rules

### Ingest

1. Read the ADRs and collection profile first.
2. Inspect the smallest possible source set.
3. Keep `raw/` immutable.
4. Materialize or update `regulation_document` and `regulation_unit` notes.
5. Preserve provenance and canonical classification fields.
6. Rebuild indexes and dashboards as needed.
7. Run verify.

### Query + Writeback

1. Ground on `index.md` and relevant wiki notes first.
2. Use raw files only when knowledge notes are insufficient.
3. Separate facts, inference, and open questions.
4. Persist reusable synthesis under `wiki/analyses/`.
5. Put project/process chatter under `docs/operations/`.

### Ontology Governance

1. Architecture and taxonomy decisions belong under `docs/architecture/adr/` and `docs/decisions/`.
2. Pilot mappings, retrieval rules, and go/no-go records belong under `docs/operations/`.
3. Do not silently promote pilot classifications into production truth.

## Done When

A write task is complete only when:

- the requested artifact exists
- durable knowledge was updated where needed
- `index.md` is current
- `docs/operations/INDEX.md` is current when operations records changed
- dashboard materializations are current
- repository-local verify passes
- unresolved risks are surfaced explicitly
