from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_responsive_grid(widget: tk.Widget, columns: int) -> None:
    """
    Thiết lập trọng số đều cho grid nhằm giúp widget co giãn tốt hơn.
    """

    if isinstance(widget, (tk.Frame, ttk.Frame, ttk.LabelFrame)):
        for col in range(columns):
            widget.columnconfigure(col, weight=1)

