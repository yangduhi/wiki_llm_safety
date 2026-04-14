from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any

from wiki_obsidian.kmvss_lexicon import load_kmvss_signal_lexicon
from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.text import compact_classifier_text, normalize_classifier_text, slugify

# Generic registries are kept together near the top of the file so the main
# classification surface stays easy to inspect and review.
GENERIC_PRE_CRASH_HINTS = (
    "aeb",
    "aebs",
    "automatic emergency braking",
    "advanced emergency braking",
    "forward collision warning",
    "fcw",
    "lane support",
    "lane departure",
    "electronic stability control",
    "esc",
    "rear visibility",
    "collision avoidance",
    "pedestrian detection",
    "vru detection",
)

GENERIC_IN_CRASH_HINTS = (
    "occupant crash protection",
    "occupant protection",
    "restraint",
    "seat belt",
    "air bag",
    "airbag",
    "frontal impact",
    "frontal collision protection",
    "side impact",
    "lateral collision protection",
    "ejection mitigation",
    "door retention",
    "door locks",
    "latch",
    "hinge",
    "impact",
    "rollover",
)

GENERIC_POST_CRASH_HINTS = (
    "post-crash",
    "post crash",
    "after crash",
    "emergency call",
    "accident emergency call",
    "ecall",
    "event data recorder",
    "edr",
    "rescue",
    "egress",
    "flammability",
    "interior flammability",
    "electrolyte spillage",
    "electrical shock protection",
    "electric shock protection",
    "high voltage",
    "high-voltage",
    "electrical isolation",
    "isolation resistance",
)

GENERIC_ADMIN_HINTS = (
    "type approval",
    "conformity",
    "market surveillance",
    "recall",
    "framework",
    "governance",
    "authority",
    "agreement",
    "wp.29",
)

EXPLICIT_PHASE_OVERRIDES = {
    "fmvss 111": "pre_crash",
    "rear visibility": "pre_crash",
    "fmvss 126": "pre_crash",
    "electronic stability control systems": "pre_crash",
    "unece r131": "pre_crash",
    "unece r152": "pre_crash",
    "advanced emergency braking systems": "pre_crash",
    "advanced emergency braking system": "pre_crash",
    "aeb for pedestrian": "pre_crash",
    "fmvss 208": "in_crash",
    "occupant crash protection": "in_crash",
    "fmvss 206": "in_crash",
    "door locks and door retention components": "in_crash",
    "door retention": "in_crash",
    "fmvss 214": "in_crash",
    "side impact protection": "in_crash",
    "fmvss 226": "in_crash",
    "ejection mitigation": "in_crash",
    "frontal collision protection": "in_crash",
    "lateral collision protection": "in_crash",
    "fmvss 302": "post_crash",
    "flammability of interior materials": "post_crash",
    "fmvss 305a": "post_crash",
    "electric-powered vehicles electrolyte spillage and electrical shock protection": "post_crash",
    "kmvss_art_112_186": "post_crash",
    "구동축전지": "post_crash",
    "연료장치": "post_crash",
    "고전원전기장치": "post_crash",
    "unece r100": "post_crash",
    "electric power train": "post_crash",
    "accident emergency call systems": "post_crash",
    "unece r144": "post_crash",
    "fmvss 205": "cross_phase",
    "glazing materials": "cross_phase",
    "창유리": "cross_phase",
    "regulation (eu) 2019/2144": "cross_phase",
    "general safety regulation": "cross_phase",
    "regulation (eu) 2018/858": "non_phase_admin",
    "type approval and market surveillance framework": "non_phase_admin",
    "기준적용의 특례": "non_phase_admin",
    "장치 기준에 관한 특례": "non_phase_admin",
    "시험방법 등의 고시": "non_phase_admin",
    "비상탈출장치": "post_crash",
    "전조등": "pre_crash",
    "1958 agreement": "non_phase_admin",
    "wp.29 introduction": "non_phase_admin",
}

GENERIC_DOMAIN_HINTS = {
    "crash_avoidance_and_vehicle_control": (
        "aeb",
        "aebs",
        "electronic stability control",
        "collision avoidance",
        "rear visibility",
        "lane",
    ),
    "occupant_protection_and_restraints": (
        "occupant",
        "restraint",
        "seat belt",
        "airbag",
        "frontal impact",
        "side impact",
        "frontal collision protection",
        "lateral collision protection",
    ),
    "structural_integrity_retention_and_egress": (
        "door",
        "ejection",
        "hinge",
        "latch",
        "egress",
    ),
    "visibility_glazing_and_driver_information": (
        "glazing",
        "windscreen",
        "windshield",
        "visibility",
    ),
    "fire_electrical_and_energy_storage_safety": (
        "electrolyte",
        "electrical shock",
        "electric shock",
        "high voltage",
        "electrical isolation",
        "battery",
        "fuel system",
        "electric power train",
    ),
    "post_crash_response_and_data": ("ecall", "emergency call", "event data recorder", "edr", "rescue"),
    "vru_protection": ("pedestrian protection", "headform"),
    "interior_materials_and_fire": ("flammability", "interior material"),
}

TOPIC_KEYWORDS = {
    "pedestrian_aeb": ("pedestrian", "aeb"),
    "rear_visibility": ("rear visibility",),
    "electronic_stability_control": ("electronic stability control",),
    "frontal_impact": ("occupant crash protection", "frontal impact", "frontal collision protection"),
    "side_impact": ("lateral collision protection", "side impact protection"),
    "door_retention": ("door retention", "door locks"),
    "ejection_mitigation": ("ejection mitigation",),
    "glazing_visibility": ("glazing materials", "windscreen", "windshield"),
    "headlamp_visibility": ("전조등",),
    "event_data_recorder": ("event data recorder", "edr"),
    "emergency_call_systems": ("accident emergency call", "emergency call", "ecall"),
    "post_crash_electrical_safety": ("electrolyte spillage", "electrical shock protection", "high voltage", "구동축전지", "고전압", "전기충격", "절연"),
    "post_crash_fire_stability": ("flammability of interior materials", "flammability", "화재"),
    "general_vehicle_safety": ("general safety regulation",),
    "fuel_system_integrity": ("연료장치", "연료탱크", "수소"),
    "automated_driving_assist": ("자율주행", "부분 자율주행", "자동긴급제동", "비상자동제동"),
    "braking_control": ("제동장치", "제동성능", "급제동"),
    "post_crash_egress": ("비상탈출장치", "탈출"),
    "administrative_exception": ("기준적용의 특례", "장치 기준에 관한 특례", "고시"),
}

PHASES = ("pre_crash", "in_crash", "post_crash", "cross_phase", "non_phase_admin")

ATTACHMENT_BUCKET_PRIORS = {
    "lighting_photometric_reflector_signaling": {
        "phase": {"pre_crash": 5},
        "domain": {"visibility_glazing_and_driver_information": 6},
    },
    "braking_performance_hardware": {
        "phase": {"pre_crash": 5},
        "domain": {"crash_avoidance_and_vehicle_control": 6},
    },
    "emc_electrical_compatibility": {
        "phase": {"non_phase_admin": 5},
        "domain": {},
    },
    "labeling_marking_indication": {
        "phase": {"non_phase_admin": 4},
        "domain": {},
    },
    "tire_wheel_hose_running_gear": {
        "phase": {},
        "domain": {},
    },
}

ARTICLE_BUCKET_PRIORS = {
    "body_visibility_signaling": {
        "phase": {"pre_crash": 4},
        "domain": {"visibility_glazing_and_driver_information": 4},
    },
    "powertrain_running_gear": {
        "phase": {"pre_crash": 4},
        "domain": {"crash_avoidance_and_vehicle_control": 4},
    },
    "braking": {
        "phase": {"pre_crash": 3},
        "domain": {"crash_avoidance_and_vehicle_control": 4},
    },
    "definitions": {
        "phase": {"non_phase_admin": 4},
        "domain": {"other_or_review": 3},
    },
    "special_exceptions": {
        "phase": {"non_phase_admin": 5},
        "domain": {"other_or_review": 4},
    },
    "software_cyber": {
        "phase": {"non_phase_admin": 4},
        "domain": {"other_or_review": 3},
    },
    "umbrella_instrument_panel": {
        "phase": {"pre_crash": 4},
        "domain": {"visibility_glazing_and_driver_information": 4},
    },
    "umbrella_towing_connection": {
        "phase": {"in_crash": 4},
        "domain": {"structural_integrity_retention_and_egress": 4},
    },
    "umbrella_gas_transport": {
        "phase": {"post_crash": 4},
        "domain": {"fire_electrical_and_energy_storage_safety": 5},
    },
    "umbrella_exhaust": {
        "phase": {"post_crash": 4},
        "domain": {"fire_electrical_and_energy_storage_safety": 4},
    },
    "umbrella_seat_back": {
        "phase": {"in_crash": 4},
        "domain": {"occupant_protection_and_restraints": 5},
    },
    "umbrella_folding_seat": {
        "phase": {"in_crash": 4},
        "domain": {"occupant_protection_and_restraints": 5},
    },
    "secondary_visibility_signaling": {
        "phase": {"pre_crash": 4},
        "domain": {"visibility_glazing_and_driver_information": 4},
    },
    "secondary_vehicle_control": {
        "phase": {"pre_crash": 4},
        "domain": {"crash_avoidance_and_vehicle_control": 4},
    },
    "secondary_dimension_scope": {},
    "secondary_efficiency_range": {},
}

ARTICLE_BUCKET_KEYWORDS = {
    "glazing_cross_phase_intentional": ("창유리 등", "창유리의 안전성 등"),
    "body_visibility_signaling": ("간접시계장치", "경광등", "사이렌", "끝단표시등", "후미등", "옆면표시등", "번호등", "전조등", "등화", "광원", "광도"),
    "powertrain_running_gear": ("원동기 및 동력전달장치", "원동기 출력", "주행장치", "접지부분", "접지압력", "최대안전경사각도", "도난방지장치"),
    "braking": ("제동장치",),
    "definitions": ("정의", "용어"),
    "special_exceptions": ("기준적용의 특례", "특례", "고시", "적용", "조사", "인증"),
    "software_cyber": ("소프트웨어", "사이버보안"),
    "umbrella_instrument_panel": ("계기판넬",),
    "umbrella_towing_connection": ("견인장치 및 연결장치",),
    "umbrella_gas_transport": ("가스운송장치",),
    "umbrella_exhaust": ("배기관",),
    "umbrella_seat_back": ("좌석등받이",),
    "umbrella_folding_seat": ("접이식좌석",),
    "secondary_visibility_signaling": ("주간주행등", "후퇴등", "차폭등", "후방추돌경고등", "비상점멸표시등"),
    "secondary_vehicle_control": ("가속제어장치",),
    "secondary_dimension_scope": ("차량총중량등", "길이ㆍ너비 및 높이", "길이 너비 및 높이", "승차장치"),
    "secondary_efficiency_range": ("에너지소비효율", "1회 충전 후 주행가능거리"),
}

STABLE_RETAIN_SUBJECTS = {
    "창유리 등",
    "창유리의 안전성 등",
    "정의",
    "기준적용의 특례",
}

TEMPORARY_RETAIN_SUBJECTS = {
    "물품적재장치",
    "입석",
    "승차정원 및 최대적재량",
}

MIXED_KEEP_REVIEW_SUBJECTS = {
    "사이버보안",
    "소프트웨어",
}

SECONDARY_UMBRELLA_PROMOTABLE_SUBJECTS = {
    "주간주행등",
    "후퇴등",
    "차폭등",
    "후방추돌경고등",
    "비상점멸표시등",
    "가속제어장치",
}

SECONDARY_UMBRELLA_KEEP_REVIEW_SUBJECTS = {
    "길이ㆍ너비 및 높이",
    "길이 너비 및 높이",
    "승차장치",
}

SECONDARY_UMBRELLA_NEEDS_POLICY_SUBJECTS = {
    "차량총중량등",
    "에너지소비효율",
    "1회 충전 후 주행가능거리",
}

TITLE_ONLY_EXPLICIT_PHRASES = {"창유리", "glazing materials"}

SECONDARY_TOPIC_HINTS = (
    ("pedestrian", "pedestrian"),
    ("vru", "vru"),
    ("seat belt", "seat_belts"),
    ("airbag", "airbags"),
    ("air bag", "airbags"),
    ("door", "doors"),
    ("egress", "egress"),
    ("glazing", "glazing"),
    ("windscreen", "windscreen"),
    ("visibility", "visibility"),
    ("battery", "battery"),
    ("electrical", "electrical_isolation"),
    ("high voltage", "high_voltage"),
    ("electrolyte", "electrolyte_spillage"),
    ("rescue", "rescue_response"),
    ("고전압", "high_voltage"),
    ("전해액", "electrolyte_spillage"),
    ("절연", "electrical_isolation"),
    ("화재", "fire"),
    ("자율주행", "automated_driving"),
    ("제동", "braking"),
    ("연료", "fuel"),
    ("특례", "special_exception"),
)

BROWSE_BUCKET_HINTS = (
    ("frontal", "frontal_impact"),
    ("정면충돌", "frontal_impact"),
    ("side", "side_impact"),
    ("측면충돌", "side_impact"),
    ("rear", "rear_impact"),
    ("후방추돌", "rear_impact"),
    ("rollover", "rollover"),
    ("전복", "rollover"),
    ("occupant", "occupant_restraints"),
    ("seat belt", "occupant_restraints"),
    ("안전띠", "occupant_restraints"),
    ("compartment", "occupant_compartment_integrity"),
    ("door", "door_retention"),
    ("문", "door_retention"),
    ("ejection", "anti_ejection"),
    ("이탈", "anti_ejection"),
    ("head", "head_impact"),
    ("child", "child_restraints"),
    ("어린이", "child_restraints"),
    ("seat", "seat_systems"),
    ("좌석", "seat_systems"),
    ("steering", "steering_control"),
    ("조향", "steering_control"),
    ("glazing", "glazing_retention"),
    ("창유리", "glazing_retention"),
    ("fuel", "fuel_system_integrity"),
    ("연료", "fuel_system_integrity"),
    ("fire", "fire_risk"),
    ("화재", "fire_risk"),
    ("pedestrian", "pedestrian_protection"),
    ("보행자", "pedestrian_protection"),
)


def classify_text(
    text: str,
    *,
    collection: str | None = None,
    jurisdiction: str | None = None,
    regulatory_layer: str | None = None,
    project_root: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = classify_text_with_trace(
        text,
        collection=collection,
        jurisdiction=jurisdiction,
        regulatory_layer=regulatory_layer,
        project_root=project_root,
        metadata=metadata,
    )
    return result["decision"]


def classify_text_with_trace(
    text: str,
    *,
    collection: str | None = None,
    jurisdiction: str | None = None,
    regulatory_layer: str | None = None,
    project_root: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {**(metadata or {}), "collection": collection}

    # Stage 1: normalize raw input plus caller-provided metadata.
    normalized_text = normalize_classifier_text(text).lower()
    compact_text = compact_classifier_text(text).lower()

    title = str(metadata.get("title") or "")
    subject = str(metadata.get("subject") or "")
    parent_title = str(metadata.get("parent_title") or "")
    attachment_section = str(metadata.get("attachment_section") or "")
    document_kind = str(metadata.get("document_kind") or "")
    attachment_bucket = str(metadata.get("attachment_bucket") or "")
    is_attachment = bool(metadata.get("is_attachment") or document_kind == "attachment")
    is_table_like_row = bool(metadata.get("is_table_like_row"))
    reference_articles = [str(item) for item in (metadata.get("reference_articles") or []) if item]
    statement = str(metadata.get("statement") or "")
    basis = str(metadata.get("basis") or "")
    parent_clause_text = str(metadata.get("parent_clause_text") or "")

    normalized_title = normalize_classifier_text(title).lower()
    normalized_subject = normalize_classifier_text(subject).lower()
    normalized_parent = normalize_classifier_text(parent_title).lower()
    normalized_attachment_section = normalize_classifier_text(attachment_section).lower()
    normalized_statement = normalize_classifier_text(statement).lower()
    normalized_basis = normalize_classifier_text(basis).lower()
    normalized_parent_clause_text = normalize_classifier_text(parent_clause_text).lower()

    title_candidates = [
        candidate
        for candidate in (normalized_title, normalized_subject, normalized_parent, normalized_attachment_section)
        if candidate
    ]
    title_compact_candidates = [compact_classifier_text(candidate) for candidate in title_candidates]
    combined_title_text = " ".join(title_candidates)
    local_body_text = _strip_inherited_prefixes(
        " ".join(part for part in (normalized_statement, normalized_basis) if part),
        inherited_candidates=[normalized_title, normalized_subject, normalized_parent, normalized_attachment_section],
    )

    matched_signals: list[dict[str, Any]] = []
    phase_scores: Counter[str] = Counter()
    domain_scores: Counter[str] = Counter()
    topic_scores: Counter[str] = Counter()
    title_prior: list[str] = []
    parent_prior: list[str] = []
    inherited_context_sources: list[str] = []
    fallback_reason = ""
    override_phrase: str | None = None

    # KMVSS article handling is intentionally collection-aware so the current
    # KR article/attachment behavior stays stable without leaking into the
    # global path.
    is_article = collection == "xml_kmvss" and not is_attachment
    article_bucket = (
        _article_bucket_from_subject(
            subject=normalized_subject or normalized_title,
            title=normalized_title,
            parent_title=normalized_parent,
        )
        if is_article
        else ""
    )
    review_lane = (
        _review_lane_metadata(
            subject=normalized_subject or normalized_title,
            article_bucket=article_bucket,
            is_article=is_article,
        )
        if is_article
        else {
            "umbrella_family": None,
            "secondary_umbrella_family": None,
            "review_lane_type": None,
            "intentional_retain": False,
            "retain_reason": None,
            "promotion_status": None,
            "promotion_reason": None,
            "retain_stability": None,
            "needs_policy_decision": False,
            "policy_basis": None,
            "reference_repo_pattern": None,
        }
    )
    is_short_clause = (
        _is_short_clause(
            local_body_text=local_body_text,
            parent_clause_text=normalized_parent_clause_text,
            title_candidates=title_candidates,
        )
        if is_article
        else False
    )

    # Stage 2: generic scoring and explicit override handling.
    if regulatory_layer in {"framework_admin", "conformity_assessment", "market_surveillance_recall"}:
        phase_scores["non_phase_admin"] += 10
        matched_signals.append(
            {"source": "regulatory_layer", "kind": "phase", "target": "non_phase_admin", "weight": 10}
        )

    explicit_match = _match_explicit_phase_override(
        normalized_text=normalized_text,
        compact_text=compact_text,
        title_text=combined_title_text,
        title_compact=" ".join(title_compact_candidates),
        document_id=str(metadata.get("document_id") or ""),
        metadata=metadata,
    )
    if explicit_match:
        override_phrase = explicit_match["phrase"]
        phase_scores[explicit_match["phase"]] += 12
        matched_signals.append(
            {
                "source": "explicit_override",
                "kind": "phase",
                "target": explicit_match["phase"],
                "weight": 12,
                "matched_phrase": override_phrase,
            }
        )

    _score_generic_phases(normalized_text, phase_scores, matched_signals)
    _score_generic_domains(normalized_text, domain_scores, matched_signals)
    _score_topics(normalized_text, topic_scores, matched_signals)

    # Stage 3: collection-specific priors and inheritance.
    if _should_apply_kmvss_logic(
        collection=collection,
        jurisdiction=jurisdiction,
        normalized_text=normalized_text,
        combined_title_text=combined_title_text,
    ):
        lexicon = load_kmvss_signal_lexicon(project_root)
        _apply_attachment_bucket_prior(
            attachment_bucket=attachment_bucket,
            subject=normalized_subject,
            phase_scores=phase_scores,
            domain_scores=domain_scores,
            matched_signals=matched_signals,
            title_prior=title_prior,
            is_attachment=is_attachment,
        )
        _apply_article_bucket_prior(
            article_bucket=article_bucket,
            phase_scores=phase_scores,
            domain_scores=domain_scores,
            matched_signals=matched_signals,
            title_prior=title_prior,
            is_article=is_article,
        )
        _apply_kmvss_weak_priors(
            lexicon=lexicon,
            title_candidates=title_candidates,
            title_compact_candidates=title_compact_candidates,
            phase_scores=phase_scores,
            domain_scores=domain_scores,
            matched_signals=matched_signals,
            title_prior=title_prior,
            parent_prior=parent_prior,
        )
        _score_kmvss_signals(
            lexicon=lexicon,
            title_candidates=title_candidates,
            title_compact_candidates=title_compact_candidates,
            metadata=metadata,
            phase_scores=phase_scores,
            domain_scores=domain_scores,
            topic_scores=topic_scores,
            matched_signals=matched_signals,
        )
        _apply_short_clause_inheritance(
            is_short_clause=is_short_clause,
            local_body_text=local_body_text,
            article_bucket=article_bucket,
            title=normalized_title,
            subject=normalized_subject,
            parent_title=normalized_parent,
            parent_clause_text=normalized_parent_clause_text,
            phase_scores=phase_scores,
            domain_scores=domain_scores,
            matched_signals=matched_signals,
            inherited_context_sources=inherited_context_sources,
            is_article=is_article,
        )

    # Stage 4: precedence resolution.
    phase_breakdown = _signal_breakdown(matched_signals, kind="phase")
    domain_breakdown = _signal_breakdown(matched_signals, kind="domain")
    local_phase_signal_weight = _local_body_signal_weight(matched_signals, is_attachment=is_attachment)
    phase, fallback_reason = _select_phase(
        phase_scores,
        fallback_reason=fallback_reason,
        metadata=metadata,
        phase_breakdown=phase_breakdown,
        local_body_signal_weight=local_phase_signal_weight,
    )
    domain, domain_fallback = _select_domain(domain_scores, phase=phase)
    if domain_fallback:
        fallback_reason = f"{fallback_reason};{domain_fallback}" if fallback_reason else domain_fallback
    if review_lane["review_lane_type"] == "stable_retain":
        if review_lane["retain_reason"] == "true_multi_phase_glazing_scope":
            phase = "cross_phase"
            fallback_reason = "stable_retain_cross_phase"
            domain = domain if domain != "other_or_review" else (_bucket_primary_target(article_bucket, kind="domain") or domain)
        else:
            if local_phase_signal_weight < 3:
                phase = "non_phase_admin"
            domain = "other_or_review"
            fallback_reason = "stable_retain_policy"
    elif review_lane["review_lane_type"] == "temporary_retain":
        if phase == "cross_phase" and local_phase_signal_weight < 2:
            fallback_reason = "temporary_retain_review_lane"
        domain = "other_or_review"
    elif review_lane["review_lane_type"] == "mixed_keep_review" and local_phase_signal_weight < 3:
        phase = "non_phase_admin"
        domain = "other_or_review"
        fallback_reason = "mixed_review_lane"
    elif review_lane["review_lane_type"] == "secondary_umbrella_promotable" and _is_secondary_promotable_bucket(article_bucket):
        phase = _bucket_primary_target(article_bucket, kind="phase") or phase
        domain = _bucket_primary_target(article_bucket, kind="domain") or domain
        fallback_reason = "promotion_candidate_family_prior"
    elif review_lane["review_lane_type"] == "secondary_umbrella_keep_review":
        domain = "other_or_review"
        if phase == "cross_phase" and local_phase_signal_weight < 2:
            fallback_reason = "secondary_keep_review_lane"
    elif review_lane["review_lane_type"] == "secondary_umbrella_needs_policy_decision":
        domain = "other_or_review"
        fallback_reason = "needs_policy_decision"

    # Stage 5: outward-facing derived fields.
    primary_topic = _select_primary_topic(topic_scores, normalized_text, title_candidates, phase, domain)
    secondary_topics = _secondary_topics(
        normalized_text,
        primary_topic=primary_topic,
        extra_keywords=[subject, title, parent_title, attachment_section, *reference_articles],
    )
    browse_buckets = _browse_buckets(normalized_text, phase=phase)
    legacy_domain = _legacy_domain(phase)

    decision = {
        "phase": phase,
        "functional_domain": [domain],
        "primary_topic": primary_topic,
        "secondary_topics": secondary_topics,
        "browse_buckets": browse_buckets,
        "legacy_domain": legacy_domain,
        "source_collection": collection,
        "jurisdiction": jurisdiction,
        "regulatory_layer": regulatory_layer,
    }

    # Stage 6: preserve the current trace contract.
    trace = {
        "normalized_text": normalized_text,
        "title_prior": title_prior,
        "parent_prior": parent_prior,
        "matched_signals": matched_signals,
        "override_phrase": override_phrase,
        "phase_scores": dict(phase_scores),
        "domain_scores": dict(domain_scores),
        "phase_signal_breakdown": phase_breakdown,
        "domain_signal_breakdown": domain_breakdown,
        "article_bucket": article_bucket or None,
        "umbrella_family": review_lane["umbrella_family"],
        "secondary_umbrella_family": review_lane["secondary_umbrella_family"],
        "review_lane_type": review_lane["review_lane_type"],
        "intentional_retain": review_lane["intentional_retain"],
        "retain_reason": review_lane["retain_reason"],
        "promotion_status": review_lane["promotion_status"],
        "promotion_reason": review_lane["promotion_reason"],
        "retain_stability": review_lane["retain_stability"],
        "needs_policy_decision": review_lane["needs_policy_decision"],
        "policy_basis": review_lane["policy_basis"],
        "reference_repo_pattern": review_lane["reference_repo_pattern"],
        "is_short_clause": is_short_clause,
        "local_body_signal_weight": local_phase_signal_weight,
        "inherited_context_sources": inherited_context_sources,
        "is_attachment": is_attachment,
        "is_table_like": is_table_like_row,
        "reference_articles": reference_articles,
        "fallback_reason": fallback_reason or None,
        "final_decision": {
            "phase": phase,
            "functional_domain": domain,
            "primary_topic": primary_topic,
        },
    }
    return {"decision": decision, "trace": trace}


def classify_phase_from_notes(
    question: str,
    *,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    result = classify_text(question, project_root=settings.paths.project_root)
    matches: list[str] = []
    for path in sorted(settings.paths.regulation_units_root.rglob("*.md")):
        if path.name in {"README.md", ".gitkeep"}:
            continue
        frontmatter, body = parse_frontmatter_file(path)
        haystack = " ".join(
            [
                str(frontmatter.get("title") or ""),
                str(frontmatter.get("summary") or ""),
                body,
            ]
        ).lower()
        tokens = {token for token in re.findall(r"[a-z0-9_]+", question.lower()) if len(token) > 2}
        score = sum(1 for token in tokens if token in haystack)
        if score > 0:
            matches.append(str(path.relative_to(settings.paths.project_root)).replace("\\", "/"))
    return result | {"question": question, "matched_notes": matches[:8]}


def _should_apply_kmvss_logic(
    *,
    collection: str | None,
    jurisdiction: str | None,
    normalized_text: str,
    combined_title_text: str,
) -> bool:
    return bool(
        collection == "xml_kmvss"
        or jurisdiction == "KR"
        or _contains_hangul(normalized_text)
        or _contains_hangul(combined_title_text)
    )


def _score_generic_phases(text: str, phase_scores: Counter[str], matched_signals: list[dict[str, Any]]) -> None:
    for signal in GENERIC_PRE_CRASH_HINTS:
        if signal in text:
            phase_scores["pre_crash"] += 2
            matched_signals.append({"source": "generic", "kind": "phase", "target": "pre_crash", "signal": signal, "weight": 2})
    for signal in GENERIC_IN_CRASH_HINTS:
        if signal in text:
            phase_scores["in_crash"] += 2
            matched_signals.append({"source": "generic", "kind": "phase", "target": "in_crash", "signal": signal, "weight": 2})
    for signal in GENERIC_POST_CRASH_HINTS:
        if signal in text:
            phase_scores["post_crash"] += 2
            matched_signals.append({"source": "generic", "kind": "phase", "target": "post_crash", "signal": signal, "weight": 2})
    for signal in GENERIC_ADMIN_HINTS:
        if signal in text:
            phase_scores["non_phase_admin"] += 3
            matched_signals.append({"source": "generic", "kind": "phase", "target": "non_phase_admin", "signal": signal, "weight": 3})


def _score_generic_domains(text: str, domain_scores: Counter[str], matched_signals: list[dict[str, Any]]) -> None:
    for domain, signals in GENERIC_DOMAIN_HINTS.items():
        for signal in signals:
            if signal in text:
                domain_scores[domain] += 2
                matched_signals.append({"source": "generic", "kind": "domain", "target": domain, "signal": signal, "weight": 2})


def _score_topics(text: str, topic_scores: Counter[str], matched_signals: list[dict[str, Any]]) -> None:
    for topic, signals in TOPIC_KEYWORDS.items():
        if any(signal in text for signal in signals):
            topic_scores[topic] += 3
            matched_signals.append({"source": "topic", "kind": "topic", "target": topic, "weight": 3})


def _strip_inherited_prefixes(text: str, *, inherited_candidates: list[str]) -> str:
    cleaned = text
    for candidate in inherited_candidates:
        normalized_candidate = normalize_classifier_text(candidate).strip()
        if normalized_candidate and cleaned.startswith(normalized_candidate):
            cleaned = cleaned[len(normalized_candidate) :].strip()
    return cleaned


def _article_bucket_from_subject(*, subject: str, title: str, parent_title: str) -> str:
    combined = " ".join(part for part in (subject, title, parent_title) if part)
    for bucket, signals in ARTICLE_BUCKET_KEYWORDS.items():
        if any(signal in combined for signal in signals):
            return bucket
    return "umbrella_titles_with_weak_unit_text"


def _deprecated_review_lane_metadata_legacy(*, subject: str, article_bucket: str, is_article: bool) -> dict[str, Any]:
    if not is_article:
        return {
            "umbrella_family": None,
            "review_lane_type": None,
            "intentional_retain": False,
            "retain_reason": None,
            "policy_basis": None,
            "reference_repo_pattern": None,
        }

    if article_bucket == "glazing_cross_phase_intentional":
        return {
            "umbrella_family": article_bucket,
            "review_lane_type": "intentional_cross_phase",
            "intentional_retain": True,
            "retain_reason": "document_scope_multi_phase",
            "policy_basis": "kmvss_round2c_review_lane_policy.intentional_cross_phase",
            "reference_repo_pattern": "wiki_llm_safety:pilot_csv_jsonl_and_policy_note",
        }

    if subject in {"정의", "기준적용의 특례", "물품적재장치", "입석", "승차정원 및 최대적재량"}:
        return {
            "umbrella_family": article_bucket or "intentional_review_lane",
            "review_lane_type": "intentional_other_or_review",
            "intentional_retain": True,
            "retain_reason": "taxonomy_gap_or_governance_scope",
            "policy_basis": "kmvss_round2c_review_lane_policy.intentional_other_or_review",
            "reference_repo_pattern": "wiki_llm_safety:policy_note_plus_review_register",
        }

    if subject in {"사이버보안", "소프트웨어"}:
        return {
            "umbrella_family": article_bucket or "software_cyber",
            "review_lane_type": "mixed_or_ambiguous_keep_for_review",
            "intentional_retain": True,
            "retain_reason": "mixed_technical_admin_scope",
            "policy_basis": "kmvss_round2c_review_lane_policy.mixed_or_ambiguous_keep_for_review",
            "reference_repo_pattern": "wiki_llm_safety:trace_diff_and_manual_review_queue",
        }

    if article_bucket in {
        "umbrella_instrument_panel",
        "umbrella_towing_connection",
        "umbrella_gas_transport",
        "umbrella_exhaust",
        "umbrella_seat_back",
        "umbrella_folding_seat",
        "umbrella_titles_with_weak_unit_text",
    }:
        return {
            "umbrella_family": article_bucket,
            "review_lane_type": "umbrella_adjudication_candidate",
            "intentional_retain": False,
            "retain_reason": None,
            "policy_basis": "kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate",
            "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
        }

    return {
        "umbrella_family": article_bucket or None,
        "review_lane_type": None,
        "intentional_retain": False,
        "retain_reason": None,
        "policy_basis": None,
        "reference_repo_pattern": None,
    }


def _deprecated_review_lane_metadata_round2c(*, subject: str, article_bucket: str, is_article: bool) -> dict[str, Any]:
    if not is_article:
        return {
            "umbrella_family": None,
            "review_lane_type": None,
            "intentional_retain": False,
            "retain_reason": None,
            "policy_basis": None,
            "reference_repo_pattern": None,
        }

    if article_bucket == "glazing_cross_phase_intentional":
        return {
            "umbrella_family": "glazing_cross_phase",
            "review_lane_type": "intentional_cross_phase",
            "intentional_retain": True,
            "retain_reason": "true_multi_phase_glazing_scope",
            "policy_basis": "kmvss_round2c_review_lane_policy.intentional_cross_phase",
            "reference_repo_pattern": "wiki_llm_safety:pilot_csv+jsonl_and_policy_note",
        }

    if subject in {"정의", "기준적용의 특례", "물품적재장치", "입석", "승차정원 및 최대적재량"}:
        return {
            "umbrella_family": article_bucket or "intentional_review_lane",
            "review_lane_type": "intentional_other_or_review",
            "intentional_retain": True,
            "retain_reason": "taxonomy_or_governance_review_lane",
            "policy_basis": "kmvss_round2c_review_lane_policy.intentional_other_or_review",
            "reference_repo_pattern": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
        }

    if subject in {"사이버보안", "소프트웨어"}:
        return {
            "umbrella_family": article_bucket or "software_cyber",
            "review_lane_type": "mixed_or_ambiguous_keep_for_review",
            "intentional_retain": True,
            "retain_reason": "mixed_technical_admin_scope",
            "policy_basis": "kmvss_round2c_review_lane_policy.mixed_or_ambiguous_keep_for_review",
            "reference_repo_pattern": "wiki_llm_safety:review_register_plus_trace_diff",
        }

    umbrella_families = {
        "umbrella_instrument_panel",
        "umbrella_towing_connection",
        "umbrella_gas_transport",
        "umbrella_exhaust",
        "umbrella_seat_back",
        "umbrella_folding_seat",
    }
    if article_bucket in umbrella_families:
        return {
            "umbrella_family": article_bucket,
            "review_lane_type": "umbrella_adjudication_candidate",
            "intentional_retain": False,
            "retain_reason": None,
            "policy_basis": "kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate",
            "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
        }

    return {
        "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
        "review_lane_type": "umbrella_adjudication_candidate",
        "intentional_retain": False,
        "retain_reason": None,
        "policy_basis": "kmvss_round2c_review_lane_policy.umbrella_adjudication_candidate",
        "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
    }


def _review_lane_defaults() -> dict[str, Any]:
    return {
        "umbrella_family": None,
        "secondary_umbrella_family": None,
        "review_lane_type": None,
        "intentional_retain": False,
        "retain_reason": None,
        "promotion_status": None,
        "promotion_reason": None,
        "retain_stability": None,
        "needs_policy_decision": False,
        "policy_basis": None,
        "reference_repo_pattern": None,
    }


def _review_lane_metadata(*, subject: str, article_bucket: str, is_article: bool) -> dict[str, Any]:
    if not is_article:
        return _review_lane_defaults()

    if article_bucket == "glazing_cross_phase_intentional":
        return {
            "umbrella_family": "glazing_cross_phase",
            "secondary_umbrella_family": None,
            "review_lane_type": "stable_retain",
            "intentional_retain": True,
            "retain_reason": "true_multi_phase_glazing_scope",
            "promotion_status": "stable_retain",
            "promotion_reason": "true_multi_phase_document_scope",
            "retain_stability": "stable_retain",
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.stable_retain",
            "reference_repo_pattern": "wiki_llm_safety:pilot_csv+jsonl_and_policy_note",
        }

    if subject in STABLE_RETAIN_SUBJECTS:
        family = article_bucket or ("definitions" if subject == "정의" else "special_exceptions")
        return {
            "umbrella_family": family,
            "secondary_umbrella_family": None,
            "review_lane_type": "stable_retain",
            "intentional_retain": True,
            "retain_reason": "taxonomy_or_governance_review_lane",
            "promotion_status": "stable_retain",
            "promotion_reason": "policy_grounded_retain",
            "retain_stability": "stable_retain",
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.stable_retain",
            "reference_repo_pattern": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
        }

    if subject in TEMPORARY_RETAIN_SUBJECTS:
        return {
            "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
            "secondary_umbrella_family": None,
            "review_lane_type": "temporary_retain",
            "intentional_retain": True,
            "retain_reason": "weak_local_text_review_lane",
            "promotion_status": "temporary_retain",
            "promotion_reason": "insufficient_local_evidence_for_safe_canonical_lowering",
            "retain_stability": "temporary_retain",
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.temporary_retain",
            "reference_repo_pattern": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
        }

    if subject in MIXED_KEEP_REVIEW_SUBJECTS:
        return {
            "umbrella_family": article_bucket or "software_cyber",
            "secondary_umbrella_family": None,
            "review_lane_type": "mixed_keep_review",
            "intentional_retain": True,
            "retain_reason": "mixed_technical_admin_scope",
            "promotion_status": "mixed_keep_review",
            "promotion_reason": "technical_admin_mix_requires_review",
            "retain_stability": "mixed_keep_review",
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.mixed_keep_review",
            "reference_repo_pattern": "wiki_llm_safety:review_register_plus_trace_diff",
        }

    if subject in SECONDARY_UMBRELLA_PROMOTABLE_SUBJECTS or article_bucket in {"secondary_visibility_signaling", "secondary_vehicle_control"}:
        return {
            "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
            "secondary_umbrella_family": article_bucket or None,
            "review_lane_type": "secondary_umbrella_promotable",
            "intentional_retain": False,
            "retain_reason": None,
            "promotion_status": "promotion_candidate",
            "promotion_reason": "family_prior_plus_parent_context_alignment",
            "retain_stability": None,
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.promotion_candidate",
            "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
        }

    if subject in SECONDARY_UMBRELLA_KEEP_REVIEW_SUBJECTS or "승차장치" in subject or (
        ("길이" in subject and "너비" in subject) and "차량총중량" not in subject
    ) or (
        article_bucket == "secondary_dimension_scope" and subject not in SECONDARY_UMBRELLA_NEEDS_POLICY_SUBJECTS
    ):
        return {
            "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
            "secondary_umbrella_family": "secondary_dimension_scope",
            "review_lane_type": "secondary_umbrella_keep_review",
            "intentional_retain": True,
            "retain_reason": "abstract_scope_requires_review",
            "promotion_status": "temporary_retain",
            "promotion_reason": "local_text_too_abstract_for_safe_canonical_lowering",
            "retain_stability": "temporary_retain",
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.temporary_retain",
            "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
        }

    if subject in SECONDARY_UMBRELLA_NEEDS_POLICY_SUBJECTS or "차량총중량" in subject or "에너지소비효율" in subject or "주행가능거리" in subject or article_bucket == "secondary_efficiency_range":
        return {
            "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
            "secondary_umbrella_family": "secondary_efficiency_range" if article_bucket == "secondary_efficiency_range" else article_bucket or None,
            "review_lane_type": "secondary_umbrella_needs_policy_decision",
            "intentional_retain": True,
            "retain_reason": "taxonomy_policy_decision_pending",
            "promotion_status": "needs_policy_decision",
            "promotion_reason": "taxonomy_or_policy_semantics_not_settled",
            "retain_stability": "temporary_retain",
            "needs_policy_decision": True,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.needs_policy_decision",
            "reference_repo_pattern": "wiki_llm_safety:operator_policy_and_fixed_slice_eval",
        }

    umbrella_families = {
        "umbrella_instrument_panel",
        "umbrella_towing_connection",
        "umbrella_gas_transport",
        "umbrella_exhaust",
        "umbrella_seat_back",
        "umbrella_folding_seat",
    }
    if article_bucket in umbrella_families:
        return {
            "umbrella_family": article_bucket,
            "secondary_umbrella_family": None,
            "review_lane_type": "promotion_candidate",
            "intentional_retain": False,
            "retain_reason": None,
            "promotion_status": "promotion_candidate",
            "promotion_reason": "umbrella_family_is_actionable",
            "retain_stability": None,
            "needs_policy_decision": False,
            "policy_basis": "kmvss_round2d_review_lane_promotion_policy.promotion_candidate",
            "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
        }

    return {
        "umbrella_family": article_bucket or "umbrella_titles_with_weak_unit_text",
        "secondary_umbrella_family": None,
        "review_lane_type": "promotion_candidate",
        "intentional_retain": False,
        "retain_reason": None,
        "promotion_status": "promotion_candidate",
        "promotion_reason": "umbrella_title_can_be_pushed_with_more_context",
        "retain_stability": None,
        "needs_policy_decision": False,
        "policy_basis": "kmvss_round2d_review_lane_promotion_policy.promotion_candidate",
        "reference_repo_pattern": "wiki_llm_safety:fixed_slice_holdout_and_helper_script",
    }


def _is_short_clause(*, local_body_text: str, parent_clause_text: str, title_candidates: list[str]) -> bool:
    trimmed = _strip_inherited_prefixes(local_body_text, inherited_candidates=title_candidates + [parent_clause_text])
    hangul_tokens = re.findall(r"[가-힣A-Za-z0-9]+", trimmed)
    governance_patterns = ("다음 각호", "다만", "경우", "해당", "적용된다", "적용하지 않는다")
    if len(trimmed) < 45:
        return True
    if len(hangul_tokens) <= 8:
        return True
    return any(pattern in trimmed for pattern in governance_patterns)


def _apply_attachment_bucket_prior(
    *,
    attachment_bucket: str,
    subject: str,
    phase_scores: Counter[str],
    domain_scores: Counter[str],
    matched_signals: list[dict[str, Any]],
    title_prior: list[str],
    is_attachment: bool,
) -> None:
    if not is_attachment:
        return
    payload = ATTACHMENT_BUCKET_PRIORS.get(attachment_bucket)
    if not payload:
        return
    title_prior.append(attachment_bucket)
    for phase, weight in (payload.get("phase") or {}).items():
        phase_scores[str(phase)] += int(weight)
        matched_signals.append(
            {
                "source": "attachment_bucket_prior",
                "kind": "phase",
                "target": str(phase),
                "signal": attachment_bucket,
                "weight": int(weight),
            }
        )
    for domain, weight in (payload.get("domain") or {}).items():
        domain_scores[str(domain)] += int(weight)
        matched_signals.append(
            {
                "source": "attachment_bucket_prior",
                "kind": "domain",
                "target": str(domain),
                "signal": attachment_bucket,
                "weight": int(weight),
            }
        )
    if attachment_bucket == "tire_wheel_hose_running_gear" and any(token in subject for token in ("표기", "표시", "식별표시")):
        phase_scores["non_phase_admin"] += 4
        matched_signals.append(
            {
                "source": "attachment_subject_prior",
                "kind": "phase",
                "target": "non_phase_admin",
                "signal": "표기/표시",
                "weight": 4,
            }
        )


def _apply_article_bucket_prior(
    *,
    article_bucket: str,
    phase_scores: Counter[str],
    domain_scores: Counter[str],
    matched_signals: list[dict[str, Any]],
    title_prior: list[str],
    is_article: bool,
) -> None:
    if not is_article:
        return
    payload = ARTICLE_BUCKET_PRIORS.get(article_bucket)
    if not payload:
        return
    title_prior.append(article_bucket)
    for phase, weight in (payload.get("phase") or {}).items():
        phase_scores[str(phase)] += int(weight)
        matched_signals.append(
            {
                "source": "article_bucket_prior",
                "kind": "phase",
                "target": str(phase),
                "signal": article_bucket,
                "weight": int(weight),
            }
        )
    for domain, weight in (payload.get("domain") or {}).items():
        domain_scores[str(domain)] += int(weight)
        matched_signals.append(
            {
                "source": "article_bucket_prior",
                "kind": "domain",
                "target": str(domain),
                "signal": article_bucket,
                "weight": int(weight),
            }
        )


def _apply_kmvss_weak_priors(
    *,
    lexicon: dict[str, Any],
    title_candidates: list[str],
    title_compact_candidates: list[str],
    phase_scores: Counter[str],
    domain_scores: Counter[str],
    matched_signals: list[dict[str, Any]],
    title_prior: list[str],
    parent_prior: list[str],
) -> None:
    for title_key, payload in (lexicon.get("weak_title_priors") or {}).items():
        normalized_key = normalize_classifier_text(title_key)
        compact_key = compact_classifier_text(title_key)
        matched_index = _match_title_index(normalized_key, compact_key, title_candidates, title_compact_candidates)
        if matched_index is None:
            continue
        target_list = title_prior if matched_index < 2 else parent_prior
        target_list.append(title_key)
        for phase, weight in (payload.get("phase") or {}).items():
            phase_scores[str(phase)] += int(weight)
            matched_signals.append({"source": "title_prior", "kind": "phase", "target": str(phase), "signal": title_key, "weight": int(weight)})
        for domain, weight in (payload.get("domain") or {}).items():
            domain_scores[str(domain)] += int(weight)
            matched_signals.append({"source": "title_prior", "kind": "domain", "target": str(domain), "signal": title_key, "weight": int(weight)})


def _score_kmvss_signals(
    *,
    lexicon: dict[str, Any],
    title_candidates: list[str],
    title_compact_candidates: list[str],
    metadata: dict[str, Any],
    phase_scores: Counter[str],
    domain_scores: Counter[str],
    topic_scores: Counter[str],
    matched_signals: list[dict[str, Any]],
) -> None:
    body_text = normalize_classifier_text(str(metadata.get("basis") or metadata.get("statement") or "")).lower()
    compact_body_text = compact_classifier_text(body_text).lower()

    for phase, payload in (lexicon.get("phase_signals") or {}).items():
        for signal in payload.get("title") or []:
            if _matches_signal(signal, title_candidates, title_compact_candidates):
                phase_scores[str(phase)] += 3
                matched_signals.append({"source": "kmvss_title", "kind": "phase", "target": str(phase), "signal": signal, "weight": 3})
        for signal in payload.get("body") or []:
            if _skip_attachment_signal(signal=signal, target=str(phase), normalized_text=body_text, metadata=metadata):
                continue
            if _matches_signal(signal, [body_text], [compact_body_text]):
                phase_scores[str(phase)] += 2
                matched_signals.append({"source": "kmvss_body", "kind": "phase", "target": str(phase), "signal": signal, "weight": 2})

    for domain, payload in (lexicon.get("domain_signals") or {}).items():
        for signal in payload.get("title") or []:
            if _matches_signal(signal, title_candidates, title_compact_candidates):
                domain_scores[str(domain)] += 3
                matched_signals.append({"source": "kmvss_title", "kind": "domain", "target": str(domain), "signal": signal, "weight": 3})
        for signal in payload.get("body") or []:
            if _skip_attachment_signal(signal=signal, target=str(domain), normalized_text=body_text, metadata=metadata):
                continue
            if _matches_signal(signal, [body_text], [compact_body_text]):
                domain_scores[str(domain)] += 2
                matched_signals.append({"source": "kmvss_body", "kind": "domain", "target": str(domain), "signal": signal, "weight": 2})

    for topic, signals in (lexicon.get("topic_aliases") or {}).items():
        for signal in signals:
            if _matches_signal(str(signal), title_candidates + [body_text], title_compact_candidates + [compact_body_text]):
                topic_scores[str(topic)] += 3
                matched_signals.append({"source": "kmvss_topic", "kind": "topic", "target": str(topic), "signal": str(signal), "weight": 3})


def _apply_short_clause_inheritance(
    *,
    is_short_clause: bool,
    local_body_text: str,
    article_bucket: str,
    title: str,
    subject: str,
    parent_title: str,
    parent_clause_text: str,
    phase_scores: Counter[str],
    domain_scores: Counter[str],
    matched_signals: list[dict[str, Any]],
    inherited_context_sources: list[str],
    is_article: bool,
) -> None:
    if not is_article or not is_short_clause:
        return
    if len(local_body_text.strip()) > 80:
        return
    inherited_bucket = article_bucket
    if not inherited_bucket and parent_clause_text:
        inherited_bucket = _article_bucket_from_subject(subject=parent_clause_text, title=parent_clause_text, parent_title=parent_clause_text)
    for source_name, value, phase_weight, domain_weight in (
        ("article_title", title, 4, 4),
        ("article_subject", subject, 3, 3),
        ("parent_clause", parent_clause_text or parent_title, 2, 2),
    ):
        normalized = normalize_classifier_text(value).strip()
        if not normalized:
            continue
        if source_name in inherited_context_sources:
            continue
        inherited_context_sources.append(source_name)
        bucket = inherited_bucket or _article_bucket_from_subject(subject=normalized, title=normalized, parent_title=normalized)
        payload = ARTICLE_BUCKET_PRIORS.get(bucket)
        if not payload:
            continue
        for phase, weight in (payload.get("phase") or {}).items():
            effective_weight = min(int(weight), phase_weight + (1 if bucket.startswith("umbrella_") else 0))
            phase_scores[str(phase)] += effective_weight
            matched_signals.append(
                {
                    "source": "article_short_clause_inheritance",
                    "kind": "phase",
                    "target": str(phase),
                    "signal": normalized,
                    "weight": effective_weight,
                }
            )
        for domain, weight in (payload.get("domain") or {}).items():
            effective_weight = min(int(weight), domain_weight + (1 if bucket.startswith("umbrella_") else 0))
            domain_scores[str(domain)] += effective_weight
            matched_signals.append(
                {
                    "source": "article_short_clause_inheritance",
                    "kind": "domain",
                    "target": str(domain),
                    "signal": normalized,
                    "weight": effective_weight,
                }
            )
    if article_bucket == "definitions" and any(token in local_body_text for token in ("다음 각호", "용어의 뜻", "말한다")):
        phase_scores["non_phase_admin"] += 3
        matched_signals.append(
            {
                "source": "article_short_clause_inheritance",
                "kind": "phase",
                "target": "non_phase_admin",
                "signal": "definitions",
                "weight": 3,
            }
        )


def _bucket_primary_target(article_bucket: str, *, kind: str) -> str | None:
    payload = ARTICLE_BUCKET_PRIORS.get(article_bucket) or {}
    targets = payload.get(kind) or {}
    if not targets:
        return None
    return max(targets.items(), key=lambda item: int(item[1]))[0]


def _is_secondary_promotable_bucket(article_bucket: str) -> bool:
    return article_bucket in {"secondary_visibility_signaling", "secondary_vehicle_control"}


def _match_explicit_phase_override(
    *,
    normalized_text: str,
    compact_text: str,
    title_text: str,
    title_compact: str,
    document_id: str,
    metadata: dict[str, Any],
) -> dict[str, str] | None:
    if bool(metadata.get("is_attachment")):
        return None
    normalized_document_id = normalize_classifier_text(document_id).lower()
    compact_document_id = compact_classifier_text(document_id).lower()
    for phrase, phase in EXPLICIT_PHASE_OVERRIDES.items():
        normalized_phrase = normalize_classifier_text(phrase).lower()
        compact_phrase = compact_classifier_text(phrase).lower()
        if phrase in TITLE_ONLY_EXPLICIT_PHRASES:
            candidates = (
                title_text.lower(),
                title_compact.lower(),
                normalized_document_id,
                compact_document_id,
            )
        else:
            candidates = (
                normalized_text,
                compact_text,
                title_text.lower(),
                title_compact.lower(),
                normalized_document_id,
                compact_document_id,
            )
        if normalized_phrase and any(normalized_phrase in candidate for candidate in candidates):
            return {"phase": phase, "phrase": phrase}
        if compact_phrase and any(compact_phrase in candidate for candidate in candidates):
            return {"phase": phase, "phrase": phrase}
    return None


def _select_phase(
    phase_scores: Counter[str],
    *,
    fallback_reason: str,
    metadata: dict[str, Any],
    phase_breakdown: dict[str, dict[str, int]],
    local_body_signal_weight: int,
) -> tuple[str, str]:
    if not phase_scores:
        return "cross_phase", "no_phase_signal"

    ordered = phase_scores.most_common()
    top_phase, top_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0

    if top_phase == "non_phase_admin" and top_score >= 5 and top_score >= second_score + 1:
        return top_phase, fallback_reason
    if top_score >= 6 and top_score >= second_score + 2:
        return top_phase, fallback_reason
    if top_score >= 4 and second_score >= 4 and top_phase != "non_phase_admin":
        if bool(metadata.get("is_attachment")) and not _attachment_multi_phase_is_strong(phase_breakdown):
            return top_phase, "attachment_prior_conflict"
        if metadata.get("collection") == "xml_kmvss" and not bool(metadata.get("is_attachment")) and local_body_signal_weight < 2:
            return top_phase, "article_inherited_context"
        return "cross_phase", "multi_phase_scores"
    if top_score >= 3:
        return top_phase, fallback_reason
    return "cross_phase", "low_phase_signal"


def _select_domain(domain_scores: Counter[str], *, phase: str) -> tuple[str, str]:
    if not domain_scores:
        return "other_or_review", "low_domain_signal"
    ordered = domain_scores.most_common()
    top_domain, top_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0
    if top_score >= 4 and top_score >= second_score + 1:
        return top_domain, ""
    if top_score >= 2 and phase != "non_phase_admin":
        return top_domain, ""
    return "other_or_review", "low_domain_signal"


def _signal_breakdown(matched_signals: list[dict[str, Any]], *, kind: str) -> dict[str, dict[str, int]]:
    breakdown: dict[str, Counter[str]] = {}
    for signal in matched_signals:
        if signal.get("kind") != kind:
            continue
        target = str(signal.get("target"))
        source = str(signal.get("source"))
        breakdown.setdefault(target, Counter())[source] += int(signal.get("weight", 0))
    return {target: dict(counter) for target, counter in breakdown.items()}


def _local_body_signal_weight(matched_signals: list[dict[str, Any]], *, is_attachment: bool) -> int:
    local_sources = {"kmvss_body", "generic"}
    if is_attachment:
        local_sources.add("attachment_subject_prior")
    return sum(
        int(signal.get("weight", 0))
        for signal in matched_signals
        if str(signal.get("source")) in local_sources and signal.get("kind") == "phase"
    )


def _attachment_multi_phase_is_strong(phase_breakdown: dict[str, dict[str, int]]) -> bool:
    contextual_sources = {"kmvss_body", "generic", "kmvss_title", "attachment_subject_prior"}
    strong_phases = 0
    for phase, breakdown in phase_breakdown.items():
        if phase == "non_phase_admin":
            continue
        if sum(weight for source, weight in breakdown.items() if source in contextual_sources) >= 2:
            strong_phases += 1
    return strong_phases >= 2


def _skip_attachment_signal(
    *,
    signal: str,
    target: str,
    normalized_text: str,
    metadata: dict[str, Any],
) -> bool:
    if not bool(metadata.get("is_attachment")):
        return False

    normalized_signal = normalize_classifier_text(signal)
    attachment_bucket = str(metadata.get("attachment_bucket") or "")
    subject = normalize_classifier_text(str(metadata.get("subject") or ""))
    attachment_section = normalize_classifier_text(str(metadata.get("attachment_section") or ""))
    combined = " ".join(part for part in (subject, attachment_section, normalized_text) if part)

    if normalized_signal == "구조":
        if attachment_bucket in {"tire_wheel_hose_running_gear", "labeling_marking_indication"}:
            return True
        if any(token in combined for token in ("타이어", "휠", "호스", "형식", "표기")):
            return True

    if normalized_signal == "유지":
        if attachment_bucket == "emc_electrical_compatibility" or bool(metadata.get("is_table_like_row")):
            return True
        if any(token in combined for token in ("전자파 적합성", "방사", "전도", "시험 주파수")):
            return True

    if normalized_signal == "적합성" and target == "non_phase_admin":
        if any(token in combined for token in ("전자파 적합성", "emc", "방사", "전도", "시험 주파수")):
            admin_tokens = ("인증", "형식승인", "장관", "고시", "조사", "적용 제외")
            return not any(token in combined for token in admin_tokens)

    return False


def _select_primary_topic(
    topic_scores: Counter[str],
    normalized_text: str,
    title_candidates: list[str],
    phase: str,
    domain: str,
) -> str:
    if topic_scores:
        return topic_scores.most_common(1)[0][0]
    if title_candidates:
        for candidate in title_candidates:
            normalized = normalize_classifier_text(candidate)
            if normalized:
                return slugify(normalized)[:80]
    if phase == "non_phase_admin":
        return "administrative_exception"
    if domain == "other_or_review":
        return slugify(" ".join(re.findall(r"[a-z0-9]+", normalized_text)[:3]) or "regulation-topic")
    return slugify(" ".join(re.findall(r"[a-z0-9]+", normalized_text)[:3]) or domain)


def _secondary_topics(
    text: str,
    *,
    primary_topic: str,
    extra_keywords: list[str] | None = None,
) -> list[str]:
    haystack = " ".join([text, *(extra_keywords or [])])
    out: list[str] = []
    for keyword, topic in SECONDARY_TOPIC_HINTS:
        if keyword in haystack and topic != primary_topic and topic not in out:
            out.append(topic)
    return out


def _browse_buckets(text: str, *, phase: str) -> list[str]:
    if phase not in {"in_crash", "cross_phase"}:
        return []
    buckets: list[str] = []
    for keyword, bucket in BROWSE_BUCKET_HINTS:
        if keyword in text and bucket not in buckets:
            buckets.append(bucket)
    return buckets


def _legacy_domain(phase: str) -> str:
    if phase == "pre_crash":
        return "active_safety"
    if phase == "in_crash":
        return "passive_crash"
    return "needs_review"


def _contains_hangul(text: str) -> bool:
    return any("\uac00" <= ch <= "\ud7a3" for ch in text)


def _matches_signal(signal: str, normalized_candidates: list[str], compact_candidates: list[str]) -> bool:
    normalized_signal = normalize_classifier_text(signal).lower()
    compact_signal = compact_classifier_text(signal).lower()
    if normalized_signal and any(normalized_signal in candidate.lower() for candidate in normalized_candidates):
        return True
    if compact_signal and any(compact_signal in candidate.lower() for candidate in compact_candidates):
        return True
    return False


def _match_title_index(
    normalized_key: str,
    compact_key: str,
    title_candidates: list[str],
    title_compact_candidates: list[str],
) -> int | None:
    for idx, candidate in enumerate(title_candidates):
        if normalized_key and normalized_key in candidate:
            return idx
    for idx, candidate in enumerate(title_compact_candidates):
        if compact_key and compact_key in candidate:
            return idx
    return None
