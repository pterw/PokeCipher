"""Tiny local dev server for the PokéCipher Vercel functions.

Vercel hosts ``api/encode.py`` and ``api/decode.py`` as serverless functions.
This serves the same two endpoints locally so ``next dev`` / ``next start`` —
which rewrite ``/api/*`` to this process — has a backend to talk to:

    python api_server.py            # http://127.0.0.1:8000
    python api_server.py 9000       # choose a port
"""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from api_support import MAX_TEXT_CHARS, read_json_body, send_json
from pokecipher import decode_message, encode_message


class DevRouter(BaseHTTPRequestHandler):
    """Route /api/encode and /api/decode through the same checks as Vercel."""

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
            send_json(self, 413, {"error": f"Field 'text' exceeds {MAX_TEXT_CHARS} characters."})
            return
        transform = decode_message if self.path.startswith("/api/decode") else encode_message
        send_json(self, 200, {"result": transform(text)})

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"PokéCipher dev API on http://127.0.0.1:{port} (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), DevRouter).serve_forever()


if __name__ == "__main__":
    main()
