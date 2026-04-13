---
record_layer: operations
id: adr-0004-obsidian-note-contract
title: ADR-0004 Obsidian Note Contract
summary: Defines the canonical frontmatter and template contract for Obsidian-centered durable knowledge notes.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - adr
  - obsidian
---

# ADR-0004 Obsidian Note Contract

## Status

Accepted

## Decision

- Shared vault notes must use frontmatter that supports machine validation and human navigation.
- `regulation_unit` is the primary note contract.
- Canonical fields include `jurisdiction`, `source_collection`, `regulatory_layer`, `phase`, `functional_domain`, `primary_topic`, `secondary_topics`, `browse_buckets`, `legacy_domain`, `aliases`, `provenance`, `effective_date`, and `confidence`.
- Dashboards are generated as markdown files with Dataview blocks, not as opaque app state.
- Repo-safe `.obsidian` configuration may be committed; personal workspace state should not.

## Consequences

- Note validation can run in CI or local harness scripts.
- Dashboard refresh becomes deterministic.
- Obsidian remains a navigable projection of canonical repo content rather than a hidden source of truth.
