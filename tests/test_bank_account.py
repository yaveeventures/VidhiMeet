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

    ver = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert ver.status_code == 200
    assert ver.json().get("demo_verified") is True

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=headers).json()
    assert acct["verified"] is True

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
    """In demo mode (no PhonePe creds), verify auto-verifies the account."""
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

    res = client.post("/api/v1/lawyers/me/bank-account/verify", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data.get("demo_verified") is True
    assert "utr" in data

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=headers).json()
    assert acct["verified"] is True
    assert acct["utr"] is not None


def test_verify_requires_bank_account(client):
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


def test_phonepe_verify_webhook_routes_correctly(client):
    """PhonePe webhook with VERIFY- prefix updates LawyerBankAccount, not a Booking."""
    import json as _json
    import base64
    import hashlib
    from backend.db import get_db
    from backend.models import LawyerBankAccount, User
    from backend.config import get_settings
    from sqlalchemy import select

    settings = get_settings()
    settings.phonepe_merchant_id = "MID123"
    settings.phonepe_salt_key = "salt-key-123"
    settings.phonepe_salt_index = "1"

    try:
        reg = client.post("/api/v1/auth/register", json={
            "email": "bank_webhook@example.com", "password": "secure-password-webhook-123",
            "full_name": "Adv. Webhook Test", "role": "lawyer",
            "consent_privacy_policy": True, "consent_terms": True
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        client.post("/api/v1/lawyers/me/bank-account", json={
            "account_holder_name": "Adv. Webhook Test",
            "account_number": "333344445555",
            "ifsc_code": "KKBK0006666",
            "bank_name": "Kotak Mahindra Bank"
        }, headers=headers)

        db = next(get_db())
        l_user = db.query(User).filter(User.email == "bank_webhook@example.com").first()
        acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == l_user.id))
        fake_txn_id = f"VERIFY-{l_user.id.replace('-', '')[:16]}"
        acct.phonepe_txn_id = fake_txn_id
        db.commit()

        response_data = {
            "success": True,
            "code": "PAYMENT_SUCCESS",
            "data": {
                "merchantTransactionId": fake_txn_id,
                "transactionId": "UTR123456789",
                "paymentInstrument": {
                    "type": "UPI",
                    "vpa": "webhooktest@upi",
                    "name": "Adv. Webhook Test"
                }
            }
        }
        json_bytes = _json.dumps(response_data).encode("utf-8")
        base64_payload = base64.b64encode(json_bytes).decode("utf-8")
        
        # Verify webhook signature using salt key
        webhook_body_dict = {"response": base64_payload}
        webhook_body_str = _json.dumps(webhook_body_dict)
        hash_input = webhook_body_str + "salt-key-123"
        sha256_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
        x_verify = f"{sha256_hash}###1"

        res = client.post(
            "/api/v1/webhooks/phonepe",
            content=webhook_body_str,
            headers={"Content-Type": "application/json", "X-VERIFY": x_verify}
        )
        assert res.status_code == 200

        db.expire_all()
        acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == l_user.id))
        assert acct.verified is True
        assert acct.utr == "UTR123456789"
        assert acct.upi_vpa == "webhooktest@upi"
    finally:
        settings.phonepe_merchant_id = ""
        settings.phonepe_salt_key = ""

