"""Live Music Request Orchestrator package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("live-music-request-orchestrator")
except PackageNotFoundError:  # pragma: no cover - supports direct source-tree imports
    __version__ = "0.0.0+local"
