---
record_layer: knowledge
id: browse-index-jurisdiction
note_type: browse_index
title: Jurisdiction Hub
summary: Browse hub for jurisdiction-specific entry into the visible regulation corpus.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
aliases: []
browse_axis: jurisdiction
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: 20260414T073313Z__a12dd3a7
confidence: medium
---

# Jurisdiction Hub

## Snapshot
- generated_at: 2026-04-14
- browse_axis: jurisdiction
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- browse_role: supporting
- canonical_axis: jurisdiction
- visible_regulation_units: 26137
- jurisdictions_present: 3

## Why This Hub Exists
> [!info] Jurisdiction is a practical entry surface for comparative law work.
> Use it alongside Phase Hub and Functional Domain Hub, not instead of them.

## Browse View
### `KR`
- unit_count: 4238
- representative_documents: [[regulation_documents/xml_kmvss-kmvss_art_100_149|조문 100 팔걸이]], [[regulation_documents/xml_kmvss-kmvss_art_101_150|조문 101 햇빛가리개]], [[regulation_documents/xml_kmvss-kmvss_art_102_151|조문 102 충돌 시의 승객보호]]
### `UNECE`
- unit_count: 11554
- representative_documents: [[regulation_documents/pdf_ece-ece_r100_un_regulation_no-_100_-_rev-2_-_electric_power_trained_vehicles_rev0_english|specific requirements for the electric power train]], [[regulation_documents/pdf_ece-ece_r11_un_regulation_no-_11_-_rev-3_-_door_latches_and_hinges_rev0_english|ECE R11 UN Regulation No. 11 - Rev.3 - Door latches and hinges Rev0 English]], [[regulation_documents/pdf_ece-ece_r127_un_regulation_no-_127_-_rev-2_-_pedestrian_safety_rev0_english|regard to their pedestrian safety performance]]
### `US`
- unit_count: 10345
- representative_documents: [[regulation_documents/official_web-fmvss-landing-sample|FMVSS Landing]], [[regulation_documents/web_clipper-pedestrian-aeb-sample|AEB for Pedestrian]], [[regulation_documents/xml_fmvss-571-101|§ 571.101 Standard No. 101; Controls and displays.]]

## Dataview
### Live Listing
```dataview
TABLE file.link, phase, functional_domain, primary_topic
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
GROUP BY jurisdiction
SORT jurisdiction ASC
```
