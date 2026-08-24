# Contributing

Contributions that improve the provider-neutral request controller, tests,
documentation, or accessibility are welcome.

## Public-development boundary

Do not contribute credentials, real viewer identities or chat logs, copyrighted
media, provider tokens, private playback integrations, or data copied from a
live session. Use the deterministic synthetic catalog and synthetic identities
in every test and example.

Security findings belong in
[private vulnerability reporting](https://github.com/soin8293/live-music-request-orchestrator/security/advisories/new),
not a public issue.

## Development checks

```text
python -m venv .venv
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest --cov=live_music_orchestrator --cov-fail-under=80
python -m build
```

Keep changes narrow, add tests for behavior changes, and update the architecture
or security documentation when a trust boundary changes. Pull requests should
explain the problem, the design choice, and the verification performed.
