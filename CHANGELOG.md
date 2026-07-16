# Changelog

All notable changes to the FS25 Engine and Transmission Config Tool are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-07-16

### Added

- Repository layout aligned with Subtitle Muxer (`src/`, `scripts/`, `requirements/`, `docs/`)
- Manual **Build** and **Build and Release** GitHub Actions workflows (Windows, macOS Intel/Apple Silicon, Linux distros)
- `CONTRIBUTING.md` for developers and packaging instructions
- Issue templates for bug reports and feature requests
- Real Windows installer via Inno Setup (`packaging/windows/setup.iss`) — single Setup `.exe`
- In-app **About** dialog with [Buy Me a Coffee](https://www.buymeacoffee.com/caveman117) support link
- Streamlined output toolbar: one **Generate XML** action for combined engine + transmission, plus Copy / Save and preset Export/Import
- XML preview vertical scrollbar is theme-matched and only appears when content overflows
- **Custom presets** on disk under `Custom Presets/Engine presets` and `Custom Presets/Transmission presets` (JSON), merged into the dropdowns automatically
- Per-section **Save** next to **Load** (engine saves engine-only; transmission saves transmission-only)
- **Settings** dialog: custom-presets folder location (default: alongside the EXE / app folder), default engine/transmission presets on startup, and **Open log file**
- Themed modal dialogs (prompts, alerts, confirmations) match the dark app UI
- Pixel-art app icon (`assets/`) for the window, Windows EXE/installer, and packaged builds
- Rotating app log file (`fs25_config_tool.log`, ~256 KiB × 2) for troubleshooting without bloating the install folder

### Changed

- Application packaged as `python -m src` with version from `src/__init__.py`
- Core logic split into `src/core/`; UI lives in `src/ui/`
- Dropped PyInstaller `--onedir` “installer” folder
- Releases use the full product name (**FS25 Engine and Transmission Config Tool**)
- Only the Windows portable build is zip-wrapped; Windows Setup and Mac/Linux ship as bare binaries
- Windows portable = onefile `.exe`; Windows installable = Inno Setup wrapper around that binary
- Release/build binary verification: exact filename, minimum size (5 MiB), and PE/ELF/Mach-O magic checks
- Main window layout: **Engine** (top) and **Transmission** (bottom) stacked on the left; XML preview and actions on the right (no tabs)
- XML preview uses **word wrap** (no horizontal scrollbar); line numbers stay aligned with wrapped lines
- Engine and transmission forms use compact paired fields and shorter numeric inputs so settings fit without clipping
- Main window centers on the primary screen at launch; Settings dialog sized to fit its contents

### Fixed

- Standard Tkinter fallback no longer tries to build the UI before form variables exist

## [1.0.0] - 2025-07-22

Initial public release of the FS25 Engine and Transmission Config Tool — a desktop app for generating Farming Simulator 25 engine and transmission XML configurations.

### Added

#### Application

- Standalone Python desktop application with a dark-mode GUI (CustomTkinter, with Tkinter fallback)
- Portable Windows executable (no installation required)
- Compact workflow with tooltips on inputs and actions

#### Engine configuration

- Full engine setup with auto-generated torque curves
- Turbocharged and naturally aspirated curve generation
- Built-in presets: 7.3 / 6.0 / 6.7 Powerstroke; 5.9 / 6.7 Cummins
- Custom engine creation with full parameter control
- Torque calculation: `(HP × 9549) / Peak RPM`

#### Transmission configuration

- Support for Manual, Automatic, CVT, and PowerShift
- Automatic gear ratio calculation by transmission type
- Low gearing option for the first 25% of forward gears
- Built-in presets: 10-speed Allison, 13-speed Eaton Fuller, 4-speed with Granny Gear, 18-speed Eaton Fuller
- Custom gear counts and ratios

#### File management and export

- Save and load presets as JSON
- FS25-compatible XML export (engine, transmission, or combined)
- Copy generated XML to clipboard
- XML preview with syntax highlighting and line numbers

### Technical notes

- Modular architecture (torque curves, gear ratios, XML generation, presets, GUI)
- Input validation and error handling
- Thread-safe preset management
- UTF-8 support for international characters

[Unreleased]: https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool/releases/tag/v1.0.0
