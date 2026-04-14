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


def normalize_classifier_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    replacements = {
        "ㆍ": " ",
        "·": " ",
        "–": "-",
        "—": "-",
        "−": "-",
        "\u3000": " ",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = re.sub(r"\[(?:[①②③④⑤⑥⑦⑧⑨⑩]|\d+)\]\s*", "", normalized)
    normalized = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", normalized)
    normalized = re.sub(r"^제\s*(\d+)\s*조", r"제\1조", normalized)
    normalized = re.sub(r"(\d+)\.\s*(\d+)\.", r"\1.\2.", normalized)
    normalized = re.sub(r"(\d+)\)\s*", r"\1) ", normalized)
    normalized = re.sub(r"([가-힣])\)\s*", r"\1) ", normalized)
    normalized = re.sub(r"\s*([:;|])\s*", r" \1 ", normalized)
    normalized = normalize_whitespace(normalized)
    return normalized


def compact_classifier_text(value: str) -> str:
    normalized = normalize_classifier_text(value)
    return re.sub(r"[\s\-\(\)\[\],.:;\"'`]+", "", normalized)


def is_table_drawing_text(value: str) -> bool:
    stripped = (value or "").strip()
    if not stripped:
        return False
    return all(character in "┯┨┠┷┳┻├┤│─═║╭╮╯╰+ " for character in stripped)


def is_attachment_table_like_text(value: str) -> bool:
    normalized = normalize_classifier_text(value)
    if not normalized:
        return False
    if is_table_drawing_text(normalized):
        return True
    compact = re.sub(r"\s+", "", normalized)
    if re.fullmatch(r"[0-9A-Za-z㎒㏈㎶㏀μ%/().,+\-~～:=]+", compact):
        return True
    hangul_count = len(re.findall(r"[가-힣]", normalized))
    digit_count = len(re.findall(r"\d", normalized))
    alpha_count = len(re.findall(r"[A-Za-z]", normalized))
    unit_count = len(re.findall(r"[㎒㏈㎶㏀μ%VWAΩ℃/]", normalized))
    if digit_count >= 3 and hangul_count <= 4:
        return True
    if alpha_count >= 2 and digit_count >= 2 and hangul_count <= 6:
        return True
    if unit_count >= 2 and digit_count >= 1 and hangul_count <= 8:
        return True
    if re.search(r"(시험\s*주파수|기준치|정격전압|시험전압|전력\(W\)|광도)", normalized):
        return True
    return False
