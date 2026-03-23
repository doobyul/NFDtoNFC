from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from normalizer import to_nfc


@dataclass(slots=True)
class RenameResult:
    status: str
    src: str
    dst: str | None = None
    reason: str | None = None


class NormalizationRenamer:
    def __init__(self, retry_count: int, retry_delay_ms: int, conflict_mode: str, logger):
        self.retry_count = max(0, retry_count)
        self.retry_delay = max(0, retry_delay_ms) / 1000.0
        self.conflict_mode = conflict_mode
        self.logger = logger
        self._ignore_lock = threading.Lock()
        self._ignore_events: dict[str, float] = {}

    def should_ignore_event(self, path: str | Path) -> bool:
        key = os.path.normcase(os.path.normpath(str(path)))
        now = time.time()
        with self._ignore_lock:
            expired = [k for k, v in self._ignore_events.items() if v < now]
            for k in expired:
                self._ignore_events.pop(k, None)
            return key in self._ignore_events

    def _mark_ignored(self, path: str | Path, ttl_sec: float = 2.5) -> None:
        key = os.path.normcase(os.path.normpath(str(path)))
        with self._ignore_lock:
            self._ignore_events[key] = time.time() + ttl_sec

    def normalize_path(self, path: str | Path, is_dir: bool = False) -> RenameResult:
        target = Path(path)
        source_name = target.name
        normalized_name = to_nfc(source_name)

        if source_name == normalized_name:
            return RenameResult(status="skipped", src=str(target), reason="already_nfc")

        destination = target.with_name(normalized_name)

        if destination.exists():
            msg = f"충돌로 스킵: {target} -> {destination}"
            self.logger.warning(msg)
            return RenameResult(status="conflict", src=str(target), dst=str(destination), reason="exists")

        attempts = self.retry_count + 1
        for attempt in range(attempts):
            try:
                target.rename(destination)
                self._mark_ignored(target)
                self._mark_ignored(destination)
                self.logger.info("RENAMED | %s -> %s", target, destination)
                return RenameResult(status="renamed", src=str(target), dst=str(destination))
            except FileNotFoundError:
                return RenameResult(status="missing", src=str(target), reason="not_found")
            except OSError as exc:
                if attempt >= attempts - 1:
                    self.logger.error("리네임 실패 | %s -> %s | %s", target, destination, exc)
                    return RenameResult(
                        status="error",
                        src=str(target),
                        dst=str(destination),
                        reason=str(exc),
                    )
                time.sleep(self.retry_delay)

        return RenameResult(status="error", src=str(target), dst=str(destination), reason="unknown")
