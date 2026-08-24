"""Typed internal contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Action = Literal["request", "skip", "status"]


@dataclass(frozen=True)
class NormalizedCommand:
    action: Action
    username: str
    nickname: str
    query: str
    source: str
    connected: bool | None = None


@dataclass(frozen=True)
class ResolvedTrack:
    track_id: str
    title: str
    artist: str
    duration_ms: int
    color_start: str
    color_end: str


@dataclass
class QueueItem:
    request_id: str
    track_id: str
    title: str
    artist: str
    duration_ms: int
    color_start: str
    color_end: str
    requested_by: str
    requester_name: str
    request_text: str
    source: str
    requested_at: str
    progress_ms: int = 0
    is_playing: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
