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

from api_support import make_handler
from pokecipher import decode_message, encode_message

EncodeHandler = make_handler(encode_message)
DecodeHandler = make_handler(decode_message)


class DevRouter(BaseHTTPRequestHandler):
    """Dispatch /api/encode and /api/decode to their Vercel handlers."""

    def do_POST(self) -> None:
        handler_cls = DecodeHandler if self.path.startswith("/api/decode") else EncodeHandler
        handler = handler_cls(self.request, self.client_address, self.server)
        handler.do_POST()

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
