import pytest
from sqlalchemy import text
from backend.db import SessionLocal
from backend.models import LawyerBankAccount, Role, User
from backend.security import create_access_token, hash_password


def test_payout_bank_account_encryption_at_rest():
    """Verify that both account_number and ifsc_code are encrypted at rest in the database."""
    db = SessionLocal()
    try:
        user = User(
            email="payout_lawyer@example.com",
            password_hash=hash_password("Pass123!"),
            full_name="Adv. Payout Test",
            role=Role.LAWYER
        )
        db.add(user)
        db.flush()

        raw_account = "987654321012"
        raw_ifsc = "SBIN0001234"

        bank_acct = LawyerBankAccount(
            user_id=user.id,
            account_holder_name="Adv. Payout Test",
            account_number=raw_account,
            ifsc_code=raw_ifsc,
            bank_name="State Bank of India"
        )
        db.add(bank_acct)
        db.commit()

        # Query ORM — decrypted transparently by EncryptedString TypeDecorator
        retrieved = db.query(LawyerBankAccount).filter_by(user_id=user.id).first()
        assert retrieved.account_number == raw_account
        assert retrieved.ifsc_code == raw_ifsc

        # Query RAW SQL — must NOT be plaintext in SQLite storage
        raw_row = db.execute(
            text("SELECT account_number, ifsc_code FROM lawyer_bank_accounts WHERE user_id = :uid"),
            {"uid": user.id}
        ).fetchone()

        db_raw_account = raw_row[0]
        db_raw_ifsc = raw_row[1]

        # Verify raw database strings do NOT contain the plaintext values
        assert db_raw_account != raw_account
        assert db_raw_ifsc != raw_ifsc
        assert raw_account not in db_raw_account
        assert raw_ifsc not in db_raw_ifsc
    finally:
        db.close()


def test_admin_payouts_masked_endpoint(client):
    """Verify that GET /api/v1/admin/payouts returns masked credentials."""
    db = SessionLocal()
    try:
        # Create Admin
        admin = User(
            email="admin_payout_test@example.com",
            password_hash=hash_password("Pass123!"),
            full_name="Admin Payout Tester",
            role=Role.ADMIN
        )
        db.add(admin)

        # Create Lawyer with Bank Account
        lawyer = User(
            email="lawyer_payout_test@example.com",
            password_hash=hash_password("Pass123!"),
            full_name="Adv. Sensitive Bank Account",
            role=Role.LAWYER
        )
        db.add(lawyer)
        db.flush()

        raw_acct_num = "112233445566"
        raw_ifsc_code = "HDFC0009988"

        bank = LawyerBankAccount(
            user_id=lawyer.id,
            account_holder_name="Adv. Sensitive Bank Account",
            account_number=raw_acct_num,
            ifsc_code=raw_ifsc_code,
            bank_name="HDFC Bank"
        )
        db.add(bank)
        db.commit()

        admin_token = create_access_token(admin)
        lawyer_id = lawyer.id
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch admin payouts list
    response = client.get("/api/v1/admin/payouts", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Find created bank account
    acct_entry = next((item for item in data if item["lawyer_id"] == lawyer_id), None)
    assert acct_entry is not None
    assert acct_entry["account_number_masked"] == "XXXXXXXX5566"
    assert acct_entry["ifsc_code_masked"] == "XXXXXXX9988"
    assert "account_number" not in acct_entry
    assert raw_acct_num not in str(acct_entry)
    assert raw_ifsc_code not in str(acct_entry)


def test_admin_payouts_forbidden_for_clients(client):
    """Verify that non-admin accounts cannot access payout list."""
    db = SessionLocal()
    try:
        client_user = User(
            email="client_forbidden@example.com",
            password_hash=hash_password("Pass123!"),
            full_name="Client Test",
            role=Role.CLIENT
        )
        db.add(client_user)
        db.commit()

        client_token = create_access_token(client_user)
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {client_token}"}

    response = client.get("/api/v1/admin/payouts", headers=headers)
    assert response.status_code == 403
