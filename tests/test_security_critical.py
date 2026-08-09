import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import Role, User
from backend.security import decrypt_field, encrypt_field, validate_participant_access

client = TestClient(app)


def test_decrypt_field_fail_closed_on_invalid_ciphertext():
    """Verify decrypt_field fails closed (raises HTTP 500) on invalid ciphertext instead of leaking raw plaintext."""
    invalid_ciphertext = "invalid_corrupted_fernet_token_xyz_123"
    
    with pytest.raises(HTTPException) as exc_info:
        decrypt_field(invalid_ciphertext)
        
    assert exc_info.value.status_code == 500
    assert "Secure storage decryption error" in exc_info.value.detail


def test_encrypt_decrypt_valid_field():
    """Verify encrypt_field and decrypt_field work cleanly for valid inputs."""
    plaintext = "Confidential Intake Form Text"
    encrypted = encrypt_field(plaintext)
    assert encrypted != plaintext
    
    decrypted = decrypt_field(encrypted)
    assert decrypted == plaintext


def test_validate_participant_access_isolation():
    """Verify validate_participant_access enforces tenant isolation (BOLA protection)."""
    user_client_a = User(id="client-101", role=Role.CLIENT, full_name="Client A")
    user_client_b = User(id="client-102", role=Role.CLIENT, full_name="Client B")
    user_lawyer_1 = User(id="lawyer-201", role=Role.LAWYER, full_name="Lawyer One")
    user_admin = User(id="admin-999", role=Role.ADMIN, full_name="Admin")

    # Participant (Client A or Lawyer One) can access
    validate_participant_access("client-101", "lawyer-201", user_client_a)
    validate_participant_access("client-101", "lawyer-201", user_lawyer_1)

    # Admin can access
    validate_participant_access("client-101", "lawyer-201", user_admin)

    # Unauthorized third-party (Client B) MUST raise HTTP 404
    with pytest.raises(HTTPException) as exc_info:
        validate_participant_access("client-101", "lawyer-201", user_client_b)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "record unavailable"


def test_security_response_headers():
    """Verify HTTP security headers (HSTS, nosniff, DENY, XSS protection, CSP) are included in API responses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    headers = response.headers
    
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "max-age=63072000" in headers["Strict-Transport-Security"]
    assert "Content-Security-Policy" in headers
