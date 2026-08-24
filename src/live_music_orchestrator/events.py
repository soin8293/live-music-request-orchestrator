"""Small in-process fan-out for browser server-sent events."""

from __future__ import annotations

import json
import queue
import threading
from collections.abc import Iterator


class EventHub:
    def __init__(self, *, subscriber_queue_size: int = 4) -> None:
        self.subscriber_queue_size = subscriber_queue_size
        self._lock = threading.Lock()
        self._subscribers: set[queue.Queue[str]] = set()

    def publish(self, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        with self._lock:
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(encoded)
            except queue.Full:
                try:
                    subscriber.get_nowait()
                except queue.Empty:
                    pass
                subscriber.put_nowait(encoded)

    def stream(self, initial: dict[str, object]) -> Iterator[str]:
        subscriber: queue.Queue[str] = queue.Queue(maxsize=self.subscriber_queue_size)
        with self._lock:
            self._subscribers.add(subscriber)
        try:
            yield self._format(initial)
            while True:
                try:
                    payload = subscriber.get(timeout=15)
                    yield f"event: state\ndata: {payload}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            with self._lock:
                self._subscribers.discard(subscriber)

    @staticmethod
    def _format(payload: dict[str, object]) -> str:
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        return f"event: state\ndata: {encoded}\n\n"
