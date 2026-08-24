from live_music_orchestrator.models import NormalizedCommand
from live_music_orchestrator.store import QueueStore


class Clock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value


def command(user: str, query: str) -> NormalizedCommand:
    return NormalizedCommand(
        action="request",
        username=user,
        nickname=user,
        query=query,
        source="test",
    )


def test_first_request_becomes_current_and_second_is_queued() -> None:
    store = QueueStore()
    assert store.request(command("one", "First Song"))["status"] == "ok"
    assert store.request(command("two", "Second Song"))["status"] == "ok"

    snapshot = store.snapshot()
    assert snapshot["current_track"]["title"] == "First Song"
    assert snapshot["queue_length"] == 1


def test_debounces_same_user_and_query() -> None:
    clock = Clock()
    store = QueueStore(clock=clock, debounce_seconds=8)
    store.request(command("viewer", "Same Song"))
    result = store.request(command("viewer", "Same Song"))
    assert result == {"status": "ignored", "reason": "debounced", "revision": 1}


def test_rejects_same_active_query_from_another_user() -> None:
    store = QueueStore()
    store.request(command("one", "Same Song"))
    result = store.request(command("two", "  same   song  "))
    assert result["reason"] == "already_queued"


def test_queue_capacity_is_bounded() -> None:
    store = QueueStore(max_queue_items=1)
    store.request(command("one", "Current"))
    store.request(command("two", "Queued"))
    result = store.request(command("three", "Rejected"))
    assert result["reason"] == "queue_full"


def test_skip_advances_queue_and_then_returns_to_idle() -> None:
    store = QueueStore()
    store.request(command("one", "Current"))
    store.request(command("two", "Next"))

    assert store.skip()["reason"] == "skipped"
    assert store.snapshot()["current_track"]["title"] == "Next"
    assert store.skip()["reason"] == "skipped"
    assert store.snapshot()["current_track"] is None
    assert store.skip()["reason"] == "nothing_playing"
