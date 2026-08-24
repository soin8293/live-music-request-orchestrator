from live_music_orchestrator.bridge import command_payload


def test_bridge_extracts_supported_command() -> None:
    payload = command_payload(
        {
            "event": "chat",
            "data": {
                "comment": "!play Neon Skyline - Demo Artist",
                "username": "viewer",
                "nickname": "Viewer",
            },
        }
    )
    assert payload is not None
    assert payload["action"] == "request"
    assert payload["command_params"] == "Neon Skyline - Demo Artist"


def test_bridge_ignores_non_command_and_missing_identity() -> None:
    assert command_payload({"data": {"comment": "hello", "username": "viewer"}}) is None
    assert command_payload({"data": {"comment": "!play Song"}}) is None
