# Contributing

Thanks for helping improve **FS25 Engine and Transmission Config Tool**. This document is for people developing or packaging the app. End-user download and usage instructions live in [README.md](README.md).

## Repository layout

Keep the **repository root** reserved for project metadata only:

| Path | Purpose |
|------|---------|
| `README.md` | End-user overview |
| `CHANGELOG.md` | Keep a Changelog + SemVer (**always committed**) |
| `KNOWN_ISSUES.md` | Public acknowledged limitations (when needed; **committed**) |
| `LICENSE` | License text (MIT) |
| `CONTRIBUTING.md` | This file |
| `.gitignore` | Tells Git which **local** files to skip (must list `LOCAL_NOTES.md`) |
| `.gitattributes` | Line-ending rules |
| `.github/` | GitHub Actions workflows and issue templates |
| `docs/images/` | Screenshots and other images for the README |
| `src/` | Application source code |
| `scripts/` | Setup / run / build helpers |
| `requirements/` | Python dependency pins |
| `Presets/` | Shipped factory engine/transmission JSON |
| `assets/` | App icons |
| `packaging/windows/` | Inno Setup script (`setup.iss`) |

Do **not** add application code, build outputs, or virtualenvs at the root.

**Local only (never commit):** `LOCAL_NOTES.md` (private next-work scratchpad), `.venv/`, `build/`, `dist/`, `__pycache__/`, IDE folders, secrets (`.env`), `RELEASE_BODY.md`, `settings.json`, `Custom Presets/`, `database/`, log files.

## Version number (single source of truth)

The app version lives in **one place only**:

```text
src/__init__.py  →  __version__ = "x.y.z"
```

Everything else reads from that value:

- Window title and About dialog
- `python scripts/read_version.py` (used by CI)
- GitHub Release tags / asset names (`vX.Y.Z`, `FS25ConfigTool-X.Y.Z-…`)

### Stage mapping

| Version shape | Stage |
|---------------|--------|
| `0.0.x` | **Alpha** |
| `0.x.x` where minor ≥ 1 (e.g. `0.1.0`) | **Beta** |
| major ≥ 1 (e.g. `1.0.0`) | **Release** |

Status badges in the README should match the stage of `__version__`. Current shipped version is **1.1.0** (release). Unreleased work stays in [CHANGELOG.md](CHANGELOG.md) under `## [Unreleased]` until the next version bump.

**During development:** keep `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) current as you land user-visible work. Use the same [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) categories (`Added`, `Changed`, `Fixed`, `Removed`, and so on), complete sentences, and no secrets. Commit CHANGELOG updates with the feature or fix they describe; do not batch everything only at release time.

**When shipping a new release:**

1. Bump `__version__` in `src/__init__.py`
2. Move items from `## [Unreleased]` into a dated version section in [CHANGELOG.md](CHANGELOG.md)
3. Commit and push
4. Run **Build and Release**

Do not hard-code the version in workflows or scripts.

## About `.gitignore`

**`.gitignore` should be committed to GitHub.** It is a normal tracked file.

What should *not* go to GitHub are the paths listed **inside** `.gitignore`, for example:

- `LOCAL_NOTES.md` (private scratchpad)
- `.venv/` (local virtual environment)
- `build/` and `dist/` (PyInstaller outputs)
- `__pycache__/`, IDE folders
- `RELEASE_BODY.md` (local draft for the GitHub Release description)
- `settings.json`, `Custom Presets/`, `database/`, log files

Those stay on your machine (or in CI artifacts).

## Development setup

Requires **Python 3.10+** (development / CI currently use **3.14**).

**Windows:**

```bat
scripts\setup_env.bat
```

**Linux / macOS:**

```bash
chmod +x scripts/setup_env.sh scripts/build_app.sh
./scripts/setup_env.sh
```

This creates `.venv`, upgrades `pip`, and installs packages from `requirements/requirements.txt`.

On Debian/Ubuntu, install tkinter if needed:

```bash
sudo apt-get install python3-tk
```

## Run from source

Building from source is always free and full-featured (same app as packaged builds).

**Windows:**

```bat
scripts\run_app.bat
```

**Any platform (from the repository root):**

```bash
python -m src
```

## Build locally

Windows builds a **portable onefile `.exe`** and a **real Inno Setup installer** (single Setup `.exe`).
Linux and Mac build a portable onefile binary only.

Artifact display name (no abbreviations): **FS25 Engine and Transmission Config Tool**

| Type | Example |
|------|---------|
| Windows portable | `dist/windows/1.1.0/portable/FS25 Engine and Transmission Config Tool.exe` |
| Windows installer | `dist/windows/1.1.0/installer/FS25 Engine and Transmission Config Tool-1.1.0-Setup.exe` |
| Mac Apple Silicon | `dist/mac-apple-silicon/1.1.0/portable/FS25 Engine and Transmission Config Tool` |
| Mac Intel | `dist/mac-intel/1.1.0/portable/FS25 Engine and Transmission Config Tool` |

**Windows prerequisites:** [Inno Setup 6](https://jrsoftware.org/isinfo.php) (`ISCC.exe`), or `choco install innosetup -y`.

```bat
scripts\build_app.bat
```

```bash
./scripts/build_app.sh
```

## GitHub Actions

Two **manual** workflows (no push/PR triggers):

| Workflow | File | What it does |
|----------|------|----------------|
| **Build** | [`.github/workflows/build.yml`](.github/workflows/build.yml) | Matrix build → upload versioned artifacts |
| **Build and Release** | [`.github/workflows/release.yml`](.github/workflows/release.yml) | Same builds → GitHub Release |

Windows/macOS default to Python **3.14**. Linux builds use each distro's system Python in containers.

### What gets built

| Platform | Artifact name example | Contents |
|----------|------------------------|----------|
| Windows portable | `fs25-config-tool-windows-1.1.0-portable` | Single `.exe` |
| Windows installer | `fs25-config-tool-windows-1.1.0-installer` | Single `*-Setup.exe` (Inno Setup) |
| Mac Apple Silicon | `fs25-config-tool-mac-apple-silicon-1.1.0` | Single binary |
| Mac Intel | `fs25-config-tool-mac-intel-1.1.0` | Single binary |
| Linux | `fs25-config-tool-ubuntu-1.1.0` (same pattern per distro) | Single binary |

### Linux matrix

GitHub only hosts Ubuntu runners, so Linux flavours are built in Docker containers:

| Platform label | Container image |
|----------------|-----------------|
| `ubuntu` | `ubuntu:24.04` |
| `debian` | `debian:bookworm` |
| `mint` | `linuxmintd/mint22.1-amd64` |
| `fedora` | `fedora:latest` |
| `arch` | `archlinux:latest` |

### Build only

1. Actions → **Build** → **Run workflow**
2. Download the versioned artifacts when finished

```bash
gh workflow run build.yml
gh run watch
gh run download
```

### Build and release

1. Bump `__version__` in `src/__init__.py`, move `CHANGELOG.md` items out of `[Unreleased]`, and push to `main`
2. Actions → **Build and Release** → **Run workflow**
3. Creates tag `vX.Y.Z` and attaches:

   - `FS25 Engine and Transmission Config Tool-1.1.0-windows-portable.zip` (**only** zip)
   - `FS25 Engine and Transmission Config Tool-1.1.0-windows-setup.exe`
   - `FS25 Engine and Transmission Config Tool-1.1.0-mac-apple-silicon`
   - `FS25 Engine and Transmission Config Tool-1.1.0-mac-intel`
   - `FS25 Engine and Transmission Config Tool-1.1.0-ubuntu`
   - (same pattern for `debian`, `mint`, `fedora`, `arch`)

Optional inputs: **draft**, **prerelease**.

```bash
gh workflow run "Build and Release"
# or: gh workflow run release.yml
```

If `vX.Y.Z` already exists, the release job fails. Bump the version and try again.

## Screenshots

Put PNG/WebP screenshots in [`docs/images/`](docs/images/).
Filename conventions and README wiring are described in [`docs/images/README.md`](docs/images/README.md).

## Code organization

- UI (CustomTkinter / Tkinter): `src/ui/`
- Torque curves, gear ratios, XML, presets: `src/core/`
- Binary safety checks for CI/releases: `scripts/verify_release_binary.py`
- Prefer small, focused pull requests
- Match existing naming and structure; this is a narrow one-job tool (configure, generate, copy/save FS25 XML)

## Known issues and local notes

- Public limitations users should know: [KNOWN_ISSUES.md](KNOWN_ISSUES.md) when that file exists (none committed yet)
- Maintainer private queue: `LOCAL_NOTES.md` (gitignored; not in the repo clone from GitHub)

## Pull requests

- Keep PRs small and focused
- Don't ship damaging known issues quietly. Delay, or disclose loudly
- Do not mention Cursor, AI, agents, or similar tooling in public docs or comments unless the maintainer asks
- Update `CHANGELOG.md` under **Unreleased** when your change is user-visible
