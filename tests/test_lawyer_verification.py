from datetime import datetime, timezone
import pytest
from backend.models import LawyerProfile, Practice, Role, User
from backend.security import create_access_token, hash_password


@pytest.fixture
def admin_user(database):
    admin = User(
        email="test_admin@vidhimeet.com",
        password_hash=hash_password("SuperAdmin123!"),
        full_name="Admin Officer",
        role=Role.ADMIN,
        active=True
    )
    database.add(admin)
    database.commit()
    database.refresh(admin)
    return admin


@pytest.fixture
def lawyer_user(database):
    lawyer = User(
        email="candidate_advocate@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Advocate Candidate",
        role=Role.LAWYER,
        active=True
    )
    database.add(lawyer)
    database.commit()
    database.refresh(lawyer)

    profile = LawyerProfile(
        user_id=lawyer.id,
        bar_number="DL/2841/2014",
        hourly_fee_minor=50000,
        practice=[Practice.PROPERTY],
        verified=False,
        verification_status="pending"
    )
    database.add(profile)
    database.commit()
    database.refresh(profile)
    return lawyer


def test_approve_lawyer_fails_without_documents(database, client, admin_user, lawyer_user):
    """Approving a lawyer without both bar license and Aadhaar document must fail with HTTP 400."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Attempt to approve without any documents uploaded
    resp = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=true",
        headers=headers
    )
    assert resp.status_code == 400
    assert "cannot approve" in resp.json()["detail"].lower()

    # Upload only one document (Bar license)
    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.bar_license_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=bar.pdf"
    database.commit()

    resp2 = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=true",
        headers=headers
    )
    assert resp2.status_code == 400
    assert "cannot approve" in resp2.json()["detail"].lower()


def test_approve_lawyer_succeeds_with_both_documents(database, client, admin_user, lawyer_user):
    """Approving a lawyer with both documents uploaded succeeds and synchronizes all flags."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.bar_license_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=bar.pdf"
    profile.aadhaar_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=aadhaar.pdf"
    profile.rejection_reason = "Old issue"
    database.commit()

    resp = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=true",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is True
    assert data["verification_status"] == "approved"
    assert data["rejection_reason"] is None

    database.refresh(profile)
    assert profile.verified is True
    assert profile.verification_status == "approved"
    assert profile.bar_license_verified is True
    assert profile.aadhaar_verified is True
    assert profile.verified_at is not None
    assert profile.rejection_reason is None


def test_reject_lawyer_stores_reason_and_resets_flags(database, client, admin_user, lawyer_user):
    """Rejecting a candidate records rejection_reason and clears document verified flags."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    reason = "Bar Council Certificate scan is blurred or illegible"
    resp = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=false&rejection_reason={reason}",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is False
    assert data["verification_status"] == "rejected"
    assert data["rejection_reason"] == reason

    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    database.refresh(profile)
    assert profile.verified is False
    assert profile.verification_status == "rejected"
    assert profile.bar_license_verified is False
    assert profile.aadhaar_verified is False
    assert profile.rejection_reason == reason


def test_revoke_previously_approved_lawyer_resets_flags(database, client, admin_user, lawyer_user):
    """Revoking a previously verified lawyer resets sub-document flags and verified state."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.bar_license_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=bar.pdf"
    profile.aadhaar_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=aadhaar.pdf"
    profile.bar_license_verified = True
    profile.aadhaar_verified = True
    profile.verified = True
    profile.verification_status = "approved"
    database.commit()

    # Revoke verification
    resp = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=false&rejection_reason=License suspended by BCD",
        headers=headers
    )
    assert resp.status_code == 200
    database.refresh(profile)
    assert profile.verified is False
    assert profile.verification_status == "rejected"
    assert profile.bar_license_verified is False
    assert profile.aadhaar_verified is False
    assert profile.rejection_reason == "License suspended by BCD"


def test_admin_pending_and_rejected_lawyer_search(database, client, admin_user, lawyer_user):
    """Admin pending and rejected endpoints support search and expose rejection_reason."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Search pending by candidate name
    resp = client.get("/api/v1/admin/lawyers/pending?search=Candidate", headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert results[0]["id"] == lawyer_user.id

    # Reject lawyer
    client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=false&rejection_reason=Aadhaar name mismatch",
        headers=headers
    )

    # Search rejected
    rej_resp = client.get("/api/v1/admin/lawyers/rejected?search=2841", headers=headers)
    assert rej_resp.status_code == 200
    rej_results = rej_resp.json()
    assert len(rej_results) >= 1
    assert rej_results[0]["rejection_reason"] == "Aadhaar name mismatch"


def test_lawyer_profile_me_returns_rejection_reason_and_status(database, client, lawyer_user):
    """GET /api/v1/lawyers/me exposes verification_status and rejection_reason to the advocate."""
    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.verification_status = "rejected"
    profile.rejection_reason = "Certificate scan too dark to read enrollment stamp"
    database.commit()

    token = create_access_token(lawyer_user)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/lawyers/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verification_status"] == "rejected"
    assert data["rejection_reason"] == "Certificate scan too dark to read enrollment stamp"


def test_admin_verification_dossier_endpoint(database, client, admin_user, lawyer_user):
    """GET /api/v1/admin/lawyers/{id}/verification-dossier returns complete matching dossier."""
    admin_token = create_access_token(admin_user)
    headers = {"Authorization": f"Bearer {admin_token}"}

    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.bar_number = "KAR/1922/2026"
    profile.enrollment_date = "2024-05-10"
    profile.aadhaar_number = "123456789012"
    profile.pan_number = "ABCDE1234F"
    profile.practice_address = "Bangalore Court Complex"
    database.commit()

    resp = client.get(f"/api/v1/admin/lawyers/{lawyer_user.id}/verification-dossier", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # User matching
    assert data["user"]["id"] == lawyer_user.id
    assert data["user"]["full_name"] == lawyer_user.full_name

    # Profile & checks
    assert data["profile"]["bar_number"] == "KAR/1922/2026"
    assert data["profile"]["aadhaar_number_masked"] == "XXXX-XXXX-9012"
    assert data["profile"]["pan_number_masked"] == "XXXXX1234F"
    assert data["checks"]["bar_year"] == "2026"
    assert data["checks"]["enrollment_year"] == "2024"
    assert data["checks"]["year_mismatch"] is True
    assert "yr" in data["checks"]["experience_text"].lower()


def test_verified_lawyer_edit_resets_verification(database, client, admin_user, lawyer_user):
    """An approved lawyer editing critical credential fields (enrollment_date, bar_number) must have status reset to pending."""
    admin_token = create_access_token(admin_user)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    profile = database.query(LawyerProfile).filter(LawyerProfile.user_id == lawyer_user.id).first()
    profile.bar_license_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=bar.pdf"
    profile.aadhaar_url = f"/api/v1/lawyers/{lawyer_user.id}/documents/download?key=aadhaar.pdf"
    profile.enrollment_date = "2020-01-15"
    database.commit()

    # 1. Admin approves lawyer
    approve_resp = client.patch(
        f"/api/v1/admin/lawyers/{lawyer_user.id}/verification?approved=true",
        headers=admin_headers
    )
    assert approve_resp.status_code == 200
    database.refresh(profile)
    assert profile.verified is True
    assert profile.verification_status == "approved"

    # 2. Lawyer edits non-critical field (hourly fee) -> remains approved
    lawyer_token = create_access_token(lawyer_user)
    lawyer_headers = {"Authorization": f"Bearer {lawyer_token}"}

    payload = {
        "full_name": lawyer_user.full_name,
        "practice": ["property"],
        "bar_number": profile.bar_number,
        "languages": ["English", "Hindi"],
        "hourly_fee_minor": 75000,
        "availability": {},
        "enrollment_date": "2020-01-15"
    }
    update_resp = client.put("/api/v1/lawyers/me", json=payload, headers=lawyer_headers)
    assert update_resp.status_code == 200

    database.refresh(profile)
    assert profile.verified is True
    assert profile.verification_status == "approved"
    assert profile.hourly_fee_minor == 75000

    # 3. Lawyer edits enrollment_date to inflate experience -> must reset verification to pending
    payload["enrollment_date"] = "2010-01-15"
    update_resp2 = client.put("/api/v1/lawyers/me", json=payload, headers=lawyer_headers)
    assert update_resp2.status_code == 200

    database.refresh(profile)
    assert profile.verified is False
    assert profile.verification_status == "pending"
    assert profile.bar_license_verified is False
    assert profile.aadhaar_verified is False
    assert profile.verified_at is None

