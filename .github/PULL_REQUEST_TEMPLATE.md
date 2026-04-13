## Summary

Describe the scope of the change and the specific notes, scripts, or governance records affected.

## Checks

- [ ] `raw/` was left immutable, except for intentional source additions
- [ ] `.\scripts\wiki.ps1 verify`
- [ ] `.\.venv\Scripts\python.exe -m pytest -q` when code paths changed
- [ ] Generated indexes and dashboards are committed

## Operations Impact

- [ ] `docs/operations/` was updated because governance or workflow changed
- [ ] No operations record update was needed

## Risks

List any unresolved risks, follow-ups, or evidence gaps.
