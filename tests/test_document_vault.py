import time
import pytest
from datetime import datetime, timedelta, timezone
import jwt
from backend.config import get_settings
from backend.models import Role, User
from backend.security import create_access_token, hash_password

settings = get_settings()


def test_booking_document_presign_expiry(database, client):
    """Verify that booking document presign returns 15-minute expiry (900s)."""
    # Create user & booking in test DB
    lawyer = User(
        email="vault_lawyer@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Adv. Vault Lawyer",
        role=Role.LAWYER
    )
    database.add(lawyer)
    database.commit()

    token = create_access_token(lawyer)
    headers = {"Authorization": f"Bearer {token}"}

    # Test presign endpoint in lawyers.py
    resp = client.post(
        "/api/v1/lawyers/me/documents/presign?filename=contract.pdf&content_type=application/pdf",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["expires_in"] == 900


def test_drafting_document_presign_expiry(database, client):
    """Verify that drafting document presign returns 15-minute expiry (900s)."""
    client_user = User(
        email="vault_client@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Client Vault Tester",
        role=Role.CLIENT
    )
    database.add(client_user)
    database.commit()

    token = create_access_token(client_user)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/v1/drafting/documents/presign?filename=agreement.pdf&content_type=application/pdf",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["expires_in"] == 900


def test_expired_document_access_link_rejection(database, client):
    """Verify that a document access token issued > 15 minutes ago (900s) is rejected with 401."""
    user = User(
        email="expired_token_user@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Expired Token User",
        role=Role.CLIENT
    )
    database.add(user)
    database.commit()

    # Create a token issued 20 minutes ago (1200 seconds ago)
    old_time = datetime.now(timezone.utc) - timedelta(minutes=20)
    expired_token = jwt.encode(
        {
            "sub": user.id,
            "role": user.role.value,
            "full_name": user.full_name,
            "iss": settings.jwt_issuer,
            "iat": old_time.timestamp(),
            "exp": (old_time + timedelta(hours=1)).timestamp(),
        },
        settings.jwt_secret,
        algorithm="HS256"
    )

    # Attempt to download document with expired link token
    resp = client.get(f"/api/v1/drafting/documents/download?key=drafting/mock-file.pdf&token={expired_token}")
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()
