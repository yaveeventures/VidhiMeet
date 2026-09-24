import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    User, Booking, Role, BookingStatus, Practice, LawyerBankAccount
)
from backend.services.invoice_service import (
    calculate_tax_breakdown,
    get_invoice_number,
    generate_client_receipt_html,
    generate_lawyer_settlement_advice_html,
)
from backend.security import create_access_token, hash_password
from backend.config import get_settings


def test_tax_breakdown_math():
    """Verify 18% inclusive GST calculation for platform fee."""
    # ₹50.00 platform fee = 5000 paise
    tax = calculate_tax_breakdown(5000)
    assert tax["total_fee"] == 50.0
    assert tax["base_taxable"] == 42.37
    assert tax["total_gst"] == 7.63
    assert tax["cgst"] == 3.81
    assert tax["sgst"] == 3.82
    assert tax["rate_percent"] == 18


def test_invoice_number_generation():
    """Verify deterministic invoice number structure."""
    booking = Booking(
        id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        created_at=datetime(2026, 9, 18, 12, 0, 0, tzinfo=timezone.utc),
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
    )
    inv_no = get_invoice_number(booking)
    assert inv_no == "VM-INV-202609-A1B2C3D4"


def test_client_receipt_html_content():
    """Verify client receipt HTML contains all legal, tax, and company requirements."""
    settings = get_settings()
    client = User(
        id="client-1",
        email="rahul.verma@example.com",
        full_name="Rahul Verma",
        phone="+919876543210",
        role=Role.CLIENT,
    )
    lawyer = User(
        id="lawyer-1",
        email="adv.sharma@example.com",
        full_name="Advocate Priya Sharma",
        role=Role.LAWYER,
    )
    booking = Booking(
        id="test-booking-1234-5678",
        client_id="client-1",
        lawyer_id="lawyer-1",
        amount_minor=105000,           # ₹1050 total
        practice=Practice.CORPORATE,
        status=BookingStatus.CONFIRMED,
        cashfree_order_id="order_CF_998877",
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        created_at=datetime(2026, 9, 18, 10, 0, tzinfo=timezone.utc),
        starts_at=datetime(2026, 9, 19, 14, 0, tzinfo=timezone.utc),
    )

    html_out = generate_client_receipt_html(booking, client, lawyer)
    # Check company details
    assert settings.company_name in html_out
    assert settings.company_gstin in html_out
    assert "Gokak" in html_out or settings.company_address in html_out
    assert settings.company_pan in html_out
    assert settings.company_support_email in html_out

    # Check statutory compliance disclaimers
    assert "Section 79 of the Information Technology Act, 2000" in html_out
    assert "Pure Agent" in html_out
    assert "Bar Council of India" in html_out
    assert "998315" in html_out
    assert "CGST (9%)" in html_out
    assert "SGST (9%)" in html_out

    # Check client & lawyer info
    assert "Rahul Verma" in html_out
    assert "Advocate Priya Sharma" in html_out
    assert "order_CF_998877" in html_out

    # Check responsive and mobile layout containers
    assert "table-wrap" in html_out
    assert "break-all" in html_out
    assert "@media screen and (max-width: 680px)" in html_out

    # Check CSP-safe navigation actions (no inline JS or blocked pseudo-protocols)
    assert 'id="btn-back"' in html_out
    assert 'href="/"' in html_out
    assert 'id="btn-save-pdf"' in html_out
    assert 'id="btn-print"' in html_out
    assert "javascript:window.history.back()" not in html_out
    assert "onclick=" not in html_out
    assert '/js/receipt.min.js' in html_out


def test_settlement_advice_html_content():
    """Verify advocate settlement voucher contains payout calculations and intermediary notices."""
    lawyer = User(
        id="lawyer-1",
        email="adv.sharma@example.com",
        full_name="Advocate Priya Sharma",
        role=Role.LAWYER,
    )
    bank = LawyerBankAccount(
        user_id="lawyer-1",
        account_holder_name="Advocate Priya Sharma",
        account_number="123456789012",
        ifsc_code="HDFC0001234",
        bank_name="HDFC Bank",
    )
    lawyer.bank_account = bank

    booking = Booking(
        id="test-booking-1234-5678",
        client_id="client-1",
        lawyer_id="lawyer-1",
        amount_minor=105000,
        payout_reference_id="CMS2026091812345678",
        practice=Practice.PROPERTY,
        status=BookingStatus.COMPLETED,
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        created_at=datetime(2026, 9, 18, 10, 0, tzinfo=timezone.utc),
    )

    html_out = generate_lawyer_settlement_advice_html(booking, lawyer)
    assert "Payout Settlement Advice" in html_out
    assert "Advocate Priya Sharma" in html_out
    assert "CMS2026091812345678" in html_out
    assert "HDFC Bank" in html_out
    assert "Section 79 of the Information Technology Act" in html_out

    # Check responsive and mobile layout containers
    assert "table-wrap" in html_out
    assert "break-all" in html_out
    assert "@media screen and (max-width: 680px)" in html_out

    # Check CSP-safe navigation actions
    assert 'id="btn-back"' in html_out
    assert 'href="/lawyer.html"' in html_out
    assert 'id="btn-save-pdf"' in html_out
    assert 'id="btn-print"' in html_out
    assert "javascript:window.history.back()" not in html_out
    assert "onclick=" not in html_out
    assert '/js/receipt.min.js' in html_out


def test_receipt_api_access_control(client: TestClient, database: Session):
    """Test API endpoint authentication, authorization, and direct token query param."""
    # 1. Create Client 1
    c1 = User(
        email="inv_client1@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Client One",
        role=Role.CLIENT,
    )
    database.add(c1)

    # 2. Create Client 2 (unrelated)
    c2 = User(
        email="inv_client2@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Client Two",
        role=Role.CLIENT,
    )
    database.add(c2)

    # 3. Create Lawyer
    lw = User(
        email="inv_lawyer1@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Advocate Priya",
        role=Role.LAWYER,
    )
    database.add(lw)
    database.commit()

    c1_token = create_access_token(c1)
    c2_token = create_access_token(c2)
    lw_token = create_access_token(lw)

    # 4. Create Booking
    booking = Booking(
        client_id=c1.id,
        lawyer_id=lw.id,
        practice="corporate",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        amount_minor=105000,
        status=BookingStatus.CONFIRMED,
        disclaimer_version="2026-01",
        disclaimer_accepted_at=datetime.now(timezone.utc),
        jitsi_room="room-test-123",
        intake={},
    )
    database.add(booking)
    database.commit()
    b_id = booking.id

    # 5. Access Receipt via Bearer header as Client 1 (allowed)
    r1 = client.get(f"/api/v1/bookings/{b_id}/receipt", headers={"Authorization": f"Bearer {c1_token}"})
    assert r1.status_code == 200
    assert "text/html" in r1.headers.get("content-type", "")
    assert "Tax Invoice" in r1.text

    # 6. Access Receipt via query parameter ?token= as Client 1 (allowed for easy new-tab opening)
    r2 = client.get(f"/api/v1/bookings/{b_id}/receipt?token={c1_token}")
    assert r2.status_code == 200
    assert "Tax Invoice" in r2.text

    # 7. Unrelated Client 2 trying to access Client 1's receipt -> 404 (booking not found / ID enumeration protection)
    r3 = client.get(f"/api/v1/bookings/{b_id}/receipt", headers={"Authorization": f"Bearer {c2_token}"})
    assert r3.status_code == 404

    # 8. Unauthenticated request without token -> 401
    r4 = client.get(f"/api/v1/bookings/{b_id}/receipt")
    assert r4.status_code == 401

    # 9. Settlement Advice access:
    # Client 1 should NOT be allowed to view lawyer's settlement advice -> 404 (restricted to assigned lawyer/admin)
    s1 = client.get(f"/api/v1/bookings/{b_id}/settlement-advice", headers={"Authorization": f"Bearer {c1_token}"})
    assert s1.status_code == 404

    # Assigned lawyer CAN view settlement advice -> 200
    s2 = client.get(f"/api/v1/bookings/{b_id}/settlement-advice", headers={"Authorization": f"Bearer {lw_token}"})
    assert s2.status_code == 200
    assert "Payout Settlement Advice" in s2.text
