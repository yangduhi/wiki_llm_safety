from __future__ import annotations

from datetime import UTC, datetime
import hashlib


def build_run_id(*parts: object) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    joined = "::".join(str(part) for part in parts if str(part))
    suffix = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:8] if joined else "bootstrap"
    return f"{timestamp}__{suffix}"
