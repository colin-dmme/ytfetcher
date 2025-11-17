from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ytfetcher_gui.controllers import ExportController, FetchController
from ytfetcher_gui.models import (
    DataScope,
    ExportConfig,
    ExportFormat,
    FetchConfig,
    FetchMode,
)
from ytfetcher_gui.views.dialogs import show_error, show_info, show_warning
from ytfetcher_gui.views.widgets import ExportSection, NetworkSection, SourceSection


class MainWindow(ttk.Frame):
    """
    View chính, kết nối sự kiện nút với controller tương ứng.
    """

    def __init__(self, master: tk.Tk, fetch_controller: FetchController, export_controller: ExportController):
        super().__init__(master, padding=12)
        self.master = master
        self.fetch_controller = fetch_controller
        self.export_controller = export_controller
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.records_var = tk.StringVar(value="")

        self._build_layout()

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
            fetch_config = self._build_fetch_config()
        except ValueError as exc:
            show_error(self, "Thiếu dữ liệu", str(exc))
            return

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

        export_config = self._build_export_config()
        metadata_fields = self.export_section.selected_metadata()
        include_timing = self.export_section.include_timing()

        self._toggle_busy(True)
        self.export_controller.start_export(
            export_config,
            data=self.fetch_controller.state.data_cache,
            metadata_fields=metadata_fields,
            include_timing=include_timing,
            on_success=self._handle_export_success,
            on_error=self._handle_export_error,
        )

    def _handle_fetch_complete(self, data: list) -> None:
        self._toggle_busy(False)
        self.export_button.configure(state="normal")
        show_info(self, "Hoàn tất", f"Đã lấy {len(data)} video.")

    def _handle_fetch_error(self, exc: Exception) -> None:
        self._toggle_busy(False)
        show_error(self, "Lỗi fetch", str(exc))

    def _handle_export_success(self, path) -> None:
        self._toggle_busy(False)
        if isinstance(path, list):
            if not path:
                show_info(self, "Export thành công", "Không có file nào được tạo.")
                return
            last_path = path[-1]
            show_info(self, "Export thành công", f"Đã tạo {len(path)} file. File cuối: {last_path}")
        else:
            show_info(self, "Export thành công", f"Đã lưu file tại:\n{path}")

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

    def _build_fetch_config(self) -> FetchConfig:
        mode = FetchMode(self.source_section.mode_var.get())
        scope = DataScope(self.source_section.scope_var.get())

        channel = self.source_section.channel_var.get().strip()
        playlist = self.source_section.playlist_var.get().strip()
        video_ids = self.source_section.video_ids()

        if mode == FetchMode.CHANNEL and not channel:
            raise ValueError("Vui lòng nhập channel handle.")
        if mode == FetchMode.PLAYLIST and not playlist:
            raise ValueError("Vui lòng nhập playlist ID.")
        if mode == FetchMode.VIDEO_IDS and not video_ids:
            raise ValueError("Vui lòng nhập danh sách video IDs.")

        try:
            max_results = int(self.source_section.max_results_var.get())
        except ValueError:
            raise ValueError("Max results phải là số.") from None

        if max_results <= 0:
            raise ValueError("Max results phải lớn hơn 0.")

        fetch_config = FetchConfig(
            mode=mode,
            scope=scope,
            channel_handle=channel,
            playlist_id=playlist,
            video_ids_raw=video_ids,
            max_results=max_results,
            manually_created=bool(self.source_section.manual_var.get()),
            languages=self.source_section.languages(),
            metadata_fields=self.export_section.selected_metadata(),
            include_timing=self.export_section.include_timing(),
        )

        fetch_config.proxy = self.network_section.to_proxy_settings()
        fetch_config.http = self.network_section.to_http_settings()
        return fetch_config

    def _build_export_config(self) -> ExportConfig:
        filename = self.export_section.filename_var.get().strip()
        if not filename:
            raise ValueError("Tên file không được rỗng.")

        export_config = ExportConfig(
            filename=filename,
            output_dir=self.export_section.output_dir(),
            format=ExportFormat(self.export_section.format_var.get()),
            per_video=self.export_section.per_video(),
        )
        return export_config

