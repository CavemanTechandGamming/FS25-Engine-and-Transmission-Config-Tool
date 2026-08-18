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

        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue

            inline_suffix = ""
            j = i + 1
            while j < len(parts) and not parts[j].strip():
                j += 1
            if j < len(parts):
                next_part = parts[j].strip()
                if next_part.startswith("<!--"):
                    inline_suffix = " " + next_part
                    i = j + 1
                else:
                    i += 1
            else:
                i += 1

            if part.startswith("<?xml"):
                lines.append(part + inline_suffix)
            elif part.startswith("<!--"):
                lines.append(" " * indent_level + part)
            elif part.startswith("</"):
                indent_level = max(0, indent_level - 1)
                lines.append(" " * indent_level + part + inline_suffix)
            elif part.startswith("<") and not part.endswith("/>"):
                lines.append(" " * indent_level + part + inline_suffix)
                indent_level += 1
            else:
                lines.append(" " * indent_level + part + inline_suffix)

        return "\n".join(lines)

    @staticmethod
    def _indent_lines(text: str, levels: int = 1) -> str:
        pad = " " * levels
        out = []
        for line in text.splitlines():
            out.append(pad + line if line.strip() else line)
        return "\n".join(out)

    @staticmethod
    def _assemble_document(*blocks: str) -> str:
        """Join pre-formatted XML blocks with a blank line between each."""
        return (
            '<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n\n'
            + "\n\n".join(block for block in blocks if block)
        )

    @staticmethod
    def _motor_configurations_xml(
        *,
        name: str,
        hp: float,
        price: float,
        motor_open: str,
        torque_xml: str,
        transmission_spec: Dict | None = None,
    ) -> str:
        motor_body = XMLGenerator.format_xml(motor_open + torque_xml + "</motor>")
        if transmission_spec is not None:
            trans_body = XMLGenerator.format_xml(
                XMLGenerator._transmission_xml(transmission_spec)
            )
            config_content = (
                XMLGenerator._indent_lines(motor_body, 2)
                + "\n\n"
                + XMLGenerator._indent_lines(trans_body, 2)
            )
        else:
            config_content = XMLGenerator._indent_lines(motor_body, 2)

        return (
            "<motorConfigurations>\n"
            f' <motorConfiguration name="{_esc(name)}" hp="{_fmt_num(hp)}" '
            f'price="{_fmt_num(price)}" consumerConfigurationIndex="1">\n'
            f"{config_content}\n"
            " </motorConfiguration>\n"
            "</motorConfigurations>"
        )

    @staticmethod
    def _torque_points(engine_data: Dict) -> List[Tuple[float, float]]:
        baked = engine_data.get("torque_curve")
        if baked:
            return [
                (float(point["rpm"]), float(point["torque"]))
                for point in baked
            ]
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
                    f'<forwardGear gearRatio="{_fmt_num(gear["gearRatio"])}"{extra}/>'
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

    _DRIVE_LAYOUTS: Dict[str, Tuple[str, List[Tuple[str, str]]]] = {
        "fwd": (
            "front-wheel drive (FWD)",
            [
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="1" wheelIndex2="2"/>',
                    "front left-right",
                ),
            ],
        ),
        "rwd": (
            "rear-wheel drive (RWD)",
            [
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="3" wheelIndex2="4"/>',
                    "rear left-right",
                ),
            ],
        ),
        "4wd": (
            "four-wheel drive (4WD)",
            [
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="1" wheelIndex2="2"/>',
                    "front left-right",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="3" wheelIndex2="4"/>',
                    "rear left-right",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'differentialIndex1="1" differentialIndex2="2"/>',
                    "front-back center",
                ),
            ],
        ),
        "6x6": (
            "six-wheel drive (6x6 / three axles)",
            [
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="1" wheelIndex2="2"/>',
                    "axle 1 left-right",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="3" wheelIndex2="4"/>',
                    "axle 2 left-right",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'wheelIndex1="5" wheelIndex2="6"/>',
                    "axle 3 left-right",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.5" '
                    'differentialIndex1="1" differentialIndex2="2"/>',
                    "axles 1-2 merge",
                ),
                (
                    '<differential torqueRatio="0.5" maxSpeedRatio="1.3" '
                    'differentialIndex1="3" differentialIndex2="4"/>',
                    "axles 1-2 to axle 3",
                ),
            ],
        ),
    }

    @staticmethod
    def _differential_xml(drive_layout: str = "4wd") -> str:
        """Open diff stack for the requested drive layout (paste at ``<motorized>`` level)."""
        layout_key = drive_layout.lower()
        if layout_key not in XMLGenerator._DRIVE_LAYOUTS:
            layout_key = "4wd"
        label, diffs = XMLGenerator._DRIVE_LAYOUTS[layout_key]
        diff_lines = "".join(f"{xml} <!-- {comment} -->" for xml, comment in diffs)
        return (
            "<differentialConfigurations>"
            f'<differentialConfiguration> <!-- {label} -->'
            "<differentials>"
            f"{diff_lines}"
            "</differentials>"
            "</differentialConfiguration>"
            "</differentialConfigurations>"
        )

    @staticmethod
    def generate_engine_xml(engine_data: Dict, drive_layout: str = "4wd") -> str:
        points = XMLGenerator._torque_points(engine_data)
        torque_scale = TorqueCurveGenerator.torque_scale_from_hp(
            engine_data["horsepower"], engine_data["max_rpm"]
        )
        return XMLGenerator._assemble_document(
            XMLGenerator.format_xml(XMLGenerator._consumer_xml(engine_data)),
            XMLGenerator.format_xml(XMLGenerator._differential_xml(drive_layout)),
            XMLGenerator._motor_configurations_xml(
                name=engine_data["name"],
                hp=engine_data["horsepower"],
                price=engine_data["cost"],
                motor_open=XMLGenerator._motor_open(
                    engine_data,
                    max_forward=120,
                    max_backward=22,
                    torque_scale=torque_scale,
                ),
                torque_xml=XMLGenerator._torque_xml(points),
            ),
        )

    @staticmethod
    def _custom_axle(transmission_data: Dict):
        if not transmission_data.get("use_custom_axle_ratio"):
            return None
        return transmission_data.get("axle_ratio")

    @staticmethod
    def _transmission_spec(transmission_data: Dict):
        return GearRatioCalculator.build_transmission(
            transmission_data["type"],
            transmission_data["num_forward"],
            transmission_data["num_reverse"],
            transmission_data["top_speed"],
            transmission_data.get("enable_low_gearing", False),
            transmission_data.get("low_gear_boost", 25.0),
            XMLGenerator._custom_axle(transmission_data),
            transmission_data.get("forward_gears"),
            transmission_data.get("reverse_gears"),
        )

    @staticmethod
    def generate_transmission_xml(transmission_data: Dict) -> str:
        spec = XMLGenerator._transmission_spec(transmission_data)
        top = transmission_data["top_speed"]
        motor_open = (
            f'<motor torqueScale="1.0" minRpm="1000" maxRpm="6000" '
            f'maxForwardSpeed="{_fmt_num(top)}" maxBackwardSpeed="22" '
            f'brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">'
        )
        return XMLGenerator._assemble_document(
            XMLGenerator._motor_configurations_xml(
                name=transmission_data["name"],
                hp=0,
                price=transmission_data["cost"],
                motor_open=motor_open,
                torque_xml=(
                    '<torque rpm="1000" torque="1.0"/>'
                    '<torque rpm="6000" torque="1.0"/>'
                ),
                transmission_spec=spec,
            ),
        )

    @staticmethod
    def generate_combined_fs25_xml(
        engine_data: Dict,
        transmission_data: Dict,
        drive_layout: str = "4wd",
    ) -> str:
        points = XMLGenerator._torque_points(engine_data)
        spec = XMLGenerator._transmission_spec(transmission_data)
        torque_scale = TorqueCurveGenerator.torque_scale_from_hp(
            engine_data["horsepower"], engine_data["max_rpm"]
        )
        top = int(round(transmission_data["top_speed"]))
        max_back = (
            22
            if spec["family"] != "discrete_maxSpeed"
            else int(round(min(32.0, top * 0.4)))
        )
        config_name = f'{engine_data["name"]} - {transmission_data["name"]}'
        price = engine_data["cost"] + transmission_data["cost"]
        return XMLGenerator._assemble_document(
            XMLGenerator.format_xml(XMLGenerator._consumer_xml(engine_data)),
            XMLGenerator.format_xml(XMLGenerator._differential_xml(drive_layout)),
            XMLGenerator._motor_configurations_xml(
                name=config_name,
                hp=engine_data["horsepower"],
                price=price,
                motor_open=XMLGenerator._motor_open(
                    engine_data,
                    max_forward=top,
                    max_backward=max_back,
                    torque_scale=torque_scale,
                ),
                torque_xml=XMLGenerator._torque_xml(points),
                transmission_spec=spec,
            ),
        )
