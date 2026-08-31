import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.main import app
from backend.models import User, PasswordResetToken, RefreshToken, Role
from backend.security import hash_password, verify_password

client = TestClient(app)


def test_forgot_password_flow_and_reset_success(database):
    """Test full forgot password -> reset password -> login with new password workflow."""
    email = "forgot_test_client@vidhimeet.in"
    old_pw = "OldSecurePass123!"
    new_pw = "NewSecurePass456!"

    user = User(
        email=email,
        password_hash=hash_password(old_pw),
        full_name="Forgot Client",
        role=Role.CLIENT,
        date_of_birth="1990-05-15"
    )
    database.add(user)
    database.commit()

    # Step 1: Request forgot password
    res1 = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "ok"
    assert "debug_reset_token" in data1
    reset_token = data1["debug_reset_token"]

    # Step 2: Login with old password works before reset
    res_login_old = client.post("/api/v1/auth/login", json={"email": email, "password": old_pw})
    assert res_login_old.status_code == 200
    old_refresh = res_login_old.json()["refresh_token"]

    # Step 3: Perform password reset
    res2 = client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_pw
    })
    assert res2.status_code == 200
    assert res2.json()["status"] == "ok"

    # Step 4: Login with old password now fails
    res_login_fail = client.post("/api/v1/auth/login", json={"email": email, "password": old_pw})
    assert res_login_fail.status_code == 401

    # Step 5: Login with new password succeeds
    res_login_new = client.post("/api/v1/auth/login", json={"email": email, "password": new_pw})
    assert res_login_new.status_code == 200
    assert "access_token" in res_login_new.json()

    # Step 6: Old refresh token is revoked
    res_ref = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert res_ref.status_code == 401


def test_forgot_password_unregistered_user():
    """Verify that forgot-password returns 404 when user is not registered."""
    res = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent_random_user_999@vidhimeet.in"})
    assert res.status_code == 404
    assert "not registered with us" in res.json()["detail"].lower()


def test_reset_password_invalid_or_used_token(database):
    """Verify that reusing a reset token or passing an invalid token is rejected with 400 Bad Request."""
    email = "single_use_test@vidhimeet.in"
    user = User(
        email=email,
        password_hash=hash_password("InitialPass123!"),
        full_name="Single Use User",
        role=Role.CLIENT,
        date_of_birth="1992-08-20"
    )
    database.add(user)
    database.commit()

    # Request reset token
    res1 = client.post("/api/v1/auth/forgot-password", json={"email": email})
    token = res1.json()["debug_reset_token"]

    # Use token once
    res2 = client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "FirstResetPass123!"})
    assert res2.status_code == 200

    # Attempt to reuse the same token
    res3 = client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "SecondResetPass123!"})
    assert res3.status_code == 400
    assert "invalid or expired" in res3.json()["detail"]

    # Attempt with garbage token
    res4 = client.post("/api/v1/auth/reset-password", json={"token": "invalid_fake_token_123456", "new_password": "ThirdResetPass123!"})
    assert res4.status_code == 400
