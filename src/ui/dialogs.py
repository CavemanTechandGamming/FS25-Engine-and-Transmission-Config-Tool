"""Themed modal dialogs that match the app (CustomTkinter dark UI, Tk fallback)."""

from __future__ import annotations

from typing import Optional

_dialog_parent = None


def set_dialog_parent(parent) -> None:
    """Register the main window so dialogs can center / stay on top."""
    global _dialog_parent
    _dialog_parent = parent


def _parent(explicit=None):
    return explicit or _dialog_parent


def _use_ctk() -> bool:
    try:
        import customtkinter  # noqa: F401

        return True
    except ImportError:
        return False


def show_info(title: str, message: str, parent=None) -> None:
    _message_dialog(title, message, kind="info", parent=parent)


def show_error(title: str, message: str, parent=None) -> None:
    _message_dialog(title, message, kind="error", parent=parent)


def ask_yes_no(title: str, message: str, parent=None) -> bool:
    return _confirm_dialog(title, message, parent=parent)


def ask_string(title: str, prompt: str, parent=None, initialvalue: str = "") -> Optional[str]:
    if _use_ctk():
        return _ask_string_ctk(title, prompt, parent, initialvalue)
    from tkinter import simpledialog

    return simpledialog.askstring(title, prompt, parent=_parent(parent), initialvalue=initialvalue)


def _message_dialog(title: str, message: str, *, kind: str, parent=None) -> None:
    if _use_ctk():
        _message_ctk(title, message, kind=kind, parent=parent)
        return
    from tkinter import messagebox

    root = _parent(parent)
    if kind == "error":
        messagebox.showerror(title, message, parent=root)
    else:
        messagebox.showinfo(title, message, parent=root)


def _confirm_dialog(title: str, message: str, parent=None) -> bool:
    if _use_ctk():
        return _confirm_ctk(title, message, parent=parent)
    from tkinter import messagebox

    return bool(messagebox.askyesno(title, message, parent=_parent(parent)))


def _center_on_parent(dialog, master) -> None:
    try:
        dialog.update_idletasks()
        if master is None:
            return
        px, py = master.winfo_rootx(), master.winfo_rooty()
        pw, ph = master.winfo_width(), master.winfo_height()
        w, h = dialog.winfo_width(), dialog.winfo_height()
        dialog.geometry(f"+{px + max(0, (pw - w) // 2)}+{py + max(0, (ph - h) // 2)}")
    except Exception:
        pass


def _message_ctk(title: str, message: str, *, kind: str, parent=None) -> None:
    import customtkinter as ctk

    master = _parent(parent)
    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(master) if master else None
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)

    accent = ("#c75050", "#c75050") if kind == "error" else ("#1f538d", "#1f538d")

    ctk.CTkLabel(
        dialog,
        text=title,
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))

    ctk.CTkLabel(
        dialog,
        text=message,
        font=ctk.CTkFont(size=13),
        wraplength=420,
        justify="left",
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))

    ctk.CTkButton(
        dialog,
        text="OK",
        width=100,
        fg_color=accent,
        hover_color=("#a04040", "#14375e") if kind == "error" else ("#174272", "#174272"),
        command=dialog.destroy,
    ).grid(row=2, column=0, sticky="e", padx=20, pady=(0, 16))

    dialog.after(10, lambda: _center_on_parent(dialog, master))
    dialog.after(20, dialog.lift)
    dialog.wait_window()


def _confirm_ctk(title: str, message: str, parent=None) -> bool:
    import customtkinter as ctk
    import tkinter as tk

    master = _parent(parent)
    result = {"ok": False}

    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.resizable(False, False)
    if master:
        dialog.transient(master)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        dialog,
        text=title,
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))

    ctk.CTkLabel(
        dialog,
        text=message,
        font=ctk.CTkFont(size=13),
        wraplength=420,
        justify="left",
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=2, column=0, sticky="e", padx=20, pady=(0, 16))

    def yes() -> None:
        result["ok"] = True
        dialog.destroy()

    def no() -> None:
        result["ok"] = False
        dialog.destroy()

    ctk.CTkButton(
        buttons,
        text="No",
        width=90,
        fg_color=("gray70", "gray35"),
        hover_color=("gray60", "gray30"),
        command=no,
    ).pack(side=tk.RIGHT, padx=(8, 0))
    ctk.CTkButton(buttons, text="Yes", width=90, command=yes).pack(side=tk.RIGHT)

    dialog.protocol("WM_DELETE_WINDOW", no)
    dialog.after(10, lambda: _center_on_parent(dialog, master))
    dialog.after(20, dialog.lift)
    dialog.wait_window()
    return bool(result["ok"])


def _ask_string_ctk(
    title: str, prompt: str, parent=None, initialvalue: str = ""
) -> Optional[str]:
    import customtkinter as ctk
    import tkinter as tk

    master = _parent(parent)
    result = {"value": None}

    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.resizable(False, False)
    if master:
        dialog.transient(master)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        dialog,
        text=title,
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))

    ctk.CTkLabel(
        dialog,
        text=prompt,
        font=ctk.CTkFont(size=13),
        wraplength=420,
        justify="left",
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

    entry_var = tk.StringVar(value=initialvalue or "")
    entry = ctk.CTkEntry(dialog, textvariable=entry_var, width=400)
    entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
    entry.focus_set()
    if initialvalue:
        entry.select_range(0, tk.END)

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=3, column=0, sticky="e", padx=20, pady=(0, 16))

    def cancel() -> None:
        result["value"] = None
        dialog.destroy()

    def ok() -> None:
        result["value"] = entry_var.get()
        dialog.destroy()

    ctk.CTkButton(
        buttons,
        text="Cancel",
        width=90,
        fg_color=("gray70", "gray35"),
        hover_color=("gray60", "gray30"),
        command=cancel,
    ).pack(side=tk.RIGHT, padx=(8, 0))
    ctk.CTkButton(buttons, text="Save", width=90, command=ok).pack(side=tk.RIGHT)

    dialog.bind("<Return>", lambda _e: ok())
    dialog.bind("<Escape>", lambda _e: cancel())
    dialog.protocol("WM_DELETE_WINDOW", cancel)
    dialog.after(10, lambda: _center_on_parent(dialog, master))
    dialog.after(20, dialog.lift)
    dialog.after(30, entry.focus_set)
    dialog.wait_window()
    return result["value"]
