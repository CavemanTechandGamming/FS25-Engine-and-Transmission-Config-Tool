#!/usr/bin/env python3
"""Fail loudly if a built/staged binary is the wrong file or suspiciously small.

Usage:
  python scripts/verify_release_binary.py PATH --kind windows-exe|windows-setup|macos|linux
      [--expect-name BASENAME] [--min-bytes N]

Catches mistakes like shipping a few-hundred-byte stub instead of a real
PyInstaller onefile binary.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# PyInstaller + CustomTkinter onefile builds are typically tens of MB.
DEFAULT_MIN_BYTES = int(os.environ.get("FS25_CONFIG_TOOL_MIN_BINARY_BYTES", "5242880"))

REJECT_SUFFIXES = {
    ".txt",
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".spec",
    ".toc",
    ".py",
    ".sh",
    ".bat",
    ".html",
    ".xml",
    ".log",
    ".zip",
}


def die(msg: str, code: int = 1) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    raise SystemExit(code)


def read_magic(path: Path, n: int = 4) -> bytes:
    with path.open("rb") as fh:
        return fh.read(n)


def looks_like_text(sample: bytes) -> bool:
    if not sample:
        return True
    # NUL in first chunk usually means binary; absence + high ASCII ratio → text
    if b"\x00" in sample:
        return False
    text_chars = sum(1 for b in sample if 9 <= b <= 13 or 32 <= b <= 126)
    return (text_chars / len(sample)) > 0.85


def verify(
    path: Path,
    kind: str,
    expect_name: str | None,
    min_bytes: int,
) -> None:
    if not path.exists():
        die(f"Binary path does not exist: {path}")
    if not path.is_file():
        die(f"Expected a regular file, got something else: {path}")
    if path.is_symlink():
        die(f"Refusing to ship a symlink: {path}")

    if expect_name and path.name != expect_name:
        die(f"Binary basename mismatch. Expected '{expect_name}', got '{path.name}'")

    if path.suffix.lower() in REJECT_SUFFIXES:
        die(f"Refusing file that looks like a document/archive, not a binary: {path.name}")

    size = path.stat().st_size
    print(f"Binary: {path}")
    print(f"Size:   {size} bytes (minimum required: {min_bytes})")

    if size < min_bytes:
        head = read_magic(path, min(200, size))
        die(
            f"Binary is only {size} bytes — far too small for a PyInstaller build "
            f"(need >= {min_bytes}). Likely the wrong file was selected. "
            f"Head={head!r}"
        )

    magic = read_magic(path, 4)
    sample = read_magic(path, min(512, size))
    if looks_like_text(sample):
        die(f"File content looks like text, not an executable: {path.name}")

    if kind in {"windows-exe", "windows-setup"}:
        if magic[:2] != b"MZ":
            die(f"Expected a Windows PE executable (MZ header). Magic={magic!r}")
        if kind == "windows-setup" and not path.name.endswith("-Setup.exe"):
            die(f"Windows setup binary name must end with '-Setup.exe' (got '{path.name}')")
    elif kind == "linux":
        if magic != b"\x7fELF":
            die(f"Expected a Linux ELF binary. Magic={magic!r}")
    elif kind == "macos":
        # Mach-O thin + fat magic numbers
        macho_magics = {
            b"\xfe\xed\xfa\xce",  # MH_MAGIC
            b"\xce\xfa\xed\xfe",  # MH_CIGAM
            b"\xfe\xed\xfa\xcf",  # MH_MAGIC_64
            b"\xcf\xfa\xed\xfe",  # MH_CIGAM_64
            b"\xca\xfe\xba\xbe",  # FAT_MAGIC
            b"\xbe\xba\xfe\xca",  # FAT_CIGAM
            b"\xca\xfe\xba\xbf",  # FAT_MAGIC_64
            b"\xbf\xba\xfe\xca",  # FAT_CIGAM_64
        }
        if magic not in macho_magics:
            die(f"Expected a macOS Mach-O binary. Magic={magic!r}")
    else:
        die(f"Unknown kind '{kind}'", code=2)

    print("Binary verification passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--kind",
        required=True,
        choices=("windows-exe", "windows-setup", "macos", "linux"),
    )
    parser.add_argument("--expect-name", default=None)
    parser.add_argument("--min-bytes", type=int, default=DEFAULT_MIN_BYTES)
    args = parser.parse_args()
    verify(args.path, args.kind, args.expect_name, args.min_bytes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
