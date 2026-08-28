"""Shared HTTP plumbing for the PokéCipher Vercel Python functions.

Lives at the repository root so the ``api/`` handlers can import it with a plain
top-level import. Vercel puts the project root on ``sys.path``, which is the
same mechanism that makes ``pokecipher`` importable from a handler, so no path
juggling is needed.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler

MAX_BODY_BYTES = 32 * 1024

# The decoder emits positions as soon as they are final, so cost is close to
# linear: ~1.2 s for 10,000 chars of prose on CPython 3.13. Text that sustains an
# unresolved ambiguity throughout cannot collapse and stays quadratic (~3.3 s at
# 4,100 chars, and ~13 s at 8,000). Capping here keeps the pathological case
# inside the function's maxDuration instead of turning a huge paste into a
# timeout.
MAX_TEXT_CHARS = 4_000


def read_json_body(handler: BaseHTTPRequestHandler) -> dict | None:
    """Parse the request body as a JSON object, or return ``None`` if unusable."""
    try:
        length = int(handler.headers.get("Content-Length") or 0)
    except (TypeError, ValueError):
        return None
    if not 0 < length <= MAX_BODY_BYTES:
        return None
    try:
        payload = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    """Write a JSON response."""
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    if status != 204:
        handler.wfile.write(body)


def make_handler(transform: Callable[[str], str]) -> type[BaseHTTPRequestHandler]:
    """Build a Vercel Python handler that applies ``transform`` to the ``text`` field."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            payload = read_json_body(self)
            if payload is None:
                send_json(self, 400, {"error": "Expected a JSON object body under 32 KiB."})
                return
            text = payload.get("text")
            if not isinstance(text, str):
                send_json(self, 400, {"error": "Field 'text' must be a string."})
                return
            if len(text) > MAX_TEXT_CHARS:
                send_json(
                    self,
                    413,
                    {"error": f"Field 'text' exceeds {MAX_TEXT_CHARS} characters."},
                )
                return
            send_json(self, 200, {"result": transform(text)})

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            """Silence the default stderr access log; the platform records requests."""

    return Handler
