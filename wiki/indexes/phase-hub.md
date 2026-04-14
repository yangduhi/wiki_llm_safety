---
record_layer: knowledge
id: browse-index-phase
note_type: browse_index
title: Phase Hub
summary: Primary browse hub for canonical phase across visible regulation units.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
aliases: []
browse_axis: phase
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: 20260414T073313Z__a12dd3a7
confidence: medium
---

# Phase Hub

## Snapshot
- generated_at: 2026-04-14
- browse_axis: phase
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- browse_role: primary
- canonical_axis: phase
- visible_regulation_units: 26137
- phases_present: 5

## Why This Hub Exists
> [!important] Phase is the canonical global root facet.
> Use this hub before any compatibility or browse-only taxonomy.

## Browse View
### `cross_phase`
- unit_count: 14138
- representative_documents: [[regulation_documents/pdf_ece-ece_r127_un_regulation_no-_127_-_rev-2_-_pedestrian_safety_rev0_english|regard to their pedestrian safety performance]], [[regulation_documents/pdf_ece-ece_r129_un_regulation_no-_129_-_enhanced_child_restraint_systems_-ecrs-_rev0_english|ECE R129 UN Regulation No. 129 - Enhanced Child Restraint Systems (ECRS) Rev0 English]], [[regulation_documents/pdf_ece-ece_r12_un_regulation_no-_12_-_rev-4_-_steering_mechanism_rev0_english|ECE R12 UN Regulation No. 12 - Rev.4 - Steering mechanism Rev0 English]]
### `in_crash`
- unit_count: 5306
- representative_documents: [[regulation_documents/pdf_ece-ece_r11_un_regulation_no-_11_-_rev-3_-_door_latches_and_hinges_rev0_english|ECE R11 UN Regulation No. 11 - Rev.3 - Door latches and hinges Rev0 English]], [[regulation_documents/pdf_ece-ece_r135_un_regulation_no-_135_-_rev-1_-_pole_side_impact_-psi-_-_01_series_of_amendments_rev0_english|ECE R135 UN Regulation No. 135 - Rev.1 - Pole Side Impact (PSI) - 01 series of amendments Rev0 English]], [[regulation_documents/pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english|ECE R137 UN Regulation No. 137 - Rev.1 - Frontal impact with focus on restraint systems Rev0 English]]
### `non_phase_admin`
- unit_count: 890
- representative_documents: [[regulation_documents/official_web-fmvss-landing-sample|FMVSS Landing]], [[regulation_documents/xml_kmvss-kmvss_art_107_160|조문 107 전자파 적합성]], [[regulation_documents/xml_kmvss-kmvss_art_114_189|조문 114 기준적용의 특례]]
### `post_crash`
- unit_count: 2256
- representative_documents: [[regulation_documents/pdf_ece-ece_r100_un_regulation_no-_100_-_rev-2_-_electric_power_trained_vehicles_rev0_english|specific requirements for the electric power train]], [[regulation_documents/pdf_ece-ece_r144_un_regulation_no-_144_-_accident_emergency_call_systems_-aecs-_rev0_english|Uniform provisions concerning the Accident Emergency Call Systems]], [[regulation_documents/xml_fmvss-571-302|§ 571.302 Standard No. 302; Flammability of interior materials.]]
### `pre_crash`
- unit_count: 3547
- representative_documents: [[regulation_documents/pdf_ece-ece_r131_un_regulation_no-_131_-_rev-1_-_advanced_emergency_braking_systems_-aebs-_rev0_english|regard to the Advanced Emergency Braking Systems (AEBS)]], [[regulation_documents/pdf_ece-ece_r152_un_regulation_no-_152_-_advanced_emergency_braking_system_-aebs-_rev0_english|regard to the Advanced Emergency Braking System (AEBS) for M1 and]], [[regulation_documents/web_clipper-pedestrian-aeb-sample|AEB for Pedestrian]]

## Dataview
### Live Listing
```dataview
TABLE file.link, jurisdiction, functional_domain, primary_topic
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
GROUP BY phase
SORT phase ASC
```
