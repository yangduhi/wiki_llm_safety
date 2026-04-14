---
record_layer: operations
id: operations-kmvss-attachment-parser-notes
title: KMVSS Attachment Parser Notes
summary: Notes for the attachment-aware KMVSS parser and normalization changes introduced in round 2A.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - attachment
  - parser
---

# KMVSS Attachment Parser Notes

## What Changed

- attachment detection is now limited to `kmvss_att_*` raw stems or `SECTNO` values that contain `별표` or `별지`
- attachment parsing no longer relies on `splitlines()` alone
- semantic headers, section headers, and table-like rows are grouped into block units
- numeric or value-heavy rows no longer fall back to generic clause markers

## Unitization Heuristics

- semantic headers:
  - roman headers such as `Ⅰ.`
  - numbered headers such as `1.`
  - Korean subheaders such as `가.`
  - descriptive headers such as `필라멘트 광원`, `전자파 방사기준`, `공기압타이어 표기 기준`
- table-like rows:
  - numeric, unit, symbol, or column-heavy rows are merged into the current semantic block
  - box-drawing rows and rule boilerplate rows are skipped
- inherited context:
  - `SUBJECT`
  - attachment title
  - current section header
  - current semantic header
  - extracted `reference_articles`

## Metadata Added To Units

- `document_kind`
- `is_attachment`
- `attachment_bucket`
- `attachment_section`
- `row_group_id`
- `is_table_like_row`
- `inherits_subject_context`
- `inherits_section_context`
- `reference_articles`
- `comparison_key`

## Practical Effect

- exemplar `KMVSS_Att_0006_066` shrank from `213` residual units to `5` grouped units
- exemplar `KMVSS_Att_0001_001` shrank from `185` units to `93`
- exemplar `KMVSS_Att_0024_125` shrank from `62` units to `25`

## Known Limits

- short-value attachments such as `camera monitor system` and generic wheel/table specs still leave residual `cross_phase` or `other_or_review`
- attachment grouping is heuristic rather than table-aware OCR/CSV reconstruction
- `EMC` remains intentionally conservative on domain assignment
