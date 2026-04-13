from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.files import read_text
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file
from wiki_obsidian.utils.text import normalize_whitespace, slugify


PRE_CRASH = (
    "aeb",
    "automatic emergency braking",
    "fcw",
    "forward collision warning",
    "lane",
    "esc",
    "pedestrian detection",
    "collision avoidance",
    "vru",
)
IN_CRASH = (
    "occupant crash protection",
    "occupant",
    "restraint",
    "seat belt",
    "air bag",
    "airbag",
    "frontal impact",
    "side impact",
    "rear impact",
    "door retention",
    "ejection",
    "crash",
    "impact",
    "latch",
    "hinge",
)
POST_CRASH = (
    "post-crash",
    "post crash",
    "ecall",
    "edr",
    "rescue",
    "emergency response",
    "after crash",
)
CROSS_PHASE = (
    "glazing",
    "windscreen",
    "windshield",
    "visibility",
    "electrical safety",
    "battery",
    "fuel system integrity",
    "fire risk",
)
ADMIN = (
    "type approval",
    "conformity",
    "market surveillance",
    "recall",
    "framework",
    "governance",
    "authority",
)


def classify_text(
    text: str,
    *,
    collection: str | None = None,
    jurisdiction: str | None = None,
    regulatory_layer: str | None = None,
) -> dict[str, Any]:
    haystack = normalize_whitespace(text).lower()
    phase = _classify_phase(haystack, regulatory_layer=regulatory_layer)
    functional_domain = _classify_functional_domain(haystack)
    primary_topic = _classify_primary_topic(haystack)
    secondary_topics = _secondary_topics(haystack, primary_topic=primary_topic)
    browse_buckets = _browse_buckets(haystack, phase=phase)
    legacy_domain = _legacy_domain(phase)
    return {
        "phase": phase,
        "functional_domain": [functional_domain],
        "primary_topic": primary_topic,
        "secondary_topics": secondary_topics,
        "browse_buckets": browse_buckets,
        "legacy_domain": legacy_domain,
        "source_collection": collection,
        "jurisdiction": jurisdiction,
        "regulatory_layer": regulatory_layer,
    }


def classify_phase_from_notes(
    question: str,
    *,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    result = classify_text(question)
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


def _classify_phase(text: str, *, regulatory_layer: str | None) -> str:
    if regulatory_layer and regulatory_layer in {
        "framework_admin",
        "conformity_assessment",
        "market_surveillance_recall",
    }:
        return "non_phase_admin"
    if any(keyword in text for keyword in ADMIN):
        return "non_phase_admin"
    if any(keyword in text for keyword in CROSS_PHASE):
        return "cross_phase"
    if any(keyword in text for keyword in POST_CRASH):
        return "post_crash"
    if any(keyword in text for keyword in PRE_CRASH):
        return "pre_crash"
    if any(keyword in text for keyword in IN_CRASH):
        return "in_crash"
    return "cross_phase"


def _classify_functional_domain(text: str) -> str:
    if any(keyword in text for keyword in PRE_CRASH):
        return "crash_avoidance_and_vehicle_control"
    if "child restraint" in text or "child occupant" in text:
        return "child_occupant_protection"
    if "door" in text or "egress" in text or "ejection" in text or "latch" in text or "hinge" in text:
        return "structural_integrity_retention_and_egress"
    if "glazing" in text or "windscreen" in text or "windshield" in text or "visibility" in text:
        return "visibility_glazing_and_driver_information"
    if "battery" in text or "electrical" in text or "fire risk" in text or "fuel system" in text:
        return "fire_electrical_and_energy_storage_safety"
    if "ecall" in text or "edr" in text or "rescue" in text:
        return "post_crash_response_and_data"
    if "pedestrian protection" in text or "headform" in text:
        return "vru_protection"
    if "interior flammability" in text or "interior material" in text:
        return "interior_materials_and_fire"
    if "occupant" in text or "restraint" in text or "seat belt" in text or "airbag" in text or "air bag" in text:
        return "occupant_protection_and_restraints"
    return "other_or_review"


def _classify_primary_topic(text: str) -> str:
    if "pedestrian" in text and "aeb" in text:
        return "pedestrian_aeb"
    if "occupant crash protection" in text or "frontal impact" in text:
        return "frontal_impact"
    if "door" in text and "retention" in text:
        return "door_retention"
    if "egress" in text:
        return "post_crash_egress"
    if "glazing" in text or "windscreen" in text or "windshield" in text or "visibility" in text:
        return "glazing_visibility"
    if "edr" in text:
        return "event_data_recorder"
    if "ecall" in text:
        return "emergency_call"
    if "battery" in text or "electrical" in text:
        return "electrical_safety"
    tokens = [token for token in re.findall(r"[a-z0-9]+", text) if len(token) > 3]
    return slugify(" ".join(tokens[:3]) or "regulation-topic")


def _secondary_topics(text: str, *, primary_topic: str) -> list[str]:
    out: list[str] = []
    for keyword, topic in (
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
    ):
        if keyword in text and topic != primary_topic and topic not in out:
            out.append(topic)
    return out


def _browse_buckets(text: str, *, phase: str) -> list[str]:
    if phase not in {"in_crash", "cross_phase"}:
        return []
    buckets: list[str] = []
    for keyword, bucket in (
        ("frontal", "frontal_impact"),
        ("side", "side_impact"),
        ("rear", "rear_impact"),
        ("rollover", "rollover"),
        ("occupant", "occupant_restraints"),
        ("seat belt", "occupant_restraints"),
        ("compartment", "occupant_compartment_integrity"),
        ("door", "door_retention"),
        ("ejection", "anti_ejection"),
        ("head", "head_impact"),
        ("child", "child_restraints"),
        ("seat", "seat_systems"),
        ("steering", "steering_control"),
        ("glazing", "glazing_retention"),
        ("fuel", "fuel_system_integrity"),
        ("fire", "fire_risk"),
        ("pedestrian", "pedestrian_protection"),
    ):
        if keyword in text and bucket not in buckets:
            buckets.append(bucket)
    return buckets


def _legacy_domain(phase: str) -> str:
    if phase == "pre_crash":
        return "active_safety"
    if phase == "in_crash":
        return "passive_crash"
    return "needs_review"
