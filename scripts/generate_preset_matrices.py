"""Generate ! ENGINE_MATRIX.md and ! TRANSMISSION_MATRIX.md from presets + Caveman source tables."""

from __future__ import annotations

import json
from pathlib import Path

ENGINE_MATRIX_NAME = "! ENGINE_MATRIX.md"
TRANSMISSION_MATRIX_NAME = "! TRANSMISSION_MATRIX.md"

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "Presets" / "Engine"
TRANS_DIR = ROOT / "Presets" / "Transmission"

I4_ENGINES = [
    {
        "name": "Toyota 22R-E",
        "hp": 112,
        "min_rpm": 750,
        "max_rpm": 5500,
        "turbo": False,
        "fuel": 1.0,
        "curve": [
            (750, 0.50),
            (1000, 0.68),
            (1400, 0.78),
            (1600, 0.84),
            (1800, 0.88),
            (2000, 0.92),
            (2400, 0.96),
            (2800, 1.00),
            (3400, 0.90),
            (4000, 0.78),
            (4500, 0.65),
            (5500, 0.42),
        ],
    },
    {
        "name": "Cummins 4BT",
        "hp": 105,
        "min_rpm": 750,
        "max_rpm": 3000,
        "turbo": False,
        "fuel": 1.0,
        "curve": [
            (750, 0.60),
            (1000, 0.85),
            (1400, 0.98),
            (1600, 1.00),
            (1800, 0.96),
            (2000, 0.88),
            (2400, 0.70),
            (2800, 0.52),
            (3000, 0.40),
        ],
    },
    {
        "name": "Willys Go-Devil",
        "hp": 60,
        "min_rpm": 600,
        "max_rpm": 3600,
        "turbo": False,
        "fuel": 1.0,
        "curve": [
            (600, 0.65),
            (1000, 0.92),
            (1400, 0.98),
            (1600, 1.00),
            (1800, 0.95),
            (2000, 0.88),
            (2400, 0.74),
            (2800, 0.55),
            (3400, 0.38),
            (3600, 0.30),
        ],
    },
    {
        "name": "Isuzu 4BD1T",
        "hp": 135,
        "min_rpm": 700,
        "max_rpm": 3200,
        "turbo": True,
        "fuel": 1.0,
        "curve": [
            (700, 0.55),
            (1000, 0.72),
            (1400, 0.88),
            (1600, 0.95),
            (1800, 1.00),
            (2000, 0.98),
            (2400, 0.88),
            (2800, 0.75),
            (3400, 0.58),
            (3200, 0.45),
        ],
    },
]

DIESEL_ORDER = [
    "7.3 Powerstroke",
    "6.0 Powerstroke",
    "6.7 Powerstroke",
    "5.9 Cummins",
    "6.7 Cummins",
]

GAS_V8_ORDER = [
    "Ford 300 I6",
    "Chevy 350",
    "Ford 351 Windsor",
    "Ford 351 Cleveland",
    "Ford 302",
    "Chevy 305",
    "Chevy 454",
    "Ford 460",
]


def load_engines():
    out = []
    for path in sorted(ENGINE_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        e = raw["engine"]
        e["_file"] = path.name
        e["_preset"] = raw.get("preset_name", path.stem)
        out.append(e)
    return out


def load_transmissions():
    out = []
    for path in sorted(TRANS_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        t = raw["transmission"]
        t["_file"] = path.name
        t["_preset"] = raw.get("preset_name", path.stem)
        out.append(t)
    return out


def fmt_torque(val: float | None) -> str:
    if val is None:
        return "—"
    if val >= 0.999:
        return f"**{val:.2f}**"
    return f"{val:.2f}"


def write_engine_matrix(engines: list) -> None:
    lines: list[str] = []
    lines += [
        "# Factory Engine Matrix",
        "",
        "Reference for shipped and queued factory engine presets. Torque values are "
        "**% of peak torque** (0.0–1.0), matching Giants `torque=\"\"` on generated XML.",
        "",
        "Source: Caveman real-world / dyno tables (2026-08-17). JSON presets: "
        "`Presets/Engine/*.json`.",
        "",
        "## Summary",
        "",
        "| Preset | HP | Cost ($) | Idle (min RPM) | Redline (max RPM) | Turbo | Fuel scale | JSON |",
        "|--------|---:|---------:|---------------:|------------------:|:-----:|-----------:|:----:|",
    ]
    for e in sorted(engines, key=lambda x: x["_preset"]):
        turbo = "Yes" if e.get("turbocharged") else "No"
        lines.append(
            f"| {e['_preset']} | {e['horsepower']:.0f} | {e['cost']} | "
            f"{e['min_rpm']:.0f} | {e['max_rpm']:.0f} | {turbo} | "
            f"{e.get('fuel_usage_scale', 1.0)} | Yes |"
        )
    for i4 in I4_ENGINES:
        if i4["name"] in {e["_preset"] for e in engines}:
            continue
        turbo = "Yes" if i4["turbo"] else "No"
        lines.append(
            f"| {i4['name']} | {i4['hp']} | TBD | {i4['min_rpm']} | {i4['max_rpm']} | "
            f"{turbo} | {i4['fuel']} | **Queued** |"
        )

    by_name = {e["_preset"]: e for e in engines}
    diesel_names = [n for n in DIESEL_ORDER if n in by_name]
    lines += [
        "",
        "## Diesel torque curves (idle → redline)",
        "",
        "Shipped in JSON. Peak: **6.0 @ 2000** · **7.3 @ 1600** · "
        "**6.7 PSD @ 1600–1800** · **5.9 @ 1600** · **6.7 Cummins @ 1600–1800**.",
        "",
    ]
    rpm_set_diesel: set[int] = set()
    for name in diesel_names:
        for pt in by_name[name].get("torque_curve", []):
            rpm_set_diesel.add(int(pt["rpm"]))
    lines.append("| RPM | " + " | ".join(diesel_names) + " |")
    lines.append("|----:|" + ":|".join(["---"] * len(diesel_names)) + "|")
    for rpm in sorted(rpm_set_diesel):
        cells = []
        for name in diesel_names:
            val = next(
                (p["torque"] for p in by_name[name]["torque_curve"] if int(p["rpm"]) == rpm),
                None,
            )
            cells.append(fmt_torque(float(val)) if val is not None else "—")
        lines.append(f"| {rpm} | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## Gas V8 torque curves (idle → redline)",
        "",
        "Shipped in JSON. Peak: **300 I6 @ 1600** · **350 @ 2800** · **351W @ 2800** · "
        "**351C @ 3400** · **302 @ 2400** · **305 @ 2400** · **454 @ 2200** · **460 @ 2400**.",
        "",
    ]
    gas_names = [n for n in GAS_V8_ORDER if n in by_name]
    rpm_set: set[int] = set()
    for name in gas_names:
        for pt in by_name[name].get("torque_curve", []):
            rpm_set.add(int(pt["rpm"]))
    lines.append("| RPM | " + " | ".join(gas_names) + " |")
    lines.append("|----:|" + ":|".join(["---"] * len(gas_names)) + "|")
    for rpm in sorted(rpm_set):
        cells = []
        for name in gas_names:
            val = next(
                (p["torque"] for p in by_name[name]["torque_curve"] if int(p["rpm"]) == rpm),
                None,
            )
            cells.append(fmt_torque(val))
        lines.append(f"| {rpm} | " + " | ".join(cells) + " |")

    i4_names = [i["name"] for i in I4_ENGINES]
    i4_queued = [i for i in I4_ENGINES if i["name"] not in by_name]
    queued_note = (
        "**Queued — not yet JSON presets.**"
        if i4_queued
        else "Shipped in JSON."
    )
    lines += [
        "",
        "## Four-cylinder torque curves (idle → redline)",
        "",
        f"{queued_note} Peak: **22R-E @ 2800** · **4BT @ 1600** · "
        "**Go-Devil @ 1600** · **4BD1T @ 1800**.",
        "",
    ]
    rpm_set_i4: set[int] = set()
    for name in i4_names:
        if name in by_name:
            for pt in by_name[name].get("torque_curve", []):
                rpm_set_i4.add(int(pt["rpm"]))
        else:
            i4 = next(i for i in I4_ENGINES if i["name"] == name)
            for rpm, _ in i4["curve"]:
                rpm_set_i4.add(rpm)
    lines.append("| RPM | " + " | ".join(i4_names) + " |")
    lines.append("|----:|" + ":|".join(["---"] * len(i4_names)) + "|")
    for rpm in sorted(rpm_set_i4):
        cells = []
        for name in i4_names:
            if name in by_name:
                val = next(
                    (
                        p["torque"]
                        for p in by_name[name]["torque_curve"]
                        if int(p["rpm"]) == rpm
                    ),
                    None,
                )
            else:
                i4 = next(i for i in I4_ENGINES if i["name"] == name)
                val = next((t for r, t in i4["curve"] if r == rpm), None)
            cells.append(fmt_torque(float(val)) if val is not None else "—")
        lines.append(f"| {rpm} | " + " | ".join(cells) + " |")

    lines += ["", "## Per-engine baked curves (JSON)", ""]
    for e in sorted(engines, key=lambda x: x["_preset"]):
        turbo = "Yes" if e.get("turbocharged") else "No"
        lines += [
            f"### {e['_preset']}",
            "",
            f"- **File:** `{e['_file']}`",
            f"- **HP:** {e['horsepower']:.0f} · **Cost:** ${e['cost']} · "
            f"**RPM:** {e['min_rpm']:.0f}–{e['max_rpm']:.0f}",
            f"- **Turbo:** {turbo} · **Fuel scale:** {e.get('fuel_usage_scale', 1.0)}",
            "",
            "| RPM | Torque (% peak) |",
            "|----:|----------------:|",
        ]
        for pt in e.get("torque_curve", []):
            lines.append(f"| {pt['rpm']:.0f} | {fmt_torque(float(pt['torque']))} |")
        lines.append("")

    (ENGINE_DIR / ENGINE_MATRIX_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_transmission_matrix(transmissions: list) -> None:
    lines: list[str] = []
    lines += [
        "# Factory Transmission Matrix",
        "",
        "Reference for all factory transmission presets. Gear ratios are real-world "
        "factory values. Reverse ratios are stored **positive** in JSON (Giants convention). "
        "Top speed is **km/h** in presets and the generator.",
        "",
        "Source: Caveman real-world ratio + top-speed matrices (2026-08-17). JSON presets: "
        "`Presets/Transmission/*.json`.",
        "",
        "**Eaton Fuller 13/18:** dual Lo/Hi numbers are baked as separate forward gears (splitters).",
        "",
        "**NV4500:** same gear ratios; gas preset **169 km/h**, diesel preset **153 km/h**.",
        "",
        "**TorqShift 5R110:** 6 mechanical configs; ECU drives **5 speeds** (1-2-3-5-6). "
        "Cold-weather strategy gear **1.09** omitted in JSON.",
        "",
        "## Summary",
        "",
        "| Preset | Type | Fwd | Rev | Top gear | Max km/h | Cost ($) | JSON |",
        "|--------|------|----:|----:|---------:|---------:|---------:|:----:|",
    ]
    for t in sorted(transmissions, key=lambda x: x["_preset"]):
        fwd = t.get("forward_gears", [])
        rev = t.get("reverse_gears", [])
        top = fwd[-1]["gearRatio"] if fwd else "—"
        lines.append(
            f"| {t['_preset']} | {t['type']} | {len(fwd)} | {len(rev)} | {top} | "
            f"{t['top_speed']:.0f} | {t['cost']} | Yes |"
        )

    lines += [
        "",
        "## Gear ratio matrix",
        "",
        "| Factory name | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th–10th / splits | Reverse |",
        "|--------------|----:|----:|----:|----:|----:|----:|-------------------|--------:|",
    ]
    ratio_rows = [
        ("New Process NP435", "6.69", "3.34", "1.66", "1.00", "—", "—", "—", "8.26"),
        ("Muncie SM465", "6.55", "3.58", "1.70", "1.00", "—", "—", "—", "6.09"),
        ("BorgWarner T18", "6.32", "3.09", "1.69", "1.00", "—", "—", "—", "7.44"),
        ("Hydra-Matic TH400", "2.48", "1.48", "1.00", "—", "—", "—", "—", "2.07"),
        ("Ford C6", "2.46", "1.46", "1.00", "—", "—", "—", "—", "2.18"),
        ("Hydra-Matic 700R4", "3.06", "1.63", "1.00", "0.70", "—", "—", "—", "2.29"),
        ("Ford E4OD", "2.71", "1.54", "1.00", "0.71", "—", "—", "—", "2.18"),
        ("Ford TorqShift 5R110", "3.11", "2.20", "1.54", "1.00", "0.71", "—", "—", "2.88"),
        ("Mazda M5OD-R2", "3.91", "2.24", "1.49", "1.00", "0.80", "—", "—", "3.70"),
        ("ZF S5-42", "5.72", "2.94", "1.61", "1.00", "0.76", "—", "—", "5.24"),
        ("New Venture NV4500 (Gas)", "5.61", "3.04", "1.67", "1.00", "0.75", "—", "—", "5.61"),
        ("New Venture NV4500 (Diesel)", "5.61", "3.04", "1.67", "1.00", "0.75", "—", "—", "5.61"),
        ("Hydra-Matic 4L80-E", "2.48", "1.48", "1.00", "0.75", "—", "—", "—", "2.07"),
        ("Allison 1000 Series (5-Spd)", "3.10", "1.81", "1.41", "1.00", "0.71", "—", "—", "4.49"),
        ("Allison 1000 Series (6-Spd)", "3.10", "1.81", "1.41", "1.00", "0.71", "0.61", "—", "4.49"),
        (
            "Allison 10L1000 (10-Spd)",
            "4.70",
            "2.99",
            "2.15",
            "1.80",
            "1.52",
            "1.28",
            "7th 1.00 · 8th 0.85 · 9th 0.69 · 10th 0.63",
            "5.06",
        ),
        (
            "Eaton Fuller RTLO-18913A",
            "12.31",
            "8.60",
            "6.22",
            "4.54",
            "3.38",
            "2.47/2.11",
            "6th 1.74/1.49 · 7th 1.23/1.05 · 8th 0.86/0.73",
            "13.23 / 3.78",
        ),
        (
            "Eaton Fuller RTLO-22918B",
            "14.40/12.29",
            "8.56/7.30",
            "6.05/5.16",
            "4.38/3.74",
            "3.20/2.73",
            "2.28/1.94",
            "6th 1.62/1.38 · 7th 1.17/1.00 · 8th 0.86/0.73",
            "4 reverses (see detail)",
        ),
        ("Toyota W56", "3.95", "2.14", "1.38", "1.00", "0.85", "—", "—", "4.09"),
        ("Willys BorgWarner T-90", "2.80", "1.55", "1.00", "—", "—", "—", "—", "3.79"),
        ("Isuzu MSA-5G", "4.98", "2.74", "1.65", "1.00", "0.78", "—", "—", "4.62"),
    ]
    for row in ratio_rows:
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Top speed matrix (km/h)",
        "",
        "| Factory name | Top gear ratio | Maximum speed (km/h) |",
        "|--------------|---------------:|---------------------:|",
    ]
    top_rows = [
        ("Willys BorgWarner T-90", "1.00", 88),
        ("New Process NP435", "1.00", 105),
        ("Muncie SM465", "1.00", 105),
        ("BorgWarner T18", "1.00", 105),
        ("Toyota W56", "0.85", 137),
        ("Eaton Fuller RTLO-18913A", "0.73", 137),
        ("Isuzu MSA-5G", "0.78", 128),
        ("Eaton Fuller RTLO-22918B", "0.73", 145),
        ("Hydra-Matic TH400", "1.00", 160),
        ("Ford C6", "1.00", 160),
        ("ZF S5-42", "0.76", 160),
        ("Allison 1000 Series (5-Spd)", "0.71", 160),
        ("Allison 1000 Series (6-Spd)", "0.61", 158),
        ("Allison 10L1000 (10-Spd)", "0.63", 158),
        ("Mazda M5OD-R2", "0.80", 169),
        ("New Venture NV4500 (Gas)", "0.75", 169),
        ("Hydra-Matic 4L80-E", "0.75", 177),
        ("Ford E4OD", "0.71", 177),
        ("Hydra-Matic 700R4", "0.70", 185),
        ("New Venture NV4500 (Diesel)", "0.75", 153),
        ("Ford TorqShift 5R110", "0.71", 153),
    ]
    for name, tg, spd in top_rows:
        lines.append(f"| {name} | {tg} | {spd} |")

    lines += ["", "## Per-transmission baked gears (JSON)", ""]
    for t in sorted(transmissions, key=lambda x: x["_preset"]):
        lines += [
            f"### {t['_preset']}",
            "",
            f"- **File:** `{t['_file']}` · **Type:** {t['type']} · **Cost:** ${t['cost']} · "
            f"**Top speed:** {t['top_speed']:.0f} km/h",
            "",
            "**Forward**",
            "",
            "| Gear | Ratio |",
            "|------|------:|",
        ]
        for g in t.get("forward_gears", []):
            lines.append(f"| {g.get('name', '')} | {g['gearRatio']} |")
        lines += [
            "",
            "**Reverse**",
            "",
            "| Gear | Ratio |",
            "|------|------:|",
        ]
        for g in t.get("reverse_gears", []):
            lines.append(f"| {g.get('name', '')} | {g['gearRatio']} |")
        lines.append("")

    (TRANS_DIR / TRANSMISSION_MATRIX_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_engine_matrix(load_engines())
    write_transmission_matrix(load_transmissions())
    print(f"Wrote {ENGINE_DIR / ENGINE_MATRIX_NAME}")
    print(f"Wrote {TRANS_DIR / TRANSMISSION_MATRIX_NAME}")


if __name__ == "__main__":
    main()
