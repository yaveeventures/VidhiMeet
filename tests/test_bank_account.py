"""
Tests for Lawyer Bank Account management and direct verification.
"""


def test_add_bank_account(client):
    """Lawyer can add a bank account; account number is masked in response."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_lawyer@example.com", "password": "secure-password-bank-123",
        "full_name": "Adv. Bank Test", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "account_holder_name": "Adv. Bank Test",
        "account_number": "123456789012",
        "ifsc_code": "HDFC0001234",
        "bank_name": "HDFC Bank",
        "upi_vpa": "banktest@upi"
    }
    res = client.post("/api/v1/lawyers/me/bank-account", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["bank_name"] == "HDFC Bank"
    assert data["ifsc_code"] == "HDFC0001234"
    assert data["upi_vpa"] == "banktest@upi"
    assert data["verified"] is False
    assert "123456789012" not in data["account_number_masked"]
    assert data["account_number_masked"].endswith("9012")


def test_get_bank_account(client):
    """Lawyer can retrieve their bank account."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_get@example.com", "password": "secure-password-bankget-123",
        "full_name": "Adv. Get Bank", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/lawyers/me/bank-account", headers=headers)
    assert res.status_code == 404

    client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Get Bank",
        "account_number": "987654321098",
        "ifsc_code": "ICIC0005678",
        "bank_name": "ICICI Bank"
    }, headers=headers)

    res = client.get("/api/v1/lawyers/me/bank-account", headers=headers)
    assert res.status_code == 200
    assert res.json()["bank_name"] == "ICICI Bank"
    assert res.json()["account_number_masked"].endswith("1098")


def test_update_bank_account_resets_verification(client):
    """Editing IFSC resets the verified flag."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_update@example.com", "password": "secure-password-update-123",
        "full_name": "Adv. Update Bank", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Update Bank",
        "account_number": "111122223333",
        "ifsc_code": "SBIN0001111",
        "bank_name": "State Bank of India"
    }, headers=headers)

    # Verify directly
    ver = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert ver.status_code == 200
    assert ver.json()["verified"] is True

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=headers).json()
    assert acct["verified"] is True

    # Changing IFSC must reset verification
    upd = client.put("/api/v1/lawyers/me/bank-account", json={"ifsc_code": "SBIN0002222"}, headers=headers)
    assert upd.status_code == 200
    assert upd.json()["verified"] is False


def test_delete_bank_account(client):
    """Lawyer can delete their bank account."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_delete@example.com", "password": "secure-password-delete-123",
        "full_name": "Adv. Delete Bank", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Delete Bank",
        "account_number": "444455556666",
        "ifsc_code": "AXIS0003333",
        "bank_name": "Axis Bank"
    }, headers=headers)

    res = client.delete("/api/v1/lawyers/me/bank-account", headers=headers)
    assert res.status_code == 204

    res = client.get("/api/v1/lawyers/me/bank-account", headers=headers)
    assert res.status_code == 404


def test_duplicate_add_returns_409(client):
    """Adding a second bank account returns 409 Conflict."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_dup@example.com", "password": "secure-password-dup-123",
        "full_name": "Adv. Dup Bank", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "account_holder_name": "Adv. Dup Bank",
        "account_number": "777788889999",
        "ifsc_code": "KKBK0000444",
        "bank_name": "Kotak Bank"
    }
    res1 = client.post("/api/v1/lawyers/me/bank-account", json=payload, headers=headers)
    assert res1.status_code == 201
    res2 = client.post("/api/v1/lawyers/me/bank-account", json=payload, headers=headers)
    assert res2.status_code == 409


def test_bank_account_verification(client):
    """Verify endpoint marks account verified and returns audit UTR."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_verify@example.com", "password": "secure-password-verify-123",
        "full_name": "Adv. Verify Bank", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Verify Bank",
        "account_number": "000011112222",
        "ifsc_code": "PUNB0005555",
        "bank_name": "Punjab National Bank",
        "upi_vpa": "verify@upi"
    }, headers=headers)

    # POST /verify marks account verified
    res = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["verified"] is True
    assert data["utr"].startswith("VERIFIED-")

    # Second call returns already_verified
    res2 = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["already_verified"] is True

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=headers).json()
    assert acct["verified"] is True
    assert acct["verification_status"] == "verified"


def test_verify_without_account_returns_404(client):
    """Calling /verify without a bank account returns 404."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_noacct@example.com", "password": "secure-password-noacct-123",
        "full_name": "Adv. No Acct", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    res = client.post("/api/v1/lawyers/me/bank-account/verify",
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404


def test_admin_verify_and_revoke_bank_account(client):
    """Admin can manually verify and revoke verification for a lawyer bank account."""
    # 1. Register lawyer and add bank account
    lawyer_reg = client.post("/api/v1/auth/register", json={
        "email": "bank_adminver@example.com", "password": "secure-password-adminver-123",
        "full_name": "Adv. Admin Verify", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    lawyer_token = lawyer_reg.json()["access_token"]
    l_headers = {"Authorization": f"Bearer {lawyer_token}"}

    bank_res = client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Admin Verify",
        "account_number": "555566667777",
        "ifsc_code": "UBIN0001234",
        "bank_name": "Union Bank of India"
    }, headers=l_headers)
    assert bank_res.status_code == 201
    bank_id = bank_res.json()["id"]
    lawyer_id = client.get("/api/v1/auth/me", headers=l_headers).json()["id"]

    # 2. Create admin
    from backend.db import SessionLocal
    from backend.models import Role, User
    from backend.security import create_access_token, hash_password
    db = SessionLocal()
    try:
        admin = User(
            email="admin_bankver@example.com",
            password_hash=hash_password("Pass123!"),
            full_name="Super Admin",
            role=Role.ADMIN
        )
        db.add(admin)
        db.commit()
        admin_token = create_access_token(admin)
    finally:
        db.close()
    a_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Non-admin forbidden
    client_reg = client.post("/api/v1/auth/register", json={
        "email": "client_forbidden@example.com", "password": "secure-client-pass-123",
        "full_name": "Test Client", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    c_token = client_reg.json()["access_token"]
    forbidden_res = client.patch(f"/api/v1/admin/payouts/{bank_id}/verify?verified=true",
                                 headers={"Authorization": f"Bearer {c_token}"})
    assert forbidden_res.status_code == 403

    # 4. Admin verifies by bank_id
    ver_res = client.patch(f"/api/v1/admin/payouts/{bank_id}/verify?verified=true", headers=a_headers)
    assert ver_res.status_code == 200
    vdata = ver_res.json()
    assert vdata["verified"] is True
    assert vdata["verification_status"] == "verified"
    assert vdata["utr"].startswith("ADM-VERIFIED-")

    # 5. Check lawyer sees verified state
    acct = client.get("/api/v1/lawyers/me/bank-account", headers=l_headers).json()
    assert acct["verified"] is True
    assert acct["verification_status"] == "verified"

    # 6. Admin revokes verification
    rev_res = client.patch(f"/api/v1/admin/payouts/{lawyer_id}/verify?verified=false", headers=a_headers)
    assert rev_res.status_code == 200
    rdata = rev_res.json()
    assert rdata["verified"] is False
    assert rdata["verification_status"] == "unverified"

