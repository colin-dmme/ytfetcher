from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ytfetcher_gui.models import HTTPSettings, ProxySettings
from ytfetcher_gui.views.layouts import apply_responsive_grid


class NetworkSection(ttk.LabelFrame):
    """
    Khu vực nhập Proxy và HTTP config.
    """

    def __init__(self, master: tk.Widget):
        super().__init__(master, text="Kết nối")
        self._init_vars()
        self._build_ui()

    def _init_vars(self) -> None:
        self.http_proxy_var = tk.StringVar()
        self.https_proxy_var = tk.StringVar()
        self.webshare_user_var = tk.StringVar()
        self.webshare_pass_var = tk.StringVar()
        self.timeout_var = tk.StringVar(value="4.0")
        self.headers_text = tk.Text(self, height=4, width=40)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(frame, text="HTTP proxy").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.http_proxy_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="HTTPS proxy").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.https_proxy_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="Webshare user").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.webshare_user_var).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="Webshare pass").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.webshare_pass_var, show="*").grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="Timeout (s)").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.timeout_var, width=10).grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="HTTP headers (JSON)").grid(row=5, column=0, sticky="nw")
        headers_holder = ttk.Frame(frame)
        headers_holder.grid(row=5, column=1, sticky="ew")
        self.headers_text.pack(in_=headers_holder, fill="both", expand=True)

        apply_responsive_grid(frame, 2)

    def to_proxy_settings(self) -> ProxySettings:
        return ProxySettings(
            http_proxy=self.http_proxy_var.get().strip(),
            https_proxy=self.https_proxy_var.get().strip(),
            webshare_username=self.webshare_user_var.get().strip(),
            webshare_password=self.webshare_pass_var.get().strip(),
        )

    def to_http_settings(self) -> HTTPSettings:
        try:
            timeout = float(self.timeout_var.get())
        except ValueError:
            timeout = 4.0
        return HTTPSettings(timeout=timeout, headers_raw=self.headers_text.get("1.0", tk.END).strip())

