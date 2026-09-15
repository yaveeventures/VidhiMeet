import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas import BankAccountCreate, RegisterRequest
from backend.validation_constants import (
    IFSC_REGEX,
    BANK_ACCOUNT_REGEX,
    UPI_VPA_REGEX,
    AADHAAR_REGEX,
    MOBILE_IN_REGEX,
    DPDPA_MIN_AGE_YEARS,
    get_public_validation_rules,
)


def test_public_validation_rules_endpoint():
    """Verify GET /api/v1/public/validation-rules returns correct schema."""
    client = TestClient(app)
    response = client.get("/api/v1/public/validation-rules")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    rules = data["rules"]
    assert rules["ifsc_regex"] == IFSC_REGEX
    assert rules["bank_account_regex"] == BANK_ACCOUNT_REGEX
    assert rules["upi_vpa_regex"] == UPI_VPA_REGEX
    assert rules["dpdpa_min_age_years"] == DPDPA_MIN_AGE_YEARS
    assert rules["max_document_size_bytes"] == 20 * 1024 * 1024


def test_bank_account_validation_rules():
    """Verify IFSC and account number patterns work as expected in Pydantic models."""
    # Valid account
    acct = BankAccountCreate(
        account_holder_name="Advocate Sharma",
        account_number="123456789012",
        ifsc_code="HDFC0001234",
        bank_name="HDFC Bank",
    )
    assert acct.ifsc_code == "HDFC0001234"

    # Invalid IFSC
    with pytest.raises(ValidationError):
        BankAccountCreate(
            account_holder_name="Advocate Sharma",
            account_number="123456789012",
            ifsc_code="INVALID_IFSC",
            bank_name="HDFC Bank",
        )

    # Invalid account number (letters or < 6 digits)
    with pytest.raises(ValidationError):
        BankAccountCreate(
            account_holder_name="Advocate Sharma",
            account_number="123",
            ifsc_code="HDFC0001234",
            bank_name="HDFC Bank",
        )


def test_dpdpa_age_verification_validation():
    """Verify DPDP Act §9 minimum age validation in RegisterRequest."""
    today = date.today()
    adult_dob = today - timedelta(days=365.25 * 20)
    minor_dob = today - timedelta(days=365.25 * 16)

    # 20 years old passes
    req = RegisterRequest(
        email="adult@example.com",
        password="ValidPassword123!",
        full_name="Adult User",
        consent_privacy_policy=True,
        consent_terms=True,
        date_of_birth=adult_dob,
    )
    assert req.email == "adult@example.com"

    # 16 years old fails DPDP check
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            email="minor@example.com",
            password="ValidPassword123!",
            full_name="Minor User",
            consent_privacy_policy=True,
            consent_terms=True,
            date_of_birth=minor_dob,
        )
    assert "at least 18 years old" in str(exc.value)
