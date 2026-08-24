"""Thread-safe canonical queue state and invariants."""

from __future__ import annotations

import re
import threading
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from .catalog import SyntheticCatalog
from .models import NormalizedCommand, QueueItem

_WHITESPACE = re.compile(r"\s+")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _norm(value: str) -> str:
    return _WHITESPACE.sub(" ", value).strip().casefold()


class QueueStore:
    def __init__(
        self,
        *,
        max_queue_items: int = 50,
        debounce_seconds: float = 8.0,
        catalog: SyntheticCatalog | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_queue_items = max_queue_items
        self.debounce_seconds = debounce_seconds
        self.catalog = catalog or SyntheticCatalog()
        self.clock = clock
        self._lock = threading.RLock()
        self._recent: dict[tuple[str, str], float] = {}
        self._current: QueueItem | None = None
        self._queue: list[QueueItem] = []
        self._sources: dict[str, bool] = {}
        self._revision = 0

    def request(self, command: NormalizedCommand) -> dict[str, object]:
        query_key = _norm(command.query)
        user_key = _norm(command.username)
        now = self.clock()
        with self._lock:
            self._expire_recent(now)
            debounce_key = (user_key, query_key)
            previous = self._recent.get(debounce_key)
            if previous is not None and now - previous < self.debounce_seconds:
                return self._result("ignored", "debounced")
            self._recent[debounce_key] = now

            active_queries = []
            if self._current:
                active_queries.append(_norm(self._current.request_text))
            active_queries.extend(_norm(item.request_text) for item in self._queue)
            if query_key in active_queries:
                return self._result("ignored", "already_queued")

            if len(self._queue) >= self.max_queue_items:
                return self._result("ignored", "queue_full")

            track = self.catalog.resolve(command.query)
            item = QueueItem(
                request_id=uuid.uuid4().hex,
                track_id=track.track_id,
                title=track.title,
                artist=track.artist,
                duration_ms=track.duration_ms,
                color_start=track.color_start,
                color_end=track.color_end,
                requested_by=command.username,
                requester_name=command.nickname,
                request_text=command.query,
                source=command.source,
                requested_at=_now_iso(),
            )
            if self._current is None:
                item.is_playing = True
                self._current = item
            else:
                self._queue.append(item)
            self._revision += 1
            return {
                "status": "ok",
                "reason": "accepted",
                "item": item.to_dict(),
                "revision": self._revision,
            }

    def skip(self) -> dict[str, object]:
        with self._lock:
            if self._current is None:
                return self._result("ignored", "nothing_playing")
            skipped = self._current
            skipped.is_playing = False
            self._current = self._queue.pop(0) if self._queue else None
            if self._current:
                self._current.is_playing = True
                self._current.progress_ms = 0
            self._revision += 1
            return {
                "status": "ok",
                "reason": "skipped",
                "skipped_request_id": skipped.request_id,
                "revision": self._revision,
            }

    def reset(self) -> dict[str, object]:
        with self._lock:
            self._current = None
            self._queue.clear()
            self._recent.clear()
            self._revision += 1
            return self._result("ok", "reset")

    def set_source_status(self, source: str, connected: bool) -> dict[str, object]:
        with self._lock:
            self._sources[_norm(source) or "unknown"] = connected
            self._revision += 1
            return self._result("ok", "source_status_updated")

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "revision": self._revision,
                "mode": "synthetic",
                "current_track": self._current.to_dict() if self._current else None,
                "queue": [item.to_dict() for item in self._queue],
                "queue_length": len(self._queue),
                "source_status": dict(self._sources),
                "limits": {
                    "max_queue_items": self.max_queue_items,
                    "debounce_seconds": self.debounce_seconds,
                },
            }

    def _result(self, status: str, reason: str) -> dict[str, object]:
        return {"status": status, "reason": reason, "revision": self._revision}

    def _expire_recent(self, now: float) -> None:
        cutoff = now - self.debounce_seconds
        expired = [key for key, timestamp in self._recent.items() if timestamp <= cutoff]
        for key in expired:
            self._recent.pop(key, None)
