import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.models import Booking, BookingStatus, LawyerProfile, Role, User
from backend.security import create_access_token, hash_password


def test_dispute_workflow_matrix(client: TestClient, database: Session):
    # Setup test users
    client_user = User(
        email="client_dispute@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Dispute Client",
        role=Role.CLIENT
    )
    lawyer_user = User(
        email="lawyer_dispute@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Adv. Dispute Lawyer",
        role=Role.LAWYER
    )
    database.add_all([client_user, lawyer_user])
    database.commit()

    lawyer_profile = LawyerProfile(
        user_id=lawyer_user.id,
        bar_number="MAH/1000/2026",
        hourly_fee_minor=100000,
        strike_count=0
    )
    database.add(lawyer_profile)
    database.commit()

    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="family",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.CONFIRMED,
        intake={"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="lc-test-dispute-room"
    )
    database.add(booking)
    database.commit()

    # Generate token for client
    token = create_access_token({"sub": client_user.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Client raises dispute with category 'no_show'
    res = client.post(
        f"/api/v1/bookings/{booking.id}/dispute",
        headers=headers,
        json={
            "category": "no_show",
            "reason": "The advocate did not join the video consultation room at all."
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "refunded"
    assert "AUTO_REFUND_RECOMMENDED: Lawyer No-Show" in data["auto_resolution_status"]

    # Refresh lawyer profile and check strike count
    database.refresh(lawyer_profile)
    assert lawyer_profile.strike_count == 1


def test_dispute_intermediary_shield(client: TestClient, database: Session):
    client_user = User(
        email="client_shield@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Shield Client",
        role=Role.CLIENT
    )
    lawyer_user = User(
        email="lawyer_shield@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Adv. Shield Lawyer",
        role=Role.LAWYER
    )
    database.add_all([client_user, lawyer_user])
    database.commit()

    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="corporate",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=200000,
        status=BookingStatus.CONFIRMED,
        intake={"business_type": "Startup", "help_needed": "Review", "deadline": "Asap"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="lc-test-shield-room"
    )
    database.add(booking)
    database.commit()

    token = create_access_token({"sub": client_user.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    # Client raises dispute for 'quality_other'
    res = client.post(
        f"/api/v1/bookings/{booking.id}/dispute",
        headers=headers,
        json={
            "category": "quality_other",
            "reason": "I did not like the legal advice provided during the call."
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "disputed"
    assert "INTERMEDIARY_SHIELD: Attendance Verified" in data["auto_resolution_status"]
