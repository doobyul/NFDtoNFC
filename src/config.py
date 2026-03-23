from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(slots=True)
class AppConfig:
    watch_roots: List[str]
    recursive: bool
    process_directories: bool
    debounce_ms: int
    retry_count: int
    retry_delay_ms: int
    conflict_mode: str
    excluded_paths: List[str]


DEFAULT_CONFIG_RELATIVE = Path("config/config.default.json")


def _app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _resolve_default_config_path() -> Path:
    # 1) 실행 파일(또는 프로젝트 루트) 기준 외부 설정 파일 우선
    external = _app_base_dir() / DEFAULT_CONFIG_RELATIVE
    if external.exists():
        return external

    # 2) PyInstaller onefile로 실행 시 번들 데이터(_MEIPASS) 경로
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundled = Path(meipass) / DEFAULT_CONFIG_RELATIVE
        if bundled.exists():
            return bundled

    # 3) 소스 실행 기준 폴백
    return DEFAULT_CONFIG_RELATIVE


def _expand_env_path(path_value: str) -> str:
    expanded = os.path.expandvars(path_value)
    return os.path.normpath(expanded)


def _load_dict(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config(config_path: str | Path | None = None) -> AppConfig:
    target = Path(config_path) if config_path else _resolve_default_config_path()
    raw = _load_dict(target)

    watch_roots = [_expand_env_path(p) for p in raw.get("watch_roots", ["%USERPROFILE%"])]

    return AppConfig(
        watch_roots=watch_roots,
        recursive=bool(raw.get("recursive", True)),
        process_directories=bool(raw.get("process_directories", False)),
        debounce_ms=int(raw.get("debounce_ms", 1000)),
        retry_count=int(raw.get("retry_count", 5)),
        retry_delay_ms=int(raw.get("retry_delay_ms", 700)),
        conflict_mode=str(raw.get("conflict_mode", "skip")).lower(),
        excluded_paths=[os.path.normpath(p) for p in raw.get("excluded_paths", [])],
    )
