from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path

import winreg


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def setup_logger(log_dir: str | Path = "logs", name: str = "NFDtoNFC") -> logging.Logger:
    ensure_dir(log_dir)
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    log_path = Path(log_dir) / f"{name}-log-{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # 현재 세션 로그 파일 경로를 다른 모듈(tray 등)에서 참조할 수 있도록 저장
    logger.session_log_path = str(log_path)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def is_path_excluded(path: str | Path, root: str | Path, excluded_paths: list[str]) -> bool:
    path_norm = os.path.normcase(os.path.normpath(str(path)))
    root_norm = os.path.normcase(os.path.normpath(str(root)))

    try:
        rel = os.path.relpath(path_norm, root_norm)
    except ValueError:
        return False

    rel_norm = os.path.normcase(os.path.normpath(rel))
    rel_parts = [p for p in rel_norm.split(os.sep) if p not in ("", ".")]

    for excluded in excluded_paths:
        ex_norm = os.path.normcase(os.path.normpath(excluded))
        if os.sep in ex_norm:
            if rel_norm == ex_norm or rel_norm.startswith(ex_norm + os.sep):
                return True
        else:
            if ex_norm in rel_parts:
                return True
    return False


def wait_for_file_stable(path: str | Path, checks: int = 3, interval_sec: float = 0.3) -> bool:
    target = Path(path)
    if not target.exists() or target.is_dir():
        return False

    last_sig: tuple[int, int] | None = None
    stable_count = 0

    for _ in range(max(1, checks) * 4):
        try:
            st = target.stat()
            sig = (st.st_size, st.st_mtime_ns)
        except FileNotFoundError:
            return False

        if sig == last_sig:
            stable_count += 1
            if stable_count >= checks:
                return True
        else:
            stable_count = 0
            last_sig = sig

        time.sleep(interval_sec)

    return False


RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def set_startup(app_name: str, command_line: str, enabled: bool) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command_line)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass


def is_startup_enabled(app_name: str) -> bool:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_QUERY_VALUE) as key:
        try:
            winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False


def tail_log(path: str | Path, max_lines: int = 80) -> str:
    target = Path(path)
    if not target.exists():
        return "로그 파일이 없습니다."

    with target.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    return "".join(lines[-max_lines:]).strip()


def get_latest_log_file(log_dir: str | Path = "logs", name: str = "NFDtoNFC") -> Path | None:
    base = Path(log_dir)
    if not base.exists():
        return None

    candidates = list(base.glob(f"{name}-log-*.log"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)
