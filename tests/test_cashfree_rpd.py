"""
Tests for Cashfree Reverse Penny Drop (RPD) bank account verification.

All tests run in sandbox/mock mode - no live Cashfree credentials required.
Covers:
  - RPD initiation (QR + mock session creation)
  - Status polling (PENDING to SUCCESS transition)
  - Mock-complete simulation (dev testing endpoint)
  - Auto bank account creation from RPD remitter details
  - Duplicate / already-verified guard
  - Webhook handler for RPD SUCCESS event
  - Account number / IFSC encrypted at rest, masked in responses
"""

import json
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_lawyer(client, email: str, name: str = "Adv. RPD Test"):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "secure-rpd-password-123",
        "full_name": name,
        "role": "lawyer",
        "consent_privacy_policy": True,
        "consent_terms": True,
    })
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# RPD Initiation
# ---------------------------------------------------------------------------

def test_rpd_initiate_creates_session_and_returns_qr(client):
    """POST /initiate returns verification_id, QR code data, and UPI intent."""
    token = _register_lawyer(client, "rpd_init@example.com")
    res = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["verification_id"], "Must return a verification_id"
    assert data["qr_code"], "Must return QR code (mock SVG in sandbox)"
    assert data["amount"] == 1.0
    assert data["currency"] == "INR"
    assert data["is_mock"] is True
    assert data["status"] == "PENDING"


def test_rpd_initiate_creates_pending_bank_account(client):
    """Initiating RPD creates a PENDING placeholder bank account row."""
    token = _register_lawyer(client, "rpd_placeholder@example.com")
    client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    acct = client.get("/api/v1/lawyers/me/bank-account", headers=_auth(token))
    assert acct.status_code == 200
    data = acct.json()
    assert data["verified"] is False
    assert data["verification_method"] == "reverse_penny_drop"
    assert data["verification_status"] == "pending"


def test_rpd_initiate_blocked_when_already_verified(client):
    """A verified account cannot trigger a new RPD session."""
    token = _register_lawyer(client, "rpd_already_verified@example.com")

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert init.status_code == 200
    v_id = init.json()["verification_id"]

    client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={"verification_id": v_id},
        headers=_auth(token),
    )

    res = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert res.status_code == 400
    assert "already verified" in res.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Status Polling
# ---------------------------------------------------------------------------

def test_rpd_status_pending_before_payment(client):
    """Polling status before payment returns PENDING / verified=False."""
    token = _register_lawyer(client, "rpd_status_pending@example.com")
    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    v_id = init.json()["verification_id"]

    status = client.get(
        f"/api/v1/lawyers/me/bank-account/reverse-penny-drop/status?verification_id={v_id}",
        headers=_auth(token),
    )
    assert status.status_code == 200
    data = status.json()
    assert data["status"] == "PENDING"
    assert data["verified"] is False


def test_rpd_status_no_verification_id_returns_400(client):
    """Polling status without a verification_id and no account returns 400."""
    token = _register_lawyer(client, "rpd_no_vid@example.com")
    res = client.get(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/status",
        headers=_auth(token),
    )
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Mock-Complete (Simulation)
# ---------------------------------------------------------------------------

def test_rpd_mock_complete_verifies_account(client):
    """Simulating payment via mock-complete marks account verified."""
    token = _register_lawyer(client, "rpd_mock_complete@example.com")

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert init.status_code == 200
    v_id = init.json()["verification_id"]

    res = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={"verification_id": v_id},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["verified"] is True
    assert data["utr"] is not None


def test_rpd_mock_complete_updates_account_details(client):
    """After mock-complete, bank account record has real account/IFSC, not PENDING."""
    token = _register_lawyer(client, "rpd_details@example.com")

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    v_id = init.json()["verification_id"]

    client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={
            "verification_id": v_id,
            "account_number": "50100498765432",
            "ifsc": "HDFC0001234",
            "name": "Adv. RPD Test",
        },
        headers=_auth(token),
    )

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=_auth(token))
    assert acct.status_code == 200
    data = acct.json()
    assert data["verified"] is True
    assert data["verification_method"] == "reverse_penny_drop"
    assert data["verification_status"] == "verified"
    assert data["ifsc_code"] == "HDFC0001234"
    assert "50100498765432" not in data["account_number_masked"]
    assert data["account_number_masked"].endswith("5432")
    assert data["utr"] is not None


def test_rpd_mock_complete_without_prior_initiate_returns_400(client):
    """Mock-complete with no active session returns 400."""
    token = _register_lawyer(client, "rpd_no_session@example.com")
    res = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={},
        headers=_auth(token),
    )
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Status SUCCESS round-trip
# ---------------------------------------------------------------------------

def test_rpd_status_success_after_mock_complete(client):
    """Polling status after mock-complete returns SUCCESS and account details."""
    token = _register_lawyer(client, "rpd_status_success@example.com")

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    v_id = init.json()["verification_id"]

    client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={"verification_id": v_id},
        headers=_auth(token),
    )

    status = client.get(
        f"/api/v1/lawyers/me/bank-account/reverse-penny-drop/status?verification_id={v_id}",
        headers=_auth(token),
    )
    assert status.status_code == 200
    data = status.json()
    assert data["status"] == "SUCCESS"
    assert data["verified"] is True
    assert data["account_number_masked"] is not None
    assert data["ifsc_code"] is not None


# ---------------------------------------------------------------------------
# Manual bank account + RPD verify flow
# ---------------------------------------------------------------------------

def test_rpd_verify_on_manually_added_account(client):
    """Lawyer who manually added an account can run RPD to verify it."""
    token = _register_lawyer(client, "rpd_manual_acct@example.com")

    client.post("/api/v1/lawyers/me/bank-account", json={
        "account_holder_name": "Adv. Manual RPD",
        "account_number": "111122223333",
        "ifsc_code": "SBIN0001111",
        "bank_name": "SBI",
    }, headers=_auth(token))

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert init.status_code == 200
    v_id = init.json()["verification_id"]

    mc = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete",
        json={"verification_id": v_id},
        headers=_auth(token),
    )
    assert mc.json()["verified"] is True

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=_auth(token)).json()
    assert acct["verified"] is True


# ---------------------------------------------------------------------------
# Access Control
# ---------------------------------------------------------------------------

def test_rpd_initiate_requires_auth(client):
    """RPD initiate endpoint requires a valid JWT."""
    res = client.post("/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate")
    assert res.status_code in (401, 403)


def test_rpd_initiate_blocked_for_non_lawyer(client):
    """Clients cannot initiate RPD - requires LAWYER role."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "rpd_client@example.com",
        "password": "secure-rpd-client-123",
        "full_name": "Non Lawyer Client",
        "role": "client",
        "consent_privacy_policy": True,
        "consent_terms": True,
    })
    token = reg.json()["access_token"]
    res = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    assert res.status_code in (403, 401)


# ---------------------------------------------------------------------------
# Webhook Handler
# ---------------------------------------------------------------------------

def test_rpd_webhook_verifies_account_on_success_event(client, database):
    """
    Cashfree RPD SUCCESS webhook marks the lawyer bank account as verified,
    saving remitter details (account number, IFSC, UTR) from the payload.
    """
    token = _register_lawyer(client, "rpd_webhook@example.com", "Adv. Webhook")

    init = client.post(
        "/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate",
        headers=_auth(token),
    )
    v_id = init.json()["verification_id"]

    webhook_payload = {
        "type": "REVERSE_PENNY_DROP_SUCCESS_WEBHOOK",
        "verification_id": v_id,
        "status": "SUCCESS",
        "data": {
            "verification_id": v_id,
            "status": "SUCCESS",
            "remitter_details": {
                "utr": "UTR2026091400001",
                "account_number": "50100498765432",
                "ifsc": "HDFC0001234",
                "name_at_bank": "ADV WEBHOOK LAWYER",
                "bank_name": "HDFC Bank",
                "vpa": "webhook@okhdfcbank",
            },
        },
    }

    from unittest.mock import patch
    with patch("backend.routers.webhooks.verify_cashfree_signature", return_value=True):
        res = client.post(
            "/api/v1/webhooks/cashfree",
            content=json.dumps(webhook_payload),
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": "1234567890",
                "x-webhook-signature": "mock-sig",
            },
        )

    assert res.status_code == 200, res.text
    assert res.json().get("event") == "rpd_verified"

    acct = client.get("/api/v1/lawyers/me/bank-account", headers=_auth(token)).json()
    assert acct["verified"] is True
    assert acct["ifsc_code"] == "HDFC0001234"
    assert acct["utr"] == "UTR2026091400001"
    assert "50100498765432" not in acct["account_number_masked"]
    assert acct["account_number_masked"].endswith("5432")


def test_rpd_webhook_unknown_verification_id_returns_ok(client):
    """Webhook with unknown verification_id is gracefully ignored."""
    webhook_payload = {
        "type": "REVERSE_PENNY_DROP_SUCCESS_WEBHOOK",
        "verification_id": "NONEXISTENT_VID_XXXX",
        "status": "SUCCESS",
        "data": {"verification_id": "NONEXISTENT_VID_XXXX", "status": "SUCCESS"},
    }
    from unittest.mock import patch
    with patch("backend.routers.webhooks.verify_cashfree_signature", return_value=True):
        res = client.post(
            "/api/v1/webhooks/cashfree",
            content=json.dumps(webhook_payload),
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": "1234567890",
                "x-webhook-signature": "mock-sig",
            },
        )
    assert res.status_code == 200


def test_rpd_webhook_rejects_invalid_signature(client):
    """Webhook with a bad signature is rejected with 400."""
    # In test env, CASHFREE_SECRET_KEY is empty so the real function allows all.
    # Explicitly patch it to return False to test the rejection path.
    from unittest.mock import patch
    with patch("backend.routers.webhooks.verify_cashfree_signature", return_value=False):
        res = client.post(
            "/api/v1/webhooks/cashfree",
            content=json.dumps({"type": "REVERSE_PENNY_DROP_SUCCESS_WEBHOOK"}),
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": "bad",
                "x-webhook-signature": "bad-sig",
            },
        )
    assert res.status_code == 400

