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


def test_lawyer_document_reupload_replaces_old_file(database, client):
    """Verify that re-uploading a lawyer document deletes the old file and resets verification status."""
    import os
    from backend.models import LawyerProfile

    lawyer = User(
        email="reupload_lawyer@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Adv. Reupload Lawyer",
        role=Role.LAWYER
    )
    database.add(lawyer)
    database.commit()

    profile = LawyerProfile(user_id=lawyer.id, bar_number="REUP12345", hourly_fee_minor=50000)
    database.add(profile)
    database.commit()

    token = create_access_token(lawyer)
    headers = {"Authorization": f"Bearer {token}"}

    # Setup mock file 1
    key1 = f"lawyers/{lawyer.id}/mock-license-v1.pdf"
    path1 = os.path.join("uploads", key1)
    os.makedirs(os.path.dirname(path1), exist_ok=True)
    with open(path1, "w") as f:
        f.write("Old License Content")

    # Confirm doc 1 upload
    resp1 = client.post(
        f"/api/v1/lawyers/me/documents/confirm?filename=license-v1.pdf&key={key1}&doc_type=bar_license",
        headers=headers
    )
    assert resp1.status_code == 200
    assert os.path.exists(path1)

    # Setup mock file 2
    key2 = f"lawyers/{lawyer.id}/mock-license-v2.pdf"
    path2 = os.path.join("uploads", key2)
    os.makedirs(os.path.dirname(path2), exist_ok=True)
    with open(path2, "w") as f:
        f.write("New License Content")

    # Confirm doc 2 re-upload
    resp2 = client.post(
        f"/api/v1/lawyers/me/documents/confirm?filename=license-v2.pdf&key={key2}&doc_type=bar_license",
        headers=headers
    )
    assert resp2.status_code == 200

    # Verify old file was deleted and new file exists
    assert not os.path.exists(path1), "Old document file should be purged on re-upload"
    assert os.path.exists(path2), "New document file should exist"

    # Verify DB profile updated and status reset
    database.refresh(profile)
    assert key2 in profile.bar_license_url
    assert profile.bar_license_verified is False
    assert profile.verification_status == "pending"
    assert profile.verified is False

    # Cleanup test file
    if os.path.exists(path2):
        os.remove(path2)

