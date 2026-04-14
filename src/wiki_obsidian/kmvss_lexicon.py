from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from wiki_obsidian.settings import load_project_settings
from wiki_obsidian.utils.text import compact_classifier_text, normalize_classifier_text


STOP_TOKENS = {"문", "등", "및", "관련", "기준"}


@lru_cache(maxsize=8)
def load_kmvss_signal_lexicon(project_root: str | Path | None = None) -> dict[str, Any]:
    settings = load_project_settings(project_root)
    path = settings.paths.taxonomy_root / "kmvss_signal_lexicon.yaml"
    if not path.exists():
        raise FileNotFoundError(f"KMVSS signal lexicon not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("KMVSS signal lexicon must be a YAML mapping.")
    for key in ("phase_signals", "domain_signals", "topic_aliases", "weak_title_priors"):
        if key not in payload or not isinstance(payload[key], dict):
            raise ValueError(f"KMVSS signal lexicon missing mapping `{key}`.")
    _validate_signal_payload(payload)
    return payload


def _validate_signal_payload(payload: dict[str, Any]) -> None:
    for phase, phase_payload in (payload.get("phase_signals") or {}).items():
        for bucket in ("title", "body"):
            for signal in phase_payload.get(bucket) or []:
                _validate_signal(signal, f"phase_signals.{phase}.{bucket}")
    for domain, domain_payload in (payload.get("domain_signals") or {}).items():
        for bucket in ("title", "body"):
            for signal in domain_payload.get(bucket) or []:
                _validate_signal(signal, f"domain_signals.{domain}.{bucket}")
    for topic, signals in (payload.get("topic_aliases") or {}).items():
        for signal in signals or []:
            _validate_signal(signal, f"topic_aliases.{topic}")
    for title_key in (payload.get("weak_title_priors") or {}).keys():
        _validate_signal(title_key, "weak_title_priors")


def _validate_signal(value: object, source: str) -> None:
    normalized = normalize_classifier_text(str(value)).strip()
    compact = compact_classifier_text(str(value)).strip()
    if not normalized or len(compact) < 2 or normalized in STOP_TOKENS:
        raise ValueError(f"Invalid KMVSS lexicon signal in {source}: {value!r}")
