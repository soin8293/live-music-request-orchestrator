"""Flask application and live browser event stream."""

from __future__ import annotations

import hmac
import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request, send_from_directory, stream_with_context

from . import __version__
from .config import LOOPBACK_HOSTS, Settings
from .events import EventHub
from .ingress import IngressError, normalize_payload
from .store import QueueStore

logger = logging.getLogger("live-music-orchestrator")
WEB_ROOT = Path(__file__).resolve().parent / "web"


def create_app(settings: Settings | None = None, store: QueueStore | None = None) -> Flask:
    settings = settings or Settings.from_env()
    settings.validate_exposure()
    store = store or QueueStore(
        max_queue_items=settings.max_queue_items,
        debounce_seconds=settings.debounce_seconds,
    )

    app = Flask(__name__, static_folder=None)
    app.config.update(MAX_CONTENT_LENGTH=32 * 1024, JSON_SORT_KEYS=True)
    event_hub = EventHub()
    app.extensions["orchestrator.settings"] = settings
    app.extensions["orchestrator.store"] = store
    app.extensions["orchestrator.events"] = event_hub

    def mutation_allowed() -> bool:
        supplied = request.headers.get("X-Ingest-Token", "")
        if settings.ingest_token:
            return hmac.compare_digest(supplied, settings.ingest_token)
        return (request.remote_addr or "").casefold() in LOOPBACK_HOSTS

    def broadcast() -> None:
        event_hub.publish(store.snapshot())

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'; "
            "script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'"
        )
        if request.path.startswith("/api/") or request.path == "/health":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return send_from_directory(WEB_ROOT, "index.html")

    @app.get("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(WEB_ROOT, filename)

    @app.get("/health")
    def health():
        snapshot = store.snapshot()
        return jsonify(
            {
                "status": "ok",
                "version": __version__,
                "mode": snapshot["mode"],
                "revision": snapshot["revision"],
                "queue_length": snapshot["queue_length"],
            }
        )

    @app.get("/api/state")
    def state():
        return jsonify(store.snapshot())

    @app.get("/events")
    def events():
        response = Response(
            stream_with_context(event_hub.stream(store.snapshot())),
            mimetype="text/event-stream",
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"
        return response

    @app.post("/ingest")
    def ingest():
        if not mutation_allowed():
            abort(403)
        try:
            command = normalize_payload(
                request.get_json(silent=True), max_request_chars=settings.max_request_chars
            )
        except IngressError as exc:
            return jsonify({"status": "error", "reason": exc.code.value}), 400

        if command.action == "request":
            result = store.request(command)
        elif command.action == "skip":
            result = store.skip()
        else:
            result = store.set_source_status(command.source, bool(command.connected))

        logger.info(
            "event action=%s source=%s result=%s queue_length=%d",
            command.action,
            command.source,
            result.get("reason"),
            store.snapshot()["queue_length"],
        )
        if result.get("status") == "ok":
            broadcast()
        return jsonify(result)

    @app.post("/api/reset")
    def reset():
        if not mutation_allowed():
            abort(403)
        result = store.reset()
        broadcast()
        logger.info("event action=reset result=reset queue_length=0")
        return jsonify(result)

    return app


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = Settings.from_env()
    settings.validate_exposure()
    app = create_app(settings)
    logger.info("Starting local controller at http://%s:%d", settings.host, settings.port)
    app.run(host=settings.host, port=settings.port, threaded=True)


if __name__ == "__main__":
    main()
