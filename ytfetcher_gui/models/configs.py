from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List


class FetchMode(str, Enum):
    CHANNEL = "channel"
    PLAYLIST = "playlist"
    VIDEO_IDS = "video_ids"


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    TXT = "txt"


class DataScope(str, Enum):
    FULL = "full"
    TRANSCRIPTS = "transcripts"
    METADATA = "metadata"


@dataclass
class ProxySettings:
    http_proxy: str = ""
    https_proxy: str = ""
    webshare_username: str = ""
    webshare_password: str = ""

    def is_webshare_enabled(self) -> bool:
        return bool(self.webshare_username and self.webshare_password)

    def has_custom_proxy(self) -> bool:
        return bool(self.http_proxy or self.https_proxy)


@dataclass
class HTTPSettings:
    timeout: float = 4.0
    headers_raw: str = ""


@dataclass
class FetchConfig:
    mode: FetchMode = FetchMode.CHANNEL
    scope: DataScope = DataScope.FULL
    channel_handle: str = ""
    playlist_id: str = ""
    video_ids_raw: str = ""
    max_results: int = 25
    manually_created: bool = False
    languages: List[str] = field(default_factory=lambda: ["en"])
    metadata_fields: List[str] = field(default_factory=list)
    include_timing: bool = True
    proxy: ProxySettings = field(default_factory=ProxySettings)
    http: HTTPSettings = field(default_factory=HTTPSettings)

    def video_ids(self) -> list[str]:
        tokens = [
            item.strip()
            for chunk in self.video_ids_raw.splitlines()
            for item in chunk.replace(",", "\n").splitlines()
        ]
        results: list[str] = []
        for token in tokens:
            if not token:
                continue
            results.append(token)
        seen: set[str] = set()
        deduped: list[str] = []
        for vid in results:
            if vid not in seen:
                seen.add(vid)
                deduped.append(vid)
        return deduped


@dataclass
class ExportConfig:
    filename: str = "ytfetcher_export"
    output_dir: Path = Path.cwd()
    format: ExportFormat = ExportFormat.JSON
    per_video: bool = False


@dataclass
class AppState:
    status: str = "idle"
    message: str = ""
    records_fetched: int = 0
    data_cache: list | None = None

