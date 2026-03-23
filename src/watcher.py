from __future__ import annotations

import os
import threading
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler, FileMovedEvent
from watchdog.observers import Observer

from config import AppConfig
from normalizer import needs_normalization
from renamer import NormalizationRenamer
from utils import is_path_excluded, wait_for_file_stable


class _NFDHandler(FileSystemEventHandler):
    def __init__(self, watcher: "FileWatcher"):
        super().__init__()
        self.watcher = watcher

    def on_created(self, event: FileSystemEvent) -> None:
        self.watcher.schedule(event.src_path, event.is_directory)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.watcher.schedule(event.src_path, event.is_directory)

    def on_moved(self, event: FileMovedEvent) -> None:
        self.watcher.schedule(event.dest_path, event.is_directory)


class FileWatcher:
    def __init__(self, config: AppConfig, renamer: NormalizationRenamer, logger):
        self.config = config
        self.renamer = renamer
        self.logger = logger
        self.observer = Observer()
        self.handler = _NFDHandler(self)
        self._lock = threading.Lock()
        self._timers: dict[str, threading.Timer] = {}
        self._paused = False

    def start(self) -> None:
        for root in self.config.watch_roots:
            if not Path(root).exists():
                self.logger.warning("감시 경로 없음: %s", root)
                continue
            self.observer.schedule(self.handler, root, recursive=self.config.recursive)
            self.logger.info("감시 시작: %s", root)
        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(timeout=5)
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()

    def pause(self) -> None:
        self._paused = True
        self.logger.info("감시 일시중지")

    def resume(self) -> None:
        self._paused = False
        self.logger.info("감시 재개")

    @property
    def paused(self) -> bool:
        return self._paused

    def _get_root_for(self, path: str) -> str | None:
        path_norm = os.path.normcase(os.path.normpath(path))
        for root in self.config.watch_roots:
            root_norm = os.path.normcase(os.path.normpath(root))
            if path_norm == root_norm or path_norm.startswith(root_norm + os.sep):
                return root
        return None

    def schedule(self, path: str, is_directory: bool) -> None:
        if self._paused:
            return

        root = self._get_root_for(path)
        if root is None:
            return

        if is_path_excluded(path, root, self.config.excluded_paths):
            return

        if is_directory and not self.config.process_directories:
            return

        if self.renamer.should_ignore_event(path):
            return

        key = os.path.normcase(os.path.normpath(path))
        delay = max(0, self.config.debounce_ms) / 1000.0

        with self._lock:
            old = self._timers.get(key)
            if old:
                old.cancel()

            timer = threading.Timer(delay, self._process_path, args=(path, is_directory))
            timer.daemon = True
            self._timers[key] = timer
            timer.start()

    def _process_path(self, path: str, is_directory: bool) -> None:
        key = os.path.normcase(os.path.normpath(path))
        with self._lock:
            self._timers.pop(key, None)

        target = Path(path)
        if not target.exists():
            return

        if target.is_dir() and not self.config.process_directories:
            return

        # 파일명이 이미 NFC면 무거운 안정화 체크/리네임 로직을 생략
        # (대용량 일반 파일 로그 노이즈 감소 목적)
        if target.is_file() and not needs_normalization(target.name):
            return

        if target.is_file() and not wait_for_file_stable(target):
            self.logger.info("파일 안정화 실패로 스킵: %s", target)
            return

        result = self.renamer.normalize_path(target, is_dir=is_directory)
        if result.status == "renamed":
            self.logger.info("정규화 완료: %s -> %s", result.src, result.dst)

    def scan_all(self) -> None:
        self.logger.info("전체 검사 시작")
        for root in self.config.watch_roots:
            base = Path(root)
            if not base.exists():
                continue

            for current_root, dirs, files in os.walk(base):
                if is_path_excluded(current_root, base, self.config.excluded_paths):
                    dirs[:] = []
                    continue

                if self.config.process_directories:
                    self._process_path(current_root, is_directory=True)

                for filename in files:
                    full = os.path.join(current_root, filename)
                    self._process_path(full, is_directory=False)

        self.logger.info("전체 검사 종료")
