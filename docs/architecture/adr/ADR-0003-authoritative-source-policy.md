---
record_layer: operations
id: adr-0003-authoritative-source-policy
title: ADR-0003 Authoritative Source Policy
summary: Defines authoritative source handling, official_web intake, and authority registry obligations.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - adr
  - authority
---

# ADR-0003 Authoritative Source Policy

## Status

Accepted

## Context

The repository must distinguish between raw convenience corpora and authoritative current sources used for policy, validation, and conflict resolution.

## Decision

- `sources/authority_registry.yaml` is the canonical authority registry.
- `sources/document_inventory.csv` is the canonical flat inventory for audits and spreadsheet-style review.
- `raw/collections/official_web/` holds official web captures and snapshots.
- Every authoritative source entry must include jurisdiction, title, source type, official status, original URL, snapshot date, effective date, parser strategy, checksum/hash, and notes.
- Web clipper intake is useful but not authoritative by default.

## Consequences

- `source-audit` becomes a first-class repo command.
- Authority data must remain separate from live wiki synthesis.
- Pilot and go/no-go decisions can point to a stable source inventory.
