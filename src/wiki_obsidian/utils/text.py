from __future__ import annotations

import hashlib
import re
import unicodedata


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    if not ascii_text.strip():
        ascii_text = normalized
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9\-_]+", "-", ascii_text)
    ascii_text = re.sub(r"-{2,}", "-", ascii_text).strip("-")
    return ascii_text or "item"


def short_hash(*parts: object, length: int = 8) -> str:
    joined = "::".join(str(part) for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:length]


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
