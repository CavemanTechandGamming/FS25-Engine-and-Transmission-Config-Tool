from __future__ import annotations

from typing import Dict, List, Tuple

from src.core.torque import TorqueCurveGenerator
from src.core.gears import GearRatioCalculator


def _esc(value) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt_num(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text


class XMLGenerator:
    """
    Generate FS25 motorConfiguration XML. UI is unchanged; only the
    emitted families/fields differ (CVT / PowerShift / highway auto).
    """

    @staticmethod
    def format_xml(xml_string: str) -> str:
        import re

        xml_string = re.sub(r"\s+", " ", xml_string.strip())
        lines = []
        indent_level = 0
        parts = re.split(r"(<[^>]+>)", xml_string)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith("<?xml"):
                lines.append(part)
            elif part.startswith("<!--"):
                lines.append(" " * indent_level + part)
            elif part.startswith("</"):
                indent_level = max(0, indent_level - 1)
                lines.append(" " * indent_level + part)
            elif part.startswith("<") and not part.endswith("/>"):
                lines.append(" " * indent_level + part)
                indent_level += 1
            else:
                lines.append(" " * indent_level + part)

        return "\n".join(lines)

    @staticmethod
    def _torque_points(engine_data: Dict) -> List[Tuple[float, float]]:
        torque_curve = TorqueCurveGenerator.generate_torque_curve(
            engine_data["horsepower"],
            engine_data["min_rpm"],
            engine_data["max_rpm"],
            engine_data["turbocharged"],
        )
        peak = max(torque for _, torque in torque_curve)
        points = []
        for norm_rpm, torque in torque_curve:
            actual_rpm = norm_rpm * engine_data["max_rpm"]
            points.append((actual_rpm, torque / peak))
        return points

    @staticmethod
    def _motor_open(
        engine_data: Dict,
        *,
        max_forward: float,
        max_backward: float,
        torque_scale: float,
    ) -> str:
        return (
            f'<motor torqueScale="{_fmt_num(torque_scale)}" '
            f'minRpm="{_fmt_num(engine_data["min_rpm"])}" '
            f'maxRpm="{_fmt_num(engine_data["max_rpm"])}" '
            f'maxForwardSpeed="{_fmt_num(max_forward)}" '
            f'maxBackwardSpeed="{_fmt_num(max_backward)}" '
            f'brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">'
        )

    @staticmethod
    def _torque_xml(points: List[Tuple[float, float]]) -> str:
        lines = []
        for rpm, torque in points:
            lines.append(
                f'<torque rpm="{rpm:.0f}" torque="{torque:.2f}"/>'
            )
        return "".join(lines)

    @staticmethod
    def _transmission_xml(spec: Dict) -> str:
        name = spec["l10n_name"]
        family = spec["family"]
        if family == "continuous_minMaxRatio":
            return (
                f'<transmission minForwardGearRatio="{_fmt_num(spec["min_forward_gear_ratio"])}" '
                f'maxForwardGearRatio="{_fmt_num(spec["max_forward_gear_ratio"])}" '
                f'minBackwardGearRatio="{_fmt_num(spec["min_backward_gear_ratio"])}" '
                f'maxBackwardGearRatio="{_fmt_num(spec["max_backward_gear_ratio"])}" '
                f'name="{_esc(name)}"/>'
            )

        attrs = [f'name="{_esc(name)}"']
        if spec.get("auto_gear_change_time") is not None:
            attrs.append(
                f'autoGearChangeTime="{_fmt_num(spec["auto_gear_change_time"])}"'
            )
        if spec.get("gear_change_time") is not None:
            attrs.append(
                f'gearChangeTime="{_fmt_num(spec["gear_change_time"])}"'
            )
        if spec.get("axle_ratio") is not None:
            attrs.append(f'axleRatio="{_fmt_num(spec["axle_ratio"])}"')
        if spec.get("start_gear_threshold") is not None:
            attrs.append(
                f'startGearThreshold="{_fmt_num(spec["start_gear_threshold"])}"'
            )

        if family == "discrete_maxSpeed":
            direction = (
                '<directionChange useGear="true" reverseGearIndex="1" '
                'changeTime="0.5"/>'
            )
        else:
            direction = '<directionChange useGear="true"/>'

        gears = [direction]
        for gear in spec.get("backward", []):
            extra = ""
            if gear.get("name"):
                extra += f' name="{_esc(gear["name"])}"'
            if "maxSpeed" in gear:
                gears.append(
                    f'<backwardGear maxSpeed="{_fmt_num(gear["maxSpeed"])}"{extra}/>'
                )
            else:
                gears.append(
                    f'<backwardGear gearRatio="{_fmt_num(gear["gearRatio"])}"{extra}/>'
                )
        for gear in spec.get("forward", []):
            extra = ""
            if gear.get("name"):
                extra += f' name="{_esc(gear["name"])}"'
            if "maxSpeed" in gear:
                gears.append(
                    f'<forwardGear maxSpeed="{_fmt_num(gear["maxSpeed"])}"{extra}/>'
                )
            else:
                gears.append(
                    f'<forwardGear gearRatio="{_fmt_num(gear["gearRatio"])}"/>'
                )

        return (
            f'<transmission {" ".join(attrs)}>'
            + "".join(gears)
            + "</transmission>"
        )

    @staticmethod
    def _consumer_xml(engine_data: Dict) -> str:
        usage = TorqueCurveGenerator.consumer_usage(
            engine_data["horsepower"],
            engine_data["fuel_usage_scale"],
        )
        return (
            "<consumerConfigurations>"
            "<consumerConfiguration>"
            f'<consumer fillUnitIndex="1" usage="{_fmt_num(usage)}" fillType="diesel"/>'
            "</consumerConfiguration>"
            "</consumerConfigurations>"
        )

    @staticmethod
    def generate_engine_xml(engine_data: Dict) -> str:
        points = XMLGenerator._torque_points(engine_data)
        torque_scale = TorqueCurveGenerator.torque_scale_from_hp(
            engine_data["horsepower"], engine_data["max_rpm"]
        )
        xml = (
            '<?xml version="1.0" encoding="utf-8" standalone="no" ?>'
            "<motorConfigurations>"
            f'<motorConfiguration name="{_esc(engine_data["name"])}" '
            f'hp="{_fmt_num(engine_data["horsepower"])}" '
            f'price="{_fmt_num(engine_data["cost"])}" consumerConfigurationIndex="1">'
            + XMLGenerator._motor_open(
                engine_data,
                max_forward=120,
                max_backward=22,
                torque_scale=torque_scale,
            )
            + XMLGenerator._torque_xml(points)
            + "</motor></motorConfiguration></motorConfigurations>"
            + XMLGenerator._consumer_xml(engine_data)
        )
        return XMLGenerator.format_xml(xml)

    @staticmethod
    def _custom_axle(transmission_data: Dict):
        if not transmission_data.get("use_custom_axle_ratio"):
            return None
        return transmission_data.get("axle_ratio")

    @staticmethod
    def generate_transmission_xml(transmission_data: Dict) -> str:
        spec = GearRatioCalculator.build_transmission(
            transmission_data["type"],
            transmission_data["num_forward"],
            transmission_data["num_reverse"],
            transmission_data["top_speed"],
            transmission_data.get("enable_low_gearing", False),
            transmission_data.get("low_gear_boost", 25.0),
            XMLGenerator._custom_axle(transmission_data),
        )
        top = transmission_data["top_speed"]
        xml = (
            '<?xml version="1.0" encoding="utf-8" standalone="no" ?>'
            "<motorConfigurations>"
            f'<motorConfiguration name="{_esc(transmission_data["name"])}" '
            f'hp="0" price="{_fmt_num(transmission_data["cost"])}">'
            f'<motor torqueScale="1.0" minRpm="1000" maxRpm="6000" '
            f'maxForwardSpeed="{_fmt_num(top)}" maxBackwardSpeed="22" '
            f'brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">'
            '<torque rpm="1000" torque="1.0"/>'
            '<torque rpm="6000" torque="1.0"/>'
            "</motor>"
            + XMLGenerator._transmission_xml(spec)
            + "</motorConfiguration></motorConfigurations>"
        )
        return XMLGenerator.format_xml(xml)

    @staticmethod
    def generate_combined_fs25_xml(engine_data: Dict, transmission_data: Dict) -> str:
        points = XMLGenerator._torque_points(engine_data)
        spec = GearRatioCalculator.build_transmission(
            transmission_data["type"],
            transmission_data["num_forward"],
            transmission_data["num_reverse"],
            transmission_data["top_speed"],
            transmission_data.get("enable_low_gearing", False),
            transmission_data.get("low_gear_boost", 25.0),
            XMLGenerator._custom_axle(transmission_data),
        )
        torque_scale = TorqueCurveGenerator.torque_scale_from_hp(
            engine_data["horsepower"], engine_data["max_rpm"]
        )
        top = transmission_data["top_speed"]
        max_back = 22 if spec["family"] != "discrete_maxSpeed" else round(min(32.0, top * 0.4), 1)
        config_name = f'{engine_data["name"]} - {transmission_data["name"]}'
        price = engine_data["cost"] + transmission_data["cost"]
        xml = (
            '<?xml version="1.0" encoding="utf-8" standalone="no" ?>'
            "<motorConfigurations>"
            f'<motorConfiguration name="{_esc(config_name)}" '
            f'hp="{_fmt_num(engine_data["horsepower"])}" '
            f'price="{_fmt_num(price)}" consumerConfigurationIndex="1">'
            + XMLGenerator._motor_open(
                engine_data,
                max_forward=top,
                max_backward=max_back,
                torque_scale=torque_scale,
            )
            + XMLGenerator._torque_xml(points)
            + "</motor>"
            + XMLGenerator._transmission_xml(spec)
            + "</motorConfiguration></motorConfigurations>"
            + XMLGenerator._consumer_xml(engine_data)
        )
        return XMLGenerator.format_xml(xml)
