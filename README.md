# FS25 Engine and Transmission Config Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)](https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/releases)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/releases)

Desktop app for generating Farming Simulator 25 engine and transmission XML configurations — with auto torque curves, gear ratio math, built-in presets, and FS25-compatible export.

---

## Screenshots

![Main window](docs/images/main-window.png)

![Engine settings](docs/images/engine-settings.png)

![XML output](docs/images/xml-output.png)

---

## Features

- Dark-mode GUI (CustomTkinter, with Tkinter fallback)
- Engine setup with auto-generated torque curves (turbo and naturally aspirated)
- Transmission support: Manual, Automatic, CVT, PowerShift
- Built-in engine and transmission presets, plus save/load for custom configs
- FS25-compatible XML export with syntax-highlighted preview
- Copy to clipboard and portable multi-platform builds

---

## Download

1. Open this repository’s **[Releases](https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/releases)** page.
2. Download the build for your OS:
   - **Windows portable** — `FS25 Engine and Transmission Config Tool-…-windows-portable.zip` (unzip, then run the `.exe`)
   - **Windows installer** — `FS25 Engine and Transmission Config Tool-…-windows-setup.exe` (run directly)
   - **Mac** — `FS25 Engine and Transmission Config Tool-…-mac-apple-silicon` or `…-mac-intel`
   - **Linux** — `FS25 Engine and Transmission Config Tool-…-<distro>` (e.g. `…-ubuntu`)
3. On macOS/Linux, make it executable if needed: `chmod +x "FS25 Engine and Transmission Config Tool-"*`

> **Linux note:** Farming Simulator 25 is not natively released for Linux, but it runs via [Steam Proton](https://www.protondb.com/app/2300320). A Linux build of this tool is included for modders on that platform.

---

## How to use

1. Configure the **engine** on the left (or pick a preset).
2. Configure the **transmission** on the right (type, gears, top speed, optional low gearing).
3. Use the actions under the panels to generate engine, transmission, or combined FS25 XML.
4. Preview, copy, or save the XML from the bottom of the window for your mod.

### Built-in presets

**Engines:** 7.3 / 6.0 / 6.7 Powerstroke · 5.9 / 6.7 Cummins

**Transmissions:** 10-speed Allison · 13-speed Eaton Fuller · 4-speed with Granny Gear · 18-speed Eaton Fuller

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contributing

Want to build from source or send a pull request? See [CONTRIBUTING.md](CONTRIBUTING.md).
