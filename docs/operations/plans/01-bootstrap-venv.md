# Phase 1 - Bootstrap + venv

## Goal

Create the Python 3.11 environment, install the package, and capture the initial raw baseline.

## Commands

```powershell
.\scripts\bootstrap.ps1
.\scripts\wiki.ps1 verify
```

## Done When

- `.venv` exists
- `python -m wiki_obsidian.cli --help` succeeds
- raw baseline manifest exists
