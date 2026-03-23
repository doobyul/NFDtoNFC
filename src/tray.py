from __future__ import annotations

import os
import sys
import threading
import importlib
from pathlib import Path
from typing import Any

from utils import get_latest_log_file

PILImage = Any


def _resolve_icon_path() -> Path | None:
    candidates: list[Path] = []

    # 1) 실행 위치 기준(외부 교체 가능한 아이콘)
    candidates.append(Path.cwd() / "assets" / "icon.ico")

    # 2) 소스 실행 기준
    candidates.append(Path(__file__).resolve().parents[1] / "assets" / "icon.ico")

    # 3) PyInstaller onefile 번들 경로
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / "icon.ico")

    for path in candidates:
        if path.exists():
            return path
    return None


def _import_tray_deps():
    try:
        pystray = importlib.import_module("pystray")
        Image = importlib.import_module("PIL.Image")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "트레이 의존성(Pillow/pystray) 로드 실패. `pip install -r requirements.txt`를 실행하세요."
        ) from exc

    return pystray, Image


def _load_icon() -> PILImage:
    _pystray, Image = _import_tray_deps()
    icon_path = _resolve_icon_path()
    if icon_path and icon_path.exists():
        # 일부 환경에서 .ico 다중 프레임 해석 이슈가 있어 RGBA 64x64로 고정
        return Image.open(icon_path).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)

    # Pillow 최소 의존을 위해 ImageDraw 없이 단색 fallback 아이콘 생성
    image = Image.new("RGBA", (64, 64), (60, 170, 100, 255))
    return image


class TrayController:
    def __init__(self, app_name: str, watcher, logger, startup_getter, startup_setter):
        pystray, _Image = _import_tray_deps()
        self._pystray = pystray
        self.app_name = app_name
        self.watcher = watcher
        self.logger = logger
        self._startup_getter = startup_getter
        self._startup_setter = startup_setter

        self.icon = self._pystray.Icon(self.app_name, _load_icon(), self.app_name)
        self.icon.menu = self._pystray.Menu(
            self._pystray.MenuItem(self._pause_label, self._toggle_pause),
            self._pystray.MenuItem("지금 전체 검사", self._scan_all),
            self._pystray.MenuItem("최근 로그 보기", self._open_log),
            self._pystray.MenuItem(self._startup_label, self._toggle_startup),
            self._pystray.MenuItem("종료", self._quit),
        )

    def _pause_label(self, _item):
        return "감시 재개" if self.watcher.paused else "감시 일시중지"

    def _startup_label(self, _item):
        return "시작프로그램 해제" if self._startup_getter() else "시작프로그램 등록"

    def _toggle_pause(self, _icon, _item):
        if self.watcher.paused:
            self.watcher.resume()
        else:
            self.watcher.pause()

    def _scan_all(self, _icon, _item):
        threading.Thread(target=self.watcher.scan_all, daemon=True).start()

    def _open_log(self, _icon, _item):
        session_log = getattr(self.logger, "session_log_path", None)
        if session_log:
            session_path = Path(session_log).resolve()
            if session_path.exists():
                os.startfile(str(session_path))
                return

        latest = get_latest_log_file("logs", self.app_name)
        if latest and latest.exists():
            os.startfile(str(latest.resolve()))

    def _toggle_startup(self, _icon, _item):
        enabled = self._startup_getter()
        self._startup_setter(not enabled)
        self.logger.info("시작프로그램 설정: %s", "ON" if not enabled else "OFF")

    def _quit(self, _icon, _item):
        self.watcher.stop()
        self.icon.stop()

    def run(self, on_start=None) -> None:
        def _setup(_icon):
            self.logger.info("트레이 아이콘 초기화 완료")
            self.icon.visible = True
            if on_start:
                threading.Thread(target=on_start, daemon=True).start()

        self.logger.info("트레이 루프 시작")
        self.icon.run(setup=_setup)
