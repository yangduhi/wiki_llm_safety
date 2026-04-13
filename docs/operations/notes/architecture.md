---
record_layer: operations
id: operations-architecture-v2
title: Repository Architecture
summary: Describes the four-layer v2 architecture and the split between generic platform and automotive domain pack.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - architecture
---

# Repository Architecture

## Summary

The repository is organized into four layers:

1. `platform layer`
2. `knowledge layer`
3. `source layer`
4. `operations layer`

The code and validation surface are generic, while taxonomy, schemas, registries, and pilot mappings are domain-pack assets for automotive regulation work.

## Generic Platform

- Python package and CLI
- wrapper scripts
- harness checks
- agent and skill assets
- MCP and external-tool contracts

## Automotive Domain Pack

- `taxonomy/`
- `schemas/`
- `sources/`
- `wiki/_templates/`
- pilot and crosswalk outputs

## Note Strategy

- `regulation_unit` is the primary durable note
- `regulation_document` is a supporting summary note
- `analysis` stores reusable synthesis
- management records stay under `docs/`
