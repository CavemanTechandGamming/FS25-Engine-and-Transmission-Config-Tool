"""Settings dialog — custom preset folder location and default presets."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from src.core import settings as app_settings
from src.core.paths import default_presets_root, log_path
from src.core.presets import PresetManager
from src.ui.dialogs import show_error, show_info

logger = logging.getLogger("fs25config.settings_ui")

_NONE_LABEL = "(None — use form defaults)"


def _open_log_file() -> None:
    """Open the app log in the system default viewer (create empty file if missing)."""
    path = log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            path.touch()
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        logger.info("Opened log file: %s", path)
    except Exception as e:
        logger.exception("Failed to open log file: %s", e)
        show_error("Settings", f"Could not open the log file:\n{e}")


def show_settings(master, on_saved=None) -> None:
    """Open the Settings dialog. on_saved() is called after a successful save."""
    try:
        import customtkinter as ctk

        _show_settings_ctk(master, ctk, on_saved)
    except ImportError:
        _show_settings_tk(master, on_saved)


def _preset_choices(names):
    return [_NONE_LABEL] + list(names)


def _from_choice(value: str) -> str:
    if not value or value == _NONE_LABEL:
        return ""
    return value


def _to_choice(stored: str, names) -> str:
    if stored and stored in names:
        return stored
    return _NONE_LABEL


def _show_settings_ctk(master, ctk, on_saved) -> None:
    current = app_settings.get_settings()
    presets_root = app_settings.get_presets_root()
    engine_names = PresetManager.list_engine_preset_names()
    trans_names = PresetManager.list_transmission_preset_names()

    dialog = ctk.CTkToplevel(master)
    dialog.title("Settings")
    dialog.geometry("640x580")
    dialog.minsize(600, 540)
    dialog.resizable(True, True)
    dialog.transient(master)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_rowconfigure(4, weight=1)

    ctk.CTkLabel(
        dialog,
        text="Settings",
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        dialog,
        text="Custom presets folder and startup defaults. Built-in presets are never overwritten.",
        font=ctk.CTkFont(size=12),
        text_color="gray65",
        wraplength=580,
        justify="left",
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

    # Presets root
    folder_frame = ctk.CTkFrame(dialog)
    folder_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
    folder_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        folder_frame,
        text="Custom Presets location",
        font=ctk.CTkFont(size=13, weight="bold"),
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))

    ctk.CTkLabel(
        folder_frame,
        text="Contains “Engine presets” and “Transmission presets” subfolders.\n"
        f"Default: {default_presets_root()}",
        font=ctk.CTkFont(size=11),
        text_color="gray65",
        wraplength=560,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 6))

    path_var = tk.StringVar(value=str(presets_root))
    path_entry = ctk.CTkEntry(folder_frame, textvariable=path_var)
    path_entry.grid(row=2, column=0, sticky="ew", padx=(12, 8), pady=(0, 10))

    def browse() -> None:
        chosen = filedialog.askdirectory(
            parent=dialog,
            title="Select Custom Presets folder",
            initialdir=path_var.get() or str(default_presets_root()),
        )
        if chosen:
            path_var.set(chosen)

    ctk.CTkButton(folder_frame, text="Browse…", width=90, command=browse).grid(
        row=2, column=1, sticky="e", padx=(0, 12), pady=(0, 10)
    )

    # Defaults
    defaults_frame = ctk.CTkFrame(dialog)
    defaults_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
    defaults_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        defaults_frame,
        text="Default presets on startup",
        font=ctk.CTkFont(size=13, weight="bold"),
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 8))

    ctk.CTkLabel(defaults_frame, text="Engine:").grid(
        row=1, column=0, sticky="w", padx=12, pady=4
    )
    engine_var = tk.StringVar(
        value=_to_choice(current.get("default_engine_preset", ""), engine_names)
    )
    engine_menu = ctk.CTkOptionMenu(
        defaults_frame,
        values=_preset_choices(engine_names),
        variable=engine_var,
        width=280,
    )
    engine_menu.grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=4)

    ctk.CTkLabel(defaults_frame, text="Transmission:").grid(
        row=2, column=0, sticky="w", padx=12, pady=(4, 12)
    )
    trans_var = tk.StringVar(
        value=_to_choice(current.get("default_transmission_preset", ""), trans_names)
    )
    trans_menu = ctk.CTkOptionMenu(
        defaults_frame,
        values=_preset_choices(trans_names),
        variable=trans_var,
        width=280,
    )
    trans_menu.grid(row=2, column=1, sticky="ew", padx=(8, 12), pady=(4, 12))

    # Log path hint
    log_frame = ctk.CTkFrame(dialog)
    log_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 8))
    log_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        log_frame,
        text="Log file (auto-rotates, stays small)",
        font=ctk.CTkFont(size=13, weight="bold"),
        anchor="w",
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))
    ctk.CTkLabel(
        log_frame,
        text=str(log_path()),
        font=ctk.CTkFont(size=11),
        text_color="gray65",
        justify="left",
        wraplength=420,
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", padx=(12, 8), pady=(0, 12))
    ctk.CTkButton(
        log_frame,
        text="Open log file",
        width=120,
        fg_color=("gray70", "gray35"),
        hover_color=("gray60", "gray30"),
        command=_open_log_file,
    ).grid(row=1, column=1, sticky="ne", padx=(0, 12), pady=(0, 12))

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=5, column=0, sticky="ew", padx=20, pady=(4, 16))
    buttons.grid_columnconfigure(0, weight=1)

    def do_save() -> None:
        try:
            root = Path(path_var.get().strip()).expanduser()
            if not str(root):
                show_error("Settings", "Please choose a Custom Presets folder.")
                return
            app_settings.save_settings(
                presets_root=root,
                default_engine_preset=_from_choice(engine_var.get()),
                default_transmission_preset=_from_choice(trans_var.get()),
            )
            PresetManager.reload_custom_presets()
            logger.info("Settings saved via dialog")
            show_info("Settings", "Settings saved.")
            dialog.destroy()
            if on_saved:
                on_saved()
        except Exception as e:
            logger.exception("Failed to save settings: %s", e)
            show_error("Settings", f"Failed to save settings:\n{e}")

    ctk.CTkButton(buttons, text="Save", width=100, command=do_save).pack(
        side=tk.RIGHT, padx=(8, 0)
    )
    ctk.CTkButton(
        buttons,
        text="Cancel",
        width=100,
        fg_color=("gray70", "gray35"),
        hover_color=("gray60", "gray30"),
        command=dialog.destroy,
    ).pack(side=tk.RIGHT)

    def _fit_and_center() -> None:
        try:
            dialog.update_idletasks()
            req_w = max(640, dialog.winfo_reqwidth() + 24)
            req_h = max(580, dialog.winfo_reqheight() + 24)
            sw = dialog.winfo_screenwidth()
            sh = dialog.winfo_screenheight()
            w = min(req_w, max(600, sw - 40))
            h = min(req_h, max(540, sh - 80))
            if master is not None:
                px, py = master.winfo_rootx(), master.winfo_rooty()
                pw, ph = master.winfo_width(), master.winfo_height()
                x = px + max(0, (pw - w) // 2)
                y = py + max(0, (ph - h) // 2)
            else:
                x = max(0, (sw - w) // 2)
                y = max(0, (sh - h) // 2)
            dialog.geometry(f"{w}x{h}+{x}+{y}")
            dialog.lift()
        except Exception:
            pass

    dialog.after(10, _fit_and_center)
    dialog.focus()


def _show_settings_tk(master, on_saved) -> None:
    current = app_settings.get_settings()
    presets_root = app_settings.get_presets_root()
    engine_names = PresetManager.list_engine_preset_names()
    trans_names = PresetManager.list_transmission_preset_names()

    dialog = tk.Toplevel(master)
    dialog.title("Settings")
    dialog.geometry("640x560")
    dialog.minsize(600, 520)
    dialog.resizable(True, True)
    dialog.transient(master)
    dialog.grab_set()
    dialog.configure(bg="#1e1e1e")

    frame = tk.Frame(dialog, bg="#1e1e1e", padx=20, pady=16)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        frame, text="Settings", font=("Arial", 14, "bold"),
        bg="#1e1e1e", fg="#ffffff",
    ).pack(anchor="w")
    tk.Label(
        frame,
        text="Custom presets folder and startup defaults.",
        font=("Arial", 9), bg="#1e1e1e", fg="#a0a0a0",
    ).pack(anchor="w", pady=(2, 10))

    tk.Label(
        frame, text="Custom Presets location", font=("Arial", 10, "bold"),
        bg="#1e1e1e", fg="#ffffff",
    ).pack(anchor="w")

    path_row = tk.Frame(frame, bg="#1e1e1e")
    path_row.pack(fill=tk.X, pady=6)
    path_var = tk.StringVar(value=str(presets_root))
    tk.Entry(
        path_row, textvariable=path_var, bg="#2d2d2d", fg="#ffffff",
        insertbackground="#ffffff",
    ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def browse() -> None:
        chosen = filedialog.askdirectory(
            parent=dialog,
            title="Select Custom Presets folder",
            initialdir=path_var.get() or str(default_presets_root()),
        )
        if chosen:
            path_var.set(chosen)

    tk.Button(
        path_row, text="Browse…", command=browse,
        bg="#3d3d3d", fg="#ffffff",
    ).pack(side=tk.RIGHT)

    tk.Label(
        frame, text="Default engine preset", bg="#1e1e1e", fg="#ffffff",
    ).pack(anchor="w", pady=(10, 2))
    engine_var = tk.StringVar(
        value=_to_choice(current.get("default_engine_preset", ""), engine_names)
    )
    engine_box = ttk_safe_combobox(
        frame, engine_var, _preset_choices(engine_names)
    )
    engine_box.pack(fill=tk.X)

    tk.Label(
        frame, text="Default transmission preset", bg="#1e1e1e", fg="#ffffff",
    ).pack(anchor="w", pady=(10, 2))
    trans_var = tk.StringVar(
        value=_to_choice(current.get("default_transmission_preset", ""), trans_names)
    )
    trans_box = ttk_safe_combobox(
        frame, trans_var, _preset_choices(trans_names)
    )
    trans_box.pack(fill=tk.X)

    tk.Label(
        frame, text="Log file (auto-rotates, stays small)", font=("Arial", 9, "bold"),
        bg="#1e1e1e", fg="#ffffff",
    ).pack(anchor="w", pady=(12, 2))
    log_row = tk.Frame(frame, bg="#1e1e1e")
    log_row.pack(fill=tk.X, pady=(0, 8))
    tk.Label(
        log_row, text=str(log_path()), font=("Arial", 8),
        bg="#1e1e1e", fg="#a0a0a0", justify=tk.LEFT, wraplength=400,
    ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(
        log_row, text="Open log file", command=_open_log_file,
        bg="#3d3d3d", fg="#ffffff",
    ).pack(side=tk.RIGHT, padx=(8, 0))

    btn_row = tk.Frame(frame, bg="#1e1e1e")
    btn_row.pack(fill=tk.X, pady=(8, 0))

    def do_save() -> None:
        try:
            root = Path(path_var.get().strip()).expanduser()
            if not str(root):
                show_error("Settings", "Please choose a Custom Presets folder.")
                return
            app_settings.save_settings(
                presets_root=root,
                default_engine_preset=_from_choice(engine_var.get()),
                default_transmission_preset=_from_choice(trans_var.get()),
            )
            PresetManager.reload_custom_presets()
            show_info("Settings", "Settings saved.")
            dialog.destroy()
            if on_saved:
                on_saved()
        except Exception as e:
            logger.exception("Failed to save settings: %s", e)
            show_error("Settings", f"Failed to save settings:\n{e}")

    tk.Button(
        btn_row, text="Cancel", command=dialog.destroy,
        bg="#3d3d3d", fg="#ffffff",
    ).pack(side=tk.RIGHT, padx=(8, 0))
    tk.Button(
        btn_row, text="Save", command=do_save,
        bg="#1f538d", fg="#ffffff",
    ).pack(side=tk.RIGHT)

    dialog.focus()


def ttk_safe_combobox(parent, variable, values):
    from tkinter import ttk

    box = ttk.Combobox(
        parent, textvariable=variable, values=values, state="readonly",
    )
    return box
