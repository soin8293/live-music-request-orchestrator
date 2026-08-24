import json

from live_music_orchestrator.events import EventHub


def event_data(frame: str) -> dict[str, object]:
    line = next(line for line in frame.splitlines() if line.startswith("data: "))
    return json.loads(line.removeprefix("data: "))


def test_stream_starts_with_canonical_state_and_receives_updates() -> None:
    hub = EventHub()
    stream = hub.stream({"revision": 1})
    assert event_data(next(stream)) == {"revision": 1}

    hub.publish({"revision": 2, "queue_length": 1})
    assert event_data(next(stream)) == {"revision": 2, "queue_length": 1}
    stream.close()


def test_slow_subscriber_keeps_latest_update() -> None:
    hub = EventHub(subscriber_queue_size=1)
    stream = hub.stream({"revision": 0})
    next(stream)
    hub.publish({"revision": 1})
    hub.publish({"revision": 2})
    assert event_data(next(stream)) == {"revision": 2}
    stream.close()
