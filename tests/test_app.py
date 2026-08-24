from live_music_orchestrator.app import create_app
from live_music_orchestrator.config import Settings


def build_client(*, token: str = ""):
    app = create_app(Settings(ingest_token=token))
    app.config["TESTING"] = True
    return app.test_client()


def request_payload() -> dict[str, str]:
    return {
        "event_type": "CHAT_COMMAND",
        "action": "request",
        "username": "demo_viewer",
        "nickname": "Demo Viewer",
        "command_params": "Neon Skyline - Demo Artist",
        "source": "test",
    }


def test_health_and_initial_state() -> None:
    client = build_client()
    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["mode"] == "synthetic"
    assert client.get("/api/state").get_json()["queue_length"] == 0


def test_ingest_updates_state() -> None:
    client = build_client()
    response = client.post("/ingest", json=request_payload())
    assert response.status_code == 200
    assert response.get_json()["reason"] == "accepted"
    assert client.get("/api/state").get_json()["current_track"]["title"] == "Neon Skyline"


def test_configured_token_is_required_for_mutation() -> None:
    client = build_client(token="correct-horse-battery-staple")
    assert client.post("/ingest", json=request_payload()).status_code == 403
    response = client.post(
        "/ingest",
        json=request_payload(),
        headers={"X-Ingest-Token": "correct-horse-battery-staple"},
    )
    assert response.status_code == 200


def test_invalid_payload_is_safe_400() -> None:
    client = build_client()
    response = client.post("/ingest", json={"action": "request"})
    assert response.status_code == 400
    assert response.get_json()["reason"] == "username_required"


def test_reset_is_post_only_and_clears_state() -> None:
    client = build_client()
    client.post("/ingest", json=request_payload())
    assert client.get("/api/reset").status_code == 405
    assert client.post("/api/reset", json={}).get_json()["reason"] == "reset"
    assert client.get("/api/state").get_json()["current_track"] is None


def test_security_headers_cover_overlay() -> None:
    response = build_client().get("/")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
