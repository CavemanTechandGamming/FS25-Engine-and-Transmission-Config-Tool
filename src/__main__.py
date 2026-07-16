#!/usr/bin/env python3
"""
FS25 Engine and Transmission Config Tool — package entry point.

Usage (from repository root):
    python -m src
"""

from src.ui.app import run_app


def main() -> None:
    run_app()


if __name__ == "__main__":
    main()
