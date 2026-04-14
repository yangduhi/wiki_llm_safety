---
name: git-sync-ops
description: Safely inspect and fast-forward the current branch to its upstream without discarding local work.
---

# Git sync ops

- Prefer `.\scripts\wiki.ps1 git-sync-status` before changing branch state.
- Use `.\scripts\wiki.ps1 git-sync-safe` only when the current branch tracks an upstream branch.
- Never reset, rebase, stash, or discard local changes automatically as part of sync.
- If the worktree is dirty, ahead, diverged, detached, or missing an upstream, report the reason and stop.
- Treat fast-forward only as the default update path.
