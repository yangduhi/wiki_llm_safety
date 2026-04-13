# Obsidian LLM Wiki

A file-first, Obsidian-centered regulatory knowledge base for building durable, cross-jurisdiction automotive safety notes with LLM assistance.

## Mission

This repository is not a chat transcript archive. It is a compounding knowledge system that:

- structures regulatory source material
- materializes durable `regulation_unit` notes
- preserves provenance and authority metadata
- builds compatibility-aware crosswalks across KR, US, EU, and UNECE contexts
- keeps Obsidian, Codex, Python automation, and operational governance in one workspace

## Four Layers

1. `platform layer`
   Python package, CLI, wrapper scripts, harness, agents, skills, MCP contracts
2. `knowledge layer`
   wiki notes, templates, taxonomies, schemas, crosswalks, dashboards
3. `source layer`
   `raw/collections`, official snapshots, clip intake, authority registry
4. `operations layer`
   ADRs, plans, decisions, validation records, pilot memos, go/no-go records

## Key Policy

- canonical classification is faceted, with `phase` as the global root
- `active_safety`, `passive_crash`, and `needs_review` remain compatibility layers only
- the 16 image-derived passive buckets stay as browse aids for `in_crash`, not ontology roots
- `AEB pedestrian` remains `pre_crash + active_safety`

## Repository Map

- `AGENTS.md` - repository contract and operating rules
- `taxonomy/` - canonical registries and compatibility mappings
- `schemas/` - note and regulation-unit schemas
- `sources/` - authoritative source registry and document inventory
- `docs/architecture/adr/` - architecture decision records
- `docs/operations/plans/` - phase-by-phase implementation instructions
- `raw/collections/` - immutable source collections and intake folders
- `wiki/` - durable knowledge notes and templates
- `configs/` - platform configuration, collection profiles, MCP/tool contracts
- `src/wiki_obsidian/` - Python package
- `harness/scripts/` - deterministic validation and materialization scripts
- `.codex/` - repo-scoped Codex defaults and specialist agents
- `.agents/skills/` - repo-scoped reusable skills
- `.obsidian/` - shared vault settings safe to commit

## Current Collections

- `xml_fmvss`
- `xml_kmvss`
- `pdf_ece`
- `web_clipper`
- `official_web`

## Quick Start

```powershell
.\scripts\bootstrap.ps1
.\scripts\wiki.ps1 verify
.\.venv\Scripts\python.exe -m wiki_obsidian.cli --help
```

## Common Commands

```powershell
.\.venv\Scripts\python.exe -m wiki_obsidian.cli inspect-collection --collection xml_fmvss
.\.venv\Scripts\python.exe -m wiki_obsidian.cli run --collection xml_fmvss
.\.venv\Scripts\python.exe -m wiki_obsidian.cli classify-phase "AEB for pedestrian"
.\.venv\Scripts\python.exe -m wiki_obsidian.cli build-crosswalk
.\.venv\Scripts\python.exe -m wiki_obsidian.cli dashboard-refresh
.\.venv\Scripts\python.exe -m wiki_obsidian.cli source-audit
.\scripts\wiki.ps1 verify
```

## Repository Operations

- primary GitHub repository: [yangduhi/wiki_llm_safety](https://github.com/yangduhi/wiki_llm_safety)
- canonical remote name: `origin`
- default integration branch: `main`
- run `.\scripts\wiki.ps1 verify` before pushing write tasks
- GitHub Actions mirrors the same verification flow and fails when generated indexes or dashboards are stale
