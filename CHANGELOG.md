# Changelog

All notable changes to the FS25 Engine and Transmission Config Tool are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Transmission form: optional **Custom axle ratio** with Giants `axleRatio` entry and hover tooltip (vanilla ranges by vehicle class). Unchecked = generator default; hidden for CVT.
- **Drive layout** selector between Engine and Transmission (FWD / RWD / 4WD / 6×6), with tooltip noting wheel indices must match the mod vehicle.
- Combined and engine-only XML include **`differentialConfigurations`** for the selected layout, with inline comments labeling the layout and each diff. Paste order matches vanilla: **consumer → differential → motor**, with blank lines between sections and between `</motor>` and `<transmission>`.
- **Preset file schema v1** (`src/core/preset_schema.py`): validated JSON envelope for engine, transmission, and full-configuration files (`schema_version`, `kind`, optional `drive_layout`, engine `torque_curve`, and transmission `forward_gears` / `reverse_gears`). Legacy unwrapped JSON still loads.
- Factory presets as JSON under `Presets/Engine/` and `Presets/Transmission/` (no longer hardcoded in Python). Portable and installer builds bundle that tree. Shipped Power Stroke and Cummins engines include full idle-to-redline engine-dyno **% of peak torque** curves. Existing `Custom Presets/` files are copied into the new folders on first load.
- Combined preset Export/Import stores **drive layout** along with engine and transmission.
- Factory manuals **New Process NP435** and **BorgWarner T18** (real 4-speed granny boxes, including the very deep reverse).
- Factory gas engines **Ford 300 I6**, **Chevy 350**, **Ford 351 Windsor**, **Ford 351 Cleveland**, **Ford 302**, **Chevy 305**, **Chevy 454**, and **Ford 460** with baked idle-to-redline **% of peak torque** curves.
- Factory four-cylinder engines **Toyota 22R-E**, **Cummins 4BT**, **Willys Go-Devil**, and **Isuzu 4BD1T** with baked idle-to-redline **% of peak torque** curves.
- Factory transmissions with baked real gear ratios and top speeds: **Muncie SM465**, **Hydra-Matic TH400**, **Ford C6**, **700R4**, **Ford E4OD**, **4L80-E**, **Mazda M5OD-R2**, **ZF S5-42**, **New Venture NV4500** (gas and diesel variants), **Allison 1000 Series** (5- and 6-speed), **Toyota W56**, **Willys BorgWarner T-90**, **Isuzu MSA-5G**, and **Ford TorqShift 5R110** (2004 Excursion; 5-speed ECU shift map).

### Changed

- Tooltips anchor below the control (flip above near screen bottom) instead of under the cursor; slightly larger readable text.
- XML generation follows vanilla FS25 families: Automatic/highway Manual use `gearRatio` plus a Giants `axleRatio` (not a US 4.10 stamp); CVT uses min/max ratio with no gears; PowerShift uses `maxSpeed` gears and axle ~0.95.
- Default preset folder is **`Presets/`** next to the app (Settings still lets you pick another location). Custom engine/transmission saves go in `Engine/` and `Transmission/` beside the factory files. Built-in names cannot be overwritten.
- Generating XML uses a preset's baked `torque_curve` when present; otherwise the previous auto-generated formula.
- Generating XML uses a preset's baked `forward_gears` / `reverse_gears` when present, including catalog gear names on the XML tags.
- Shipped **Allison 10L1000** uses real ratios (three overdrives, last gear 0.63) and **158 km/h** top speed.
- Shipped **Eaton Fuller RTLO-18913A** (**137 km/h**) and **RTLO-22918B** (**145 km/h**) use real splits, crawlers, and reverse sets.
- Shipped **Power Stroke** and **Cummins** diesel presets use full idle-to-redline baked torque curves (not 1200–3000 only).
- Factory transmission dropdown names are catalog model names.
- `torqueScale` is derived from horsepower. Fuel Scale writes `<consumer usage>` instead of being stuffed into `torqueScale`.
- Automatic gear spreads use overdrive (about 0.61 in 10th) instead of a linear 4.5→1.3.
- PowerShift forward gears emit **whole km/h** `maxSpeed` values (Giants convention) instead of decimals.

### Fixed

- PowerShift with a single reverse gear no longer emits an unrealistically slow reverse `maxSpeed` (first-gear floor); reverse uses the proper reverse speed cap for the configured top speed.

### Removed

- Factory preset **4-speed with Granny Gear**.
- Factory dropdown nicknames **10-speed Allison Automatic**, **13-speed Eaton Fuller**, and **18-speed Eaton Fuller** (replaced by catalog model names).

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
