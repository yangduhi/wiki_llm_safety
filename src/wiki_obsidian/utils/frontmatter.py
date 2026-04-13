from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter_text(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :]
    try:
        payload = yaml.safe_load(block) or {}
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}, body


def parse_frontmatter_file(path: str | Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter_text(Path(path).read_text(encoding="utf-8"))


def render_frontmatter(payload: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---\n"
