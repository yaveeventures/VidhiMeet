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
    
    order = create_cashfree_order(booking, user, expiry_minutes=25)
    assert order["order_id"].startswith("order_")
    assert "payment_session_id" in order
    assert order["order_status"] in ("ACTIVE", "PAID")
    assert "order_expiry_time" in order
    # Verify ISO 8601 UTC format ending with Z
    assert order["order_expiry_time"].endswith("Z")
    expiry_dt = datetime.fromisoformat(order["order_expiry_time"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    # Expiry should be roughly 25 minutes from now
    diff_minutes = (expiry_dt - now).total_seconds() / 60
    assert 24 <= diff_minutes <= 26


def test_expire_abandoned_bookings(database):
    from backend.services.payment_service import expire_abandoned_bookings
    from backend.security import hash_password

    lawyer = User(email="l_expire@test.com", password_hash=hash_password("pw123"), full_name="Lawyer E", role=Role.LAWYER)
    client_u = User(email="c_expire@test.com", password_hash=hash_password("pw123"), full_name="Client E", role=Role.CLIENT)
    database.add(lawyer)
    database.add(client_u)
    database.commit()

    now = datetime.now(timezone.utc)
    # Stale booking: created 45 minutes ago, still pending_payment
    b_stale = Booking(
        client_id=client_u.id, lawyer_id=lawyer.id, practice=Practice.PROPERTY,
        starts_at=now + timedelta(days=1), duration_minutes=30, amount_minor=100000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "test intake"},
        created_at=now - timedelta(minutes=45),
        disclaimer_version="2026-01", disclaimer_accepted_at=now, jitsi_room="r-stale"
    )
    # Fresh booking: created 5 minutes ago, still pending_payment
    b_fresh = Booking(
        client_id=client_u.id, lawyer_id=lawyer.id, practice=Practice.PROPERTY,
        starts_at=now + timedelta(days=2), duration_minutes=30, amount_minor=100000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "test intake"},
        created_at=now - timedelta(minutes=5),
        disclaimer_version="2026-01", disclaimer_accepted_at=now, jitsi_room="r-fresh"
    )
    # Confirmed booking: created 60 minutes ago, already confirmed
    b_confirmed = Booking(
        client_id=client_u.id, lawyer_id=lawyer.id, practice=Practice.PROPERTY,
        starts_at=now + timedelta(days=3), duration_minutes=30, amount_minor=100000,
        status=BookingStatus.CONFIRMED,
        intake={"notes": "test intake"},
        created_at=now - timedelta(minutes=60),
        disclaimer_version="2026-01", disclaimer_accepted_at=now, jitsi_room="r-conf"
    )

    database.add_all([b_stale, b_fresh, b_confirmed])
    database.commit()

    expired_ids = expire_abandoned_bookings(database, max_age_minutes=20)
    assert b_stale.id in expired_ids
    assert b_fresh.id not in expired_ids
    assert b_confirmed.id not in expired_ids

    database.refresh(b_stale)
    database.refresh(b_fresh)
    database.refresh(b_confirmed)

    assert b_stale.status == BookingStatus.CANCELLED
    assert b_fresh.status == BookingStatus.PENDING_PAYMENT
    assert b_confirmed.status == BookingStatus.CONFIRMED


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


def test_admin_expire_abandoned_endpoint(database):
    from backend.security import hash_password
    from backend.routers.admin import trigger_expire_abandoned_bookings

    admin_user = User(email="admin_exp@test.com", password_hash=hash_password("AdminPass123!"), full_name="Admin E", role=Role.ADMIN)
    lawyer_user = User(email="lawyer_exp@test.com", password_hash=hash_password("Pass123!"), full_name="Lawyer E", role=Role.LAWYER)
    client_user = User(email="client_exp@test.com", password_hash=hash_password("Pass123!"), full_name="Client E", role=Role.CLIENT)
    database.add_all([admin_user, lawyer_user, client_user])
    database.commit()

    now = datetime.now(timezone.utc)

    # Create stale pending booking (> 30 mins ago)
    b_stale = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice=Practice.PROPERTY,
        starts_at=now + timedelta(days=5),
        duration_minutes=30,
        amount_minor=105000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "abandoned checkout"},
        created_at=now - timedelta(minutes=40),
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now,
        jitsi_room="r-stale-admin",
    )
    database.add(b_stale)
    database.commit()

    # Trigger admin function
    res = trigger_expire_abandoned_bookings(max_age_minutes=20, admin=admin_user, db=database)
    assert res["expired_count"] >= 1
    assert b_stale.id in res["expired_ids"]

    database.refresh(b_stale)
    assert b_stale.status == BookingStatus.CANCELLED


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


def test_admin_expire_abandoned_endpoint(database):
    from backend.security import hash_password
    from backend.routers.admin import trigger_expire_abandoned_bookings

    admin_user = User(email="admin_exp@test.com", password_hash=hash_password("AdminPass123!"), full_name="Admin E", role=Role.ADMIN)
    lawyer_user = User(email="lawyer_exp@test.com", password_hash=hash_password("Pass123!"), full_name="Lawyer E", role=Role.LAWYER)
    client_user = User(email="client_exp@test.com", password_hash=hash_password("Pass123!"), full_name="Client E", role=Role.CLIENT)
    database.add_all([admin_user, lawyer_user, client_user])
    database.commit()

    now = datetime.now(timezone.utc)

    # Create stale pending booking (> 30 mins ago)
    b_stale = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice=Practice.PROPERTY,
        starts_at=now + timedelta(days=5),
        duration_minutes=30,
        amount_minor=105000,
        status=BookingStatus.PENDING_PAYMENT,
        intake={"notes": "abandoned checkout"},
        created_at=now - timedelta(minutes=40),
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now,
        jitsi_room="r-stale-admin",
    )
    database.add(b_stale)
    database.commit()

    # Trigger admin function
    res = trigger_expire_abandoned_bookings(max_age_minutes=20, admin=admin_user, db=database)
    assert res["expired_count"] >= 1
    assert b_stale.id in res["expired_ids"]

    database.refresh(b_stale)
    assert b_stale.status == BookingStatus.CANCELLED
