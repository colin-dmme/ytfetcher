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

