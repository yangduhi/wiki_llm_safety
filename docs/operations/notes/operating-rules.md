---
record_layer: operations
id: operations-rules-v2
title: Operating Rules
summary: Defines ingest, classification, dashboard, and verification rules for the Obsidian-centered repository.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - rules
---

# Operating Rules

## Ingest

- ingest starts from one collection at a time
- source files remain immutable
- one source file creates one `regulation_document`
- clause-like units are materialized as `regulation_unit` notes
- canonical classification is assigned during normalization, not ad hoc in the final markdown

## Classification

- `phase` is canonical
- `active_safety`, `passive_crash`, and `needs_review` are compatibility only
- the 16 image-derived passive buckets are browse aids for `in_crash`, not ontology roots
- `AEB pedestrian` remains `pre_crash + active_safety`

## Query

- query grounding reads `index.md` first
- use wiki notes before raw documents
- durable synthesis goes to `wiki/analyses/`
- project or process chatter goes to `docs/operations/`

## Verify

Verify includes:

- frontmatter completeness
- valid `phase`
- valid `functional_domain`
- valid `browse_buckets`
- provenance integrity
- note id uniqueness
- raw immutability baseline
- index and operations index refresh
- dashboard refresh
