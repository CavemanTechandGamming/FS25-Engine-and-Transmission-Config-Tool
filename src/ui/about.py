"""
Simple About dialog — short blurb + Buy Me a Coffee support link.
"""

from __future__ import annotations

import webbrowser

from src import __version__

# ── Support link ─────────────────────────────────────────────────────────────
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/caveman117"
# ─────────────────────────────────────────────────────────────────────────────

_APP_NAME = "FS25 Engine and Transmission Config Tool"

_ABOUT_BLURB = (
    "Generate Farming Simulator 25 engine and transmission XML configurations "
    "with auto torque curves, gear ratio math, built-in presets, and "
    "FS25-compatible export.\n\n"
    "Configure an engine and transmission, preview the XML, then copy or save "
    "it for your mod."
)


def _open_coffee() -> None:
    webbrowser.open(BUY_ME_A_COFFEE_URL)


def show_about(master) -> None:
    """Open the About dialog (CustomTkinter or standard Tkinter)."""
    try:
        import customtkinter as ctk

        _show_about_ctk(master, ctk)
    except ImportError:
        _show_about_tk(master)


def _show_about_ctk(master, ctk) -> None:
    dialog = ctk.CTkToplevel(master)
    dialog.title(f"About {_APP_NAME}")
    dialog.geometry("460x340")
    dialog.minsize(420, 300)
    dialog.resizable(False, False)
    dialog.transient(master)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        dialog,
        text=_APP_NAME,
        font=ctk.CTkFont(size=18, weight="bold"),
        wraplength=410,
        justify="left",
        anchor="w",
    ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 2))

    ctk.CTkLabel(
        dialog,
        text=f"Version {__version__}",
        font=ctk.CTkFont(size=12),
        text_color="gray65",
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

    ctk.CTkLabel(
        dialog,
        text=_ABOUT_BLURB,
        font=ctk.CTkFont(size=13),
        wraplength=410,
        justify="left",
        anchor="w",
    ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))
    buttons.grid_columnconfigure(0, weight=1)

    ctk.CTkButton(
        buttons,
        text="Buy Me a Coffee",
        command=_open_coffee,
    ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

    ctk.CTkButton(
        buttons,
        text="Close",
        fg_color=("gray40", "gray30"),
        hover_color=("gray35", "gray25"),
        command=dialog.destroy,
    ).grid(row=1, column=0, sticky="ew")

    def _center() -> None:
        try:
            dialog.update_idletasks()
            px = master.winfo_rootx()
            py = master.winfo_rooty()
            pw = master.winfo_width()
            ph = master.winfo_height()
            w = dialog.winfo_width()
            h = dialog.winfo_height()
            dialog.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        except Exception:
            pass

    dialog.after(10, _center)
    dialog.focus()


def _show_about_tk(master) -> None:
    import tkinter as tk
    from tkinter import ttk

    dialog = tk.Toplevel(master)
    dialog.title(f"About {_APP_NAME}")
    dialog.geometry("460x340")
    dialog.minsize(420, 300)
    dialog.resizable(False, False)
    dialog.transient(master)
    dialog.grab_set()
    dialog.configure(bg="#1e1e1e")

    frame = tk.Frame(dialog, bg="#1e1e1e", padx=20, pady=18)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        frame,
        text=_APP_NAME,
        font=("Arial", 14, "bold"),
        bg="#1e1e1e",
        fg="#ffffff",
        wraplength=410,
        justify=tk.LEFT,
        anchor="w",
    ).pack(anchor="w")

    tk.Label(
        frame,
        text=f"Version {__version__}",
        font=("Arial", 10),
        bg="#1e1e1e",
        fg="#a0a0a0",
    ).pack(anchor="w", pady=(2, 10))

    tk.Label(
        frame,
        text=_ABOUT_BLURB,
        font=("Arial", 10),
        bg="#1e1e1e",
        fg="#e0e0e0",
        wraplength=410,
        justify=tk.LEFT,
        anchor="w",
    ).pack(anchor="w", fill=tk.X, pady=(0, 16))

    ttk.Button(frame, text="Buy Me a Coffee", command=_open_coffee).pack(fill=tk.X, pady=(0, 8))
    ttk.Button(frame, text="Close", command=dialog.destroy).pack(fill=tk.X)

    dialog.focus()
