from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Sequence

from ytfetcher_gui.models import (
    DataScope,
    ExportConfig,
    ExportFormat,
    FetchConfig,
    FetchMode,
    HTTPSettings,
    ProxySettings,
)


class SettingsManager:
    """
    Quản lý lưu/đọc cấu hình GUI (tự động áp dụng cho lần chạy sau).
    """

    def __init__(self, path: Path | None = None):
        default_path = Path.home() / ".ytfetcher_gui_settings.json"
        self.path = path or default_path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def save(
        self,
        fetch_config: FetchConfig,
        export_config: ExportConfig,
        metadata_fields: Sequence[str],
        include_timing: bool,
    ) -> None:
        payload = {
            "fetch": self._serialize_fetch(fetch_config),
            "export": self._serialize_export(export_config),
            "metadata_fields": list(metadata_fields),
            "include_timing": bool(include_timing),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    def deserialize_fetch(self, data: Dict[str, Any]) -> FetchConfig:
        proxy = ProxySettings(**data.get("proxy", {}))
        http = HTTPSettings(**data.get("http", {}))

        return FetchConfig(
            mode=FetchMode(data.get("mode", FetchMode.CHANNEL.value)),
            scope=DataScope(data.get("scope", DataScope.FULL.value)),
            channel_handle=data.get("channel_handle", ""),
            playlist_id=data.get("playlist_id", ""),
            video_ids_raw=data.get("video_ids_raw", ""),
            max_results=int(data.get("max_results", 25)),
            manually_created=bool(data.get("manually_created", False)),
            languages=list(data.get("languages", ["en"])),
            metadata_fields=list(data.get("metadata_fields", [])),
            include_timing=bool(data.get("include_timing", True)),
            proxy=proxy,
            http=http,
        )

    def deserialize_export(self, data: Dict[str, Any]) -> ExportConfig:
        return ExportConfig(
            filename=data.get("filename", "ytfetcher_export"),
            output_dir=Path(data.get("output_dir", str(Path.cwd()))),
            format=ExportFormat(data.get("format", ExportFormat.JSON.value)),
            per_video=bool(data.get("per_video", False)),
        )

    def _serialize_fetch(self, config: FetchConfig) -> Dict[str, Any]:
        return {
            "mode": config.mode.value,
            "scope": config.scope.value,
            "channel_handle": config.channel_handle,
            "playlist_id": config.playlist_id,
            "video_ids_raw": config.video_ids_raw,
            "max_results": config.max_results,
            "manually_created": config.manually_created,
            "languages": list(config.languages),
            "metadata_fields": list(config.metadata_fields),
            "include_timing": config.include_timing,
            "proxy": asdict(config.proxy),
            "http": asdict(config.http),
        }

    def _serialize_export(self, config: ExportConfig) -> Dict[str, Any]:
        return {
            "filename": config.filename,
            "output_dir": str(config.output_dir),
            "format": config.format.value,
            "per_video": config.per_video,
        }

