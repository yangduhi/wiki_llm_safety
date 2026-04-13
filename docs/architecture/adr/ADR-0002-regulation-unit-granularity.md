---
record_layer: operations
id: adr-0002-regulation-unit-granularity
title: ADR-0002 Regulation Unit Granularity
summary: Sets regulation_unit as the default durable note granularity for canonical wiki materialization.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - adr
  - note-contract
---

# ADR-0002 Regulation Unit Granularity

## Status

Accepted

## Context

Document-level summaries are useful, but they are too coarse to support durable comparison, clause-grounded retrieval, and targeted writeback.

## Decision

- The default atomic note type is `regulation_unit`.
- `regulation_document` notes remain as supporting summaries and source anchors.
- A `regulation_unit` should correspond to the smallest practically reviewable clause-like unit produced by the parser.
- Obsidian dashboards and retrieval flows should prioritize `regulation_unit` notes over document-level summaries.

## Consequences

- Parsing and ingest must preserve clause paths and provenance.
- Tests must validate the note contract at the unit level.
- Cross-jurisdiction comparison becomes materially easier.
