"""Resolve portable app paths (next to the EXE / project root when running from source)."""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE_PRESETS_DIRNAME = "Engine"
TRANSMISSION_PRESETS_DIRNAME = "Transmission"
DEFAULT_PRESETS_FOLDER_NAME = "Presets"
LEGACY_PRESETS_FOLDER_NAME = "Custom Presets"
LEGACY_ENGINE_PRESETS_DIRNAME = "Engine presets"
LEGACY_TRANSMISSION_PRESETS_DIRNAME = "Transmission presets"
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


def legacy_presets_root() -> Path:
    return get_app_dir() / LEGACY_PRESETS_FOLDER_NAME


def settings_path() -> Path:
    return get_app_dir() / SETTINGS_FILENAME


def log_path() -> Path:
    return get_app_dir() / LOG_FILENAME


def resource_root() -> Path:
    """Bundled assets root (PyInstaller _MEIPASS) or project root when running from source."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def bundled_presets_root() -> Path:
    """Shipped factory presets (read-only in a frozen build)."""
    return resource_root() / DEFAULT_PRESETS_FOLDER_NAME


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


def engine_preset_scan_dirs(presets_root: Path) -> list[Path]:
    """Current Engine/ folder plus legacy 'Engine presets' if it still exists."""
    root = Path(presets_root)
    dirs = [root / ENGINE_PRESETS_DIRNAME]
    legacy = root / LEGACY_ENGINE_PRESETS_DIRNAME
    if legacy.is_dir() and legacy.resolve() != dirs[0].resolve():
        dirs.append(legacy)
    return dirs


def transmission_preset_scan_dirs(presets_root: Path) -> list[Path]:
    root = Path(presets_root)
    dirs = [root / TRANSMISSION_PRESETS_DIRNAME]
    legacy = root / LEGACY_TRANSMISSION_PRESETS_DIRNAME
    if legacy.is_dir() and legacy.resolve() != dirs[0].resolve():
        dirs.append(legacy)
    return dirs


def ensure_presets_tree(presets_root: Path) -> None:
    """Create Presets / Engine / Transmission if missing."""
    root = Path(presets_root)
    root.mkdir(parents=True, exist_ok=True)
    engine_presets_dir(root).mkdir(parents=True, exist_ok=True)
    transmission_presets_dir(root).mkdir(parents=True, exist_ok=True)
