#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# build_app.sh — portable onefile PyInstaller builds (Linux / macOS)
#
# Version comes from src/__init__.py (single source of truth).
# Windows installers are built separately via scripts/build_app.bat + Inno Setup.
#
# Outputs (example):
#   dist/mac-apple-silicon/1.0.0/portable/FS25 Engine and Transmission Config Tool
#   dist/ubuntu/1.0.0/portable/FS25 Engine and Transmission Config Tool
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APP_NAME="FS25 Engine and Transmission Config Tool"

if [[ -n "${FS25_CONFIG_TOOL_PLATFORM:-}" ]]; then
  PLATFORM="$FS25_CONFIG_TOOL_PLATFORM"
else
  uname_s="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "$uname_s" in
    linux*)
      PLATFORM="linux"
      ;;
    darwin*)
      machine="$(uname -m)"
      if [[ "$machine" == "arm64" ]]; then
        PLATFORM="mac-apple-silicon"
      else
        PLATFORM="mac-intel"
      fi
      ;;
    msys*|cygwin*|mingw*)
      PLATFORM="windows"
      ;;
    *)
      echo "ERROR: Unsupported OS: $(uname -s)"
      exit 1
      ;;
  esac
fi

echo
echo "=== ${APP_NAME} — portable build (${PLATFORM}) ==="
echo "Working directory: $ROOT"
echo

if [[ ! -x .venv/bin/python ]]; then
  echo "Virtual environment not found. Running setup_env.sh ..."
  bash scripts/setup_env.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "ERROR: pyinstaller not found in the virtual environment."
  echo "Run scripts/setup_env.sh first."
  exit 1
fi

VERSION="$(python scripts/read_version.py)"
echo "App version: ${VERSION}"
echo

rm -rf "dist/${PLATFORM}/${VERSION}/portable" "build/${PLATFORM}/${VERSION}/portable"
mkdir -p "dist/${PLATFORM}/${VERSION}/portable" "build/${PLATFORM}/${VERSION}/portable"

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --onefile \
  --name "$APP_NAME" \
  --paths=. \
  --collect-all customtkinter \
  --distpath "dist/${PLATFORM}/${VERSION}/portable" \
  --workpath "build/${PLATFORM}/${VERSION}/portable" \
  --specpath "build/${PLATFORM}/${VERSION}/portable" \
  src/__main__.py

echo
echo "Build complete:"
echo "  Portable: dist/${PLATFORM}/${VERSION}/portable/${APP_NAME}"
echo
