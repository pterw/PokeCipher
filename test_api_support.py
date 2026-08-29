"""Tests for the HTTP plumbing shared by the Vercel functions."""

import io
import unittest

from api_support import send_json


class _FakeHandler:
    """Minimal stand-in for BaseHTTPRequestHandler used by send_json."""

    def __init__(self) -> None:
        self.status: int | None = None
        self.headers: list[tuple[str, str]] = []
        self.wfile = io.BytesIO()

    def send_response(self, status: int) -> None:
        self.status = status

    def send_header(self, key: str, value: str) -> None:
        self.headers.append((key, value))

    def end_headers(self) -> None:
        pass


class SendJsonTests(unittest.TestCase):
    """send_json adds the CORS allow-origin header to every response."""

    def test_send_json_includes_cors_header(self) -> None:
        handler = _FakeHandler()
        send_json(handler, 200, {"result": "Zubat"})
        self.assertEqual(handler.status, 200)
        self.assertIn(("Access-Control-Allow-Origin", "*"), handler.headers)


if __name__ == "__main__":
    unittest.main()
