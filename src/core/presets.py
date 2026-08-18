from __future__ import annotations

import json
import logging
import re
import shutil
import threading
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.core.paths import (
    bundled_presets_root,
    engine_preset_scan_dirs,
    engine_presets_dir,
    ensure_presets_tree,
    legacy_presets_root,
    transmission_preset_scan_dirs,
    transmission_presets_dir,
)
from src.core import settings as app_settings
from src.core.preset_schema import (
    parse_preset_file,
    validate_engine_payload,
    validate_transmission_payload,
    wrap_engine_file,
    wrap_transmission_file,
)

logger = logging.getLogger("fs25config.presets")


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", name.strip())
    cleaned = cleaned.strip(" .") or "preset"
    return cleaned[:80] + ".json"


class PresetManager:
    """
    Factory presets ship as JSON under Presets/Engine and Presets/Transmission.
    Custom presets use the same folders (user-chosen root; default next to the app).
    Built-in names cannot be overwritten or deleted.
    """

    _preset_lock = None
    _builtin_engine: Dict = {}
    _builtin_transmission: Dict = {}
    _custom_engine: Dict = {}
    _custom_transmission: Dict = {}

    @classmethod
    def _get_lock(cls):
        if cls._preset_lock is None:
            cls._preset_lock = threading.Lock()
        return cls._preset_lock

    @staticmethod
    def save_preset(data: Dict, filename: str):
        """Save a configuration preset to a JSON file (file dialog)."""
        if isinstance(data, dict) and data.get("schema_version") is None:
            if "engine" in data and "transmission" in data:
                from src.core.preset_schema import wrap_configuration_file

                drive = data.get("drive_layout")
                data = wrap_configuration_file(
                    data["engine"],
                    data["transmission"],
                    drive_layout=drive,
                )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Exported preset file: %s", filename)

    @staticmethod
    def load_preset(filename: str) -> Optional[Dict]:
        """Load a configuration preset from a JSON file (file dialog)."""
        with open(filename, "r", encoding="utf-8") as f:
            raw = json.load(f)
        kind, payload, _preset_name = parse_preset_file(raw)
        logger.info("Imported preset file: %s (%s)", filename, kind)
        if kind == "configuration":
            return payload
        if kind == "engine":
            return {"engine": payload}
        return {"transmission": payload}

    @classmethod
    def is_builtin_engine(cls, name: str) -> bool:
        with cls._get_lock():
            return name in cls._builtin_engine

    @classmethod
    def is_builtin_transmission(cls, name: str) -> bool:
        with cls._get_lock():
            return name in cls._builtin_transmission

    @classmethod
    def reload_custom_presets(cls, presets_root: Optional[Path] = None) -> None:
        """Reload factory + custom presets (name kept for existing call sites)."""
        cls.reload_presets(presets_root)

    @classmethod
    def reload_presets(cls, presets_root: Optional[Path] = None) -> None:
        """Load shipped factory JSON, seed/migrate user folders, then scan customs."""
        root = Path(presets_root) if presets_root else app_settings.get_presets_root()
        ensure_presets_tree(root)
        cls._migrate_legacy_custom_presets(root)
        cls._seed_builtin_copies(root)

        builtin_engine, builtin_transmission = cls._load_bundled_factory()
        custom_engine: Dict = {}
        custom_transmission: Dict = {}

        for folder in engine_preset_scan_dirs(root):
            for path in sorted(folder.glob("*.json")):
                loaded = cls._load_engine_file(path)
                if loaded is None:
                    continue
                name, data = loaded
                if name in builtin_engine:
                    continue
                if name in custom_engine:
                    logger.warning(
                        "Duplicate custom engine preset name %r in %s", name, path
                    )
                custom_engine[name] = data

        for folder in transmission_preset_scan_dirs(root):
            for path in sorted(folder.glob("*.json")):
                loaded = cls._load_transmission_file(path)
                if loaded is None:
                    continue
                name, data = loaded
                if name in builtin_transmission:
                    continue
                if name in custom_transmission:
                    logger.warning(
                        "Duplicate custom transmission preset name %r in %s", name, path
                    )
                custom_transmission[name] = data

        with cls._get_lock():
            cls._builtin_engine = builtin_engine
            cls._builtin_transmission = builtin_transmission
            cls._custom_engine = custom_engine
            cls._custom_transmission = custom_transmission

        logger.info(
            "Loaded presets (factory engines=%d transmissions=%d; "
            "custom engines=%d transmissions=%d) from %s",
            len(builtin_engine),
            len(builtin_transmission),
            len(custom_engine),
            len(custom_transmission),
            root,
        )

    @classmethod
    def _load_bundled_factory(cls) -> Tuple[Dict, Dict]:
        bundled = bundled_presets_root()
        engines: Dict = {}
        transmissions: Dict = {}
        e_dir = engine_presets_dir(bundled)
        t_dir = transmission_presets_dir(bundled)
        if e_dir.is_dir():
            for path in sorted(e_dir.glob("*.json")):
                loaded = cls._load_engine_file(path)
                if loaded is None:
                    continue
                name, data = loaded
                engines[name] = data
        if t_dir.is_dir():
            for path in sorted(t_dir.glob("*.json")):
                loaded = cls._load_transmission_file(path)
                if loaded is None:
                    continue
                name, data = loaded
                transmissions[name] = data
        if not engines or not transmissions:
            logger.warning(
                "Factory presets missing or incomplete under %s "
                "(engines=%d, transmissions=%d)",
                bundled,
                len(engines),
                len(transmissions),
            )
        return engines, transmissions

    @classmethod
    def _seed_builtin_copies(cls, user_root: Path) -> None:
        """Copy shipped factory files into the user tree if they are not there yet."""
        bundled = bundled_presets_root()
        try:
            if bundled.resolve() == Path(user_root).resolve():
                return
        except OSError:
            pass
        pairs = (
            (engine_presets_dir(bundled), engine_presets_dir(user_root)),
            (transmission_presets_dir(bundled), transmission_presets_dir(user_root)),
        )
        for src_dir, dest_dir in pairs:
            if not src_dir.is_dir():
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            for src in src_dir.glob("*.json"):
                dest = dest_dir / src.name
                if dest.exists():
                    continue
                try:
                    shutil.copy2(src, dest)
                    logger.info("Seeded factory preset %s -> %s", src.name, dest)
                except OSError as e:
                    logger.warning("Could not seed factory preset %s: %s", src, e)

    @classmethod
    def _migrate_legacy_custom_presets(cls, dest_root: Path) -> None:
        """Copy old Custom Presets/* into Presets/Engine and Presets/Transmission."""
        legacy = legacy_presets_root()
        if not legacy.is_dir():
            return
        try:
            if legacy.resolve() == Path(dest_root).resolve():
                return
        except OSError:
            return
        pairs = (
            (legacy / "Engine presets", engine_presets_dir(dest_root)),
            (legacy / "Transmission presets", transmission_presets_dir(dest_root)),
            (legacy / "Engine", engine_presets_dir(dest_root)),
            (legacy / "Transmission", transmission_presets_dir(dest_root)),
        )
        for src_dir, dest_dir in pairs:
            if not src_dir.is_dir():
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            for src in src_dir.glob("*.json"):
                dest = dest_dir / src.name
                if dest.exists():
                    continue
                try:
                    shutil.copy2(src, dest)
                    logger.info("Migrated custom preset %s -> %s", src.name, dest)
                except OSError as e:
                    logger.warning("Could not migrate %s: %s", src, e)

    @classmethod
    def _load_engine_file(cls, path: Path) -> Optional[Tuple[str, Dict]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            kind, data, preset_name = parse_preset_file(raw)
            if kind != "engine":
                raise ValueError(f"Expected engine preset, got {kind!r}")
            name = preset_name or str(data.get("name") or path.stem).strip()
            if not name:
                raise ValueError("Empty name")
            return name, data
        except Exception as e:
            logger.warning("Could not load engine preset %s: %s", path, e)
            return None

    @classmethod
    def _load_transmission_file(cls, path: Path) -> Optional[Tuple[str, Dict]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            kind, data, preset_name = parse_preset_file(raw)
            if kind != "transmission":
                raise ValueError(f"Expected transmission preset, got {kind!r}")
            name = preset_name or str(data.get("name") or path.stem).strip()
            if not name:
                raise ValueError("Empty name")
            return name, data
        except Exception as e:
            logger.warning("Could not load transmission preset %s: %s", path, e)
            return None

    @classmethod
    def add_engine_preset(cls, name: str, data: Dict, *, persist: bool = True):
        """Add/update a custom engine preset under Presets/Engine."""
        name = name.strip()
        if not name:
            raise ValueError("Preset name cannot be empty")
        if cls.is_builtin_engine(name):
            raise ValueError(
                f"'{name}' is a built-in engine preset and cannot be overwritten"
            )

        payload = validate_engine_payload(deepcopy(data))
        root = app_settings.get_presets_root()
        ensure_presets_tree(root)

        if persist:
            path = engine_presets_dir(root) / _safe_filename(name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(wrap_engine_file(name, payload), f, indent=2, ensure_ascii=False)
            logger.info("Saved custom engine preset %r -> %s", name, path)

        with cls._get_lock():
            cls._custom_engine[name] = payload

    @classmethod
    def add_transmission_preset(cls, name: str, data: Dict, *, persist: bool = True):
        """Add/update a custom transmission preset under Presets/Transmission."""
        name = name.strip()
        if not name:
            raise ValueError("Preset name cannot be empty")
        if cls.is_builtin_transmission(name):
            raise ValueError(
                f"'{name}' is a built-in transmission preset and cannot be overwritten"
            )

        payload = validate_transmission_payload(deepcopy(data))
        root = app_settings.get_presets_root()
        ensure_presets_tree(root)

        if persist:
            path = transmission_presets_dir(root) / _safe_filename(name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    wrap_transmission_file(name, payload),
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            logger.info("Saved custom transmission preset %r -> %s", name, path)

        with cls._get_lock():
            cls._custom_transmission[name] = payload

    @classmethod
    def get_engine_presets(cls) -> Dict:
        """Factory + custom engine presets (custom names never replace built-ins)."""
        with cls._get_lock():
            merged = deepcopy(cls._builtin_engine)
            for key, value in cls._custom_engine.items():
                if key not in merged:
                    merged[key] = deepcopy(value)
            return merged

    @classmethod
    def get_transmission_presets(cls) -> Dict:
        """Factory + custom transmission presets."""
        with cls._get_lock():
            merged = deepcopy(cls._builtin_transmission)
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
