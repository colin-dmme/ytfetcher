from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ytfetcher_gui.models import FetchMode
from ytfetcher_gui.views.layouts import apply_responsive_grid


class SourceSection(ttk.LabelFrame):
    """
    Khối nhập liệu chính cho nguồn dữ liệu.
    """

    def __init__(self, master: tk.Widget):
        super().__init__(master, text="Nguồn dữ liệu")
        self._init_vars()
        self._build_ui()
        self._bind_events()
        self.after(10, self._toggle_inputs)

    def _init_vars(self) -> None:
        self.mode_var = tk.StringVar(value=FetchMode.CHANNEL.value)
        self.channel_var = tk.StringVar()
        self.playlist_var = tk.StringVar()
        self.max_results_var = tk.StringVar(value="25")
        self.manual_var = tk.BooleanVar(value=False)
        self.languages_var = tk.StringVar(value="en")
        self.scope_var = tk.StringVar(value="full")

    def _build_ui(self) -> None:
        grid = ttk.Frame(self)
        grid.pack(fill="x", padx=8, pady=8)

        ttk.Label(grid, text="Chế độ").grid(row=0, column=0, sticky="w")
        mode_box = ttk.Combobox(
            grid,
            textvariable=self.mode_var,
            values=[mode.value for mode in FetchMode],
            state="readonly",
            width=15,
        )
        mode_box.grid(row=0, column=1, sticky="w")

        ttk.Label(grid, text="Channel handle").grid(row=1, column=0, sticky="w")
        self.channel_entry = ttk.Entry(grid, textvariable=self.channel_var)
        self.channel_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=2)

        ttk.Label(grid, text="Playlist ID").grid(row=2, column=0, sticky="w")
        self.playlist_entry = ttk.Entry(grid, textvariable=self.playlist_var)
        self.playlist_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=2)

        self.video_label = ttk.Label(grid, text="Video IDs (mỗi dòng)")
        self.video_label.grid(row=3, column=0, sticky="nw")
        self.video_container = ttk.Frame(grid)
        self.video_container.grid(row=3, column=1, columnspan=3, sticky="ew")
        self.video_text = tk.Text(self.video_container, height=4, width=40)
        self.video_scroll = ttk.Scrollbar(self.video_container, orient="vertical", command=self.video_text.yview)
        self.video_text.configure(yscrollcommand=self.video_scroll.set)
        self.video_text.pack(side="left", fill="both", expand=True)
        self.video_scroll.pack(side="right", fill="y")

        self.video_stats_var = tk.StringVar(value="0 IDs")
        ttk.Label(grid, textvariable=self.video_stats_var, foreground="#555555").grid(row=4, column=1, columnspan=3, sticky="w", pady=(2, 0))

        ttk.Label(grid, text="Max results").grid(row=5, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.max_results_var, width=10).grid(row=5, column=1, sticky="w")

        ttk.Label(grid, text="Ngôn ngữ (cách nhau bởi dấu phẩy)").grid(row=6, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.languages_var).grid(row=6, column=1, columnspan=3, sticky="ew")

        ttk.Label(grid, text="Kiểu dữ liệu").grid(row=7, column=0, sticky="w")
        scope_box = ttk.Combobox(
            grid,
            textvariable=self.scope_var,
            values=["full", "transcripts", "metadata"],
            state="readonly",
            width=15,
        )
        scope_box.grid(row=7, column=1, sticky="w")

        ttk.Checkbutton(grid, text="Chỉ transcript tạo thủ công", variable=self.manual_var).grid(row=8, column=0, columnspan=2, sticky="w", pady=4)

        apply_responsive_grid(grid, 4)

    def _bind_events(self) -> None:
        self.mode_var.trace_add("write", lambda *_: self._toggle_inputs())
        self.video_text.bind("<<Modified>>", self._update_stats)

    def _toggle_inputs(self) -> None:
        mode = FetchMode(self.mode_var.get())

        if mode == FetchMode.CHANNEL:
            self.channel_entry.configure(state=tk.NORMAL)
            self.playlist_entry.configure(state=tk.DISABLED)
            self.video_label.grid_remove()
            self.video_container.grid_remove()
        elif mode == FetchMode.PLAYLIST:
            self.channel_entry.configure(state=tk.DISABLED)
            self.playlist_entry.configure(state=tk.NORMAL)
            self.video_label.grid_remove()
            self.video_container.grid_remove()
        else:
            self.channel_entry.configure(state=tk.DISABLED)
            self.playlist_entry.configure(state=tk.DISABLED)
            self.video_label.grid(row=3, column=0, sticky="nw")
            self.video_container.grid(row=3, column=1, columnspan=3, sticky="ew")
            self.video_text.focus_set()
            self._update_stats()

    def _update_stats(self, *_):
        text = self.video_text.get("1.0", tk.END).strip()
        count = len([item for item in text.splitlines() if item.strip()])
        self.video_stats_var.set(f"{count} IDs")
        if self.video_text.edit_modified():
            self.video_text.edit_modified(False)

    def languages(self) -> list[str]:
        text = self.languages_var.get()
        return [lang.strip() for lang in text.split(",") if lang.strip()] or ["en"]

    def video_ids(self) -> str:
        return self.video_text.get("1.0", tk.END).strip()

