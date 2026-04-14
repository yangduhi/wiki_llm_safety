---
record_layer: operations
id: operations-github-repository-management
title: GitHub Repository Management
summary: Documents the canonical remote, branch model, PR expectations, and CI verification flow for the shared repository.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - github
  - git
  - ci
---

# GitHub Repository Management

## Canonical Remote

- primary remote is `origin`
- repository URL is `https://github.com/yangduhi/wiki_llm_safety`
- local clones should treat `main` as the default integration branch

## Branching

- create feature branches from `main`
- keep branch names short and task-oriented
- open pull requests back into `main`
- default workflow is PR-first, with admin bypass kept available for urgent maintenance

## Verification

- run `.\scripts\wiki.ps1 verify` before pushing write tasks
- run `.\.venv\Scripts\python.exe -m pytest -q` when Python code changes
- treat generated `index.md`, `docs/operations/INDEX.md`, and dashboard pages as committed artifacts
- use `.\scripts\wiki.ps1 git-sync-status` before manual repo updates when local state is unclear
- use `.\scripts\wiki.ps1 git-sync-safe` for fast-forward-only local updates that must not discard work

## GitHub Automation

- GitHub Actions runs repository verification on pushes and pull requests targeting `main`
- the workflow also runs on feature-branch pushes so verification fails early
- the workflow fails if tests fail, verify fails, or generated files are stale
- concurrency cancels superseded runs on the same ref to reduce queue noise
- `CODEOWNERS` assigns default review ownership to `@yangduhi`
- local recurring sync automation should use the repo-safe git sync commands instead of raw `pull` logic

## Merge Policy

- `main` is protected by a repository ruleset instead of ad hoc direct-push practice
- required status check name is `verify`
- merge strategy is `squash` only
- merged branches should be deleted automatically

## Collaboration

- use the PR template to summarize scope, verification, and operations impact
- keep management records under `docs/operations/` instead of `wiki/`
