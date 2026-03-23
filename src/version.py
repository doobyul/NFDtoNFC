from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def _resolve_meta_path(filename: str) -> Path:
    external = Path.cwd() / filename
    if external.exists():
        return external

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundled = Path(meipass) / filename
        if bundled.exists():
            return bundled

    return BASE_DIR / filename


def _read_text(path: Path, default: str) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return default


def get_version() -> str:
    return _read_text(_resolve_meta_path("VERSION"), "0.0.0")


def get_build_number() -> str:
    return _read_text(_resolve_meta_path("BUILD_NUMBER"), "0")


def get_version_label() -> str:
    return f"v{get_version()}-b{get_build_number()}"
