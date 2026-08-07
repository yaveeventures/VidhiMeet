import base64
import json
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.db import get_db
from backend.models import User, LawyerProfile, Booking, BookingStatus, Role, Practice
from backend.config import get_settings

settings = get_settings()

def test_get_booking_by_id(client):
    # Register client
    reg_c = client.post("/api/v1/auth/register", json={
        "email": "phonepe_client@example.com", "password": "secure-password-123",
        "full_name": "PhonePe Client", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token = reg_c.json()["access_token"]
    
    # Register lawyer
    reg_l = client.post("/api/v1/auth/register", json={
        "email": "phonepe_lawyer@example.com", "password": "secure-password-123",
        "full_name": "Adv. PhonePe", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    
    db = next(get_db())
    c_user = db.query(User).filter(User.email == "phonepe_client@example.com").first()
    l_user = db.query(User).filter(User.email == "phonepe_lawyer@example.com").first()
    
    # Verify lawyer
    db.query(LawyerProfile).filter(LawyerProfile.user_id == l_user.id).update({"verified": True, "practice": "family"})
    db.commit()
    
    # Create booking directly
    booking = Booking(
        client_id=c_user.id,
        lawyer_id=l_user.id,
        practice="family",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=150000,
        intake={"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        status=BookingStatus.PENDING_PAYMENT,
        jitsi_room="test-phonepe-room"
    )
    db.add(booking)
    db.commit()
    
    # Try fetching it
    res = client.get(f"/api/v1/bookings/{booking.id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["id"] == booking.id
    assert res.json()["status"] == "pending_payment"

def test_phonepe_webhook_verification(client):
    db = next(get_db())
    # Create a user and booking to verify webhook matching
    client_user = User(email="webhook_c@example.com", password_hash="hash", full_name="Web Client", role=Role.CLIENT)
    lawyer_user = User(email="webhook_l@example.com", password_hash="hash", full_name="Web Lawyer", role=Role.LAWYER)
    db.add(client_user)
    db.add(lawyer_user)
    db.flush()
    
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice=Practice.FAMILY,
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        amount_minor=100000,
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        status=BookingStatus.PENDING_PAYMENT,
        phonepe_transaction_id="TXN12345TEST",
        jitsi_room="room-txn-12345"
    )
    db.add(booking)
    db.commit()
    
    # Configure mock phonepe settings
    settings.phonepe_merchant_id = "MID123"
    settings.phonepe_salt_key = "salt-key-123"
    settings.phonepe_salt_index = "1"
    
    # Construct response
    callback_payload = {
        "success": True,
        "code": "PAYMENT_SUCCESS",
        "message": "Payment successful",
        "data": {
            "merchantId": "MID123",
            "merchantTransactionId": "TXN12345TEST",
            "transactionId": "T260720120000",
            "amount": 100000
        }
    }
    
    json_bytes = json.dumps(callback_payload).encode("utf-8")
    base64_response = base64.b64encode(json_bytes).decode("utf-8")
    
    req_body = {
        "response": base64_response
    }
    
    req_body_str = json.dumps(req_body)
    
    # Signature: Method 1 (raw body + salt_key)
    hash_input = req_body_str + "salt-key-123"
    sha256_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    x_verify = f"{sha256_hash}###1"
    
    res = client.post(
        "/api/v1/webhooks/phonepe",
        content=req_body_str,
        headers={"X-VERIFY": x_verify, "Content-Type": "application/json"}
    )
    
    assert res.status_code == 200
    assert res.json()["received"] is True
    
    # Verify booking status updated to CONFIRMED
    db.refresh(booking)
    assert booking.status == BookingStatus.CONFIRMED

    # Reset credentials
    settings.phonepe_merchant_id = ""
    settings.phonepe_salt_key = ""
