# Contributing

## Workflow

- Create a short-lived feature branch from `main`.
- Open a pull request back into `main` for normal changes.
- `main` is PR-first, but repository admins can still bypass protections when needed.

## Required Checks

- Run `.\scripts\wiki.ps1 verify` before pushing write tasks.
- Run `.\.venv\Scripts\python.exe -m pytest -q` whenever Python code changes.
- Commit generated `index.md`, `docs/operations/INDEX.md`, and refreshed dashboard pages when verification updates them.

## Repository Rules

- Treat `raw/` as immutable source input. Add new source files if needed, but do not edit, rename, move, or delete existing raw files.
- Keep durable knowledge in `wiki/` and management/governance records in `docs/operations/`.
