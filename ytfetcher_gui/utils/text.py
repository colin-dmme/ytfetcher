from __future__ import annotations

import re
import unicodedata
from typing import Iterable


def slugify_title(value: str) -> str:
    """
    Biến title thành slug ASCII (không dấu, không khoảng trắng, không ký tự đặc biệt).
    """

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized


def extract_primary_language(languages: Iterable[str]) -> str:
    for lang in languages:
        if lang:
            return lang
    return "unknown"


def extract_video_id(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    # Direct ID (no spaces, no protocol)
    if "http://" not in value and "https://" not in value:
        return value if " " not in value else None

    # Standard URL with v= parameter
    if "v=" in value:
        fragment = value.split("v=", 1)[1]
        for sep in ("&", "#"):
            if sep in fragment:
                fragment = fragment.split(sep, 1)[0]
        fragment = fragment.strip()
        if fragment:
            return fragment

    # youtu.be short link or /embed/ style
    if "youtu.be" in value or "/embed/" in value or "/shorts/" in value:
        parts = value.split("/")
        candidate = parts[-1]
        for sep in ("?", "&", "#"):
            if sep in candidate:
                candidate = candidate.split(sep, 1)[0]
        candidate = candidate.strip()
        if candidate:
            return candidate

    return None

