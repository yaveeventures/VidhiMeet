def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_and_role_protection(client):
    payload = {"email": "client@example.com", "password": "a-secure-password-123",
               "full_name": "Test Client", "role": "client",
               "consent_privacy_policy": True, "consent_terms": True}
    registered = client.post("/api/v1/auth/register", json=payload)
    assert registered.status_code == 201
    assert registered.json()["access_token"]
    logged_in = client.post("/api/v1/auth/login",
                            json={"email": payload["email"], "password": payload["password"]})
    assert logged_in.status_code == 200
    forbidden = client.get("/api/v1/admin/metrics",
                           headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"})
    assert forbidden.status_code == 403


def test_rejects_admin_self_registration(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "admin@example.com", "password": "a-secure-password-123",
        "full_name": "Bad Admin", "role": "admin",
        "consent_privacy_policy": True, "consent_terms": True})
    assert response.status_code == 422


def test_booking_requires_authentication(client):
    response = client.post("/api/v1/bookings", json={})
    assert response.status_code == 401


def test_refresh_token_rotation(client):
    # Register client
    reg = client.post("/api/v1/auth/register", json={
        "email": "refresher@example.com", "password": "a-secure-password-123",
        "full_name": "Refresher Test", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    assert reg.status_code == 201
    refresh_token = reg.json()["refresh_token"]

    # Exchange refresh token
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    # Reuse old refresh token should fail because of rotation/revocation
    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reused.status_code == 401


def test_lawyer_profile_update(client):
    # Register lawyer
    reg = client.post("/api/v1/auth/register", json={
        "email": "lawyer1@example.com", "password": "a-secure-password-123",
        "full_name": "Adv. Lawyer One", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]

    # Get my profile (will auto-create a pending profile)
    profile = client.get("/api/v1/lawyers/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["bar_number"].startswith("PENDING-")

    # Update my profile
    update = client.put("/api/v1/lawyers/me", json={
        "full_name": "Adv. Lawyer Updated",
        "practice": "corporate",
        "bar_number": "CORP/2026/001",
        "languages": ["English", "French"],
        "hourly_fee_minor": 150000,
        "availability": {"monday": {"active": True, "start": "10:00 AM", "end": "05:00 PM"}},
        "enrollment_date": "2020-01-01",
        "practice_address": "123 Court Street",
        "aadhaar_number": "123456789012",
        "mobile_number": "9876543210"
    }, headers={"Authorization": f"Bearer {token}"})
    assert update.status_code == 200

    # Retrieve updated profile
    profile = client.get("/api/v1/lawyers/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["full_name"] == "Adv. Lawyer Updated"
    assert profile.json()["bar_number"] == "CORP/2026/001"
    assert profile.json()["verified"] is False


def test_meeting_token_endpoint(client):
    from backend.db import get_db
    from backend.models import LawyerProfile, Booking, BookingStatus
    from datetime import datetime, timezone, timedelta
    
    # Register client
    reg_client = client.post("/api/v1/auth/register", json={
        "email": "tclient@example.com", "password": "a-secure-password-123",
        "full_name": "Test Client", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    client_token = reg_client.json()["access_token"]
    
    # Register lawyer
    client.post("/api/v1/auth/register", json={
        "email": "tlawyer@example.com", "password": "a-secure-password-123",
        "full_name": "Adv. Test Lawyer", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    
    # Query database to set lawyer profile to verified and get client/lawyer ids
    db = next(get_db())
    from backend.models import User
    c_user = db.query(User).filter(User.email == "tclient@example.com").first()
    l_user = db.query(User).filter(User.email == "tlawyer@example.com").first()
    
    # Verify lawyer profile
    db.query(LawyerProfile).filter(LawyerProfile.user_id == l_user.id).update({"verified": True, "practice": "family"})
    
    # Create a confirmed booking
    booking = Booking(
        client_id=c_user.id,
        lawyer_id=l_user.id,
        practice="family",
        starts_at=datetime.now(timezone.utc),
        duration_minutes=45,
        amount_minor=150000,
        intake={"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        status=BookingStatus.CONFIRMED,
        jitsi_room="test-daily-room-xyz"
    )
    db.add(booking)
    db.commit()
    
    # Request meeting token
    response = client.post(f"/api/v1/bookings/{booking.id}/meeting-token", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "room_name" in data
    assert data["room_name"] in ("test-daily-room-xyz", "hello")


def test_verified_reviews_only(client):
    from backend.db import get_db
    from backend.models import User, LawyerProfile, Booking, BookingStatus
    from datetime import datetime, timezone, timedelta

    # 1. Register Client A and Client B
    reg_a = client.post("/api/v1/auth/register", json={
        "email": "client_a@example.com", "password": "secure-password-a",
        "full_name": "Client A", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token_a = reg_a.json()["access_token"]

    reg_b = client.post("/api/v1/auth/register", json={
        "email": "client_b@example.com", "password": "secure-password-b",
        "full_name": "Client B", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    token_b = reg_b.json()["access_token"]

    # 2. Register a lawyer
    client.post("/api/v1/auth/register", json={
        "email": "lawyer_r@example.com", "password": "secure-password-l",
        "full_name": "Adv. Reviewed Lawyer", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })

    db = next(get_db())
    c_a = db.query(User).filter(User.email == "client_a@example.com").first()
    l_user = db.query(User).filter(User.email == "lawyer_r@example.com").first()

    # Verify lawyer profile
    db.query(LawyerProfile).filter(LawyerProfile.user_id == l_user.id).update({"verified": True, "practice": "family"})
    
    # 3. Create a booking for Client A
    booking = Booking(
        client_id=c_a.id,
        lawyer_id=l_user.id,
        practice="family",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=150000,
        intake={"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        status=BookingStatus.PENDING_PAYMENT,
        jitsi_room="test-review-room"
    )
    db.add(booking)
    db.commit()

    # 4. Review submission is disabled under BCI Rule 36
    review_payload = {"rating": 5, "comment": "Excellent consultation"}
    res = client.post(f"/api/v1/bookings/{booking.id}/review", json=review_payload, headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 400
    assert "Rule 36" in res.json()["detail"]


def test_booking_duration_validation(client):
    # Register client
    reg_client = client.post("/api/v1/auth/register", json={
        "email": "durationclient@example.com", "password": "a-secure-password-123",
        "full_name": "Duration Client", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    client_token = reg_client.json()["access_token"]
    
    # Try to create a booking with 60 minutes (which is > 45)
    from datetime import datetime, timezone, timedelta
    payload = {
        "lawyer_id": "some-lawyer-id",
        "practice": "family",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "duration_minutes": 60,
        "intake": {"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        "disclaimer_accepted": True,
        "disclaimer_version": "2026-01"
    }
    
    res = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {client_token}"})
    assert res.status_code == 422
    assert "duration_minutes" in res.text


def test_lawyer_complete_booking_duration_restriction(client):
    from unittest.mock import patch
    from backend.db import get_db
    from backend.models import User, LawyerProfile, Booking, BookingStatus
    from datetime import datetime, timezone, timedelta

    # Register client
    client.post("/api/v1/auth/register", json={
        "email": "c_comp@example.com", "password": "secure-password-123",
        "full_name": "Client Complete", "role": "client",
        "consent_privacy_policy": True, "consent_terms": True
    })
    
    # Register lawyer
    reg_l = client.post("/api/v1/auth/register", json={
        "email": "l_comp@example.com", "password": "secure-password-123",
        "full_name": "Adv. Lawyer Complete", "role": "lawyer",
        "consent_privacy_policy": True, "consent_terms": True
    })
    lawyer_token = reg_l.json()["access_token"]
    
    db = next(get_db())
    c_user = db.query(User).filter(User.email == "c_comp@example.com").first()
    l_user = db.query(User).filter(User.email == "l_comp@example.com").first()
    
    # Verify lawyer profile
    db.query(LawyerProfile).filter(LawyerProfile.user_id == l_user.id).update({"verified": True, "practice": "family"})
    
    # Create booking
    booking = Booking(
        client_id=c_user.id,
        lawyer_id=l_user.id,
        practice="family",
        starts_at=datetime.now(timezone.utc),
        duration_minutes=45,
        amount_minor=150000,
        intake={"matter_type": "General advice", "children_involved": "No", "existing_order": "No"},
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        status=BookingStatus.CONFIRMED,
        jitsi_room="test-comp-room"
    )
    db.add(booking)
    db.commit()
    
    # Patch verify_daily_meeting_duration to return 5 minutes (less than 15 mins)
    with patch("backend.services.verify_daily_meeting_duration", return_value=5.0):
        res = client.post(f"/api/v1/bookings/{booking.id}/complete", headers={"Authorization": f"Bearer {lawyer_token}"})
        assert res.status_code == 400
        assert "duration is too short" in res.json()["detail"]
        
    # Patch verify_daily_meeting_duration to return 20 minutes (greater than 15 mins)
    with patch("backend.services.verify_daily_meeting_duration", return_value=20.0):
        res = client.post(f"/api/v1/bookings/{booking.id}/complete", headers={"Authorization": f"Bearer {lawyer_token}"})
        assert res.status_code == 200
        assert res.json()["status"] == "completed"


def test_video_consultation_dual_platform_fee():
    from backend.models import Booking
    # Case 1: Base fee = ₹500 (50,000 paise). 5% = ₹25. Max(35, 25) = ₹35 (3,500 paise).
    # Client total charged = 50,000 + 3,500 = 53,500 paise.
    b1 = Booking(amount_minor=53500)
    assert b1.base_price_minor == 50000
    assert b1.client_platform_fee_minor == 3500
    assert b1.lawyer_platform_fee_minor == 3500
    assert b1.platform_fee_minor == 7000
    assert b1.lawyer_amount_minor == 46500

    # Case 2: Base fee = ₹1,000 (100,000 paise). 5% = ₹50. Max(35, 50) = ₹50 (5,000 paise).
    # Client total charged = 100,000 + 5,000 = 105,000 paise.
    b2 = Booking(amount_minor=105000)
    assert b2.base_price_minor == 100000
    assert b2.client_platform_fee_minor == 5000
    assert b2.lawyer_platform_fee_minor == 5000
    assert b2.platform_fee_minor == 10000
    assert b2.lawyer_amount_minor == 95000




