import pytest
from pydantic import ValidationError
from backend.sanitizer import sanitize_text, sanitize_filename, sanitize_key
from backend.schemas import (
    RegisterRequest, MessageCreate, ReviewCreate, DraftingRequestCreate,
    DraftCommentCreate, DraftSubmit, BankAccountCreate, BankAccountUpdate
)


def test_sanitize_text():
    assert sanitize_text("  hello world  ") == "hello world"
    assert sanitize_text("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert sanitize_text(None) is None


def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my resume (1).pdf") == "my_resume__1_.pdf"
    assert sanitize_filename(None) is None


def test_sanitize_key():
    assert sanitize_key("/drafts/../user/doc.pdf") == "drafts/user/doc.pdf"
    assert sanitize_key(r"lawyers\123\..\doc.pdf") == "lawyers/123/doc.pdf"
    assert sanitize_key(None) is None


def test_register_request_name_sanitizing():
    req = RegisterRequest(
        email="test@example.com",
        password="secure-password-123",
        full_name="<b >John Doe</b>",
        consent_privacy_policy=True,
        consent_terms=True
    )
    assert req.full_name == "&lt;b &gt;John Doe&lt;/b&gt;"


def test_message_create_sanitizing_and_bounds():
    # Unencrypted message is HTML sanitized
    msg = MessageCreate(content="<img src=x onerror=alert(1)>", encrypted=False)
    assert "<img" not in msg.content
    assert "&lt;img" in msg.content

    # Encrypted message is not modified beyond whitespace trimming
    msg_enc = MessageCreate(content="  encryptedpayload123  ", encrypted=True, iv="abc")
    assert msg_enc.content == "encryptedpayload123"

    # Too long message raises validation error
    with pytest.raises(ValidationError):
        MessageCreate(content="a" * 5001)


def test_review_create_bounds_and_sanitizing():
    rev = ReviewCreate(rating=5, comment="<b>Great service!</b>")
    assert rev.comment == "&lt;b&gt;Great service!&lt;/b&gt;"

    with pytest.raises(ValidationError):
        ReviewCreate(rating=6, comment="Invalid rating")

    with pytest.raises(ValidationError):
        ReviewCreate(rating=0, comment="Invalid rating")


def test_bank_account_vpa_validation():
    acct = BankAccountCreate(
        account_holder_name="Jane Doe",
        account_number="1234567890",
        ifsc_code="SBIN0001234",
        bank_name="State Bank",
        upi_vpa="jane@okaxis"
    )
    assert acct.upi_vpa == "jane@okaxis"

    with pytest.raises(ValidationError):
        BankAccountCreate(
            account_holder_name="Jane Doe",
            account_number="1234567890",
            ifsc_code="SBIN0001234",
            bank_name="State Bank",
            upi_vpa="invalid_vpa_without_at"
        )


def test_drafting_request_bounds_and_sanitization():
    draft = DraftingRequestCreate(
        title="<script>Title</script>",
        description="Detailed legal description text",
        price_minor=150000
    )
    assert draft.title == "&lt;script&gt;Title&lt;/script&gt;"

    # Out of bounds price
    with pytest.raises(ValidationError):
        DraftingRequestCreate(title="Title", description="Desc", price_minor=500)
