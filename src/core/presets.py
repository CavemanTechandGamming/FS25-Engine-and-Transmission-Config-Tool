from __future__ import annotations

import json
import logging
import re
import threading
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from src.core.paths import (
    engine_presets_dir,
    ensure_presets_tree,
    transmission_presets_dir,
)
from src.core import settings as app_settings

logger = logging.getLogger("fs25config.presets")

# Built-in presets (never written to disk; never overwritten by custom files)
_BUILTIN_ENGINE_PRESETS = {
    "7.3 Powerstroke": {
        "name": "7.3 Powerstroke",
        "cost": 8500,
        "horsepower": 275,
        "min_rpm": 600,
        "max_rpm": 3500,
        "fuel_usage_scale": 1.0,
        "turbocharged": True,
    },
    "6.0 Powerstroke": {
        "name": "6.0 Powerstroke",
        "cost": 12000,
        "horsepower": 325,
        "min_rpm": 650,
        "max_rpm": 3500,
        "fuel_usage_scale": 1.1,
        "turbocharged": True,
    },
    "6.7 Powerstroke": {
        "name": "6.7 Powerstroke",
        "cost": 18000,
        "horsepower": 475,
        "min_rpm": 650,
        "max_rpm": 3500,
        "fuel_usage_scale": 1.3,
        "turbocharged": True,
    },
    "5.9 Cummins": {
        "name": "5.9 Cummins",
        "cost": 11000,
        "horsepower": 325,
        "min_rpm": 700,
        "max_rpm": 3500,
        "fuel_usage_scale": 1.0,
        "turbocharged": True,
    },
    "6.7 Cummins": {
        "name": "6.7 Cummins",
        "cost": 15000,
        "horsepower": 400,
        "min_rpm": 700,
        "max_rpm": 3500,
        "fuel_usage_scale": 1.2,
        "turbocharged": True,
    },
}

_BUILTIN_TRANSMISSION_PRESETS = {
    "10-speed Allison Automatic": {
        "name": "10-speed Allison Automatic",
        "cost": 8000,
        "type": "Automatic",
        "top_speed": 120,
        "num_forward": 10,
        "num_reverse": 2,
        "enable_low_gearing": False,
        "low_gear_boost": 25.0,
    },
    "13-speed Eaton Fuller": {
        "name": "13-speed Eaton Fuller",
        "cost": 12000,
        "type": "Manual",
        "top_speed": 140,
        "num_forward": 13,
        "num_reverse": 2,
        "enable_low_gearing": False,
        "low_gear_boost": 25.0,
    },
    "4-speed with Granny Gear": {
        "name": "4-speed with Granny Gear",
        "cost": 5000,
        "type": "Manual",
        "top_speed": 80,
        "num_forward": 5,
        "num_reverse": 1,
        "enable_low_gearing": True,
        "low_gear_boost": 50.0,
    },
    "18-speed Eaton Fuller": {
        "name": "18-speed Eaton Fuller",
        "cost": 15000,
        "type": "Manual",
        "top_speed": 160,
        "num_forward": 18,
        "num_reverse": 2,
        "enable_low_gearing": False,
        "low_gear_boost": 25.0,
    },
}

_ENGINE_REQUIRED = (
    "name",
    "cost",
    "horsepower",
    "min_rpm",
    "max_rpm",
    "fuel_usage_scale",
    "turbocharged",
)
_TRANSMISSION_REQUIRED = (
    "name",
    "cost",
    "type",
    "top_speed",
    "num_forward",
    "num_reverse",
    "enable_low_gearing",
    "low_gear_boost",
)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", name.strip())
    cleaned = cleaned.strip(" .") or "preset"
    return cleaned[:80] + ".json"


class PresetManager:
    """
    Manages built-in and custom engine/transmission presets.
    Custom presets live under:
      {presets_root}/Engine presets/*.json
      {presets_root}/Transmission presets/*.json
    """

    _preset_lock = None
    _custom_engine: Dict = {}
    _custom_transmission: Dict = {}

    # Back-compat aliases used by older call sites / docs
    ENGINE_PRESETS = _BUILTIN_ENGINE_PRESETS
    TRANSMISSION_PRESETS = _BUILTIN_TRANSMISSION_PRESETS

    @classmethod
    def _get_lock(cls):
        if cls._preset_lock is None:
            cls._preset_lock = threading.Lock()
        return cls._preset_lock

    @staticmethod
    def save_preset(data: Dict, filename: str):
        """Save a combined (or any) configuration preset to a JSON file (file dialog)."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Exported preset file: %s", filename)

    @staticmethod
    def load_preset(filename: str) -> Optional[Dict]:
        """Load a configuration preset from a JSON file (file dialog)."""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Imported preset file: %s", filename)
        return data

    @classmethod
    def is_builtin_engine(cls, name: str) -> bool:
        return name in _BUILTIN_ENGINE_PRESETS

    @classmethod
    def is_builtin_transmission(cls, name: str) -> bool:
        return name in _BUILTIN_TRANSMISSION_PRESETS

    @classmethod
    def reload_custom_presets(cls, presets_root: Optional[Path] = None) -> None:
        """Scan custom preset folders and refresh in-memory custom lists."""
        root = Path(presets_root) if presets_root else app_settings.get_presets_root()
        ensure_presets_tree(root)

        engine: Dict = {}
        transmission: Dict = {}

        e_dir = engine_presets_dir(root)
        t_dir = transmission_presets_dir(root)

        for path in sorted(e_dir.glob("*.json")):
            loaded = cls._load_engine_file(path)
            if loaded is None:
                continue
            name, data = loaded
            if name in _BUILTIN_ENGINE_PRESETS:
                logger.warning(
                    "Skipping custom engine preset %r (conflicts with built-in)", name
                )
                continue
            if name in engine:
                logger.warning("Duplicate custom engine preset name %r in %s", name, path)
            engine[name] = data

        for path in sorted(t_dir.glob("*.json")):
            loaded = cls._load_transmission_file(path)
            if loaded is None:
                continue
            name, data = loaded
            if name in _BUILTIN_TRANSMISSION_PRESETS:
                logger.warning(
                    "Skipping custom transmission preset %r (conflicts with built-in)",
                    name,
                )
                continue
            if name in transmission:
                logger.warning(
                    "Duplicate custom transmission preset name %r in %s", name, path
                )
            transmission[name] = data

        with cls._get_lock():
            cls._custom_engine = engine
            cls._custom_transmission = transmission

        logger.info(
            "Loaded custom presets from %s (engines=%d, transmissions=%d)",
            root,
            len(engine),
            len(transmission),
        )

    @classmethod
    def _load_engine_file(cls, path: Path) -> Optional[Tuple[str, Dict]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            data = raw.get("engine", raw) if isinstance(raw, dict) else None
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            for field in _ENGINE_REQUIRED:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")
            name = str(data.get("name") or path.stem).strip()
            if not name:
                raise ValueError("Empty name")
            # Prefer display name from file stem only if name missing; keep data['name']
            display = name
            # Allow optional top-level "preset_name" for dropdown label
            if isinstance(raw, dict) and raw.get("preset_name"):
                display = str(raw["preset_name"]).strip() or display
            return display, data
        except Exception as e:
            logger.warning("Could not load engine preset %s: %s", path, e)
            return None

    @classmethod
    def _load_transmission_file(cls, path: Path) -> Optional[Tuple[str, Dict]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            data = raw.get("transmission", raw) if isinstance(raw, dict) else None
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            for field in _TRANSMISSION_REQUIRED:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")
            name = str(data.get("name") or path.stem).strip()
            if not name:
                raise ValueError("Empty name")
            display = name
            if isinstance(raw, dict) and raw.get("preset_name"):
                display = str(raw["preset_name"]).strip() or display
            return display, data
        except Exception as e:
            logger.warning("Could not load transmission preset %s: %s", path, e)
            return None

    @classmethod
    def add_engine_preset(cls, name: str, data: Dict, *, persist: bool = True):
        """Add/update a custom engine preset (optionally write JSON under Engine presets)."""
        name = name.strip()
        if not name:
            raise ValueError("Preset name cannot be empty")
        if name in _BUILTIN_ENGINE_PRESETS:
            raise ValueError(
                f"'{name}' is a built-in engine preset and cannot be overwritten"
            )

        payload = deepcopy(data)
        root = app_settings.get_presets_root()
        ensure_presets_tree(root)

        if persist:
            path = engine_presets_dir(root) / _safe_filename(name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {"preset_name": name, "engine": payload},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            logger.info("Saved custom engine preset %r -> %s", name, path)

        with cls._get_lock():
            cls._custom_engine[name] = payload

    @classmethod
    def add_transmission_preset(cls, name: str, data: Dict, *, persist: bool = True):
        """Add/update a custom transmission preset (optionally write JSON)."""
        name = name.strip()
        if not name:
            raise ValueError("Preset name cannot be empty")
        if name in _BUILTIN_TRANSMISSION_PRESETS:
            raise ValueError(
                f"'{name}' is a built-in transmission preset and cannot be overwritten"
            )

        payload = deepcopy(data)
        root = app_settings.get_presets_root()
        ensure_presets_tree(root)

        if persist:
            path = transmission_presets_dir(root) / _safe_filename(name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {"preset_name": name, "transmission": payload},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            logger.info("Saved custom transmission preset %r -> %s", name, path)

        with cls._get_lock():
            cls._custom_transmission[name] = payload

    @classmethod
    def get_engine_presets(cls) -> Dict:
        """Built-in + custom engine presets (custom names never replace built-ins)."""
        with cls._get_lock():
            merged = deepcopy(_BUILTIN_ENGINE_PRESETS)
            for key, value in cls._custom_engine.items():
                if key not in merged:
                    merged[key] = deepcopy(value)
            return merged

    @classmethod
    def get_transmission_presets(cls) -> Dict:
        """Built-in + custom transmission presets."""
        with cls._get_lock():
            merged = deepcopy(_BUILTIN_TRANSMISSION_PRESETS)
            for key, value in cls._custom_transmission.items():
                if key not in merged:
                    merged[key] = deepcopy(value)
            return merged

    @classmethod
    def list_engine_preset_names(cls) -> List[str]:
        return list(cls.get_engine_presets().keys())

    @classmethod
    def list_transmission_preset_names(cls) -> List[str]:
        return list(cls.get_transmission_presets().keys())
