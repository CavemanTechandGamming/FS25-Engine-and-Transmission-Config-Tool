#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# setup_env.sh — create/refresh the local virtual environment (Linux / macOS)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo
echo "=== FS25 Config Tool — environment setup (Unix) ==="
echo "Working directory: $ROOT"
echo

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "ERROR: Python 3 was not found on PATH."
  exit 1
fi

echo "[1/3] Creating virtual environment at .venv ..."
"$PYTHON" -m venv .venv

VENV_PY="$ROOT/.venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: venv python was not created at $VENV_PY"
  exit 1
fi

echo "[2/3] Upgrading pip ..."
"$VENV_PY" -m pip install --upgrade pip

echo "[3/3] Installing dependencies from requirements/requirements.txt ..."
"$VENV_PY" -m pip install -r requirements/requirements.txt

echo
echo "Setup complete. Activate later with:"
echo "  source .venv/bin/activate"
echo
