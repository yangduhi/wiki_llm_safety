---
record_layer: knowledge
id: browse-index-functional-domain
note_type: browse_index
title: Functional Domain Hub
summary: Primary browse hub for functional_domain across visible regulation units.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
generated_at: '2026-04-14'
aliases: []
browse_axis: functional_domain
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: 20260414T073313Z__a12dd3a7
confidence: medium
---

# Functional Domain Hub

## Snapshot
- generated_at: 2026-04-14
- browse_axis: functional_domain
- refresh_run_id: `20260414T073313Z__a12dd3a7`
- browse_role: primary
- canonical_axis: functional_domain
- visible_regulation_units: 26137
- domains: 10

## Why This Hub Exists
> [!important] Functional domain is a primary global browse axis.
> Use this hub before in-crash browse buckets when the question is about safety function or subsystem intent.

## Browse View
### `child_occupant_protection`
- unit_count: 21
- representative_documents: [[regulation_documents/xml_kmvss-kmvss_art_103_156|조문 103 어린이보호용 좌석부착장치]], [[regulation_documents/xml_kmvss-kmvss_art_27_041|조문 27 어린이보호용 좌석부착장치]], [[regulation_documents/xml_kmvss-kmvss_att_0005_012|별표 0005 어린이보호용 좌석부착장치의 설치기준(제27조의2제7호 관련)]]
### `crash_avoidance_and_vehicle_control`
- unit_count: 2738
- representative_documents: [[regulation_documents/pdf_ece-ece_r131_un_regulation_no-_131_-_rev-1_-_advanced_emergency_braking_systems_-aebs-_rev0_english|regard to the Advanced Emergency Braking Systems (AEBS)]], [[regulation_documents/pdf_ece-ece_r152_un_regulation_no-_152_-_advanced_emergency_braking_system_-aebs-_rev0_english|regard to the Advanced Emergency Braking System (AEBS) for M1 and]], [[regulation_documents/web_clipper-pedestrian-aeb-sample|AEB for Pedestrian]]
### `fire_electrical_and_energy_storage_safety`
- unit_count: 1375
- representative_documents: [[regulation_documents/pdf_ece-ece_r100_un_regulation_no-_100_-_rev-2_-_electric_power_trained_vehicles_rev0_english|specific requirements for the electric power train]], [[regulation_documents/xml_fmvss-571-301|§ 571.301 Standard No. 301; Fuel system integrity.]], [[regulation_documents/xml_fmvss-571-303|§ 571.303 Standard No. 303; Fuel system integrity of compressed natural gas vehicles.]]
### `interior_materials_and_fire`
- unit_count: 28
- representative_documents: [[regulation_documents/xml_fmvss-571-302|§ 571.302 Standard No. 302; Flammability of interior materials.]]
### `occupant_protection_and_restraints`
- unit_count: 7250
- representative_documents: [[regulation_documents/pdf_ece-ece_r129_un_regulation_no-_129_-_enhanced_child_restraint_systems_-ecrs-_rev0_english|ECE R129 UN Regulation No. 129 - Enhanced Child Restraint Systems (ECRS) Rev0 English]], [[regulation_documents/pdf_ece-ece_r135_un_regulation_no-_135_-_rev-1_-_pole_side_impact_-psi-_-_01_series_of_amendments_rev0_english|ECE R135 UN Regulation No. 135 - Rev.1 - Pole Side Impact (PSI) - 01 series of amendments Rev0 English]], [[regulation_documents/pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english|ECE R137 UN Regulation No. 137 - Rev.1 - Frontal impact with focus on restraint systems Rev0 English]]
### `other_or_review`
- unit_count: 10905
- representative_documents: [[regulation_documents/official_web-fmvss-landing-sample|FMVSS Landing]], [[regulation_documents/pdf_ece-ece_r127_un_regulation_no-_127_-_rev-2_-_pedestrian_safety_rev0_english|regard to their pedestrian safety performance]], [[regulation_documents/pdf_ece-ece_r12_un_regulation_no-_12_-_rev-4_-_steering_mechanism_rev0_english|ECE R12 UN Regulation No. 12 - Rev.4 - Steering mechanism Rev0 English]]
### `post_crash_response_and_data`
- unit_count: 930
- representative_documents: [[regulation_documents/pdf_ece-ece_r144_un_regulation_no-_144_-_accident_emergency_call_systems_-aecs-_rev0_english|Uniform provisions concerning the Accident Emergency Call Systems]], [[regulation_documents/xml_kmvss-kmvss_art_56_083|조문 56 사고기록장치]], [[regulation_documents/xml_kmvss-kmvss_att_0005_033|별표 0005 사고기록장치의 장착기준(제56조의2제3항 관련)]]
### `structural_integrity_retention_and_egress`
- unit_count: 1023
- representative_documents: [[regulation_documents/pdf_ece-ece_r11_un_regulation_no-_11_-_rev-3_-_door_latches_and_hinges_rev0_english|ECE R11 UN Regulation No. 11 - Rev.3 - Door latches and hinges Rev0 English]], [[regulation_documents/xml_fmvss-571-113|§ 571.113 Standard No. 113; Hood latch system.]], [[regulation_documents/xml_fmvss-571-206|§ 571.206 Standard No. 206; Door locks and door retention components.]]
### `visibility_glazing_and_driver_information`
- unit_count: 1775
- representative_documents: [[regulation_documents/xml_fmvss-571-103|§ 571.103 Standard No. 103; Windshield defrosting and defogging systems.]], [[regulation_documents/xml_fmvss-571-104|§ 571.104 Standard No. 104; Windshield wiping and washing systems.]], [[regulation_documents/xml_fmvss-571-205-a|§ 571.205(a) Glazing equipment manufactured before September 1, 2006 and glazing materials used in vehicles manufactured before November 1, 2006.]]
### `vru_protection`
- unit_count: 92
- representative_documents: [[regulation_documents/xml_kmvss-kmvss_art_102_152|조문 102 보행자 보호]]

## Dataview
### Live Listing
```dataview
TABLE file.link, phase, jurisdiction, primary_topic
FROM "wiki/regulation_units"
WHERE note_type = "regulation_unit" AND clause_path != "document"
FLATTEN functional_domain AS value
GROUP BY value
SORT value ASC
```
