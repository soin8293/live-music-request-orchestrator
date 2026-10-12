import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from live_music_orchestrator import app, bridge
from live_music_orchestrator.config import Settings, load_configuration


@pytest.fixture
def working_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for key in ("ORCHESTRATOR_PORT", "ORCHESTRATOR_INGEST_TOKEN", "ORCHESTRATOR_INGEST_URL"):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(
        "ORCHESTRATOR_PORT=5057\nORCHESTRATOR_INGEST_TOKEN=synthetic-test-token\n"
        "ORCHESTRATOR_INGEST_URL=http://127.0.0.1:5057/ingest\n",
        encoding="utf-8",
    )


def test_controller_uses_working_directory_env(working_env, monkeypatch):
    fake_app = Mock()
    monkeypatch.setattr(app, "create_app", Mock(return_value=fake_app))
    app.main()
    assert fake_app.run.call_args.kwargs["port"] == 5057
    assert app.create_app.call_args.args[0].ingest_token == "synthetic-test-token"


def test_process_environment_wins(working_env, monkeypatch):
    monkeypatch.setenv("ORCHESTRATOR_PORT", "5060")
    load_configuration()
    assert Settings.from_env().port == 5060


def test_demo_forwards_configured_token(working_env, monkeypatch):
    path = Path(__file__).parents[1] / "scripts" / "send_demo_event.py"
    spec = importlib.util.spec_from_file_location("demo_helper", path)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    post = Mock(return_value=Mock(ok=True, json=lambda: {"status": "ok"}))
    monkeypatch.setattr(demo.requests, "post", post)
    monkeypatch.setattr(sys, "argv", ["demo", "skip"])
    assert demo.main() == 0
    assert post.call_args.args[0] == "http://127.0.0.1:5057/ingest"
    assert post.call_args.kwargs["headers"] == {"X-Ingest-Token": "synthetic-test-token"}


def test_bridge_forwards_same_configuration(working_env, monkeypatch):
    connection = Mock()
    connection.recv.side_effect = [
        json.dumps({"data": {"comment": "!skip", "username": "fixture"}}),
        KeyboardInterrupt(),
    ]
    monkeypatch.setattr(bridge.websocket, "create_connection", Mock(return_value=connection))
    post = Mock(return_value=Mock(json=lambda: {"reason": "ok"}))
    monkeypatch.setattr(bridge.requests, "post", post)
    with pytest.raises(KeyboardInterrupt):
        bridge.main()
    assert post.call_args.args[0] == "http://127.0.0.1:5057/ingest"
    assert post.call_args.kwargs["headers"] == {"X-Ingest-Token": "synthetic-test-token"}
    connection.close.assert_called_once()
