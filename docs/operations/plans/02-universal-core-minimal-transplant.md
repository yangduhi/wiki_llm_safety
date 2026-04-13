# Phase 2 - Universal Core Minimal Transplant

## Goal

Bring over only the reusable core from `3__wiki_universal` and adapt it to the new package, directory, and note contracts.

## Scope

- `src/`
- `scripts/`
- `harness/`
- `.codex/`
- `.agents/`
- `configs/collections/`
- `raw/collections/`

## Done When

- no dependency remains on the old package name
- the CLI round-trip `scan -> parse -> normalize -> ingest -> verify` works on at least one collection
