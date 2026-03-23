from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from config import load_config
from renamer import NormalizationRenamer
from utils import is_startup_enabled, set_startup, setup_logger
from version import get_version_label


APP_NAME = "NFDtoNFC"


def _startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}"'

    script_path = Path(__file__).resolve()
    return f'"{Path(sys.executable).resolve()}" "{script_path}"'


def main() -> int:
    parser = argparse.ArgumentParser(description="NFD 한글 파일명을 NFC로 자동 복구")
    parser.add_argument("--config", type=str, default=None, help="설정 파일 경로")
    parser.add_argument("--scan-now", action="store_true", help="시작 시 전체 검사 1회 수행")
    parser.add_argument("--no-tray", action="store_true", help="트레이 없이 콘솔 모드로 실행")
    args = parser.parse_args()

    logger = setup_logger("logs", APP_NAME)
    version_label = get_version_label()
    logger.info("%s 시작 (%s)", APP_NAME, version_label)
    cfg = load_config(args.config)

    renamer = NormalizationRenamer(
        retry_count=cfg.retry_count,
        retry_delay_ms=cfg.retry_delay_ms,
        conflict_mode=cfg.conflict_mode,
        logger=logger,
    )
    try:
        from watcher import FileWatcher
    except ModuleNotFoundError as exc:
        logger.error(
            "감시 모듈 로드 실패: %s. `pip install -r requirements.txt` 후 다시 실행하세요.",
            exc,
        )
        return 1

    watcher = FileWatcher(cfg, renamer, logger)

    def startup_getter() -> bool:
        return is_startup_enabled(APP_NAME)

    def startup_setter(enabled: bool) -> None:
        set_startup(APP_NAME, _startup_command(), enabled)

    try:
        if args.no_tray:
            watcher.start()
            if args.scan_now:
                watcher.scan_all()
            logger.info("콘솔 모드 실행 중. 종료하려면 Ctrl+C")
            while True:
                time.sleep(1)
        else:
            try:
                from tray import TrayController
            except ModuleNotFoundError as exc:
                logger.error(
                    "트레이 모듈 로드 실패: %s. `pip install -r requirements.txt` 후 다시 실행하세요.",
                    exc,
                )
                return 1

            def _on_tray_start() -> None:
                watcher.start()
                if args.scan_now:
                    watcher.scan_all()

            tray = TrayController(APP_NAME, watcher, logger, startup_getter, startup_setter)
            tray.run(on_start=_on_tray_start)
        return 0
    except KeyboardInterrupt:
        logger.info("사용자 중단")
        return 0
    except Exception:
        logger.exception("치명적 오류")
        return 1
    finally:
        try:
            watcher.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
