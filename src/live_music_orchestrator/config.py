"""Environment-backed configuration and network-exposure guardrails."""

from __future__ import annotations

import os
from dataclasses import dataclass

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _positive_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 5000
    ingest_token: str = ""
    debounce_seconds: float = 8.0
    max_queue_items: int = 50
    max_request_chars: int = 180

    @property
    def is_loopback(self) -> bool:
        return self.host.strip().lower() in LOOPBACK_HOSTS

    def validate_exposure(self) -> None:
        if not self.is_loopback and not self.ingest_token:
            raise ValueError("A non-loopback ORCHESTRATOR_HOST requires ORCHESTRATOR_INGEST_TOKEN")

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            host=os.getenv("ORCHESTRATOR_HOST", "127.0.0.1").strip(),
            port=_positive_int("ORCHESTRATOR_PORT", 5000),
            ingest_token=os.getenv("ORCHESTRATOR_INGEST_TOKEN", "").strip(),
            debounce_seconds=_positive_float("REQUEST_DEBOUNCE_SECONDS", 8.0),
            max_queue_items=_positive_int("MAX_QUEUE_ITEMS", 50),
            max_request_chars=_positive_int("MAX_REQUEST_CHARS", 180),
        )
