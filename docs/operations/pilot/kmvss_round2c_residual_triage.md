---
record_layer: operations
id: operations-kmvss-round2c-residual-triage
title: KMVSS Round 2C Residual Triage
summary: Lane-based triage for KMVSS article residuals in round 2C.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2c
  - triage
---

# KMVSS Round 2C Residual Triage

- run_id: `20260414T011841Z__e42c6ca0`

## 창유리 등
- document_id: `xml_kmvss-kmvss_art_34_048`
- current_phase: `cross_phase`
- current_domain: `visibility_glazing_and_driver_information`
- lane: `intentional_cross_phase`
- umbrella_family: `glazing_cross_phase`
- intentional_retain: `True`
- retain_reason: `true_multi_phase_glazing_scope`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_cross_phase`
- reference_repo_pattern: `wiki_llm_safety:pilot_csv+jsonl_and_policy_note`
- residual_summary: cross=`18` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: true multi-phase
- risk_note: forcing a single phase would discard genuine visibility-retention overlap
- final_decision_kind: `policy retain`

## 창유리의 안전성 등
- document_id: `xml_kmvss-kmvss_art_105_158`
- current_phase: `cross_phase`
- current_domain: `visibility_glazing_and_driver_information`
- lane: `intentional_cross_phase`
- umbrella_family: `glazing_cross_phase`
- intentional_retain: `True`
- retain_reason: `true_multi_phase_glazing_scope`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_cross_phase`
- reference_repo_pattern: `wiki_llm_safety:pilot_csv+jsonl_and_policy_note`
- residual_summary: cross=`10` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: true multi-phase
- risk_note: forcing a single phase would discard genuine visibility-retention overlap
- final_decision_kind: `policy retain`

## 정의
- document_id: `xml_kmvss-kmvss_art_2_002`
- current_phase: `non_phase_admin`
- current_domain: `other_or_review`
- lane: `intentional_other_or_review`
- umbrella_family: `definitions`
- intentional_retain: `True`
- retain_reason: `taxonomy_or_governance_review_lane`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_other_or_review`
- reference_repo_pattern: `wiki_llm_safety:operator_policy_and_fixed_slice_eval`
- residual_summary: cross=`0` / other=`83`
- local_text_weakness: `high`
- taxonomy_fit: taxonomy gap or governance scope
- risk_note: forcing a canonical domain would create artificial precision
- final_decision_kind: `policy retain`

## 기준적용의 특례
- document_id: `xml_kmvss-kmvss_art_114_189`
- current_phase: `non_phase_admin`
- current_domain: `other_or_review`
- lane: `intentional_other_or_review`
- umbrella_family: `special_exceptions`
- intentional_retain: `True`
- retain_reason: `taxonomy_or_governance_review_lane`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_other_or_review`
- reference_repo_pattern: `wiki_llm_safety:operator_policy_and_fixed_slice_eval`
- residual_summary: cross=`0` / other=`13`
- local_text_weakness: `high`
- taxonomy_fit: taxonomy gap or governance scope
- risk_note: forcing a canonical domain would create artificial precision
- final_decision_kind: `policy retain`

## 물품적재장치
- document_id: `xml_kmvss-kmvss_art_32_046`
- current_phase: `non_phase_admin`
- current_domain: `other_or_review`
- lane: `intentional_other_or_review`
- umbrella_family: `umbrella_titles_with_weak_unit_text`
- intentional_retain: `True`
- retain_reason: `taxonomy_or_governance_review_lane`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_other_or_review`
- reference_repo_pattern: `wiki_llm_safety:operator_policy_and_fixed_slice_eval`
- residual_summary: cross=`0` / other=`11`
- local_text_weakness: `high`
- taxonomy_fit: taxonomy gap or governance scope
- risk_note: forcing a canonical domain would create artificial precision
- final_decision_kind: `policy retain`

## 입석
- document_id: `xml_kmvss-kmvss_art_28_042`
- current_phase: `cross_phase`
- current_domain: `other_or_review`
- lane: `intentional_other_or_review`
- umbrella_family: `umbrella_titles_with_weak_unit_text`
- intentional_retain: `True`
- retain_reason: `taxonomy_or_governance_review_lane`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_other_or_review`
- reference_repo_pattern: `wiki_llm_safety:operator_policy_and_fixed_slice_eval`
- residual_summary: cross=`5` / other=`5`
- local_text_weakness: `high`
- taxonomy_fit: taxonomy gap or governance scope
- risk_note: forcing a canonical domain would create artificial precision
- final_decision_kind: `policy retain`

## 승차정원 및 최대적재량
- document_id: `xml_kmvss-kmvss_art_113_188`
- current_phase: `cross_phase`
- current_domain: `other_or_review`
- lane: `intentional_other_or_review`
- umbrella_family: `umbrella_titles_with_weak_unit_text`
- intentional_retain: `True`
- retain_reason: `taxonomy_or_governance_review_lane`
- policy_basis: `kmvss_round2c_review_lane_policy.intentional_other_or_review`
- reference_repo_pattern: `wiki_llm_safety:operator_policy_and_fixed_slice_eval`
- residual_summary: cross=`5` / other=`5`
- local_text_weakness: `high`
- taxonomy_fit: taxonomy gap or governance scope
- risk_note: forcing a canonical domain would create artificial precision
- final_decision_kind: `policy retain`

## 사이버보안
- document_id: `xml_kmvss-kmvss_art_18_028`
- current_phase: `non_phase_admin`
- current_domain: `other_or_review`
- lane: `mixed_or_ambiguous_keep_for_review`
- umbrella_family: `software_cyber`
- intentional_retain: `True`
- retain_reason: `mixed_technical_admin_scope`
- policy_basis: `kmvss_round2c_review_lane_policy.mixed_or_ambiguous_keep_for_review`
- reference_repo_pattern: `wiki_llm_safety:review_register_plus_trace_diff`
- residual_summary: cross=`0` / other=`9`
- local_text_weakness: `high`
- taxonomy_fit: mixed technical/admin
- risk_note: technical and admin phrases coexist, so over-committing is risky
- final_decision_kind: `policy retain`

## 소프트웨어
- document_id: `xml_kmvss-kmvss_art_18_029`
- current_phase: `non_phase_admin`
- current_domain: `other_or_review`
- lane: `mixed_or_ambiguous_keep_for_review`
- umbrella_family: `software_cyber`
- intentional_retain: `True`
- retain_reason: `mixed_technical_admin_scope`
- policy_basis: `kmvss_round2c_review_lane_policy.mixed_or_ambiguous_keep_for_review`
- reference_repo_pattern: `wiki_llm_safety:review_register_plus_trace_diff`
- residual_summary: cross=`0` / other=`9`
- local_text_weakness: `high`
- taxonomy_fit: mixed technical/admin
- risk_note: technical and admin phrases coexist, so over-committing is risky
- final_decision_kind: `policy retain`

## 계기판넬
- document_id: `xml_kmvss-kmvss_art_88_129`
- current_phase: `pre_crash`
- current_domain: `visibility_glazing_and_driver_information`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_instrument_panel`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `계기판넬` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`

## 견인장치 및 연결장치
- document_id: `xml_kmvss-kmvss_art_20_032`
- current_phase: `in_crash`
- current_domain: `structural_integrity_retention_and_egress`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_towing_connection`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`1`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `견인장치 및 연결장치` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`

## 가스운송장치
- document_id: `xml_kmvss-kmvss_art_33_047`
- current_phase: `post_crash`
- current_domain: `fire_electrical_and_energy_storage_safety`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_gas_transport`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `가스운송장치` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`

## 배기관
- document_id: `xml_kmvss-kmvss_art_37_051`
- current_phase: `post_crash`
- current_domain: `fire_electrical_and_energy_storage_safety`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_exhaust`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `배기관` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`

## 좌석등받이
- document_id: `xml_kmvss-kmvss_art_98_147`
- current_phase: `in_crash`
- current_domain: `occupant_protection_and_restraints`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_seat_back`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `좌석등받이` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`

## 접이식좌석
- document_id: `xml_kmvss-kmvss_art_25_038`
- current_phase: `in_crash`
- current_domain: `occupant_protection_and_restraints`
- lane: `umbrella_adjudication_candidate`
- umbrella_family: `umbrella_folding_seat`
- intentional_retain: `False`
- retain_reason: `None`
- policy_basis: `kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate`
- reference_repo_pattern: `wiki_llm_safety:fixed_slice_holdout_and_helper_script`
- residual_summary: cross=`0` / other=`0`
- local_text_weakness: `high`
- taxonomy_fit: umbrella title needs adjudication
- risk_note: `접이식좌석` still looks like an umbrella family that can be pushed further with family priors
- final_decision_kind: `classification improvement target`
