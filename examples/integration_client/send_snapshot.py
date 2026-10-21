#!/usr/bin/env python3
"""Send one partner inventory snapshot to AegisFlow using only stdlib Python.

The integration key is read from the environment, never from CLI arguments.
This script is a sample client for the gateway contract, not an HIS/ERP adapter.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post a batch-level inventory snapshot to AegisFlow."
    )
    parser.add_argument(
        "payload",
        type=Path,
        help="Path to a JSON snapshot that matches docs/EXTERNAL_INTEGRATION.md.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP timeout in seconds (default: 15).",
    )
    args = parser.parse_args()

    api_base = os.getenv("AEGISFLOW_API_URL", "http://localhost:8000/api/v1").rstrip("/")
    integration_key = os.getenv("AEGISFLOW_INTEGRATION_KEY")
    if not integration_key:
        print(
            "Missing AEGISFLOW_INTEGRATION_KEY. Set it in the server-side environment; "
            "do not put it in source code or commit it.",
            file=sys.stderr,
        )
        return 2

    try:
        payload_text = args.payload.read_text(encoding="utf-8")
        # Parse before sending so malformed JSON is rejected locally.
        payload_obj = json.loads(payload_text)
        body = json.dumps(payload_obj, separators=(",", ":")).encode("utf-8")
    except OSError as exc:
        print(f"Cannot read payload file: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Payload is not valid JSON: {exc}", file=sys.stderr)
        return 2

    request = Request(
        url=f"{api_base}/integrations/inventory/snapshot",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Integration-Key": integration_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=args.timeout) as response:
            response_text = response.read().decode("utf-8", errors="replace")
            print(f"HTTP {response.status}")
            try:
                print(json.dumps(json.loads(response_text), indent=2))
            except json.JSONDecodeError:
                print(response_text)
            return 0 if 200 <= response.status < 300 else 1
    except HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        print(f"Integration request rejected (HTTP {exc.code}).", file=sys.stderr)
        try:
            print(json.dumps(json.loads(response_text), indent=2), file=sys.stderr)
        except json.JSONDecodeError:
            print(response_text, file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"Could not reach AegisFlow: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
