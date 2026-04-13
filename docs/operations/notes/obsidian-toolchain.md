---
record_layer: operations
id: operations-obsidian-toolchain
title: Obsidian Toolchain
summary: Explains how Obsidian, Dataview, qmd, Marp, and web clip intake are connected in the repository.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - obsidian
  - tooling
---

# Obsidian Toolchain

## Obsidian

- `.obsidian/` contains repo-safe vault configuration
- workspace-specific state should not be committed

## Dataview

- dashboards are generated under `docs/operations/dashboards/`
- each dashboard includes both a static snapshot and a Dataview block

## qmd

- qmd is optional and treated as an external local executable
- use `.\scripts\wiki.ps1 search` for presence checks and documented fallback behavior

## Marp

- Marp is optional and used for materialized overview export
- use `.\scripts\wiki.ps1 slides` for graceful presence checks

## Web Clipper

- drop captured markdown or HTML under `raw/collections/web_clipper/`
- run scan or ingest after intake
