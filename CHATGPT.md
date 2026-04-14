# ChatGPT Repo Guide

This file is a quick entrypoint for general-purpose assistants, including ChatGPT, when the user asks about this repository from GitHub.

## What This Repository Is

- An Obsidian-centered regulatory knowledge base for automotive safety regulations.
- Durable knowledge lives in `wiki/`.
- Governance, plans, dashboards, and operating notes live in `docs/`.
- Raw source snapshots live in `raw/` and are immutable.

## Read This First

1. `CHATGPT.md`
2. `AGENTS.md`
3. `README.md`
4. `docs/architecture/adr/ADR-0001-classification-model.md`
5. `docs/architecture/adr/ADR-0004-obsidian-note-contract.md`
6. `docs/operations/notes/architecture.md`
7. `docs/operations/notes/operating-rules.md`
8. Relevant pages in `wiki/`
9. Only then the minimum necessary files in `raw/`

## Hard Rules

- Do not edit, rename, move, or delete anything under `raw/`.
- Treat `phase` as the canonical top-level classification axis.
- Keep management/process material in `docs/`, not `wiki/`.
- Prefer updating existing durable pages over creating duplicate notes.
- When answering questions, ground on `index.md` and existing wiki notes before raw files.

## Where To Look

- `index.md`: global starting point for repository grounding
- `wiki/regulation_units/`: canonical note-level material
- `wiki/regulation_documents/`: supporting source summaries
- `wiki/analyses/`: reusable synthesis
- `docs/operations/dashboards/`: generated operational views
- `schemas/` and `taxonomy/`: note contract and classification support
- `src/wiki_obsidian/`: Python CLI and repository automation

## Helpful Commands

```powershell
.\scripts\bootstrap.ps1
.\scripts\wiki.ps1 verify
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m wiki_obsidian.cli --help
```

## How ChatGPT Should Help

- Separate repository facts from inference.
- Prefer citing concrete file paths when making claims.
- Use `docs/` for governance explanations and `wiki/` for domain knowledge.
- If a user asks about repository state or behavior, summarize the current files rather than inventing missing structure.

## Copy/Paste Prompt For ChatGPT

```text
This GitHub repository has a repo guide for assistants. Start by reading CHATGPT.md, AGENTS.md, and README.md. Follow the documented read order, treat raw/ as immutable, prefer wiki/ before raw/, and cite the file paths you used when answering.
```
