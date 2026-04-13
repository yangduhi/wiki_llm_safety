---
record_layer: operations
id: operations-automotive-safety-regulation-project-understanding
title: Automotive Safety Regulation Project Understanding
summary: Records the repository-level interpretation of how this project should implement a Karpathy-style regulatory wiki.
status: active
created: 2026-04-10
updated: 2026-04-10
tags:
  - operations
  - project-understanding
  - regulatory-wiki
---
# Automotive Safety Regulation Project Understanding

## Context

This note captures repository-level understanding of the project direction after reviewing Andrej Karpathy's "LLM Wiki" gist and the current source collections.

## Findings

- The repository already follows the core pattern of immutable raw sources, a mutable knowledge wiki, and an agent control layer.
- The loaded corpus is already domain-specific:
  - `raw/collections/pdf_ece/` contains UNECE regulation PDFs.
  - `raw/collections/xml_fmvss/` contains FMVSS XML files.
  - `raw/collections/xml_kmvss/` contains KMVSS XML files.
- The live knowledge layer is still near-empty, so the main missing capability is repeatable ingest and knowledge writeback, not additional raw-source loading.
- Collection handling is heterogeneous. UNECE content arrives as PDF while FMVSS and KMVSS arrive as XML, so collection-specific parsing and normalization remain necessary.
- KMVSS XML decodes correctly as UTF-8 in Python, even when terminal rendering appears garbled.

## Why This Is An Operations Note

- This document is about repository intent, implementation posture, and next-step planning.
- It is not a durable statement of automotive safety law.
- For that reason it belongs in `docs/operations/notes/` rather than the live knowledge layer.

## Evidence

- Andrej Karpathy's gist, "LLM Wiki": <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- `AGENTS.md` defines the control contract and the separation between raw, knowledge, and operations records.
- `docs/operations/notes/architecture.md` describes the repository architecture.
- `docs/operations/notes/operating-rules.md` defines ingest, query, lint, and verification rules.
- `src/wiki_obsidian/ingest/service.py`, `src/wiki_obsidian/query/service.py`, and `src/wiki_obsidian/lint/service.py` establish how the repository currently materializes or validates records.

## Open Questions

- What should become the canonical comparison unit for cross-jurisdiction work: regulation, clause, safety function, test procedure, or subsystem?
- Should the first milestone optimize for broad coverage or a narrow but deep set of safety domains?
- Which cross-jurisdiction equivalence relationships should be first-class in claim materialization?

