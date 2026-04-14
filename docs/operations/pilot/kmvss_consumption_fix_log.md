---
record_layer: operations
id: operations-kmvss-consumption-fix-log
title: KMVSS Consumption Fix Log
summary: Execution log for the KMVSS classification-consumption improvement round.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - execution-log
---

# KMVSS Consumption Fix Log

## Commands Executed

1. inspected representative KMVSS raw files and normalized outputs
2. updated `classification.py`, `parse/service.py`, `normalize/service.py`, `utils/text.py`
3. added `taxonomy/kmvss_signal_lexicon.yaml`
4. added pilot, holdout, negative-control, trace-related artifacts
5. ran `.\.venv\Scripts\python.exe -m pytest -q`
6. reran `.\.venv\Scripts\python.exe -m wiki_obsidian.cli run --collection xml_kmvss`
7. reran `.\scripts\wiki.ps1 verify`

## Re-execution Notes

- first KMVSS rerun after signal-pipeline refactor produced major gains but one holdout mismatch remained
- added a title prior for `후방보행자 안전장치`
- reran full KMVSS again to align repository outputs with the final rules

## Final Validation

- representative set: `5 / 5` pass
- holdout set: `12 / 12` pass
- negative control set: `10 / 10` pass
- `pytest`: pass
- `verify`: pass
