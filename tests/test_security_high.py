import pyotp
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import Role, User
from backend.security import create_access_token, decode_token, hash_password, revoke_jti

client = TestClient(app)


def test_totp_secret_generation_and_mfa_flow(database):
    """Test TOTP secret generation, QR URI creation, enabling MFA, and 2FA login verification."""
    # Register/create lawyer user
    lawyer_email = "mfa_lawyer@example.com"
    lawyer = User(
        email=lawyer_email,
        password_hash=hash_password("LawyerPassword123!"),
        full_name="MFA Advocate",
        role=Role.LAWYER,
        date_of_birth="1985-05-15"
    )
    database.add(lawyer)
    database.commit()

    token = create_access_token(lawyer)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Setup MFA
    res_setup = client.post("/api/v1/auth/mfa/setup", headers=headers)
    assert res_setup.status_code == 200
    data_setup = res_setup.json()
    assert "secret" in data_setup
    assert "qr_uri" in data_setup
    secret = data_setup["secret"]

    # 2. Enable MFA with valid TOTP code
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()

    res_enable = client.post("/api/v1/auth/mfa/enable", json={"code": valid_code}, headers=headers)
    assert res_enable.status_code == 200
    assert res_enable.json()["status"] == "ok"

    # Refresh user state
    database.refresh(lawyer)
    assert lawyer.mfa_enabled is True

    # 3. Login without TOTP code -> returns mfa_required = True
    res_login_no_mfa = client.post("/api/v1/auth/login", json={"email": lawyer_email, "password": "LawyerPassword123!"})
    assert res_login_no_mfa.status_code == 200
    assert res_login_no_mfa.json()["mfa_required"] is True

    # 4. Login with invalid TOTP code -> HTTP 401
    res_login_bad_mfa = client.post("/api/v1/auth/login", json={"email": lawyer_email, "password": "LawyerPassword123!", "totp_code": "000000"})
    assert res_login_bad_mfa.status_code == 401

    # 5. Login with valid TOTP code -> returns tokens
    res_login_valid_mfa = client.post("/api/v1/auth/login", json={"email": lawyer_email, "password": "LawyerPassword123!", "totp_code": totp.now()})
    assert res_login_valid_mfa.status_code == 200
    assert res_login_valid_mfa.json()["access_token"] != ""


def test_jwt_logout_and_revocation(database):
    """Test logout endpoint revokes JWT access token (jti blocklist)."""
    user_email = "revocation_user@example.com"
    user = User(
        email=user_email,
        password_hash=hash_password("SecurePassword123!"),
        full_name="Revoke User",
        role=Role.CLIENT,
        date_of_birth="1992-08-20"
    )
    database.add(user)
    database.commit()

    token = create_access_token(user)
    headers = {"Authorization": f"Bearer {token}"}

    # Verify active token works
    payload = decode_token(token)
    assert payload["sub"] == user.id
    jti = payload["jti"]

    # Revoke jti
    revoke_jti(jti)

    # Subsequent decode_token call with revoked token MUST raise HTTP 401 Revoked Token
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401
    assert "token has been revoked" in exc_info.value.detail
