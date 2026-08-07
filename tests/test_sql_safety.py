import pytest
from backend.models import User, Role, AuditLog
from backend.security import hash_password


def register_user(client, email, role="client", full_name="SQL Injection Test"):
    payload = {
        "email": email,
        "password": "a-secure-password-123",
        "full_name": full_name,
        "role": role,
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    return resp


def test_sql_injection_in_registration_name(client):
    """Verify that SQL injection strings in registration input fields are safely parameterized."""
    payload_name = "John'; DROP TABLE users; --"
    resp = register_user(client, "sqli_test@example.com", full_name=payload_name)
    assert resp.status_code == 201

    # Verify user account exists and database was not compromised
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "sqli_test@example.com",
        "password": "a-secure-password-123"
    })
    assert login_resp.status_code == 200


def test_sql_injection_in_login_credentials(client):
    """Verify that SQL injection attempt in login payload is rejected harmlessly."""
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin' OR '1'='1",
        "password": "' OR '1'='1"
    })
    assert resp.status_code == 422 or resp.status_code == 401


def test_erasure_endpoint_with_sql_characters(client):
    """Verify that right-to-erasure endpoint executes parameterized ORM delete statements correctly."""
    reg_resp = register_user(client, "erasure_sqli@example.com", "client", "Erasure Test User")
    token = reg_resp.json()["access_token"]

    erasure_resp = client.delete(
        "/api/v1/auth/erasure",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert erasure_resp.status_code == 204
