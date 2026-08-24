# Setup guide

This guide covers the credential-free demo, release downloads, OBS, the optional
TikFinity bridge, configuration, and common startup problems.

## Know the boundary first

The project accepts request commands, manages an in-memory queue, resolves
deterministic demo metadata, and renders an overlay. It does not play audio and
does not contain Spotify, YouTube, Twitch, TikTok, or other provider OAuth code.

The queue resets when the controller restarts.

## Recommended: run from a clone

You need Git and Python 3.11 or newer.

```text
git clone https://github.com/soin8293/live-music-request-orchestrator.git
cd live-music-request-orchestrator
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install and launch:

```text
python -m pip install .
live-music-orchestrator
```

Keep that terminal open. A successful startup prints a local address. Visit:

- Interactive demo: <http://127.0.0.1:5000/?controls=1>
- Clean overlay: <http://127.0.0.1:5000/>
- Health response: <http://127.0.0.1:5000/health>

The interactive page can add, skip, and reset requests without a second
terminal or any credentials.

Stop the controller with `Ctrl+C`.

## What the release downloads mean

GitHub automatically adds **Source code (zip)** and **Source code (tar.gz)** to
every release. They are snapshots of the repository, not Windows or macOS
installers.

| Download | Intended use |
|---|---|
| `live_music_request_orchestrator-0.1.2-py3-none-any.whl` | Install the packaged app into Python |
| `live_music_request_orchestrator-0.1.2.tar.gz` | Python source distribution for packaging workflows |
| `SHA256SUMS.txt` | Verify the two uploaded package files |
| GitHub's automatic source ZIP/tarball | Browse the exact tagged source |

For most reviewers, cloning the repository is clearer because it includes the
tests, setup guide, demo-event script, and commit history.

To use the wheel instead, download it from the
[v0.1.2 release](https://github.com/soin8293/live-music-request-orchestrator/releases/tag/v0.1.2),
create and activate a virtual environment as above, then run:

```text
python -m pip install path/to/live_music_request_orchestrator-0.1.2-py3-none-any.whl
live-music-orchestrator
```

## API keys and secrets

No API key is needed for the local demo, overlay, or health endpoint.

| Name | Default | When it is needed | Where it comes from |
|---|---|---|---|
| `ORCHESTRATOR_INGEST_TOKEN` | empty | Required if `ORCHESTRATOR_HOST` is not loopback; optional for bridge/API clients on loopback | You generate it locally |
| `TIKFINITY_WS_URL` | `ws://127.0.0.1:21213/` | Only for the optional bridge | The local TikFinity WebSocket address |
| `ORCHESTRATOR_INGEST_URL` | `http://127.0.0.1:5000/ingest` | Only when the bridge should target another controller address | Your controller address |

There are no Spotify, YouTube, Twitch, or TikTok client IDs, client secrets, or
OAuth tokens to obtain for this repository. Provider playback is outside its
scope.

To create an ingest token, run:

```text
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy `.env.example` to `.env`, paste the generated value after
`ORCHESTRATOR_INGEST_TOKEN=`, and never commit `.env`. The repository ignores
that file.

## OBS Browser Source

1. Start `live-music-orchestrator` and leave it running.
2. In OBS, add a **Browser** source.
3. Set its URL to `http://127.0.0.1:5000/`.
4. Use the width and height that fit your scene; the overlay is responsive.
5. Keep the controls URL (`/?controls=1`) in a normal browser, not in the scene.

OBS and the controller must run on the same computer for the default loopback
address to work. No OBS plugin or API key is required.

## Optional TikFinity bridge

This adapter reads recognized `!play`, `!request`, and `!skip` messages from a
TikFinity WebSocket and forwards only the normalized command to the controller.

1. Install and run TikFinity separately.
2. Confirm that its local WebSocket is available at
   `ws://127.0.0.1:21213/`, or set `TIKFINITY_WS_URL` in `.env` to the address
   your installation exposes.
3. Start `live-music-orchestrator` in one terminal.
4. Activate the same virtual environment in a second terminal and run:

```text
live-music-bridge
```

TikFinity is a third-party product and is not bundled or CI-tested here. The
bridge does not read a TikFinity account password or provider API key.

## All configuration

Copy `.env.example` to `.env` only when changing defaults.

| Variable | Default | Purpose |
|---|---|---|
| `ORCHESTRATOR_HOST` | `127.0.0.1` | Controller bind address |
| `ORCHESTRATOR_PORT` | `5000` | Controller port |
| `ORCHESTRATOR_INGEST_TOKEN` | empty | Shared secret for mutation requests |
| `REQUEST_DEBOUNCE_SECONDS` | `8` | Duplicate-request suppression window |
| `MAX_QUEUE_ITEMS` | `50` | Maximum queued requests |
| `MAX_REQUEST_CHARS` | `180` | Maximum request-text length |
| `TIKFINITY_WS_URL` | `ws://127.0.0.1:21213/` | Optional bridge source |
| `ORCHESTRATOR_INGEST_URL` | `http://127.0.0.1:5000/ingest` | Bridge destination |
| `BRIDGE_RECONNECT_SECONDS` | `3` | Bridge retry delay |

Binding `ORCHESTRATOR_HOST` to a LAN address requires
`ORCHESTRATOR_INGEST_TOKEN`. Even with a token, the built-in Flask server is not
a production internet-facing deployment. Keep it behind a trusted local network
and read [SECURITY.md](../SECURITY.md).

When a token is configured, mutation requests must send it in the
`X-Ingest-Token` header. The optional bridge and demo-event script do this. The
browser's interactive demo controls intentionally do not accept or retain a
secret, so use them only in the default loopback/no-token demo.

## Troubleshooting

### `python` is not recognized

Install Python 3.11 or newer and enable its PATH option. On Windows, `py -3.11`
can be used in place of `python` when the Python launcher is installed.

### PowerShell blocks `Activate.ps1`

You can avoid activation and call the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\live-music-orchestrator.exe
```

### Port 5000 is already in use

Set another port in `.env`, for example `ORCHESTRATOR_PORT=5050`, then use that
port in the browser and OBS URLs.

### The TikFinity bridge keeps retrying

The bridge logs that message when it cannot reach the configured local
WebSocket. Verify TikFinity is running and check `TIKFINITY_WS_URL`. The local
demo does not require the bridge.
