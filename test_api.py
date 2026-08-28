import json

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test index route renders single page UI."""
    response = client.get("/")
    assert response.status_code == 200
    assert (
        b"GAME BOY // POK\xc3\x89MON CIPHER" in response.data or b"POK" in response.data
    )


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert data["num_regions"] == 3


def test_encode_endpoint_success(client):
    """Test /api/encode endpoint with valid text input."""
    response = client.post(
        "/api/encode",
        data=json.dumps({"text": "Test"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["encoded"] == "Persian Weepinbell Doduo Dodrio"
    assert len(data["tokens"]) == 4
    assert data["tokens"][0]["name"] == "Persian"
    assert data["tokens"][0]["dex_id"] == 53


def test_encode_endpoint_empty(client):
    """Test /api/encode endpoint with empty input."""
    response = client.post(
        "/api/encode", data=json.dumps({"text": ""}), content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_decode_endpoint_success(client):
    """Test /api/decode endpoint with valid encoded sequence."""
    response = client.post(
        "/api/decode",
        data=json.dumps({"text": "Persian Weepinbell Doduo Dodrio"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["decoded"] == "Test"


def test_decode_endpoint_ambiguity(client):
    """Test /api/decode endpoint with ambiguous sequence."""
    encoded_seq = "Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur"
    response = client.post(
        "/api/decode",
        data=json.dumps({"text": encoded_seq}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["decoded"] == "Hello W[n,o]rld!"


def test_decode_endpoint_empty(client):
    """Test /api/decode endpoint with empty input."""
    response = client.post(
        "/api/decode", data=json.dumps({"text": ""}), content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
