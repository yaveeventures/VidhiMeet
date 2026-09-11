import base64
import hashlib
import hmac
import json
import pytest
from datetime import datetime, timezone, timedelta
from backend.services.payment_service import (
    create_cashfree_order,
    get_cashfree_order,
    verify_cashfree_signature,
    initiate_refund,
)
from backend.models import Booking, BookingStatus, Practice, Role, User
from backend.config import get_settings


def test_verify_cashfree_signature_hmac():
    settings = get_settings()
    original_secret = settings.cashfree_secret_key
    try:
        settings.cashfree_secret_key = "test_secret_key_12345"
        timestamp = "1692257212"
        raw_body = b'{"data":{"order":{"order_id":"order_test_123"}},"type":"PAYMENT_SUCCESS_WEBHOOK"}'

        # Compute valid signature
        data = timestamp.encode("utf-8") + raw_body
        expected_sig = base64.b64encode(
            hmac.new(b"test_secret_key_12345", data, hashlib.sha256).digest()
        ).decode("utf-8")

        assert verify_cashfree_signature(raw_body, timestamp, expected_sig) is True
        assert verify_cashfree_signature(raw_body, timestamp, "invalid_sig_abc") is False
    finally:
        settings.cashfree_secret_key = original_secret


def test_create_cashfree_order_fallback():
    user = User(id="user-123", email="client@vidhimeet.in", full_name="Client Test", role=Role.CLIENT)
    booking = Booking(id="book-456", client_id=user.id, lawyer_id="lawyer-789",
                      practice=Practice.PROPERTY, amount_minor=150000,
                      disclaimer_version="2026-01", disclaimer_accepted_at=datetime.now(timezone.utc),
                      jitsi_room="room-123")
    
    order = create_cashfree_order(booking, user)
    assert order["order_id"].startswith("order_")
    assert "payment_session_id" in order
    assert order["order_status"] in ("ACTIVE", "PAID")


def test_cashfree_webhook_endpoint(client, database):
    # Setup test user, lawyer, booking
    from backend.security import hash_password
    lawyer_user = User(email="lawyer_cf@test.com", password_hash=hash_password("pw123"),
                       full_name="Lawyer CF", role=Role.LAWYER)
    client_user = User(email="client_cf@test.com", password_hash=hash_password("pw123"),
                       full_name="Client CF", role=Role.CLIENT)
    database.add(lawyer_user)
    database.add(client_user)
    database.commit()

    test_order_id = "order_cf_test_webhook_999"
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice=Practice.CORPORATE,
        starts_at=datetime.now(timezone.utc) + timedelta(days=2),
        duration_minutes=45,
        amount_minor=200000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "test"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        cashfree_order_id=test_order_id,
        jitsi_room="room-cf-123"
    )
    database.add(booking)
    database.commit()

    webhook_payload = {
        "data": {
            "order": {
                "order_id": test_order_id,
                "order_amount": 2000.0,
                "order_currency": "INR"
            },
            "payment": {
                "payment_status": "SUCCESS"
            }
        },
        "type": "PAYMENT_SUCCESS_WEBHOOK"
    }

    resp = client.post(
        "/api/v1/webhooks/cashfree",
        json=webhook_payload,
        headers={"x-webhook-timestamp": "12345678", "x-webhook-signature": "dev_mock"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "OK"}

    database.refresh(booking)
    assert booking.status == BookingStatus.CONFIRMED


def test_verify_payment_endpoint(client, database):
    from backend.security import create_access_token, hash_password
    c_user = User(email="client_verify@test.com", password_hash=hash_password("Password123!"),
                  full_name="Client Verify", role=Role.CLIENT)
    l_user = User(email="lawyer_verify@test.com", password_hash=hash_password("Password123!"),
                  full_name="Lawyer Verify", role=Role.LAWYER)
    database.add(c_user)
    database.add(l_user)
    database.commit()

    token = create_access_token(c_user)

    booking = Booking(
        client_id=c_user.id,
        lawyer_id=l_user.id,
        practice=Practice.FAMILY,
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=150000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "test"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        cashfree_order_id="order_mock_test_verify",
        jitsi_room="room-verify-123"
    )
    database.add(booking)
    database.commit()

    resp = client.post(
        f"/api/v1/bookings/{booking.id}/verify-payment",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["booking_status"] == "confirmed"

    database.refresh(booking)
    assert booking.status == BookingStatus.CONFIRMED
