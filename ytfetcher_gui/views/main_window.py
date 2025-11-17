from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Sequence

from ytfetcher_gui.controllers import ExportController, FetchController
from ytfetcher_gui.models import (
    DataScope,
    ExportConfig,
    ExportFormat,
    FetchConfig,
    FetchMode,
)
from ytfetcher_gui.storage import SettingsManager
from ytfetcher_gui.views.dialogs import show_error, show_info, show_warning
from ytfetcher_gui.views.widgets import ExportSection, NetworkSection, SourceSection

logger = logging.getLogger(__name__)


class MainWindow(ttk.Frame):
    """
    View chính, kết nối sự kiện nút với controller tương ứng.
    """

    def __init__(self, master: tk.Tk, fetch_controller: FetchController, export_controller: ExportController):
        super().__init__(master, padding=12)
        self.master = master
        self.fetch_controller = fetch_controller
        self.export_controller = export_controller
        self.settings_manager = SettingsManager()
        self._last_fetch_config: FetchConfig | None = None
        self._pending_fetch_config: FetchConfig | None = None
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.records_var = tk.StringVar(value="")

        self._build_layout()
        self._load_settings()

    def _build_layout(self) -> None:
        self.master.title("YTFetcher GUI")
        self.pack(fill="both", expand=True)

        self.source_section = SourceSection(self)
        self.source_section.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.network_section = NetworkSection(self)
        self.network_section.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        self.export_section = ExportSection(self)
        self.export_section.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=4, pady=4)

        controls = ttk.Frame(self)
        controls.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.fetch_button = ttk.Button(controls, text="Fetch dữ liệu", command=self._on_fetch_click)
        self.fetch_button.pack(side="left")

        self.export_button = ttk.Button(controls, text="Export", command=self._on_export_click, state="disabled")
        self.export_button.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(controls, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=12)

        ttk.Label(controls, textvariable=self.records_var).pack(side="right")
        ttk.Label(controls, textvariable=self.status_var).pack(side="right", padx=12)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _on_fetch_click(self) -> None:
        try:
            fetch_config = self._get_fetch_config(validate=True)
        except ValueError as exc:
            show_error(self, "Thiếu dữ liệu", str(exc))
            return

        self._pending_fetch_config = fetch_config
        self._toggle_busy(True)
        self.fetch_controller.start_fetch(
            fetch_config,
            on_complete=self._handle_fetch_complete,
            on_error=self._handle_fetch_error,
            on_status=self._update_status,
        )

    def _on_export_click(self) -> None:
        if not self.fetch_controller.state.data_cache:
            show_warning(self, "Chưa có dữ liệu", "Hãy fetch trước khi export.")
            return

        export_config = self._get_export_config(validate=True)
        metadata_fields = self.export_section.selected_metadata()
        include_timing = self.export_section.include_timing()
        language_codes = self._resolve_language_codes()

        self._toggle_busy(True)
        self.export_controller.start_export(
            export_config,
            data=self.fetch_controller.state.data_cache,
            metadata_fields=metadata_fields,
            include_timing=include_timing,
            language_codes=language_codes,
            on_success=self._handle_export_success,
            on_error=self._handle_export_error,
        )

    def _handle_fetch_complete(self, data: list) -> None:
        self._toggle_busy(False)
        self.export_button.configure(state="normal")
        self._last_fetch_config = self._pending_fetch_config
        self._pending_fetch_config = None
        show_info(self, "Hoàn tất", f"Đã lấy {len(data)} video.")

    def _handle_fetch_error(self, exc: Exception) -> None:
        self._toggle_busy(False)
        self._pending_fetch_config = None
        show_error(self, "Lỗi fetch", str(exc))

    def _handle_export_success(self, paths: Sequence[Path]) -> None:
        self._toggle_busy(False)
        if not paths:
            show_info(self, "Export thành công", "Không có file nào được tạo.")
            return
        if len(paths) == 1:
            show_info(self, "Export thành công", f"Đã lưu file tại:\n{paths[0]}")
        else:
            show_info(self, "Export thành công", f"Đã tạo {len(paths)} file. File cuối: {paths[-1]}")

    def _handle_export_error(self, exc: Exception) -> None:
        self._toggle_busy(False)
        show_error(self, "Lỗi export", str(exc))

    def _update_status(self, state) -> None:
        self.status_var.set(state.message or state.status)
        self.records_var.set(f"{state.records_fetched} video")

    def _toggle_busy(self, is_busy: bool) -> None:
        if is_busy:
            self.fetch_button.configure(state="disabled")
            self.export_button.configure(state="disabled")
            self.progress.start(10)
        else:
            self.fetch_button.configure(state="normal")
            if self.fetch_controller.state.data_cache:
                self.export_button.configure(state="normal")
            self.progress.stop()

    def _get_fetch_config(self, validate: bool) -> FetchConfig:
        config = self.source_section.build_config(validate=validate)
        config.proxy = self.network_section.to_proxy_settings()
        config.http = self.network_section.to_http_settings()
        config.metadata_fields = self.export_section.selected_metadata()
        config.include_timing = self.export_section.include_timing()
        return config

    def _get_export_config(self, validate: bool) -> ExportConfig:
        return self.export_section.build_config(validate=validate)

    def _resolve_language_codes(self) -> list[str]:
        if self._last_fetch_config and self._last_fetch_config.languages:
            return list(self._last_fetch_config.languages)
        return self.source_section.languages()

    def persist_settings(self) -> None:
        self._persist_settings()

    def _persist_settings(self) -> None:
        try:
            fetch_config = self._get_fetch_config(validate=False)
            export_config = self._get_export_config(validate=False)
            metadata_fields = self.export_section.selected_metadata()
            include_timing = self.export_section.include_timing()
            self.settings_manager.save(
                fetch_config=fetch_config,
                export_config=export_config,
                metadata_fields=metadata_fields,
                include_timing=include_timing,
            )
        except Exception as exc:
            logger.debug("Không thể lưu cấu hình GUI: %s", exc)

    def _load_settings(self) -> None:
        data = self.settings_manager.load()
        if not data:
            return

        fetch_data = data.get("fetch")
        if fetch_data:
            try:
                fetch_config = self.settings_manager.deserialize_fetch(fetch_data)
                self.source_section.apply_config(fetch_config)
                self.network_section.apply_proxy_settings(fetch_config.proxy)
                self.network_section.apply_http_settings(fetch_config.http)
            except Exception as exc:
                logger.debug("Không thể áp dụng cấu hình fetch: %s", exc)

        export_data = data.get("export")
        if export_data:
            try:
                export_config = self.settings_manager.deserialize_export(export_data)
                metadata_fields = data.get("metadata_fields", [])
                include_timing = data.get("include_timing", True)
                self.export_section.apply_config(export_config, metadata_fields, include_timing)
            except Exception as exc:
                logger.debug("Không thể áp dụng cấu hình export: %s", exc)

