from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from typing import Callable, Sequence

from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig

from ytfetcher import YTFetcher
from ytfetcher.config import HTTPConfig

from ytfetcher_gui.models import AppState, DataScope, FetchConfig, FetchMode
from ytfetcher_gui.services import AsyncTaskRunner


class FetchController:
    """
    Điều phối việc tạo `YTFetcher` và chạy coroutine lấy dữ liệu.
    """

    def __init__(self, runner: AsyncTaskRunner):
        self._runner = runner
        self.state = AppState()

    def start_fetch(
        self,
        config: FetchConfig,
        on_complete: Callable[[list], None],
        on_error: Callable[[Exception], None],
        on_status: Callable[[AppState], None],
    ) -> None:
        self.state = replace(self.state, status="fetching", message="Đang tải dữ liệu...", records_fetched=0)
        on_status(self.state)

        def _task():
            fetcher = self._create_fetcher(config)
            return self._dispatch_fetch(fetcher, config.scope)

        self._runner.submit(
            _task,
            lambda data: self._handle_success(data, on_complete, on_status),
            lambda exc: self._handle_error(exc, on_error, on_status),
        )

    def _handle_success(self, data: list, on_complete: Callable[[list], None], on_status: Callable[[AppState], None]):
        self.state = replace(
            self.state,
            status="idle",
            message=f"Hoàn tất {len(data)} video.",
            records_fetched=len(data),
            data_cache=data,
        )
        on_status(self.state)
        on_complete(data)

    def _handle_error(self, exc: Exception, on_error: Callable[[Exception], None], on_status: Callable[[AppState], None]):
        self.state = replace(self.state, status="error", message=str(exc))
        on_status(self.state)
        on_error(exc)

    def _dispatch_fetch(self, fetcher: YTFetcher, scope: DataScope) -> list:
        if scope == DataScope.TRANSCRIPTS:
            return asyncio.run(fetcher.fetch_transcripts())
        if scope == DataScope.METADATA:
            return asyncio.run(fetcher.fetch_snippets())
        return asyncio.run(fetcher.fetch_youtube_data())

    def _create_fetcher(self, config: FetchConfig) -> YTFetcher:
        http_config = HTTPConfig(timeout=config.http.timeout, headers=self._parse_headers(config.http.headers_raw))
        proxy_config = self._build_proxy_config(config)
        languages = config.languages or ["en"]

        kwargs = {
            "proxy_config": proxy_config,
            "http_config": http_config,
            "languages": languages,
            "manually_created": config.manually_created,
        }

        if config.mode == FetchMode.CHANNEL:
            return YTFetcher.from_channel(channel_handle=config.channel_handle.strip(), max_results=config.max_results, **kwargs)
        if config.mode == FetchMode.PLAYLIST:
            return YTFetcher.from_playlist_id(playlist_id=config.playlist_id.strip(), max_results=config.max_results, **kwargs)
        video_ids = config.video_ids()
        return YTFetcher.from_video_ids(video_ids=video_ids, **kwargs)

    def _build_proxy_config(self, config: FetchConfig):
        proxy = config.proxy
        if proxy.is_webshare_enabled():
            return WebshareProxyConfig(proxy_username=proxy.webshare_username.strip(), proxy_password=proxy.webshare_password.strip())
        if proxy.has_custom_proxy():
            return GenericProxyConfig(http_proxy=proxy.http_proxy.strip() or None, https_proxy=proxy.https_proxy.strip() or None)
        return None

    @staticmethod
    def _parse_headers(value: str | None) -> dict | None:
        if not value:
            return None
        text = value.strip()
        if not text:
            return None

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Headers phải ở dạng JSON hợp lệ.") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Headers phải là đối tượng dict.")

        return parsed

