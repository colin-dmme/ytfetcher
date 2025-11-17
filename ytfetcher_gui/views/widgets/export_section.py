from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from ytfetcher_gui.models import ExportFormat
from ytfetcher_gui.views.layouts import apply_responsive_grid


class ExportSection(ttk.LabelFrame):
    """
    Thiết lập tham số export và metadata.
    """

    METADATA_OPTIONS = ["title", "description", "url", "duration", "view_count", "thumbnails"]

    def __init__(self, master: tk.Widget):
        super().__init__(master, text="Xuất dữ liệu")
        self._init_vars()
        self._build_ui()

    def _init_vars(self) -> None:
        self.filename_var = tk.StringVar(value="ytfetcher_export")
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))
        self.include_timing_var = tk.BooleanVar(value=True)
        self.per_video_var = tk.BooleanVar(value=False)
        self.format_var = tk.StringVar(value=ExportFormat.JSON.value)
        self.metadata_flags = {field: tk.BooleanVar(value=(field in {"title", "description"})) for field in self.METADATA_OPTIONS}

    def _build_ui(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(frame, text="Tên file").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.filename_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="Thư mục xuất").grid(row=1, column=0, sticky="w")
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=1, sticky="ew")
        ttk.Entry(dir_frame, textvariable=self.output_dir_var).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="Chọn...", command=self._choose_dir).pack(side="left", padx=4)

        ttk.Label(frame, text="Định dạng").grid(row=2, column=0, sticky="w")
        format_box = ttk.Combobox(
            frame,
            textvariable=self.format_var,
            values=[fmt.value for fmt in ExportFormat],
            state="readonly",
            width=10,
        )
        format_box.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Checkbutton(frame, text="Bao gồm thời gian transcript", variable=self.include_timing_var).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(frame, text="Mỗi video xuất 1 file riêng", variable=self.per_video_var).grid(row=3, column=2, columnspan=1, sticky="w")

        meta_frame = ttk.LabelFrame(frame, text="Metadata")
        meta_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)

        for idx, field in enumerate(self.METADATA_OPTIONS):
            ttk.Checkbutton(meta_frame, text=field, variable=self.metadata_flags[field]).grid(row=idx // 3, column=idx % 3, sticky="w", padx=4, pady=2)

        apply_responsive_grid(frame, 2)
        apply_responsive_grid(meta_frame, 3)

    def _choose_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def selected_metadata(self) -> list[str]:
        return [field for field, flag in self.metadata_flags.items() if flag.get()]

    def export_format(self) -> ExportFormat:
        return ExportFormat(self.format_var.get())

    def include_timing(self) -> bool:
        return bool(self.include_timing_var.get())

    def per_video(self) -> bool:
        return bool(self.per_video_var.get())

    def output_dir(self) -> Path:
        return Path(self.output_dir_var.get())

