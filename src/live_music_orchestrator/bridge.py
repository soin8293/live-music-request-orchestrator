"""Optional local TikFinity WebSocket-to-HTTP bridge."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests
import websocket
from dotenv import load_dotenv

logger = logging.getLogger("live-music-bridge")


def _first_text(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def command_payload(event: dict[str, Any]) -> dict[str, object] | None:
    data = event.get("data") if isinstance(event.get("data"), dict) else event
    comment = _first_text(data, "comment", "commentText", "message", "text", "content")
    lowered = comment.casefold()
    if lowered.startswith(("!play ", "play ", "!request ", "request ")):
        prefix = next(
            item
            for item in ("!request ", "request ", "!play ", "play ")
            if lowered.startswith(item)
        )
        action = "request"
        query = comment[len(prefix) :].strip()
    elif lowered in {"!skip", "skip"}:
        action = "skip"
        query = ""
    else:
        return None

    username = _first_text(data, "username", "uniqueId")
    nickname = _first_text(data, "nickname", "displayName") or username
    if not username:
        return None
    return {
        "event_type": "CHAT_COMMAND",
        "action": action,
        "username": username[:64],
        "nickname": nickname[:80],
        "command_params": query[:180],
        "source": "tikfinity_local_bridge",
    }


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ws_url = os.getenv("TIKFINITY_WS_URL", "ws://127.0.0.1:21213/")
    ingest_url = os.getenv("ORCHESTRATOR_INGEST_URL", "http://127.0.0.1:5000/ingest")
    token = os.getenv("ORCHESTRATOR_INGEST_TOKEN", "").strip()
    reconnect = int(os.getenv("BRIDGE_RECONNECT_SECONDS", "3"))
    headers = {"X-Ingest-Token": token} if token else {}

    while True:
        connection = None
        try:
            logger.info("Connecting to local event bridge")
            connection = websocket.create_connection(ws_url, timeout=20)
            logger.info("Local event bridge connected")
            while True:
                try:
                    raw = connection.recv()
                except websocket.WebSocketTimeoutException:
                    continue
                event = json.loads(raw)
                payload = command_payload(event)
                if payload is None:
                    continue
                response = requests.post(ingest_url, json=payload, headers=headers, timeout=5)
                response.raise_for_status()
                reason = response.json().get("reason", "unknown")
                logger.info("Forwarded recognized command result=%s", reason)
        except (
            OSError,
            ValueError,
            requests.RequestException,
            websocket.WebSocketException,
        ) as exc:
            logger.warning("Local bridge unavailable; retrying: %s", type(exc).__name__)
            time.sleep(reconnect)
        finally:
            if connection is not None:
                try:
                    connection.close()
                except websocket.WebSocketException:
                    pass


if __name__ == "__main__":
    main()
