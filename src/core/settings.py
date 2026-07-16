"""Persistent app settings (JSON next to the EXE / project root)."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.paths import default_presets_root, ensure_presets_tree, settings_path

logger = logging.getLogger("fs25config.settings")

_DEFAULTS: Dict[str, Any] = {
    "presets_root": None,  # None => use default_presets_root()
    "default_engine_preset": "",
    "default_transmission_preset": "",
}

_settings: Dict[str, Any] = deepcopy(_DEFAULTS)
_loaded = False


def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(_DEFAULTS)
    if not isinstance(data, dict):
        return out
    root = data.get("presets_root")
    if root:
        out["presets_root"] = str(Path(root))
    else:
        out["presets_root"] = None
    out["default_engine_preset"] = str(data.get("default_engine_preset") or "")
    out["default_transmission_preset"] = str(
        data.get("default_transmission_preset") or ""
    )
    return out


def load_settings() -> Dict[str, Any]:
    """Load settings from disk (or defaults). Creates presets folders."""
    global _settings, _loaded
    path = settings_path()
    try:
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                _settings = _normalize(json.load(f))
            logger.info("Loaded settings from %s", path)
        else:
            _settings = deepcopy(_DEFAULTS)
            logger.info("No settings file yet; using defaults (%s)", path)
    except Exception as e:
        logger.exception("Failed to load settings; using defaults: %s", e)
        _settings = deepcopy(_DEFAULTS)

    # Mark loaded before resolving paths (avoids load ↔ get_settings recursion)
    _loaded = True
    ensure_presets_tree(get_presets_root())
    return get_settings()


def get_settings() -> Dict[str, Any]:
    global _loaded
    if not _loaded:
        return load_settings()
    return deepcopy(_settings)


def get_presets_root() -> Path:
    if not _loaded:
        load_settings()
    raw = _settings.get("presets_root")
    if raw:
        return Path(raw)
    return default_presets_root()


def get_default_engine_preset() -> str:
    if not _loaded:
        load_settings()
    return str(_settings.get("default_engine_preset") or "")


def get_default_transmission_preset() -> str:
    if not _loaded:
        load_settings()
    return str(_settings.get("default_transmission_preset") or "")


def save_settings(
    *,
    presets_root: Optional[str | Path] = None,
    default_engine_preset: Optional[str] = None,
    default_transmission_preset: Optional[str] = None,
) -> Dict[str, Any]:
    """Update and persist settings. Pass only fields you want to change."""
    global _settings, _loaded
    current = get_settings()

    if presets_root is not None:
        root = Path(presets_root).expanduser().resolve()
        current["presets_root"] = str(root)
    if default_engine_preset is not None:
        current["default_engine_preset"] = str(default_engine_preset).strip()
    if default_transmission_preset is not None:
        current["default_transmission_preset"] = str(
            default_transmission_preset
        ).strip()

    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    _settings = _normalize(current)
    _loaded = True
    ensure_presets_tree(get_presets_root())
    logger.info("Saved settings to %s", path)
    return get_settings()
