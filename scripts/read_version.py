#!/usr/bin/env python3
"""
Print the application version from ``src/__init__.py``.

That file is the single source of truth — do not hard-code the version elsewhere.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "src" / "__init__.py"


def read_version() -> str:
    text = INIT_FILE.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise SystemExit(f"Could not find __version__ in {INIT_FILE}")
    return match.group(1)


if __name__ == "__main__":
    sys.stdout.write(read_version())
