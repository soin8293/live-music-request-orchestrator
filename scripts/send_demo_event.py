"""Send a synthetic request or skip event to a local controller."""

from __future__ import annotations

import argparse
import os
import sys

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="action", required=True)

    request_parser = subcommands.add_parser("request")
    request_parser.add_argument("--user", default="demo_viewer")
    request_parser.add_argument("--song", required=True)

    skip_parser = subcommands.add_parser("skip")
    skip_parser.add_argument("--user", default="demo_moderator")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url = os.getenv("ORCHESTRATOR_INGEST_URL", "http://127.0.0.1:5000/ingest")
    token = os.getenv("ORCHESTRATOR_INGEST_TOKEN", "").strip()
    payload = {
        "event_type": "CHAT_COMMAND",
        "action": args.action,
        "username": args.user,
        "nickname": args.user,
        "command_params": getattr(args, "song", ""),
        "source": "demo_script",
    }
    headers = {"X-Ingest-Token": token} if token else {}
    response = requests.post(url, json=payload, headers=headers, timeout=5)
    print(response.json())
    return 0 if response.ok else 1


if __name__ == "__main__":
    sys.exit(main())
