"""FS25 preset file schema (version 1).

Single source of truth for engine, transmission, and full-configuration JSON
presets. Factory and custom files use the same envelope and field rules.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Tuple

SCHEMA_VERSION = 1

PresetKind = Literal["engine", "transmission", "configuration"]

TRANSMISSION_TYPES = ("Manual", "Automatic", "CVT", "PowerShift")

DRIVE_LAYOUT_KEYS = ("fwd", "rwd", "4wd", "6x6")
DRIVE_LAYOUT_LABELS: Dict[str, str] = {
    "fwd": "Front-wheel drive (FWD)",
    "rwd": "Rear-wheel drive (RWD)",
    "4wd": "Four-wheel drive (4WD)",
    "6x6": "Six-wheel drive (6×6)",
}
DRIVE_LAYOUT_CHOICES: List[str] = [DRIVE_LAYOUT_LABELS[k] for k in DRIVE_LAYOUT_KEYS]
LABEL_TO_DRIVE_LAYOUT: Dict[str, str] = {
    label: key for key, label in DRIVE_LAYOUT_LABELS.items()
}

ENGINE_REQUIRED = (
    "name",
    "cost",
    "horsepower",
    "min_rpm",
    "max_rpm",
    "fuel_usage_scale",
    "turbocharged",
)

TRANSMISSION_REQUIRED = (
    "name",
    "cost",
    "type",
    "top_speed",
    "num_forward",
    "num_reverse",
    "enable_low_gearing",
    "low_gear_boost",
)

# Optional explicit gear data (generator uses these when present instead of calculating).
TRANSMISSION_OPTIONAL_GEAR_FIELDS = (
    "forward_gears",
    "reverse_gears",
    "cvt_min_ratio",
    "cvt_max_ratio",
    "powershift_forward",
    "powershift_reverse",
)


def drive_layout_key(value: str) -> str:
    """Normalize UI label or key to a generator drive-layout key."""
    text = (value or "").strip()
    if text in DRIVE_LAYOUT_KEYS:
        return text
    return LABEL_TO_DRIVE_LAYOUT.get(text, "4wd")


def _require_dict(data: Any, label: str) -> Dict:
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def _require_fields(data: Dict, fields: Tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"{label} missing required field(s): {', '.join(missing)}")


def _normalize_torque_curve(raw: Any, label: str) -> List[Dict[str, float]]:
    """List of {rpm, torque} where torque is 0–1 fraction of peak."""
    if not isinstance(raw, list) or len(raw) < 2:
        raise ValueError(f"{label}: torque_curve must be a list of at least 2 points")
    points: List[Dict[str, float]] = []
    for i, item in enumerate(raw):
        if isinstance(item, dict):
            if "rpm" not in item or "torque" not in item:
                raise ValueError(f"{label}: torque_curve[{i}] needs rpm and torque")
            rpm = float(item["rpm"])
            torque = float(item["torque"])
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            rpm = float(item[0])
            torque = float(item[1])
        else:
            raise ValueError(f"{label}: torque_curve[{i}] must be {{rpm, torque}}")
        if rpm <= 0:
            raise ValueError(f"{label}: torque_curve[{i}] rpm must be greater than 0")
        if torque < 0:
            raise ValueError(f"{label}: torque_curve[{i}] torque cannot be negative")
        points.append({"rpm": rpm, "torque": torque})
    points.sort(key=lambda p: p["rpm"])
    return points


def validate_engine_payload(data: Dict, *, label: str = "Engine preset") -> Dict:
    """Validate and normalize an engine payload dict."""
    payload = _require_dict(data, label)
    _require_fields(payload, ENGINE_REQUIRED, label)

    name = str(payload["name"]).strip()
    if not name:
        raise ValueError(f"{label}: name cannot be empty")

    cost = int(payload["cost"])
    horsepower = float(payload["horsepower"])
    min_rpm = float(payload["min_rpm"])
    max_rpm = float(payload["max_rpm"])
    fuel_usage_scale = float(payload["fuel_usage_scale"])
    turbocharged = bool(payload["turbocharged"])

    if cost < 0:
        raise ValueError(f"{label}: cost cannot be negative")
    if horsepower <= 0:
        raise ValueError(f"{label}: horsepower must be greater than 0")
    if min_rpm < 0:
        raise ValueError(f"{label}: min_rpm cannot be negative")
    if max_rpm <= min_rpm:
        raise ValueError(f"{label}: max_rpm must be greater than min_rpm")
    if fuel_usage_scale <= 0:
        raise ValueError(f"{label}: fuel_usage_scale must be greater than 0")

    normalized: Dict[str, Any] = {
        "name": name,
        "cost": cost,
        "horsepower": horsepower,
        "min_rpm": min_rpm,
        "max_rpm": max_rpm,
        "fuel_usage_scale": fuel_usage_scale,
        "turbocharged": turbocharged,
    }
    if "torque_curve" in payload:
        normalized["torque_curve"] = _normalize_torque_curve(
            payload["torque_curve"], label
        )
    return normalized


def validate_transmission_payload(data: Dict, *, label: str = "Transmission preset") -> Dict:
    """Validate and normalize a transmission payload dict."""
    payload = _require_dict(data, label)
    _require_fields(payload, TRANSMISSION_REQUIRED, label)

    name = str(payload["name"]).strip()
    if not name:
        raise ValueError(f"{label}: name cannot be empty")

    trans_type = str(payload["type"])
    if trans_type not in TRANSMISSION_TYPES:
        raise ValueError(
            f"{label}: type must be one of {', '.join(TRANSMISSION_TYPES)}"
        )

    cost = int(payload["cost"])
    top_speed = float(payload["top_speed"])
    num_forward = int(payload["num_forward"])
    num_reverse = int(payload["num_reverse"])
    enable_low_gearing = bool(payload["enable_low_gearing"])
    low_gear_boost = float(payload["low_gear_boost"])
    use_custom_axle_ratio = bool(payload.get("use_custom_axle_ratio", False))

    if cost < 0:
        raise ValueError(f"{label}: cost cannot be negative")
    if top_speed <= 0:
        raise ValueError(f"{label}: top_speed must be greater than 0")
    if num_forward <= 0:
        raise ValueError(f"{label}: num_forward must be greater than 0")
    if num_reverse < 0:
        raise ValueError(f"{label}: num_reverse cannot be negative")
    if low_gear_boost < 0:
        raise ValueError(f"{label}: low_gear_boost cannot be negative")

    normalized: Dict[str, Any] = {
        "name": name,
        "cost": cost,
        "type": trans_type,
        "top_speed": top_speed,
        "num_forward": num_forward,
        "num_reverse": num_reverse,
        "enable_low_gearing": enable_low_gearing,
        "low_gear_boost": low_gear_boost,
        "use_custom_axle_ratio": use_custom_axle_ratio,
    }

    if use_custom_axle_ratio:
        if trans_type == "CVT":
            raise ValueError(f"{label}: custom axle ratio does not apply to CVT")
        if "axle_ratio" not in payload:
            raise ValueError(f"{label}: axle_ratio required when use_custom_axle_ratio is true")
        axle_ratio = float(payload["axle_ratio"])
        if axle_ratio <= 0:
            raise ValueError(f"{label}: axle_ratio must be greater than 0")
        normalized["axle_ratio"] = axle_ratio

    for field in TRANSMISSION_OPTIONAL_GEAR_FIELDS:
        if field in payload:
            normalized[field] = deepcopy(payload[field])

    return normalized


def validate_configuration_payload(data: Dict) -> Dict:
    """Validate a full engine + transmission (+ optional drive layout) export."""
    root = _require_dict(data, "Configuration preset")
    if "engine" not in root and "transmission" not in root:
        raise ValueError("Configuration preset must include engine and/or transmission")

    normalized: Dict[str, Any] = {}
    if "engine" in root:
        normalized["engine"] = validate_engine_payload(root["engine"])
    if "transmission" in root:
        normalized["transmission"] = validate_transmission_payload(root["transmission"])
    if "drive_layout" in root:
        key = drive_layout_key(str(root["drive_layout"]))
        if key not in DRIVE_LAYOUT_KEYS:
            raise ValueError(
                f"drive_layout must be one of {', '.join(DRIVE_LAYOUT_KEYS)}"
            )
        normalized["drive_layout"] = key
    return normalized


def detect_preset_kind(raw: Dict) -> PresetKind:
    """Infer preset kind from file contents (supports legacy unwrapped payloads)."""
    kind = raw.get("kind")
    if kind in ("engine", "transmission", "configuration"):
        return kind
    if "engine" in raw and "transmission" in raw:
        return "configuration"
    if "engine" in raw:
        return "engine"
    if "transmission" in raw:
        return "transmission"
    if any(field in raw for field in ENGINE_REQUIRED):
        return "engine"
    if any(field in raw for field in TRANSMISSION_REQUIRED):
        return "transmission"
    raise ValueError("Could not determine preset kind from file contents")


def parse_preset_file(raw: Any) -> Tuple[PresetKind, Dict[str, Any], Optional[str]]:
    """
    Parse a loaded JSON preset file.

    Returns (kind, normalized_payload, preset_name).
    ``normalized_payload`` is the inner engine/transmission/configuration dict.
    """
    if not isinstance(raw, dict):
        raise ValueError("Preset file must be a JSON object")

    version = raw.get("schema_version")
    if version is not None and int(version) != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema_version {version!r} (expected {SCHEMA_VERSION})"
        )

    kind = detect_preset_kind(raw)
    preset_name = None
    if raw.get("preset_name"):
        preset_name = str(raw["preset_name"]).strip() or None

    if kind == "engine":
        inner = raw.get("engine", raw)
        return kind, validate_engine_payload(inner), preset_name
    if kind == "transmission":
        inner = raw.get("transmission", raw)
        return kind, validate_transmission_payload(inner), preset_name
    return kind, validate_configuration_payload(raw), preset_name


def wrap_engine_file(preset_name: str, engine: Dict, *, builtin: bool = False) -> Dict:
    payload: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "engine",
        "preset_name": preset_name,
        "engine": validate_engine_payload(engine),
    }
    if builtin:
        payload["builtin"] = True
    return payload


def wrap_transmission_file(
    preset_name: str, transmission: Dict, *, builtin: bool = False
) -> Dict:
    payload: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "transmission",
        "preset_name": preset_name,
        "transmission": validate_transmission_payload(transmission),
    }
    if builtin:
        payload["builtin"] = True
    return payload


def wrap_configuration_file(
    engine: Dict,
    transmission: Dict,
    *,
    drive_layout: Optional[str] = None,
) -> Dict:
    payload: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "configuration",
        "engine": validate_engine_payload(engine),
        "transmission": validate_transmission_payload(transmission),
    }
    if drive_layout is not None:
        key = drive_layout_key(drive_layout)
        if key not in DRIVE_LAYOUT_KEYS:
            raise ValueError(f"Invalid drive_layout: {drive_layout!r}")
        payload["drive_layout"] = key
    return payload
