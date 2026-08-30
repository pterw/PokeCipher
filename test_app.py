"""Tests for the FastAPI application that serves the cipher over HTTP.

These replace ``test_api_support.py``, which exercised the ``BaseHTTPRequestHandler``
factory behind the retired ``api/*.py`` functions. Going through ``TestClient``
covers routing, status codes and the JSON envelope in one pass, which the old
fake-handler unit test could not reach.

The assertions here are the server half of a contract: ``next-app/lib/pokecipher-api.ts``
reads ``result`` on success and ``error`` on failure, and its vitest suite pins
the same shapes on the client side.
"""

import unittest

from fastapi.testclient import TestClient

from app import MAX_TEXT_CHARS, app

client = TestClient(app)


class EncodeDecodeTests(unittest.TestCase):
    """The two happy paths and their round trip."""

    def test_encode_returns_pokemon_names(self) -> None:
        response = client.post("/api/encode", json={"text": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": "Zubat Weepinbell Ponyta Gyarados Slowbro"})

    def test_decode_reverses_encode(self) -> None:
        encoded = client.post("/api/encode", json={"text": "Pikachu"}).json()["result"]
        response = client.post("/api/decode", json={"text": encoded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": "Pikachu"})

    def test_empty_text_is_valid(self) -> None:
        """An empty string is a legal message, unlike an empty request body."""
        response = client.post("/api/encode", json={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": ""})


class NamesEndpointTests(unittest.TestCase):
    """/api/names serves the decoder's vocabulary for client-side validation."""

    def test_returns_every_indexed_name_sorted(self) -> None:
        from pokecipher import NAME_INDEX

        response = client.get("/api/names")
        self.assertEqual(response.status_code, 200)
        names = response.json()["names"]
        self.assertEqual(names, sorted(NAME_INDEX))

    def test_is_cacheable(self) -> None:
        """The list only changes on deploy, so it must not be refetched per keystroke."""
        response = client.get("/api/names")
        self.assertIn("max-age", response.headers["cache-control"])

    def test_allows_cross_origin_get(self) -> None:
        """The frontend is a separate deployment, so GET must pass CORS too."""
        response = client.get("/api/names", headers={"Origin": "https://example.com"})
        self.assertEqual(response.headers["access-control-allow-origin"], "*")


class RequestValidationTests(unittest.TestCase):
    """Every rejection is a 400 or 413 carrying an ``error`` string."""

    def test_empty_body_is_rejected(self) -> None:
        response = client.post("/api/encode", content=b"")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Expected a JSON object body under 32 KiB."})

    def test_unparseable_body_is_rejected(self) -> None:
        response = client.post("/api/encode", content=b"{not json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Expected a JSON object body under 32 KiB."})

    def test_non_object_body_is_rejected(self) -> None:
        response = client.post("/api/encode", json=["Hello"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Expected a JSON object body under 32 KiB."})

    def test_oversized_body_is_rejected(self) -> None:
        response = client.post("/api/encode", content=b"x" * (32 * 1024 + 1))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Expected a JSON object body under 32 KiB."})

    def test_missing_text_field_is_rejected(self) -> None:
        response = client.post("/api/encode", json={"message": "Hello"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Field 'text' must be a string."})

    def test_non_string_text_is_rejected(self) -> None:
        response = client.post("/api/decode", json={"text": 42})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Field 'text' must be a string."})

    def test_text_at_the_cap_is_accepted(self) -> None:
        response = client.post("/api/encode", json={"text": "a" * MAX_TEXT_CHARS})
        self.assertEqual(response.status_code, 200)

    def test_text_over_the_cap_is_rejected(self) -> None:
        response = client.post("/api/encode", json={"text": "a" * (MAX_TEXT_CHARS + 1)})
        self.assertEqual(response.status_code, 413)
        self.assertEqual(
            response.json(), {"error": f"Field 'text' exceeds {MAX_TEXT_CHARS} characters."}
        )


class ErrorEnvelopeTests(unittest.TestCase):
    """Framework-generated errors use the same envelope as our own."""

    def test_unknown_route_reports_error_not_detail(self) -> None:
        response = client.post("/api/enchant", json={"text": "Hello"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())
        self.assertNotIn("detail", response.json())

    def test_wrong_method_reports_error_not_detail(self) -> None:
        response = client.get("/api/encode")
        self.assertEqual(response.status_code, 405)
        self.assertIn("error", response.json())
        self.assertNotIn("detail", response.json())


class CorsTests(unittest.TestCase):
    """The split deployment calls this API cross-origin, so CORS is load-bearing."""

    def test_response_carries_allow_origin(self) -> None:
        response = client.post(
            "/api/encode", json={"text": "Hello"}, headers={"Origin": "https://example.com"}
        )
        self.assertEqual(response.headers["access-control-allow-origin"], "*")

    def test_preflight_is_answered(self) -> None:
        response = client.options(
            "/api/encode",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "*")


if __name__ == "__main__":
    unittest.main()
