---
record_layer: knowledge
id: browse-index-in-crash-browse
note_type: browse_index
title: In-Crash Browse Hub
summary: Secondary browse hub for the in-crash browse taxonomy only.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
aliases: []
browse_axis: in_crash_browse
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: 20260414T073313Z__a12dd3a7
confidence: medium
---

# In-Crash Browse Hub

## Snapshot
- generated_at: 2026-04-14
- browse_axis: in_crash_browse
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- browse_role: secondary
- browse_scope: in_crash only
- visible_in_crash_units: 5306
- buckets_present: 16

## Why This Hub Exists
> [!warning] Browse buckets are in-crash browse aids, not canonical ontology roots.
> Start with Phase Hub or Functional Domain Hub when the task is not specifically in-crash browsing.

## Browse View
### Scenario Browse
- `frontal_impact` -> 973 | documents: [[regulation_documents/pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english|ECE R137 UN Regulation No. 137 - Rev.1 - Frontal impact with focus on restraint systems Rev0 English]], [[regulation_documents/pdf_ece-ece_r94_un_regulation_no-_94_-_rev-3_-_frontal_collision_protection_-_03_series_rev0_english|ECE R94 UN Regulation No. 94 - Rev.3 - Frontal collision protection - 03 series Rev0 English]], [[regulation_documents/xml_kmvss-kmvss_art_102_153|조문 102 고정벽정면충돌 안전성]]
- `side_impact` -> 1250 | documents: [[regulation_documents/pdf_ece-ece_r135_un_regulation_no-_135_-_rev-1_-_pole_side_impact_-psi-_-_01_series_of_amendments_rev0_english|ECE R135 UN Regulation No. 135 - Rev.1 - Pole Side Impact (PSI) - 01 series of amendments Rev0 English]], [[regulation_documents/xml_fmvss-571-213a|§ 571.213a Standard No. 213a; Child restraint systems—side impact protection.]], [[regulation_documents/xml_fmvss-571-214|§ 571.214 Standard No. 214; Side impact protection.]]
- `rear_impact` -> 405 | documents: n/a
- `rollover` -> 35 | documents: n/a

### Component Browse
- `anti_ejection` -> 127 | documents: [[regulation_documents/xml_fmvss-571-226|§ 571.226 Standard No. 226; Ejection Mitigation.]]
- `child_restraints` -> 462 | documents: [[regulation_documents/xml_fmvss-571-213a|§ 571.213a Standard No. 213a; Child restraint systems—side impact protection.]], [[regulation_documents/xml_kmvss-kmvss_art_103_156|조문 103 어린이보호용 좌석부착장치]], [[regulation_documents/xml_kmvss-kmvss_art_27_041|조문 27 어린이보호용 좌석부착장치]]
- `door_retention` -> 930 | documents: [[regulation_documents/pdf_ece-ece_r11_un_regulation_no-_11_-_rev-3_-_door_latches_and_hinges_rev0_english|ECE R11 UN Regulation No. 11 - Rev.3 - Door latches and hinges Rev0 English]], [[regulation_documents/xml_fmvss-571-206|§ 571.206 Standard No. 206; Door locks and door retention components.]], [[regulation_documents/xml_kmvss-kmvss_art_102_151|조문 102 충돌 시의 승객보호]]
- `fire_risk` -> 5 | documents: n/a
- `fuel_system_integrity` -> 51 | documents: n/a
- `glazing_retention` -> 31 | documents: n/a
- `head_impact` -> 338 | documents: n/a
- `occupant_compartment_integrity` -> 87 | documents: n/a
- `occupant_restraints` -> 1832 | documents: [[regulation_documents/xml_fmvss-571-201|§ 571.201 Standard No. 201; Occupant protection in interior impact.]], [[regulation_documents/xml_fmvss-571-208|§ 571.208 Standard No. 208; Occupant crash protection.]], [[regulation_documents/xml_kmvss-kmvss_art_103_155|조문 103 좌석안전띠장치 등]]
- `seat_systems` -> 1228 | documents: [[regulation_documents/xml_kmvss-kmvss_art_103_155|조문 103 좌석안전띠장치 등]], [[regulation_documents/xml_kmvss-kmvss_art_103_156|조문 103 어린이보호용 좌석부착장치]], [[regulation_documents/xml_kmvss-kmvss_art_112_175|조문 112 좌석안전띠장치]]
- `steering_control` -> 90 | documents: n/a

### Protection Target Browse
- `pedestrian_protection` -> 10 | documents: [[regulation_documents/xml_kmvss-kmvss_art_102_152|조문 102 보행자 보호]]

### Fallback / Review-Prone Cases
- units_needing_bucket_review: 557
- note: the current committed browse registry does not define an explicit `interior` fallback bucket, so unbucketed or weakly bucketed in-crash units are treated as review-prone here.

## Dataview
### Live Listing
```dataview
TABLE file.link, primary_topic, functional_domain, browse_buckets
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document" AND phase = "in_crash"
SORT primary_topic ASC
LIMIT 25
```
