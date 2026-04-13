---
record_layer: operations
id: operations-source-authority-policy-v1
title: Source Authority Policy
summary: Defines how official legal texts, administrative framework texts, and explanatory sources are prioritized for the regulatory ontology pilot.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - sources
  - authority
---

# Source Authority Policy

## Source Priority
1. Official consolidated legal text or official current law page
2. Official administrative framework or competent authority landing page
3. Official explanatory page from the same authority
4. Secondary commentary only when the official source is unavailable or structurally ambiguous

## Authority Rules By Jurisdiction
- KR: 국가법령정보센터 current text or official government rule/gosi page is primary.
- US: NHTSA and eCFR current text are primary.
- EU: EUR-Lex current or consolidated text is primary.
- UNECE: UNECE official pages, WP.29 materials, and official agreement documents are primary.

## Inventory Rules
- `official_status` must distinguish `primary_official`, `official_explainer`, `secondary_official_index`, and `pending_official_confirmation`.
- `version_or_effective_date` must be filled wherever the official page exposes an effective date or consolidated-text date.
- `citation_preferred_form` must prefer the citation form used by the official source, not an LLM-normalized nickname.

## Pilot Rules
- Pilot mapping uses official texts first.
- Raw wording disputes are settled against the official source, not a summary page.
- If an official source is found but its canonical URL is still uncertain, keep the row as `pending_official_confirmation` rather than silently guessing.

## Non-Goals
- This phase does not standardize parser code or automate source scraping.
- This phase does not merge duplicated sources automatically.
- This phase does not rewrite the live wiki from the inventory.
