import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import (
    Booking, BookingStatus, DraftingRequest, DraftingStatus,
    LawyerBankAccount, LawyerProfile, Role, User
)
from backend.security import create_access_token, hash_password
from backend.services.payout_service import sweep_all_payouts, sweep_booking_payouts, sweep_draft_payouts


def _create_user(db: Session, email: str, role: Role, name: str) -> User:
    u = User(
        email=email,
        password_hash=hash_password("Pass123!"),
        full_name=name,
        role=role,
    )
    db.add(u)
    db.commit()
    return u


def _create_verified_bank(db: Session, user_id: str) -> LawyerBankAccount:
    acct = LawyerBankAccount(
        user_id=user_id,
        account_holder_name="Advocate Test",
        account_number="123456789012",
        ifsc_code="HDFC0001234",
        bank_name="HDFC Bank",
        verified=True,
        verified_at=datetime.now(timezone.utc),
        verification_status="verified",
    )
    db.add(acct)
    db.commit()
    return acct


def _create_lawyer_profile_with_pan(db: Session, user_id: str, pan: str = "ABCDE1234F") -> LawyerProfile:
    """Creates a LawyerProfile with a PAN number for the given lawyer user."""
    profile = LawyerProfile(
        user_id=user_id,
        practice=["property"],
        bar_number=f"BARTEST{user_id[:6]}",
        languages=["English"],
        hourly_fee_minor=150000,
        pan_number=pan,
    )
    db.add(profile)
    db.commit()
    return profile


def test_booking_completed_sets_deadline_and_pending_payout(client: TestClient, database: Session):
    client_user = _create_user(database, "cl_payout_1@test.com", Role.CLIENT, "Client One")
    lawyer_user = _create_user(database, "lw_payout_1@test.com", Role.LAWYER, "Lawyer One")

    starts = datetime.now(timezone.utc) - timedelta(hours=1)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="corporate",
        starts_at=starts,
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.CONFIRMED,
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="lc-test-payout-room-1",
    )
    database.add(booking)
    database.commit()

    token = create_access_token({"sub": client_user.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(f"/api/v1/bookings/{booking.id}/complete", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["payout_status"] == "pending"
    assert data["completed_at"] is not None
    assert data["dispute_deadline_at"] is not None

    # Verify dispute deadline is approx 7 days in future
    deadline = datetime.fromisoformat(data["dispute_deadline_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff_days = (deadline - now).total_seconds() / 86400
    assert 6.9 < diff_days < 7.1


def test_dispute_window_enforced(client: TestClient, database: Session):
    client_user = _create_user(database, "cl_payout_2@test.com", Role.CLIENT, "Client Two")
    lawyer_user = _create_user(database, "lw_payout_2@test.com", Role.LAWYER, "Lawyer Two")

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="family",
        starts_at=now - timedelta(days=10),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        completed_at=now - timedelta(days=9),
        dispute_deadline_at=now - timedelta(days=2),  # 2 days expired!
        payout_status="pending",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now - timedelta(days=10),
        jitsi_room="lc-test-payout-room-2",
    )
    database.add(booking)
    database.commit()

    token = create_access_token({"sub": client_user.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        f"/api/v1/bookings/{booking.id}/dispute",
        headers=headers,
        json={"category": "quality_other", "reason": "Too late dispute attempt"}
    )
    assert res.status_code == 400
    assert "Dispute window has expired" in res.json()["detail"]


def test_dispute_within_window_allowed(client: TestClient, database: Session):
    client_user = _create_user(database, "cl_payout_3@test.com", Role.CLIENT, "Client Three")
    lawyer_user = _create_user(database, "lw_payout_3@test.com", Role.LAWYER, "Lawyer Three")

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="family",
        starts_at=now - timedelta(days=3),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        completed_at=now - timedelta(days=3),
        dispute_deadline_at=now + timedelta(days=4),  # 4 days remaining!
        payout_status="pending",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now - timedelta(days=3),
        jitsi_room="lc-test-payout-room-3",
    )
    database.add(booking)
    database.commit()

    token = create_access_token({"sub": client_user.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        f"/api/v1/bookings/{booking.id}/dispute",
        headers=headers,
        json={"category": "quality_other", "reason": "Timely dispute attempt"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "disputed"


def test_payout_sweep_processes_expired_bookings(database: Session):
    client_user = _create_user(database, "cl_payout_4@test.com", Role.CLIENT, "Client Four")
    lawyer_user = _create_user(database, "lw_payout_4@test.com", Role.LAWYER, "Lawyer Four")
    _create_verified_bank(database, lawyer_user.id)
    _create_lawyer_profile_with_pan(database, lawyer_user.id)

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="property",
        starts_at=now - timedelta(days=8),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        completed_at=now - timedelta(days=8),
        dispute_deadline_at=now - timedelta(days=1),  # Expired
        payout_status="pending",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now - timedelta(days=8),
        jitsi_room="lc-test-payout-room-4",
    )
    database.add(booking)
    database.commit()

    res = sweep_booking_payouts(database)
    assert res["processed"] >= 1

    database.refresh(booking)
    assert booking.payout_status == "paid"
    assert booking.payout_reference_id is not None
    assert booking.payout_at is not None


def test_payout_held_without_verified_bank(database: Session):
    client_user = _create_user(database, "cl_payout_5@test.com", Role.CLIENT, "Client Five")
    lawyer_user = _create_user(database, "lw_payout_5@test.com", Role.LAWYER, "Lawyer Five")
    # No verified bank account added for lawyer_user!

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="property",
        starts_at=now - timedelta(days=8),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        completed_at=now - timedelta(days=8),
        dispute_deadline_at=now - timedelta(days=1),
        payout_status="pending",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now - timedelta(days=8),
        jitsi_room="lc-test-payout-room-5",
    )
    database.add(booking)
    database.commit()

    res = sweep_booking_payouts(database)
    assert res["held"] >= 1

    database.refresh(booking)
    assert booking.payout_status == "held"


def test_payout_held_without_pan(database: Session):
    """Verify payouts are held when lawyer has a verified bank but no PAN on file."""
    client_user = _create_user(database, "cl_payout_nopan@test.com", Role.CLIENT, "Client NoPAN")
    lawyer_user = _create_user(database, "lw_payout_nopan@test.com", Role.LAWYER, "Lawyer NoPAN")
    _create_verified_bank(database, lawyer_user.id)
    # Deliberately NOT creating a LawyerProfile with PAN

    now = datetime.now(timezone.utc)
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer_user.id,
        practice="property",
        starts_at=now - timedelta(days=8),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        completed_at=now - timedelta(days=8),
        dispute_deadline_at=now - timedelta(days=1),
        payout_status="pending",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=now - timedelta(days=8),
        jitsi_room="lc-test-payout-nopan-room",
    )
    database.add(booking)
    database.commit()

    res = sweep_booking_payouts(database)
    # Should be held due to missing PAN (even though bank account is verified)
    assert res["held"] >= 1

    database.refresh(booking)
    assert booking.payout_status == "held"



def test_draft_payout_triggers_on_approval(client: TestClient, database: Session):
    creator = _create_user(database, "creator_draft_1@test.com", Role.CLIENT, "Draft Creator")
    drafter = _create_user(database, "drafter_1@test.com", Role.LAWYER, "Draft Drafter")
    _create_verified_bank(database, drafter.id)
    _create_lawyer_profile_with_pan(database, drafter.id)

    draft = DraftingRequest(
        title="Commercial Lease Agreement",
        description="Drafting commercial lease",
        price_minor=500000,
        agreed_price_minor=500000,
        creator_id=creator.id,
        drafter_id=drafter.id,
        status=DraftingStatus.SUBMITTED,
        draft_text="Drafted terms...",
        draft_file_key="contracts/lease.pdf",
        draft_filename="lease.pdf",
        submitted_at=datetime.now(timezone.utc),
    )
    database.add(draft)
    database.commit()

    token = create_access_token({"sub": creator.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(f"/api/v1/drafting/{draft.id}/approve", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None
    assert data["payout_status"] == "paid"
    assert data["payout_reference_id"] is not None


def test_draft_payout_held_without_verified_bank(client: TestClient, database: Session):
    creator = _create_user(database, "creator_draft_2@test.com", Role.CLIENT, "Draft Creator 2")
    drafter = _create_user(database, "drafter_2@test.com", Role.LAWYER, "Draft Drafter 2")
    # No bank account for drafter

    draft = DraftingRequest(
        title="Employment Agreement",
        description="Drafting employment contract",
        price_minor=300000,
        agreed_price_minor=300000,
        creator_id=creator.id,
        drafter_id=drafter.id,
        status=DraftingStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )
    database.add(draft)
    database.commit()

    token = create_access_token({"sub": creator.id, "role": Role.CLIENT.value})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(f"/api/v1/drafting/{draft.id}/approve", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["payout_status"] == "held"


def test_admin_force_release_endpoints(client: TestClient, database: Session):
    admin = _create_user(database, "admin_payout_test@test.com", Role.ADMIN, "Admin User")
    lawyer = _create_user(database, "lawyer_force_test@test.com", Role.LAWYER, "Adv. Force")
    _create_verified_bank(database, lawyer.id)
    _create_lawyer_profile_with_pan(database, lawyer.id)
    client_user = _create_user(database, "client_force_test@test.com", Role.CLIENT, "Client Force")

    # 1. Booking force release
    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer.id,
        practice="corporate",
        starts_at=datetime.now(timezone.utc) - timedelta(days=2),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.COMPLETED,
        payout_status="held",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="lc-force-payout-booking",
    )
    database.add(booking)

    # 2. Draft force release
    draft = DraftingRequest(
        title="NDA Draft",
        description="Mutual NDA",
        price_minor=200000,
        agreed_price_minor=200000,
        creator_id=client_user.id,
        drafter_id=lawyer.id,
        status=DraftingStatus.COMPLETED,
        payout_status="held",
    )
    database.add(draft)
    database.commit()

    token = create_access_token({"sub": admin.id, "role": Role.ADMIN.value})
    headers = {"Authorization": f"Bearer {token}"}

    # Force release booking
    b_res = client.post(f"/api/v1/admin/payouts/bookings/{booking.id}/release", headers=headers)
    assert b_res.status_code == 200
    assert b_res.json()["payout"]["status"] == "paid"

    # Force release draft
    d_res = client.post(f"/api/v1/admin/payouts/drafts/{draft.id}/release", headers=headers)
    assert d_res.status_code == 200
    assert d_res.json()["payout"]["status"] == "paid"


def test_admin_pending_payouts_and_sweep_endpoints(client: TestClient, database: Session):
    admin = _create_user(database, "admin_sweep_test@test.com", Role.ADMIN, "Admin Sweep")
    token = create_access_token({"sub": admin.id, "role": Role.ADMIN.value})
    headers = {"Authorization": f"Bearer {token}"}

    # Pending payouts query
    pending_res = client.get("/api/v1/admin/payouts/pending", headers=headers)
    assert pending_res.status_code == 200
    assert isinstance(pending_res.json(), list)

    # Sweep trigger
    sweep_res = client.post("/api/v1/admin/payouts/sweep", headers=headers)
    assert sweep_res.status_code == 200
    data = sweep_res.json()
    assert "bookings" in data
    assert "drafts" in data
    assert "total_processed" in data


def test_admin_resolve_dispute_release_triggers_payout(client: TestClient, database: Session):
    admin = _create_user(database, "admin_dispute_rel@test.com", Role.ADMIN, "Admin Resolve")
    lawyer = _create_user(database, "lawyer_dispute_rel@test.com", Role.LAWYER, "Adv. Rel")
    _create_verified_bank(database, lawyer.id)
    _create_lawyer_profile_with_pan(database, lawyer.id)
    client_user = _create_user(database, "client_dispute_rel@test.com", Role.CLIENT, "Client Rel")

    booking = Booking(
        client_id=client_user.id,
        lawyer_id=lawyer.id,
        practice="family",
        starts_at=datetime.now(timezone.utc) - timedelta(days=2),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.DISPUTED,
        dispute_category="quality_other",
        dispute_reason="Call disconnected early",
        intake={},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="lc-dispute-rel-room",
    )
    database.add(booking)
    database.commit()

    token = create_access_token({"sub": admin.id, "role": Role.ADMIN.value})
    headers = {"Authorization": f"Bearer {token}"}

    patch_res = client.patch(
        f"/api/v1/admin/bookings/{booking.id}/resolve?outcome=release",
        headers=headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "completed"

    database.refresh(booking)
    assert booking.payout_status == "paid"
    assert booking.payout_reference_id is not None
