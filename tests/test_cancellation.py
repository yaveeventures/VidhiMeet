from datetime import datetime, timedelta, timezone
import pytest
from backend.models import Booking, BookingStatus, User, Role, Voucher, Practice, LawyerProfile
from backend.ntp_time import ntp_now

def register_user(client, email, role, full_name="Test User"):
    payload = {
        "email": email,
        "password": "a-secure-password-123",
        "full_name": full_name,
        "role": role,
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()["access_token"]


def verify_lawyer(database, user_id):
    profile = database.query(LawyerProfile).filter_by(user_id=user_id).first()
    if profile:
        profile.verified = True
        profile.practice = [Practice.FAMILY, Practice.CORPORATE]
        database.commit()


def create_confirmed_booking(client, client_token, lawyer_id, starts_at_iso):
    headers = {"Authorization": f"Bearer {client_token}"}
    payload = {
        "lawyer_id": lawyer_id,
        "practice": "family",
        "starts_at": starts_at_iso,
        "duration_minutes": 45,
        "intake": {
            "matter_type": "Divorce",
            "children_involved": "No",
            "existing_order": "None"
        },
        "disclaimer_accepted": True,
        "disclaimer_version": "2026-01"
    }
    res = client.post("/api/v1/bookings", json=payload, headers=headers)
    assert res.status_code == 201
    booking_id = res.json()["id"]

    # Confirm booking payment
    res_confirm = client.post(f"/api/v1/bookings/{booking_id}/confirm-payment", headers=headers)
    assert res_confirm.status_code == 200
    return booking_id


def test_client_cancel_more_than_24h_full_refund(client, database):
    c_token = register_user(client, "c_cancel1@example.com", "client", "Client Cancel1")
    l_token = register_user(client, "l_cancel1@example.com", "lawyer", "Lawyer Cancel1")
    lawyer_user = database.query(User).filter_by(email="l_cancel1@example.com").first()
    verify_lawyer(database, lawyer_user.id)

    now_dt = datetime.now(timezone.utc)
    starts_at = now_dt + timedelta(hours=36) # 36 hours in future (>24h)
    starts_iso = starts_at.isoformat()

    b_id = create_confirmed_booking(client, c_token, lawyer_user.id, starts_iso)
    headers = {"Authorization": f"Bearer {c_token}"}

    # Preview
    preview = client.get(f"/api/v1/bookings/{b_id}/cancellation-preview", headers=headers)
    assert preview.status_code == 200
    pdata = preview.json()
    assert pdata["policy_tier"] == "client_more_than_24h"
    assert pdata["refund_pct"] == 100
    assert pdata["penalty_pct"] == 0

    # Cancel
    cancel_res = client.post(f"/api/v1/bookings/{b_id}/cancel", json={"reason": "Plans changed"}, headers=headers)
    assert cancel_res.status_code == 200
    cdata = cancel_res.json()
    assert cdata["status"] == "cancelled"
    assert cdata["cancelled_by_role"] == "client"
    assert cdata["refund_amount_minor"] == pdata["total_amount_minor"]
    assert cdata["penalty_amount_minor"] == 0
    assert "within 3 to 5 business days" in cdata["reversal_timeline_notice"]


def test_client_cancel_between_2h_and_24h_partial_refund(client, database):
    c_token = register_user(client, "c_cancel2@example.com", "client", "Client Cancel2")
    l_token = register_user(client, "l_cancel2@example.com", "lawyer", "Lawyer Cancel2")
    lawyer_user = database.query(User).filter_by(email="l_cancel2@example.com").first()
    verify_lawyer(database, lawyer_user.id)

    now_dt = datetime.now(timezone.utc)
    starts_at = now_dt + timedelta(hours=10) # 10 hours in future (2h-24h)
    starts_iso = starts_at.isoformat()

    b_id = create_confirmed_booking(client, c_token, lawyer_user.id, starts_iso)
    headers = {"Authorization": f"Bearer {c_token}"}

    # Cancel
    cancel_res = client.post(f"/api/v1/bookings/{b_id}/cancel", json={"reason": "Work emergency"}, headers=headers)
    assert cancel_res.status_code == 200
    cdata = cancel_res.json()
    assert cdata["status"] == "cancelled"
    assert cdata["refund_amount_minor"] > 0
    assert cdata["penalty_amount_minor"] > 0


def test_client_cancel_under_2h_zero_refund(client, database):
    c_token = register_user(client, "c_cancel3@example.com", "client", "Client Cancel3")
    l_token = register_user(client, "l_cancel3@example.com", "lawyer", "Lawyer Cancel3")
    lawyer_user = database.query(User).filter_by(email="l_cancel3@example.com").first()
    verify_lawyer(database, lawyer_user.id)

    now_dt = datetime.now(timezone.utc)
    starts_at = now_dt + timedelta(minutes=45) # 45 mins in future (<2h)
    starts_iso = starts_at.isoformat()

    b_id = create_confirmed_booking(client, c_token, lawyer_user.id, starts_iso)
    headers = {"Authorization": f"Bearer {c_token}"}

    # Cancel
    cancel_res = client.post(f"/api/v1/bookings/{b_id}/cancel", json={"reason": "Late cancel"}, headers=headers)
    assert cancel_res.status_code == 200
    cdata = cancel_res.json()
    assert cdata["status"] == "cancelled"
    assert cdata["refund_amount_minor"] == 0
    assert cdata["penalty_amount_minor"] > 0


def test_lawyer_cancel_full_refund_plus_voucher(client, database):
    c_token = register_user(client, "c_cancel4@example.com", "client", "Client Cancel4")
    l_token = register_user(client, "l_cancel4@example.com", "lawyer", "Lawyer Cancel4")
    lawyer_user = database.query(User).filter_by(email="l_cancel4@example.com").first()
    verify_lawyer(database, lawyer_user.id)

    now_dt = datetime.now(timezone.utc)
    starts_at = now_dt + timedelta(hours=3)
    starts_iso = starts_at.isoformat()

    b_id = create_confirmed_booking(client, c_token, lawyer_user.id, starts_iso)
    l_headers = {"Authorization": f"Bearer {l_token}"}

    # Lawyer cancels
    cancel_res = client.post(f"/api/v1/bookings/{b_id}/cancel", json={"reason": "Court hearing conflict"}, headers=l_headers)
    assert cancel_res.status_code == 200
    cdata = cancel_res.json()
    assert cdata["status"] == "cancelled"
    assert cdata["cancelled_by_role"] == "lawyer"
    assert cdata["refund_amount_minor"] > 0
    assert cdata["voucher_code"] is not None
    assert cdata["voucher_code"].startswith("REBOOK-")

    # Verify voucher stored in database
    v = database.query(Voucher).filter_by(code=cdata["voucher_code"]).first()
    assert v is not None
    assert v.discount_percent == 20


def test_cancelled_slot_relisting(client, database):
    c1_token = register_user(client, "c_relist1@example.com", "client", "Client Relist1")
    c2_token = register_user(client, "c_relist2@example.com", "client", "Client Relist2")
    l_token = register_user(client, "l_relist@example.com", "lawyer", "Lawyer Relist")
    lawyer_user = database.query(User).filter_by(email="l_relist@example.com").first()
    verify_lawyer(database, lawyer_user.id)

    now_dt = datetime.now(timezone.utc)
    starts_at = now_dt + timedelta(hours=48)
    starts_iso = starts_at.isoformat()

    # Client 1 books
    b1_id = create_confirmed_booking(client, c1_token, lawyer_user.id, starts_iso)

    # Client 1 cancels
    c1_headers = {"Authorization": f"Bearer {c1_token}"}
    client.post(f"/api/v1/bookings/{b1_id}/cancel", json={"reason": "Cancelled"}, headers=c1_headers)

    # Client 2 books exact same slot -> Success
    b2_id = create_confirmed_booking(client, c2_token, lawyer_user.id, starts_iso)
    assert b2_id != b1_id
