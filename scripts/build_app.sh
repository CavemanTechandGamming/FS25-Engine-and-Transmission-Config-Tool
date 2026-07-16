#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# build_app.sh — versioned PyInstaller builds (Linux / macOS)
#
# Version comes from src/__init__.py (single source of truth).
#
# By default builds a single onefile binary. Set FS25_CONFIG_TOOL_BUILD_KINDS=both
# to also build the onedir (installer) layout.
#
# Outputs (example):
#   dist/mac-apple-silicon/1.0.0/portable/FS25ConfigTool-1.0.0
#   dist/ubuntu/1.0.0/portable/FS25ConfigTool-1.0.0
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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

BUILD_KINDS="${FS25_CONFIG_TOOL_BUILD_KINDS:-portable}"

echo
echo "=== FS25 Config Tool — PyInstaller build (${PLATFORM}) ==="
echo "Working directory: $ROOT"
echo "Build kinds: ${BUILD_KINDS}"
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
APP_NAME="FS25ConfigTool-${VERSION}"
echo "App version: ${VERSION}"
echo

COMMON_ARGS=(
  --noconfirm
  --clean
  --windowed
  --name "$APP_NAME"
  --paths=.
  --collect-all customtkinter
)

build_portable() {
  echo "Building portable (onefile) ..."
  rm -rf "dist/${PLATFORM}/${VERSION}/portable" "build/${PLATFORM}/${VERSION}/portable"
  mkdir -p "dist/${PLATFORM}/${VERSION}/portable" "build/${PLATFORM}/${VERSION}/portable"

  pyinstaller "${COMMON_ARGS[@]}" \
    --onefile \
    --distpath "dist/${PLATFORM}/${VERSION}/portable" \
    --workpath "build/${PLATFORM}/${VERSION}/portable" \
    --specpath "build/${PLATFORM}/${VERSION}/portable" \
    src/__main__.py

  echo "  -> dist/${PLATFORM}/${VERSION}/portable/${APP_NAME}"
}

build_installer() {
  echo "Building installer (onedir) ..."
  rm -rf "dist/${PLATFORM}/${VERSION}/installer" "build/${PLATFORM}/${VERSION}/installer"
  mkdir -p "dist/${PLATFORM}/${VERSION}/installer" "build/${PLATFORM}/${VERSION}/installer"

  pyinstaller "${COMMON_ARGS[@]}" \
    --onedir \
    --distpath "dist/${PLATFORM}/${VERSION}/installer" \
    --workpath "build/${PLATFORM}/${VERSION}/installer" \
    --specpath "build/${PLATFORM}/${VERSION}/installer" \
    src/__main__.py

  echo "  -> dist/${PLATFORM}/${VERSION}/installer/${APP_NAME}/"
}

case "$BUILD_KINDS" in
  portable)
    build_portable
    ;;
  installer)
    build_installer
    ;;
  both)
    build_portable
    build_installer
    ;;
  *)
    echo "ERROR: FS25_CONFIG_TOOL_BUILD_KINDS must be portable, installer, or both (got: ${BUILD_KINDS})"
    exit 1
    ;;
esac

echo
echo "Build complete."
echo
