"""
Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification.
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
    """Editing IFSC resets the verified flag; verification done via RPD mock-complete."""
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

    # Verify via RPD: initiate -> mock-complete
    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=headers
    )
    assert init.status_code == 200
    v_id = init.json()["verification_id"]
    mc = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={"verification_id": v_id},
        headers=headers
    )
    assert mc.json()["verified"] is True

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


def test_upi_verification_demo_mode(client):
    """Verify endpoint now delegates to RPD; returns verification_id and qr_code in mock mode."""
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

    # POST /verify now initiates RPD and returns session data
    res = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert res.status_code == 200
    data = res.json()
    # In RPD mode, response contains verification_id (not yet verified)
    assert data.get("already_verified") is not True
    assert "verification_id" in data or "qr_code" in data

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=headers).json()
    # Account not yet verified — awaiting RPD ₹1 payment
    assert acct["verified"] is False


def test_verify_without_account_triggers_rpd(client):
    """Calling /verify without a bank account now initiates RPD (auto-link flow)."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "bank_noacct@example.com", "password": "secure-password-noacct-123",
        "full_name": "Adv. No Acct", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg.json()["access_token"]
    res = client.post("/api/v1/lawyers/me/bank-account/verify",
                      headers={"Authorization": f"Bearer {token}"})
    # RPD is initiated automatically — returns 200 with verification_id
    assert res.status_code == 200
    data = res.json()
    assert "verification_id" in data
    assert data.get("already_verified") is not True
