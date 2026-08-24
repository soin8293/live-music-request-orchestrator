import pytest

from live_music_orchestrator.ingress import IngressError, normalize_payload


def test_normalizes_camel_case_request() -> None:
    command = normalize_payload(
        {
            "type": "CHAT_COMMAND",
            "action": "play",
            "username": "viewer_one",
            "displayName": "Viewer One",
            "commandParams": "Neon Skyline - Demo Artist",
            "source": "connector",
        }
    )

    assert command.action == "request"
    assert command.nickname == "Viewer One"
    assert command.query == "Neon Skyline - Demo Artist"


def test_normalizes_raw_comment_command() -> None:
    command = normalize_payload(
        {"comment": "!request Quiet Circuit - Demo Artist", "username": "viewer"}
    )
    assert command.action == "request"
    assert command.query == "Quiet Circuit - Demo Artist"


def test_normalizes_status_without_user() -> None:
    command = normalize_payload(
        {"type": "CONNECTION_STATUS_UPDATE", "source": "bridge", "connected": True}
    )
    assert command.action == "status"
    assert command.connected is True


@pytest.mark.parametrize(
    "payload, code",
    [
        ({}, "recognized_action_required"),
        ({"action": "request", "command_params": "song"}, "username_required"),
        (
            {"action": "request", "username": "viewer", "command_params": "x" * 181},
            "command_params_too_long",
        ),
    ],
)
def test_rejects_invalid_payloads(payload: dict, code: str) -> None:
    with pytest.raises(IngressError) as exc_info:
        normalize_payload(payload)
    assert exc_info.value.code.value == code
