import sqlite3
from fastapi.testclient import TestClient
from backend.db import get_db
from backend.models import User, LawyerProfile, UserConsent, AuditLog

def test_dpdpa_consent_enforcement_and_logging(client):
    # 1. Attempt registration without consent - should fail with 422
    payload_no_consent = {
        "email": "noconsent@example.com",
        "password": "secure-password-123",
        "full_name": "No Consent",
        "role": "client",
        "consent_privacy_policy": False,
        "consent_terms": False
    }
    res = client.post("/api/v1/auth/register", json=payload_no_consent)
    assert res.status_code == 422

    # 2. Register with consent - should succeed with 201
    payload_consent = {
        "email": "consent@example.com",
        "password": "secure-password-123",
        "full_name": "Consent Given",
        "role": "client",
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    res = client.post("/api/v1/auth/register", json=payload_consent)
    assert res.status_code == 201

    # 3. Verify consent logging in database
    db = next(get_db())
    user = db.query(User).filter(User.email == "consent@example.com").first()
    assert user is not None

    consents = db.query(UserConsent).filter(UserConsent.user_id == user.id).all()
    assert len(consents) == 2
    types = {c.consent_type for c in consents}
    assert "privacy_policy" in types
    assert "terms_of_service" in types
    for c in consents:
        assert c.status == "granted"
        assert c.consent_version == "v1.0"


def test_pii_encryption_at_rest(client):
    # 1. Register a lawyer
    payload = {
        "email": "lawyer_encrypt@example.com",
        "password": "secure-password-123",
        "full_name": "Adv. Encrypted",
        "role": "lawyer",
        "bar_number": "ENCRYPT/2026/01",
        "practice": "family",
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    token = res.json()["access_token"]

    # 2. Add sensitive information (Aadhaar, address) via profile update
    update_res = client.put("/api/v1/lawyers/me", json={
        "full_name": "Adv. Encrypted",
        "practice": "family",
        "bar_number": "ENCRYPT/2026/01",
        "languages": ["English", "Hindi"],
        "hourly_fee_minor": 150000,
        "availability": {},
        "aadhaar_number": "1234-5678-9012",
        "practice_address": "123 MG Road, Bangalore, India",
        "enrollment_date": "2020-01-01",
        "mobile_number": "9876543210"
    }, headers={"Authorization": f"Bearer {token}"})
    assert update_res.status_code == 200

    # 3. Retrieve via API - should return decrypted clean PII
    profile_res = client.get("/api/v1/lawyers/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["aadhaar_number"] == "1234-5678-9012"
    assert profile_data["practice_address"] == "123 MG Road, Bangalore, India"
    assert profile_data["mobile_number"] == "9876543210"

    # 4. Verify DB storage is encrypted (ciphertext)
    conn = sqlite3.connect("./test_lexconnect.db")
    cursor = conn.cursor()
    row = cursor.execute("SELECT aadhaar_number, practice_address, mobile_number FROM lawyer_profiles WHERE stripe_account_id IS NULL").fetchone()
    conn.close()

    assert row is not None
    db_aadhaar, db_address, db_mobile = row
    
    # Assert they are not stored in plaintext
    assert db_aadhaar != "1234-5678-9012"
    assert db_address != "123 MG Road, Bangalore, India"
    assert db_mobile != "9876543210"
    
    # Assert they look like Fernet ciphertexts (typically start with gAAAA)
    assert db_aadhaar.startswith("gAAAA")
    assert db_address.startswith("gAAAA")
    assert db_mobile.startswith("gAAAA")


def test_right_to_erasure(client):
    # 1. Register user
    payload = {
        "email": "erase_me@example.com",
        "password": "secure-password-123",
        "full_name": "Erase Me",
        "role": "client",
        "consent_privacy_policy": True,
        "consent_terms": True
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    token = res.json()["access_token"]

    db = next(get_db())
    user = db.query(User).filter(User.email == "erase_me@example.com").first()
    uid = user.id

    # Add an audit log to test anonymization
    db.add(AuditLog(actor_id=uid, action="test_action", target_type="test", target_id="1"))
    db.commit()

    # 2. Request erasure
    erasure_res = client.delete("/api/v1/auth/erasure", headers={"Authorization": f"Bearer {token}"})
    assert erasure_res.status_code == 204

    # 3. Verify user and all PII is completely deleted from the database
    db = next(get_db())
    user_deleted = db.query(User).filter(User.id == uid).first()
    assert user_deleted is None

    # Consents deleted
    consents = db.query(UserConsent).filter(UserConsent.user_id == uid).all()
    assert len(consents) == 0

    # Audit logs actor_id anonymized (set to NULL)
    audit_logs = db.query(AuditLog).filter(AuditLog.target_type == "test").all()
    for log in audit_logs:
        assert log.actor_id is None
