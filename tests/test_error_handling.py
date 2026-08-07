from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app, raise_server_exceptions=False)

def test_unhandled_500_error_handling():
    """Verify unhandled 500 exceptions return sanitized public message with request_id without exposing internals."""
    with patch("sqlalchemy.orm.Session.execute", side_effect=RuntimeError("Database connection dropped secret_key_999")):
        response = client.get("/api/v1/health")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "An unexpected server error occurred. Please try again later."
        assert "request_id" in data
        assert "secret_key_999" not in response.text
        assert "RuntimeError" not in response.text

def test_http_exception_handling():
    """Verify HTTP exceptions return structured error format."""
    response = client.get("/api/v1/public/lawyer/non-existent-uuid-999")
    assert response.status_code in (404, 405)
    data = response.json()
    assert data["status"] == "error"
    assert "request_id" in data

def test_validation_error_handling():
    """Verify invalid request payloads produce sanitized clean error lists."""
    response = client.post("/api/v1/auth/login", json={"invalid_field": True})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid request parameter(s)"
    assert isinstance(data["errors"], list)
    assert "request_id" in data
