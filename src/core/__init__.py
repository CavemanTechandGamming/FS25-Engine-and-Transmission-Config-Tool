"""Core calculation and XML helpers."""

from src.core.gears import GearRatioCalculator
from src.core.presets import PresetManager
from src.core.torque import TorqueCurveGenerator
from src.core.xml_gen import XMLGenerator

__all__ = [
    "GearRatioCalculator",
    "PresetManager",
    "TorqueCurveGenerator",
    "XMLGenerator",
]
