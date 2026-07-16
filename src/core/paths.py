"""Resolve portable app paths (next to the EXE / project root when running from source)."""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE_PRESETS_DIRNAME = "Engine presets"
TRANSMISSION_PRESETS_DIRNAME = "Transmission presets"
DEFAULT_PRESETS_FOLDER_NAME = "Custom Presets"
SETTINGS_FILENAME = "settings.json"
LOG_FILENAME = "fs25_config_tool.log"


def get_app_dir() -> Path:
    """
    Directory next to the frozen EXE, or the repo/project root when running from source.
    Used as the default home for settings, logs, and custom presets.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # src/core/paths.py -> parents[2] == project root
    return Path(__file__).resolve().parents[2]


def default_presets_root() -> Path:
    return get_app_dir() / DEFAULT_PRESETS_FOLDER_NAME


def settings_path() -> Path:
    return get_app_dir() / SETTINGS_FILENAME


def log_path() -> Path:
    return get_app_dir() / LOG_FILENAME


def resource_root() -> Path:
    """Bundled assets root (PyInstaller _MEIPASS) or project root when running from source."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def app_icon_png() -> Path | None:
    candidates = [
        resource_root() / "assets" / "app_icon_256.png",
        get_app_dir() / "assets" / "app_icon_256.png",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def app_icon_ico() -> Path | None:
    candidates = [
        resource_root() / "assets" / "app_icon.ico",
        get_app_dir() / "assets" / "app_icon.ico",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def engine_presets_dir(presets_root: Path) -> Path:
    return Path(presets_root) / ENGINE_PRESETS_DIRNAME


def transmission_presets_dir(presets_root: Path) -> Path:
    return Path(presets_root) / TRANSMISSION_PRESETS_DIRNAME


def ensure_presets_tree(presets_root: Path) -> None:
    """Create Custom Presets / Engine presets / Transmission presets if missing."""
    root = Path(presets_root)
    root.mkdir(parents=True, exist_ok=True)
    engine_presets_dir(root).mkdir(parents=True, exist_ok=True)
    transmission_presets_dir(root).mkdir(parents=True, exist_ok=True)
