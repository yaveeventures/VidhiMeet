import io
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.logging_config import scrub_sensitive_pii_processor
from backend.main import app
from backend.models import Role, User
from backend.security import create_access_token, hash_password
from backend.services.malware_scanner import scan_document_payload

client = TestClient(app)


def test_structlog_pii_scrubbing_processor():
    """Verify structlog processor scrubs sensitive PII fields and credentials from log dictionaries."""
    log_event = {
        "event": "auth.login_attempt",
        "user_id": "usr-123",
        "role": "client",
        "email": "user@example.com",
        "password": "SuperSecretPassword123!",
        "aadhaar": "9999-8888-7777",
        "intake_form": "Private legal details regarding land dispute",
        "vpa": "user@okaxis",
        "account_number": "123456789012"
    }

    processed = scrub_sensitive_pii_processor(None, "info", log_event)

    assert processed["user_id"] == "usr-123"
    assert processed["role"] == "client"
    assert processed["email"] == "user@example.com"
    assert processed["password"] == "[REDACTED_PII]"
    assert processed["aadhaar"] == "[REDACTED_PII]"
    assert processed["intake_form"] == "[REDACTED_PII]"
    assert processed["vpa"] == "[REDACTED_PII]"
    assert processed["account_number"] == "[REDACTED_PII]"


def test_malware_scanner_rejects_malicious_pdf_js():
    """Verify scan_document_payload rejects PDF files containing embedded JavaScript triggers."""
    malicious_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R /OpenAction << /S /JavaScript /JS (app.alert('PWNED')) >> >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
    )

    with pytest.raises(HTTPException) as exc_info:
        scan_document_payload(malicious_pdf, "malicious.pdf")

    assert exc_info.value.status_code == 422
    assert "Security Violation" in exc_info.value.detail
    assert "disallowed active script trigger" in exc_info.value.detail


def test_malware_scanner_rejects_vba_macro_binaries():
    """Verify scan_document_payload rejects Office document archives containing VBA macro binaries."""
    malicious_docx = b"PK\x03\x04\x14\x00\x00\x00word/vbaProject.bin\x00\x00\x00"

    with pytest.raises(HTTPException) as exc_info:
        scan_document_payload(malicious_docx, "contract_with_macro.docx")

    assert exc_info.value.status_code == 422
    assert "Security Violation" in exc_info.value.detail
    assert "executable VBA macro binaries" in exc_info.value.detail


def test_malware_scanner_accepts_clean_pdf():
    """Verify scan_document_payload accepts clean PDF files."""
    clean_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Title (Legitimate Legal Agreement) >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
    )

    assert scan_document_payload(clean_pdf, "clean_contract.pdf") is True


def test_mock_upload_endpoint_rejects_malicious_pdf(database):
    """Verify document mock upload endpoint rejects infected PDF uploads with HTTP 422."""
    client_user = User(
        email="upload_tester@example.com",
        password_hash=hash_password("ClientPass123!"),
        full_name="Upload Tester",
        role=Role.CLIENT,
        date_of_birth="1990-01-01"
    )
    database.add(client_user)
    database.commit()

    token = create_access_token(client_user)
    headers = {"Authorization": f"Bearer {token}"}

    malicious_pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Action /S /JavaScript /JS (evil()) >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
    )

    response = client.post(
        "/api/v1/drafting/documents/mock-upload",
        data={"key": "drafting/test-key-123.pdf"},
        files={"file": ("malicious.pdf", io.BytesIO(malicious_pdf_bytes), "application/pdf")},
        headers=headers
    )

    assert response.status_code == 422
    assert "Security Violation" in response.json()["detail"]
