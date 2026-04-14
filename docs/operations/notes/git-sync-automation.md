---
record_layer: operations
id: operations-git-sync-automation
title: Git Sync Automation
summary: Defines the repository-safe git sync commands and the expected automation behavior for keeping local clones current.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - git
  - automation
  - codex
---

# Git Sync Automation

## Goal

- keep a local clone current without discarding or mutating in-progress work
- automate fetch and fast-forward only when repository state is safe

## Safe Commands

- `.\scripts\wiki.ps1 git-sync-status`
  reports branch, upstream, ahead/behind counts, worktree cleanliness, and blocking files
- `.\scripts\wiki.ps1 git-sync-safe`
  fetches the upstream remote and fast-forwards only when the current branch is clean and strictly behind its upstream

## Skip Conditions

Automation must skip updates when:

- the worktree is dirty
- the current branch is ahead of upstream
- the current branch and upstream have diverged
- the branch has no upstream
- the repository is in detached `HEAD`

## Automation Policy

- default automation behavior is safe-check first, fast-forward second
- automation must never run `reset`, `checkout --`, `stash`, or destructive cleanup as part of sync
- when sync is skipped, the automation should report the branch, upstream, and first blocking files instead of forcing a change

## Operator Guidance

- use branch-per-task workflows for active work
- keep `main` or a dedicated local sync branch tracking `origin/main`
- let periodic automation handle fetch/fast-forward for clean branches and use manual review for everything else
