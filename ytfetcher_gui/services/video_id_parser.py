from __future__ import annotations

import re
from typing import Iterable


YOUTUBE_URL_PATTERNS = [
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{6,})"),
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{6,})"),
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{6,})"),
    re.compile(r"(?:https?://)?youtu\.be/([A-Za-z0-9_-]{6,})"),
]


class VideoIdParser:
    """
    Chuẩn hóa danh sách đầu vào (ID hoặc URL) thành danh sách video_id hợp lệ.
    """

    @staticmethod
    def parse(raw_values: Iterable[str]) -> list[str]:
        candidates = []
        for raw in raw_values:
            token = raw.strip()
            if not token:
                continue
            video_id = VideoIdParser._extract_id(token)
            if video_id:
                candidates.append(video_id)
        return VideoIdParser._deduplicate(candidates)

    @staticmethod
    def _extract_id(value: str) -> str | None:
        # Nếu không có http(s) thì giả định là ID thuần
        if "http://" not in value and "https://" not in value:
            return value if " " not in value else None

        for pattern in YOUTUBE_URL_PATTERNS:
            match = pattern.search(value)
            if match:
                return match.group(1)

        # fallback: tìm tham số v=
        if "v=" in value:
            fragment = value.split("v=", 1)[1]
            for sep in ("&", "#"):
                if sep in fragment:
                    fragment = fragment.split(sep, 1)[0]
            fragment = fragment.strip()
            if fragment:
                return fragment

        return None

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

