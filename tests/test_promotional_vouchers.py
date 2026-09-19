import uuid
from datetime import datetime, timedelta, timezone
import pytest
from backend.models import Booking, BookingStatus, LawyerProfile, Practice, Role, User, Voucher
from backend.security import create_access_token


def _create_user(db, email, role, full_name="Test User"):
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        role=role,
        full_name=full_name,
        password_hash="test-hash",
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_header(user):
    token = create_access_token({"sub": user.id, "role": user.role.value if hasattr(user.role, "value") else str(user.role)})
    return {"Authorization": f"Bearer {token}"}


def test_admin_create_promotional_voucher(client, database):
    admin = _create_user(database, f"admin_promo_{uuid.uuid4().hex[:6]}@test.com", Role.ADMIN, "Admin Promo")
    headers = _auth_header(admin)

    # 1. Create promo voucher with 35% discount
    code = f"PROMO{uuid.uuid4().hex[:4].upper()}"
    exp = (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
    payload = {
        "code": code,
        "discount_percent": 35,
        "expires_at": exp,
        "max_uses": 50,
        "description": "35% off spring promotion"
    }
    res = client.post("/api/v1/admin/vouchers", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["code"] == code
    assert data["discount_percent"] == 35
    assert data["is_promotional"] is True
    assert data["max_uses"] == 50
    assert data["times_used"] == 0
    assert data["is_active"] is True

    # 2. List vouchers
    list_res = client.get("/api/v1/admin/vouchers", headers=headers)
    assert list_res.status_code == 200
    vouchers = list_res.json()
    assert any(v["code"] == code for v in vouchers)

    # 3. Toggle voucher status
    toggle_res = client.patch(f"/api/v1/admin/vouchers/{data['id']}/toggle?active=false", headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False

    # Toggle back
    toggle_res2 = client.patch(f"/api/v1/admin/vouchers/{data['id']}/toggle?active=true", headers=headers)
    assert toggle_res2.status_code == 200
    assert toggle_res2.json()["is_active"] is True


def test_client_cannot_create_voucher(client, database):
    c_user = _create_user(database, f"client_unauth_{uuid.uuid4().hex[:6]}@test.com", Role.CLIENT, "Client Unauth")
    headers = _auth_header(c_user)

    payload = {
        "code": "HACK50",
        "discount_percent": 50,
        "max_uses": 10
    }
    res = client.post("/api/v1/admin/vouchers", json=payload, headers=headers)
    assert res.status_code == 403


def test_validate_and_apply_promotional_voucher(client, database):
    admin = _create_user(database, f"admin_apply_{uuid.uuid4().hex[:6]}@test.com", Role.ADMIN, "Admin Apply")
    c_user = _create_user(database, f"client_apply_{uuid.uuid4().hex[:6]}@test.com", Role.CLIENT, "Client Apply")
    l_user = _create_user(database, f"lawyer_apply_{uuid.uuid4().hex[:6]}@test.com", Role.LAWYER, "Advocate Apply")

    # Setup lawyer profile
    lawyer_profile = LawyerProfile(
        id=str(uuid.uuid4()),
        user_id=l_user.id,
        practice=[Practice.CORPORATE],
        bar_number=f"MH/{uuid.uuid4().hex[:6].upper()}/2020",
        hourly_fee_minor=100000,  # ₹1000
        verified=True
    )
    database.add(lawyer_profile)
    database.commit()

    # Admin creates 25% promo voucher
    code = f"SAVE25_{uuid.uuid4().hex[:4].upper()}"
    admin_headers = _auth_header(admin)
    client_headers = _auth_header(c_user)

    create_res = client.post("/api/v1/admin/vouchers", json={
        "code": code,
        "discount_percent": 25,
        "max_uses": 2,
        "description": "25% discount"
    }, headers=admin_headers)
    assert create_res.status_code == 201

    # 1. Client validates voucher
    val_res = client.post("/api/v1/bookings/validate-voucher", json={
        "code": code,
        "lawyer_id": l_user.id,
        "duration_minutes": 45
    }, headers=client_headers)
    assert val_res.status_code == 200
    vdata = val_res.json()
    assert vdata["valid"] is True
    assert vdata["discount_percent"] == 25
    # Original: 100000 + max(3500, 5000) = 105000
    assert vdata["original_amount_minor"] == 105000
    # Discount: 25% of 105000 = 26250
    assert vdata["discount_amount_minor"] == 26250
    assert vdata["final_amount_minor"] == 78750

    # 2. Client books with voucher
    starts_at = (datetime.now(timezone.utc) + timedelta(days=2, hours=2)).isoformat()
    booking_payload = {
        "lawyer_id": l_user.id,
        "practice": "corporate",
        "starts_at": starts_at,
        "duration_minutes": 45,
        "intake": {
            "business_type": "Private Limited",
            "deadline": "1 month",
            "help_needed": "Contract review"
        },
        "disclaimer_accepted": True,
        "disclaimer_version": "2026-01",
        "voucher_code": code
    }
    book_res = client.post("/api/v1/bookings", json=booking_payload, headers=client_headers)
    assert book_res.status_code == 201
    b_data = book_res.json()
    assert b_data["amount_minor"] == 78750
    assert b_data["voucher_code"] == code

    # Check voucher usage incremented
    v_db = database.query(Voucher).filter_by(code=code).first()
    assert v_db.times_used == 1
    assert v_db.used is False  # max_uses was 2


def test_100_percent_free_promotional_voucher(client, database):
    admin = _create_user(database, f"admin_free_{uuid.uuid4().hex[:6]}@test.com", Role.ADMIN, "Admin Free")
    c_user = _create_user(database, f"client_free_{uuid.uuid4().hex[:6]}@test.com", Role.CLIENT, "Client Free")
    l_user = _create_user(database, f"lawyer_free_{uuid.uuid4().hex[:6]}@test.com", Role.LAWYER, "Advocate Free")

    lawyer_profile = LawyerProfile(
        id=str(uuid.uuid4()),
        user_id=l_user.id,
        practice=[Practice.FAMILY],
        bar_number=f"DL/{uuid.uuid4().hex[:6].upper()}/2021",
        hourly_fee_minor=50000,
        verified=True
    )
    database.add(lawyer_profile)
    database.commit()

    code = f"FREE100_{uuid.uuid4().hex[:4].upper()}"
    client.post("/api/v1/admin/vouchers", json={
        "code": code,
        "discount_percent": 100,
        "max_uses": 1
    }, headers=_auth_header(admin))

    starts_at = (datetime.now(timezone.utc) + timedelta(days=3, hours=3)).isoformat()
    book_res = client.post("/api/v1/bookings", json={
        "lawyer_id": l_user.id,
        "practice": "family",
        "starts_at": starts_at,
        "duration_minutes": 45,
        "intake": {
            "matter_type": "Divorce",
            "children_involved": "No",
            "existing_order": "None"
        },
        "disclaimer_accepted": True,
        "disclaimer_version": "2026-01",
        "voucher_code": code
    }, headers=_auth_header(c_user))

    assert book_res.status_code == 201
    b_data = book_res.json()
    # Free booking should have amount_minor == 0 and be confirmed immediately
    assert b_data["amount_minor"] == 0
    assert b_data["status"] == "confirmed"
    assert b_data["voucher_code"] == code

    v_db = database.query(Voucher).filter_by(code=code).first()
    assert v_db.times_used == 1
    assert v_db.used is True  # max_uses was 1
