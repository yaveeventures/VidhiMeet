import enum
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from .models import BookingStatus, Practice, Role, DraftingStatus, ProposalStatus
from .sanitizer import sanitize_text, sanitize_filename, sanitize_key, clean_string
from .validation_constants import (
    IFSC_REGEX,
    BANK_ACCOUNT_REGEX,
    UPI_VPA_REGEX,
    PAN_REGEX,
    DPDPA_MIN_AGE_YEARS,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    NAME_MIN_LENGTH,
    NAME_MAX_LENGTH,
    BAR_NUMBER_MAX_LENGTH,
)


class GoogleLoginRequest(BaseModel):
    id_token: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    role: Role = Role.CLIENT
    practice: Practice | None = None
    bar_number: str | None = None

    @model_validator(mode="after")
    def check_token_or_email(self):
        if not self.id_token and not self.email:
            raise ValueError("Either id_token or email must be provided")
        return self


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    full_name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    role: Role = Role.CLIENT
    bar_number: str | None = Field(default=None, max_length=BAR_NUMBER_MAX_LENGTH)
    enrollment_date: str | None = Field(default=None, max_length=50)
    practice: Practice | None = None
    consent_privacy_policy: bool = False
    consent_terms: bool = False
    # DPDP §9 — mandatory age verification; must be 18+
    date_of_birth: date = Field(default=date(1990, 1, 1), description="Date of birth (YYYY-MM-DD). Must be 18 or older (DPDP §9).")

    @field_validator("full_name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return sanitize_text(v) or v

    @field_validator("bar_number")
    @classmethod
    def sanitize_bar(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v

    @field_validator("role")
    @classmethod
    def no_admin_signup(cls, value):
        if value == Role.ADMIN:
            raise ValueError("admin accounts cannot self-register")
        return value

    @field_validator("consent_privacy_policy", "consent_terms")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("consent to both privacy policy and terms is mandatory under DPDPA")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def must_be_adult(cls, dob: date) -> date:
        """Reject registration if the user is under 18 (DPDP Act 2023, Section 9)."""
        if dob is None:
            return dob
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < DPDPA_MIN_AGE_YEARS:
            raise ValueError(
                f"You must be at least {DPDPA_MIN_AGE_YEARS} years old to register. "
                "Processing personal data of minors requires verifiable parental consent "
                "under the Digital Personal Data Protection Act, 2023 (Section 9)."
            )
        return dob


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=256)
    password: str = Field(..., min_length=1, max_length=PASSWORD_MAX_LENGTH)
    totp_code: str | None = Field(default=None, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    mfa_required: bool = False


class MfaSetupResponse(BaseModel):
    secret: str
    qr_uri: str


class MfaEnableRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class MfaVerifyRequest(BaseModel):
    email: EmailStr = Field(..., max_length=256)
    code: str = Field(..., min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=256)


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=16, max_length=128)
    new_password: str = Field(..., min_length=12, max_length=128)



class BookingCreate(BaseModel):
    lawyer_id: str = Field(..., max_length=128)
    practice: Practice
    starts_at: datetime
    duration_minutes: int = Field(default=45, ge=30, le=45)
    intake: dict
    disclaimer_accepted: bool
    disclaimer_version: str = Field(default="2026-01", max_length=20)
    voucher_code: str | None = Field(default=None, max_length=30)


class DisputeCategory(str, enum.Enum):
    NO_SHOW = "no_show"
    BAD_CONNECTIVITY = "bad_connectivity"
    SHORT_DURATION = "short_duration"
    QUALITY_OTHER = "quality_other"


class DisputeCreate(BaseModel):
    category: DisputeCategory
    reason: str = Field(..., min_length=10, max_length=1000)


class BookingOut(BaseModel):
    id: str
    client_id: str
    lawyer_id: str
    practice: Practice | str
    starts_at: datetime | None = None
    original_starts_at: datetime | None = None
    duration_minutes: int
    amount_minor: int
    currency: str
    status: BookingStatus | str
    intake: dict
    jitsi_room: str
    video_room: str = ""
    client_name: str | None = None
    lawyer_name: str | None = None
    documents: list = []
    chat_key_salt: str
    base_price_minor: int = 0
    client_platform_fee_minor: int = 0
    lawyer_platform_fee_minor: int = 0
    platform_fee_minor: int = 0
    lawyer_amount_minor: int = 0
    payment_url: str | None = None
    cashfree_order_id: str | None = None
    payment_session_id: str | None = None
    cashfree_mode: str | None = None
    last_message_at: datetime | None = None
    dispute_category: str | None = None
    dispute_reason: str | None = None
    disputed_at: datetime | None = None
    lawyer_duration_seconds: int = 0
    client_duration_seconds: int = 0
    auto_resolution_status: str | None = None
    cancellation_reason: str | None = None
    cancelled_by_role: str | None = None
    refund_amount_minor: int | None = None
    penalty_amount_minor: int | None = None
    refund_tx_id: str | None = None
    voucher_code: str | None = None
    relisted_at: datetime | None = None
    completed_at: datetime | None = None
    dispute_deadline_at: datetime | None = None
    payout_status: str | None = None
    payout_reference_id: str | None = None
    payout_at: datetime | None = None
    model_config = {"from_attributes": True}


class CancellationPreviewOut(BaseModel):
    policy_tier: str
    hours_until_start: float
    total_amount_minor: int
    refund_pct: int
    penalty_pct: int
    refund_amount_minor: int
    penalty_amount_minor: int
    voucher_issued: bool
    reversal_timeline_notice: str


class CancellationRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

    @field_validator("reason")
    @classmethod
    def sanitize_reason(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v


class CancellationResultOut(BaseModel):
    booking_id: str
    status: str
    cancelled_by_role: str
    refund_amount_minor: int
    penalty_amount_minor: int
    refund_tx_id: str | None = None
    voucher_code: str | None = None
    reversal_timeline_notice: str
    message: str


class VoucherOut(BaseModel):
    id: str
    code: str
    discount_percent: int
    expires_at: datetime
    used: bool
    is_promotional: bool = False
    max_uses: int = 1
    times_used: int = 0
    is_active: bool = True
    description: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class PromoVoucherCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=30)
    discount_percent: int = Field(..., ge=1, le=100)
    expires_at: datetime | None = None
    max_uses: int = Field(default=1, ge=0)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("code")
    @classmethod
    def format_code(cls, v: str) -> str:
        code_clean = v.strip().upper()
        if not code_clean.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Voucher code must contain only alphanumeric characters, dashes, or underscores")
        return code_clean


class AdminVoucherOut(BaseModel):
    id: str
    code: str
    discount_percent: int
    expires_at: datetime
    used: bool
    is_promotional: bool
    max_uses: int
    times_used: int
    is_active: bool
    description: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class VoucherValidateRequest(BaseModel):
    code: str = Field(..., min_length=2, max_length=30)
    lawyer_id: str = Field(..., min_length=1)
    duration_minutes: int = Field(default=45, ge=30, le=45)


class VoucherValidateResponse(BaseModel):
    valid: bool
    code: str
    discount_percent: int
    original_amount_minor: int
    discount_amount_minor: int
    final_amount_minor: int
    message: str




class LawyerOut(BaseModel):
    id: str
    full_name: str
    email: str | None = None
    practice: list[Practice]
    languages: list
    hourly_fee_minor: int
    rating: float
    verified: bool
    verification_status: str | None = "pending"
    bar_number: str | None = None
    availability: dict = {}
    enrollment_date: str | None = None
    practice_address: str | None = None
    bar_license_url: str | None = None
    aadhaar_url: str | None = None
    bar_license_verified: bool = False
    aadhaar_verified: bool = False
    aadhaar_number: str | None = None
    pan_number: str | None = None
    pan_number_masked: str | None = None
    mobile_number: str | None = None
    rejection_reason: str | None = None
    verified_at: datetime | None = None
    created_at: datetime
    model_config = {"from_attributes": True}

    @field_validator("practice", mode="before")
    @classmethod
    def convert_to_list(cls, v):
        def _normalize_item(x):
            if isinstance(x, Practice):
                return x
            if isinstance(x, str):
                s = x.lower().strip()
                if "property" in s:
                    return Practice.PROPERTY
                if "corporate" in s:
                    return Practice.CORPORATE
                if "family" in s:
                    return Practice.FAMILY
                try:
                    return Practice(s)
                except ValueError:
                    return Practice.PROPERTY
            return x

        if isinstance(v, (str, Practice)):
            return [_normalize_item(v)]
        elif isinstance(v, (list, tuple, set)):
            return [_normalize_item(x) for x in v]
        return v


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, max_length=512)


class LawyerProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=160)
    practice: list[Practice]
    bar_number: str = Field(..., min_length=2, max_length=100)
    languages: list[str]
    hourly_fee_minor: int = Field(..., ge=100, le=5000000)
    availability: dict = {}
    enrollment_date: str | None = Field(None, max_length=10)
    practice_address: str | None = Field(None, max_length=500)
    aadhaar_number: str | None = Field(None, pattern=r"^\d{12}$|^\d{4}-\d{4}-\d{4}$")
    pan_number: str | None = Field(None, pattern=PAN_REGEX)
    mobile_number: str | None = Field(None, pattern=r"^[0-9]{10}$")

    @field_validator("pan_number", mode="before")
    @classmethod
    def clean_pan(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v

    @field_validator("full_name", "practice_address", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str | None) -> str | None:
        return sanitize_text(v) if isinstance(v, str) else v

    @field_validator("practice", mode="before")
    @classmethod
    def convert_to_list(cls, v):
        if isinstance(v, (str, Practice)):
            val = v.value if isinstance(v, Practice) else v.lower()
            return [val]
        elif isinstance(v, list):
            return [x.value if isinstance(x, Practice) else (x.lower() if isinstance(x, str) else x) for x in v]
        return v

    @field_validator("practice")
    @classmethod
    def check_not_empty(cls, v):
        if not v:
            raise ValueError("At least one practice area must be selected")
        return v


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: Role
    active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: str
    actor_id: str | None = None
    actor_name: str | None = None
    action: str
    target_type: str
    target_id: str | None = None
    metadata_json: dict = {}
    ip_address: str = "127.0.0.1"
    created_at: datetime
    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    encrypted: bool = False
    iv: str | None = Field(default=None, max_length=255)

    @field_validator("content")
    @classmethod
    def sanitize_message(cls, v: str, info) -> str:
        # If message is not encrypted, strip and escape HTML
        is_encrypted = info.data.get("encrypted", False)
        if not is_encrypted:
            return sanitize_text(v) or v
        return v.strip()


class MessageOut(BaseModel):
    id: str
    booking_id: str
    sender_id: str
    sender_name: str | None = None
    content: str
    encrypted: bool
    iv: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)

    @field_validator("comment")
    @classmethod
    def sanitize_review_comment(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v


class ReviewOut(BaseModel):
    id: str
    booking_id: str
    client_id: str
    lawyer_id: str
    client_name: str | None = None
    rating: int
    comment: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Bank Account ──────────────────────────────────────────────────────────────

class BankAccountCreate(BaseModel):
    account_holder_name: str = Field(..., min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    account_number: str = Field(..., min_length=6, max_length=18, pattern=BANK_ACCOUNT_REGEX)
    ifsc_code: str = Field(..., pattern=IFSC_REGEX)
    bank_name: str = Field(..., min_length=2, max_length=120)
    upi_vpa: str | None = Field(default=None, max_length=255)
    pan_number: str | None = Field(default=None, pattern=PAN_REGEX)

    @field_validator("pan_number", mode="before")
    @classmethod
    def clean_pan(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v

    @field_validator("account_holder_name", "bank_name")
    @classmethod
    def sanitize_account_text(cls, v: str) -> str:
        return sanitize_text(v) or v

    @field_validator("upi_vpa")
    @classmethod
    def validate_vpa(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if not v:
                return None
            if "@" not in v:
                raise ValueError("Invalid UPI VPA format")
        return v


class BankAccountUpdate(BaseModel):
    account_holder_name: str | None = Field(default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    account_number: str | None = Field(default=None, min_length=6, max_length=18, pattern=BANK_ACCOUNT_REGEX)
    ifsc_code: str | None = Field(default=None, pattern=IFSC_REGEX)
    bank_name: str | None = Field(default=None, min_length=2, max_length=120)
    upi_vpa: str | None = Field(default=None, max_length=255)
    pan_number: str | None = Field(default=None, pattern=PAN_REGEX)

    @field_validator("pan_number", mode="before")
    @classmethod
    def clean_pan(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v

    @field_validator("account_holder_name", "bank_name")
    @classmethod
    def sanitize_account_text(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v

    @field_validator("upi_vpa")
    @classmethod
    def validate_vpa(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if not v:
                return None
            if "@" not in v:
                raise ValueError("Invalid UPI VPA format")
        return v


class BankAccountOut(BaseModel):
    id: str
    account_holder_name: str
    account_number_masked: str          # e.g. 'XXXXXX4821'
    ifsc_code: str                      # Returned to lawyer owner for verification
    ifsc_code_masked: str               # e.g. 'XXXXXXX1234'
    bank_name: str
    upi_vpa: str | None = None
    upi_name: str | None = None
    verified: bool
    verified_at: datetime | None = None
    utr: str | None = None
    verification_status: str | None = "unverified"
    verification_method: str | None = "reverse_penny_drop"
    verification_id: str | None = None
    pan_number_masked: str | None = None
    has_pan: bool = False
    created_at: datetime
    model_config = {'from_attributes': True}


class RpdInitiateResponse(BaseModel):
    verification_id: str
    reference_id: str | None = None
    status: str
    payment_link: str | None = None
    qr_code: str | None = None
    upi_intent: dict | None = None
    valid_upto: int | str | None = None
    amount: float = 1.0
    currency: str = "INR"
    is_mock: bool = False
    message: str = "Scan UPI QR code or click UPI app link to complete ₹1 verification."


class RpdStatusResponse(BaseModel):
    verification_id: str
    status: str
    verified: bool
    utr: str | None = None
    account_holder_name: str | None = None
    bank_name: str | None = None
    account_number_masked: str | None = None
    ifsc_code: str | None = None
    upi_vpa: str | None = None
    message: str


class AdminPayoutAccountOut(BaseModel):
    id: str
    lawyer_id: str
    lawyer_name: str
    account_holder_name: str
    account_number_masked: str          # e.g. 'XXXXXX4821'
    ifsc_code_masked: str               # e.g. 'XXXXXXX1234'
    bank_name: str
    upi_vpa: str | None = None
    upi_name: str | None = None
    verified: bool
    verified_at: datetime | None = None
    utr: str | None = None
    created_at: datetime
    model_config = {'from_attributes': True}


# ── Drafting feature schemas ──────────────────────────────────────────────────

class DraftingRequestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5, max_length=20000)
    price_minor: int = Field(..., ge=1000, le=50000000)
    documents: list = []

    @field_validator("title", "description")
    @classmethod
    def sanitize_drafting_text(cls, v: str) -> str:
        return sanitize_text(v) or v


class DraftingProposalCreate(BaseModel):
    amount_minor: int = Field(..., ge=1000, le=50000000)


class DraftingProposalOut(BaseModel):
    id: str
    request_id: str
    lawyer_id: str
    lawyer_name: str | None = None
    amount_minor: int
    status: ProposalStatus
    created_at: datetime
    model_config = {"from_attributes": True}


class DraftCommentCreate(BaseModel):
    page_number: int = Field(1, ge=1)
    position_x: float = Field(0.0, ge=0.0, le=100.0)
    position_y: float = Field(0.0, ge=0.0, le=100.0)
    selected_text: str | None = Field(default=None, max_length=1000)
    comment: str = Field(..., min_length=1, max_length=2000)

    @field_validator("comment", "selected_text")
    @classmethod
    def sanitize_comment_text(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v


class DraftCommentOut(BaseModel):
    id: str
    request_id: str
    user_id: str
    user_name: str | None = None
    page_number: int
    position_x: float
    position_y: float
    selected_text: str | None = None
    comment: str
    created_at: datetime
    model_config = {"from_attributes": True}


class DraftingRequestOut(BaseModel):
    id: str
    title: str
    description: str
    price_minor: int
    creator_id: str
    creator_name: str | None = None
    drafter_id: str | None = None
    drafter_name: str | None = None
    status: DraftingStatus
    agreed_price_minor: int | None = None
    draft_text: str | None = None
    draft_file_key: str | None = None
    draft_filename: str | None = None
    platform_fee_minor: int
    drafter_amount_minor: int
    submitted_at: datetime | None = None
    auto_approve_at: datetime | None = None
    completed_at: datetime | None = None
    payout_status: str | None = None
    payout_reference_id: str | None = None
    payout_at: datetime | None = None
    created_at: datetime
    proposals: list[DraftingProposalOut] = []
    documents: list = []
    comments: list[DraftCommentOut] = []
    model_config = {"from_attributes": True}


class PayoutSweepStats(BaseModel):
    total: int = 0
    processed: int = 0
    held: int = 0
    failed: int = 0


class PayoutSweepResult(BaseModel):
    bookings: PayoutSweepStats
    drafts: PayoutSweepStats
    total_processed: int = 0
    total_held: int = 0
    total_failed: int = 0


class PendingPayoutOut(BaseModel):
    entity_type: str
    id: str
    lawyer_id: str | None = None
    lawyer_name: str | None = None
    client_name: str | None = None
    amount_minor: int
    total_amount_minor: int
    payout_status: str
    payout_reference_id: str | None = None
    completed_at: str | None = None
    dispute_deadline_at: str | None = None
    dispute_window_expired: bool = False


class DraftSubmit(BaseModel):
    draft_file_key: str | None = Field(None, max_length=255, description="Storage key for uploaded draft file")
    draft_filename: str | None = Field(None, max_length=255)
    draft_text: str | None = Field(None, max_length=100000)

    @field_validator("draft_file_key")
    @classmethod
    def clean_key(cls, v: str | None) -> str | None:
        return sanitize_key(v) if v else v

    @field_validator("draft_filename")
    @classmethod
    def clean_filename(cls, v: str | None) -> str | None:
        return sanitize_filename(v) if v else v

    @field_validator("draft_text")
    @classmethod
    def clean_text(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v else v


class PlatformFeedbackCreate(BaseModel):
    rating: int = Field(5, ge=1, le=5)
    comments: str = Field(..., min_length=1, max_length=2000)

    @field_validator("comments")
    @classmethod
    def clean_comments(cls, v: str) -> str:
        return sanitize_text(v) or v


class PlatformFeedbackOut(BaseModel):
    id: str
    rating: int
    comments: str
    created_at: datetime
    user_name: str
    user_email: str
    model_config = {"from_attributes": True}

