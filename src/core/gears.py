from __future__ import annotations

from typing import Dict, List, Optional


L10N = {
    "Automatic": "$l10n_info_transmission_automatic",
    "Manual": "$l10n_info_transmission_manual",
    "CVT": "$l10n_info_transmission_cvt",
    "PowerShift": "$l10n_info_transmission_powerShift",
}


def _geometric(first: float, last: float, count: int) -> List[float]:
    if count <= 0:
        return []
    if count == 1:
        return [round(first, 3)]
    step = (last / first) ** (1.0 / (count - 1))
    return [round(first * (step ** i), 3) for i in range(count)]


def _int_geometric_speeds(first: float, last: float, count: int) -> List[int]:
    """PowerShift ``maxSpeed`` values — whole km/h only (Giants convention)."""
    if count <= 0:
        return []
    last_i = int(round(last))
    first_i = max(2, int(round(first)))
    if count == 1:
        return [last_i]
    raw = _geometric(float(first_i), float(last_i), count)
    speeds: List[int] = []
    for i, value in enumerate(raw):
        if i == 0:
            speeds.append(first_i)
        elif i == count - 1:
            speeds.append(last_i)
        else:
            speeds.append(int(round(value)))
    for i in range(1, len(speeds)):
        if speeds[i] <= speeds[i - 1]:
            speeds[i] = speeds[i - 1] + 1
    speeds[-1] = last_i
    if len(speeds) > 1 and speeds[-2] >= last_i:
        step = max(1, (last_i - first_i) // (count - 1))
        speeds = [first_i + step * i for i in range(count - 1)] + [last_i]
    return speeds


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class GearRatioCalculator:
    """
    Builds FS25 transmission data per Type family (not a US 4.10 axle stamp).
    """

    @staticmethod
    def calculate_gear_ratios(
        transmission_type: str,
        num_forward: int,
        num_reverse: int,
        top_speed: float,
        enable_low_gearing: bool = False,
        low_gear_boost: float = 25.0,
    ) -> Dict[str, List[float]]:
        spec = GearRatioCalculator.build_transmission(
            transmission_type,
            num_forward,
            num_reverse,
            top_speed,
            enable_low_gearing,
            low_gear_boost,
        )
        forward = [
            g["gearRatio"]
            for g in spec.get("forward", [])
            if "gearRatio" in g
        ]
        reverse = [
            g["gearRatio"]
            for g in spec.get("backward", [])
            if "gearRatio" in g
        ]
        return {"forward": forward, "reverse": reverse}

    @staticmethod
    def build_transmission(
        transmission_type: str,
        num_forward: int,
        num_reverse: int,
        top_speed: float,
        enable_low_gearing: bool = False,
        low_gear_boost: float = 25.0,
        custom_axle_ratio: Optional[float] = None,
        forward_gears: Optional[List] = None,
        reverse_gears: Optional[List] = None,
    ) -> Dict:
        if num_forward <= 0:
            raise ValueError("Number of forward gears must be greater than 0")
        if num_reverse < 0:
            raise ValueError("Number of reverse gears cannot be negative")
        if top_speed <= 0:
            raise ValueError("Top speed must be greater than 0")

        kind = (transmission_type or "Manual").strip()
        if kind.lower() == "cvt":
            spec = GearRatioCalculator._cvt(top_speed)
        elif kind.lower() == "powershift":
            spec = GearRatioCalculator._powershift(
                num_forward, num_reverse, top_speed
            )
        elif kind.lower() == "automatic":
            spec = GearRatioCalculator._automatic(
                num_forward,
                num_reverse,
                top_speed,
                enable_low_gearing,
                low_gear_boost,
            )
        else:
            spec = GearRatioCalculator._manual(
                num_forward,
                num_reverse,
                top_speed,
                enable_low_gearing,
                low_gear_boost,
            )

        if forward_gears and spec.get("family") == "discrete_gearRatio":
            spec["forward"] = [
                {"gearRatio": g["gearRatio"], **({"name": g["name"]} if g.get("name") else {})}
                if isinstance(g, dict)
                else {"gearRatio": float(g)}
                for g in forward_gears
            ]
        if reverse_gears is not None and spec.get("family") == "discrete_gearRatio":
            spec["backward"] = [
                {
                    "gearRatio": g["gearRatio"] if isinstance(g, dict) else abs(float(g)),
                    **(
                        {"name": g["name"]}
                        if isinstance(g, dict) and g.get("name")
                        else {}
                    ),
                }
                for g in reverse_gears
            ]
            for i, gear in enumerate(spec["backward"]):
                if "name" not in gear:
                    gear["name"] = "R" if len(spec["backward"]) == 1 else f"R{i + 1}"

        if (
            custom_axle_ratio is not None
            and spec.get("family") != "continuous_minMaxRatio"
        ):
            spec["axle_ratio"] = custom_axle_ratio
        return spec

    @staticmethod
    def _apply_low_gearing(
        ratios: List[float],
        enable: bool,
        boost_pct: float,
    ) -> List[float]:
        if not enable or not ratios:
            return ratios
        cutoff = max(1, int(len(ratios) * 0.25))
        factor = 1.0 + (boost_pct / 100.0)
        out = []
        for i, ratio in enumerate(ratios):
            if i < cutoff:
                out.append(round(ratio * factor, 3))
            else:
                out.append(ratio)
        return out

    @staticmethod
    def _highway_axle(top_speed: float, truck: bool) -> float:
        if truck:
            if top_speed >= 100:
                return 12.5
            if top_speed >= 80:
                return 10.0
            return 8.0
        if top_speed >= 140:
            return 15.0
        if top_speed >= 100:
            return 25.0
        if top_speed >= 80:
            return 19.0
        return 15.0

    @staticmethod
    def _automatic(
        num_forward: int,
        num_reverse: int,
        top_speed: float,
        enable_low_gearing: bool,
        low_gear_boost: float,
    ) -> Dict:
        # Allison-shaped band: ~4.70 first, ~0.61 overdrive (not a linear 4.5→1.3).
        if num_forward == 6:
            forward = [4.784, 2.423, 1.443, 1.000, 0.826, 0.643]
        else:
            forward = _geometric(4.70, 0.61, num_forward)
        forward = GearRatioCalculator._apply_low_gearing(
            forward, enable_low_gearing, low_gear_boost
        )
        reverse_count = max(1, num_reverse) if num_reverse == 0 else num_reverse
        if reverse_count == 1:
            reverse = [round(forward[0] * 1.036, 3)]
        else:
            reverse = [
                round(forward[0] * (1.036 + i * 0.25), 3)
                for i in range(reverse_count)
            ]
        axle = GearRatioCalculator._highway_axle(top_speed, truck=False)
        return {
            "family": "discrete_gearRatio",
            "l10n_name": L10N["Automatic"],
            "axle_ratio": axle,
            "auto_gear_change_time": 1.0,
            "gear_change_time": 0.3,
            "start_gear_threshold": 0.3,
            "forward": [{"gearRatio": r} for r in forward],
            "backward": [
                {
                    "gearRatio": r,
                    "name": "R" if len(reverse) == 1 else f"R{i + 1}",
                }
                for i, r in enumerate(reverse)
            ],
        }

    @staticmethod
    def _manual(
        num_forward: int,
        num_reverse: int,
        top_speed: float,
        enable_low_gearing: bool,
        low_gear_boost: float,
    ) -> Dict:
        truck = num_forward >= 10
        if num_forward == 6 and not truck:
            forward = [4.784, 2.423, 1.443, 1.000, 0.826, 0.643]
        elif truck:
            forward = _geometric(13.91, 0.71, num_forward)
        else:
            forward = _geometric(4.784, 0.643, num_forward)
        forward = GearRatioCalculator._apply_low_gearing(
            forward, enable_low_gearing, low_gear_boost
        )
        if num_reverse <= 0:
            reverse: List[float] = []
        elif num_reverse == 1:
            reverse = [round(forward[0] * 1.15, 3)]
        else:
            reverse = [
                round(forward[0] * (1.15 + i * 0.2), 3)
                for i in range(num_reverse)
            ]
        axle = GearRatioCalculator._highway_axle(top_speed, truck=truck)
        return {
            "family": "discrete_gearRatio",
            "l10n_name": L10N["Manual"],
            "axle_ratio": axle,
            "auto_gear_change_time": 0.3,
            "gear_change_time": 0.3,
            "start_gear_threshold": 0.3,
            "forward": [{"gearRatio": r} for r in forward],
            "backward": [
                {
                    "gearRatio": r,
                    "name": "R" if len(reverse) == 1 else f"R{i + 1}",
                }
                for i, r in enumerate(reverse)
            ],
        }

    @staticmethod
    def _cvt(top_speed: float) -> Dict:
        min_fwd = round(_clamp(12.3 * (53.0 / top_speed), 8.8, 40.0), 1)
        min_back = round(_clamp(min_fwd * 2.6, 16.0, 80.0), 1)
        return {
            "family": "continuous_minMaxRatio",
            "l10n_name": L10N["CVT"],
            "axle_ratio": None,
            "auto_gear_change_time": None,
            "gear_change_time": None,
            "start_gear_threshold": None,
            "min_forward_gear_ratio": min_fwd,
            "max_forward_gear_ratio": 320.0,
            "min_backward_gear_ratio": min_back,
            "max_backward_gear_ratio": 320.0,
            "forward": [],
            "backward": [],
        }

    @staticmethod
    def _powershift(
        num_forward: int,
        num_reverse: int,
        top_speed: float,
    ) -> Dict:
        last = int(round(top_speed))
        first = max(2, int(round(max(2.2, top_speed * 0.05))))
        forward_speeds = _int_geometric_speeds(first, last, num_forward)
        if num_reverse <= 0:
            reverse_speeds: List[int] = []
        else:
            r_last = max(first, int(round(min(top_speed * 0.35, last * 0.4))))
            reverse_speeds = _int_geometric_speeds(first, r_last, num_reverse)
        return {
            "family": "discrete_maxSpeed",
            "l10n_name": L10N["PowerShift"],
            "axle_ratio": 0.95,
            "auto_gear_change_time": 0.0,
            "gear_change_time": 0.0,
            "start_gear_threshold": None,
            "forward": [
                {"maxSpeed": s, "name": str(i + 1)}
                for i, s in enumerate(forward_speeds)
            ],
            "backward": [
                {
                    "maxSpeed": s,
                    "name": "R" if len(reverse_speeds) == 1 else f"R{i + 1}",
                }
                for i, s in enumerate(reverse_speeds)
            ],
        }
