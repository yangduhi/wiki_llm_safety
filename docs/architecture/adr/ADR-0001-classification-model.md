---
record_layer: operations
id: adr-0001-classification-model
title: ADR-0001 Classification Model
summary: Establishes faceted canonical classification with phase as the global root and active/passive retained as compatibility only.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - adr
  - classification
---

# ADR-0001 Classification Model

## Status

Accepted

## Context

The repository needs a classification system that can scale across KR, US, EU, and UNECE materials without collapsing everything into a single `active/passive` split.

## Decision

- Canonical classification is faceted.
- `phase` is the global root facet.
- Allowed `phase` values are `pre_crash`, `in_crash`, `post_crash`, `cross_phase`, `non_phase_admin`.
- `functional_domain`, `primary_topic`, and `secondary_topics` refine the note after phase assignment.
- `active_safety`, `passive_crash`, and `needs_review` are kept as compatibility layers only.
- The image-derived 16 categories are retained only as `in_crash` browse taxonomy.
- `AEB pedestrian` remains `pre_crash + active_safety`.

## Consequences

- Existing assets are preserved instead of discarded.
- Crosswalk files become mandatory.
- Old registry files must not be treated as canonical ontology roots.
