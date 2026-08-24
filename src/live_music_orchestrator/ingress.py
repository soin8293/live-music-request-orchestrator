"""Normalize multiple external payload shapes before state mutation."""

from __future__ import annotations

from typing import Any

from .models import NormalizedCommand


class IngressError(ValueError):
    """A public, safe validation error for an inbound event."""


def _bounded(value: Any, *, field: str, maximum: int, required: bool = False) -> str:
    text = " ".join(str(value or "").split())
    if required and not text:
        raise IngressError(f"{field} is required")
    if len(text) > maximum:
        raise IngressError(f"{field} exceeds {maximum} characters")
    return text


def _command_from_comment(comment: str) -> tuple[str, str]:
    lowered = comment.casefold()
    for prefix in ("!request ", "request ", "!play ", "play "):
        if lowered.startswith(prefix):
            return "request", comment[len(prefix) :].strip()
    if lowered in {"!skip", "skip"}:
        return "skip", ""
    return "", ""


def normalize_payload(payload: Any, *, max_request_chars: int = 180) -> NormalizedCommand:
    if not isinstance(payload, dict):
        raise IngressError("JSON object required")

    event_type = _bounded(
        payload.get("event_type") or payload.get("type"), field="event_type", maximum=40
    ).upper()
    source = _bounded(payload.get("source") or "unknown", field="source", maximum=40)

    if event_type == "CONNECTION_STATUS_UPDATE":
        return NormalizedCommand(
            action="status",
            username="system",
            nickname="System",
            query="",
            source=source,
            connected=bool(payload.get("connected")),
        )

    username = _bounded(
        payload.get("username") or payload.get("uniqueId") or payload.get("requester_username"),
        field="username",
        maximum=64,
    )
    nickname = _bounded(
        payload.get("nickname")
        or payload.get("displayName")
        or payload.get("requester_nickname")
        or username,
        field="nickname",
        maximum=80,
    )
    raw_action = _bounded(payload.get("action"), field="action", maximum=32).casefold()
    query = _bounded(
        payload.get("command_params") or payload.get("commandParams"),
        field="command_params",
        maximum=max_request_chars,
    )
    comment = _bounded(
        payload.get("comment")
        or payload.get("commentText")
        or payload.get("message")
        or payload.get("text"),
        field="comment",
        maximum=max_request_chars + 16,
    )

    action = ""
    if raw_action in {"request", "song_request", "play"}:
        action = "request"
    elif raw_action == "skip":
        action = "skip"
    elif comment:
        action, parsed_query = _command_from_comment(comment)
        query = query or parsed_query

    if action not in {"request", "skip"}:
        raise IngressError("recognized request or skip action required")

    username = _bounded(username, field="username", maximum=64, required=True)
    nickname = nickname or username

    if action == "request":
        query = _bounded(query, field="command_params", maximum=max_request_chars, required=True)
    else:
        query = ""

    return NormalizedCommand(
        action=action,
        username=username,
        nickname=nickname,
        query=query,
        source=source,
    )
