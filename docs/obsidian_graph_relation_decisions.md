# Obsidian Graph Relation Decisions

## Purpose
- This document records evidence-backed document-to-document semantic relation decisions without turning the registry into a long-form memo.

## Active Document-to-Document Relations
### § 571.208 Standard No. 208; Occupant crash protection. -> 조문 102 충돌 시의 승객보호
- relation_type: `same_safety_function`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-208, regdoc-xml_kmvss-kmvss_art_102_151
- rationale_summary: Both source-grounded notes are in-crash technical requirements in the occupant protection and restraints domain and operate as broad occupant crash protection anchors in their jurisdictions.
- decision: retained as `active`
- follow_up: none

### § 571.208 Standard No. 208; Occupant crash protection. -> 조문 102 고정벽정면충돌 안전성
- relation_type: `same_test_family`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-208, regdoc-xml_kmvss-kmvss_art_102_153
- rationale_summary: FMVSS 208 and KMVSS Art. 102_153 both ground frontal crash occupant protection and test-family interpretation
- decision: retained as `active`
- follow_up: none

### § 571.214 Standard No. 214; Side impact protection. -> 조문 102 기둥측면충돌 안전성
- relation_type: `same_safety_function`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-214, regdoc-xml_kmvss-kmvss_art_102_154
- rationale_summary: Both source-grounded notes explicitly center side impact occupant protection and are used as side-impact anchors within the in-crash occupant protection cluster.
- decision: retained as `active`
- follow_up: none

### § 571.305a Standard No. 305a; electric-powered vehicles: Electric powertrain integrity; mandatory applicability begins on September 1, 2027. -> 조문 112 전기자동차 등에 사용되는 구동축전지
- relation_type: `same_safety_function`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-305a, regdoc-xml_kmvss-kmvss_art_112_186
- rationale_summary: Both source-grounded notes center electric vehicle powertrain safety
- decision: retained as `active`
- follow_up: none

### § 571.208 Standard No. 208; Occupant crash protection. -> ECE R137 UN Regulation No. 137 - Rev.1 - Frontal impact with focus on restraint systems Rev0 English
- relation_type: `same_test_family`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-208, regdoc-pdf_ece-ece_r137_un_regulation_no-_137_-_rev-1_-_frontal_impact_with_focus_on_restraint_systems_rev0_english
- rationale_summary: FMVSS 208 and UNECE R137 both anchor frontal impact occupant protection with explicit restraint-system test-family proximity
- decision: retained as `active`
- follow_up: none

### § 571.214 Standard No. 214; Side impact protection. -> ECE R95 UN Regulation No. 95 - Rev.2 - Lateral collision protection Rev0 English
- relation_type: `jurisdictional_analog`
- status: `active`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-214, regdoc-pdf_ece-ece_r95_un_regulation_no-_95_-_rev-2_-_lateral_collision_protection_rev0_english
- rationale_summary: FMVSS 214 and UNECE R95 both serve as side or lateral impact protection anchors in their jurisdictions
- decision: retained as `active`
- follow_up: none

### § 571.206 Standard No. 206; Door locks and door retention components. -> § 571.226 Standard No. 226; Ejection Mitigation.
- relation_type: `same_safety_function`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_fmvss-571-206, regdoc-xml_fmvss-571-226
- rationale_summary: Door retention and anti-ejection notes share occupant containment concerns within the same neighborhood.
- decision: retained as `active`
- follow_up: none

### § 571.208 Standard No. 208; Occupant crash protection. -> § 571.214 Standard No. 214; Side impact protection.
- relation_type: `same_safety_function`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_fmvss-571-208, regdoc-xml_fmvss-571-214
- rationale_summary: Both notes belong to the occupant protection cluster but emphasize different crash directions.
- decision: retained as `active`
- follow_up: none

### 조문 114 기준적용의 특례 -> 조문 102 충돌 시의 승객보호
- relation_type: `admin_governs`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_kmvss-kmvss_art_114_189, regdoc-xml_kmvss-kmvss_art_102_151
- rationale_summary: The KR approval-framework note governs how technical passenger-protection requirements are situated administratively.
- decision: retained as `active`
- follow_up: none

### 조문 114 기준적용의 특례 -> 조문 102 보행자 보호
- relation_type: `admin_governs`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_kmvss-kmvss_art_114_189, regdoc-xml_kmvss-kmvss_art_102_152
- rationale_summary: The KR approval-framework note also governs applicability of pedestrian-protection requirements.
- decision: retained as `active`
- follow_up: none

### 조문 114 기준적용의 특례 -> 조문 112 전기자동차 등에 사용되는 구동축전지
- relation_type: `admin_governs`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_kmvss-kmvss_art_114_189, regdoc-xml_kmvss-kmvss_art_112_186
- rationale_summary: The KR approval-framework note governs placement and applicability of battery safety requirements.
- decision: retained as `active`
- follow_up: none

### 조문 114 장치 기준에 관한 특례 -> 조문 102 기둥측면충돌 안전성
- relation_type: `admin_governs`
- status: `active`
- confidence: `medium`
- evidence_basis: regdoc-xml_kmvss-kmvss_art_114_190, regdoc-xml_kmvss-kmvss_art_102_154
- rationale_summary: The KR conformity note governs how side-impact requirements are assessed and confirmed.
- decision: retained as `active`
- follow_up: none

## Adjudicated Exclusions
### § 571.214 Standard No. 214; Side impact protection. -> 조문 102 충돌 시의 승객보호
- relation_type: `same_safety_function`
- current_status: `excluded`
- confidence: `medium`
- evidence_basis: regdoc-xml_fmvss-571-214, regdoc-xml_kmvss-kmvss_art_102_151
- rationale_summary: Both notes sit under occupant protection
- decision: excluded after review
- follow_up: docs/obsidian_graph_relation_decisions.md

### § 571.205 Standard No. 205, Glazing materials. -> 조문 102 보행자 보호
- relation_type: `same_safety_function`
- current_status: `excluded`
- confidence: `high`
- evidence_basis: regdoc-xml_fmvss-571-205, regdoc-xml_kmvss-kmvss_art_102_152
- rationale_summary: FMVSS 205 covers glazing materials and visibility-linked glazing performance
- decision: excluded after review
- follow_up: docs/obsidian_graph_relation_decisions.md

## Deferred / Not Yet Adjudicated
### § 571.208 Standard No. 208; Occupant crash protection. -> EU 2019/2144 General Safety Regulation
- relation_type: `same_safety_function`
- current_status: `pending_source_note`
- confidence: `medium`
- evidence_basis: regdoc-xml_fmvss-571-208
- rationale_summary: EU 2019/2144 likely belongs in the same broad occupant and safety umbrella neighborhood
- decision: still pending because a source-grounded target note does not yet exist
- follow_up: assumptions.md
