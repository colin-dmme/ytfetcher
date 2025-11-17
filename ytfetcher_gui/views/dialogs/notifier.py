from __future__ import annotations

from tkinter import messagebox


def show_info(parent, title: str, message: str) -> None:
    messagebox.showinfo(title, message, parent=parent)


def show_warning(parent, title: str, message: str) -> None:
    messagebox.showwarning(title, message, parent=parent)


def show_error(parent, title: str, message: str) -> None:
    messagebox.showerror(title, message, parent=parent)

