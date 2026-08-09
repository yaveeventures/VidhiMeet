import enum
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
from .security import encrypt_field, decrypt_field


def now() -> datetime:
    return datetime.now(timezone.utc)


class EncryptedString(TypeDecorator):
    impl = Text
    cache_ok = False

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_field(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt_field(value)



class Role(str, enum.Enum):
    CLIENT = "client"
    LAWYER = "lawyer"
    ADMIN = "admin"


class Practice(str, enum.Enum):
    PROPERTY = "property"
    CORPORATE = "corporate"
    FAMILY = "family"


class BookingStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[Role] = mapped_column(Enum(Role))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # DPDP §9 — age verification; stored to prove user was 18+ at registration time
    date_of_birth: Mapped[str | None] = mapped_column(String(10), nullable=True)  # ISO-8601 date string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lawyer_profile: Mapped["LawyerProfile | None"] = relationship(back_populates="user", uselist=False)
    bank_account: Mapped["LawyerBankAccount | None"] = relationship(back_populates="user", uselist=False)


class LawyerProfile(Base):
    __tablename__ = "lawyer_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    practice: Mapped[list] = mapped_column(JSON, default=list)
    bar_number: Mapped[str] = mapped_column(String(100), unique=True)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    hourly_fee_minor: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), default=0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    verification_status: Mapped[str | None] = mapped_column(String(20), default="pending", server_default="pending", index=True, nullable=True)
    stripe_account_id: Mapped[str | None] = mapped_column(String(255))
    availability: Mapped[dict] = mapped_column(JSON, default=dict)
    # New fields for verification (encrypted at rest for DPDPA compliance)
    aadhaar_number: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enrollment_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    practice_address: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    bar_license_url: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    aadhaar_url: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(EncryptedString, nullable=True)
    strike_count: Mapped[int] = mapped_column(Integer, default=0)
    ical_token: Mapped[str] = mapped_column(String(64), unique=True, default=lambda: secrets.token_urlsafe(48))
    user: Mapped[User] = relationship(back_populates="lawyer_profile")




class LawyerBankAccount(Base):
    """One-per-lawyer bank account for payout and UPI identity verification."""
    __tablename__ = "lawyer_bank_accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    # Bank details (account number and IFSC code encrypted at rest for security and DPDPA compliance)
    account_holder_name: Mapped[str] = mapped_column(String(160))
    account_number: Mapped[str] = mapped_column(EncryptedString)
    ifsc_code: Mapped[str] = mapped_column(EncryptedString)
    bank_name: Mapped[str] = mapped_column(String(120))
    upi_vpa: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. lawyer@upi
    # Verification state — populated by PhonePe Reverse Penny Drop webhook
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    utr: Mapped[str | None] = mapped_column(String(100), nullable=True)   # PhonePe UTR (audit trail)
    upi_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # VPA display name from webhook
    phonepe_txn_id: Mapped[str | None] = mapped_column(String(80), nullable=True)  # tracks ₹1 verification payment
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    user: Mapped["User"] = relationship(back_populates="bank_account")


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    lawyer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    practice: Mapped[Practice] = mapped_column(Enum(Practice))
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    original_starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    amount_minor: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING_PAYMENT)
    intake: Mapped[dict] = mapped_column(JSON)
    disclaimer_version: Mapped[str] = mapped_column(String(30))
    disclaimer_accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    phonepe_transaction_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    jitsi_room: Mapped[str] = mapped_column(String(255), unique=True)
    documents: Mapped[list] = mapped_column(JSON, default=list)
    chat_key_salt: Mapped[str] = mapped_column(String(64), default=lambda: secrets.token_hex(32))
    # Structured Dispute Metadata (3-Step Dispute Matrix)
    dispute_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    disputed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lawyer_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    client_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    auto_resolution_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Cancellation & Time-Tiered Refund Tracking
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_by_role: Mapped[str | None] = mapped_column(String(20), nullable=True)
    refund_amount_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    penalty_amount_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    refund_tx_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    voucher_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    relisted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])
    lawyer: Mapped["User"] = relationship("User", foreign_keys=[lawyer_id])
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="booking", cascade="all, delete-orphan")

    @property
    def client_name(self) -> str:
        return self.client.full_name if self.client else ""

    @property
    def lawyer_name(self) -> str:
        return self.lawyer.full_name if self.lawyer else ""

    @property
    def base_price_minor(self) -> int:
        if self.amount_minor <= 73500:
            return max(0, self.amount_minor - 3500)
        else:
            return round(self.amount_minor / 1.05)

    @property
    def client_platform_fee_minor(self) -> int:
        return self.amount_minor - self.base_price_minor

    @property
    def lawyer_platform_fee_minor(self) -> int:
        base = self.base_price_minor
        return max(3500, round(base * 0.05))

    @property
    def platform_fee_minor(self) -> int:
        return self.client_platform_fee_minor + self.lawyer_platform_fee_minor

    @property
    def lawyer_amount_minor(self) -> int:
        return self.base_price_minor - self.lawyer_platform_fee_minor

    @property
    def last_message_at(self) -> datetime:
        if self.messages:
            return max(m.created_at for m in self.messages)
        return self.created_at

    __table_args__ = (UniqueConstraint("lawyer_id", "starts_at", name="uq_lawyer_slot"),)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    provider_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(120))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id: Mapped[str] = mapped_column(ForeignKey("bookings.id"), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    iv: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="messages")
    sender: Mapped["User"] = relationship("User")

    @property
    def sender_name(self) -> str:
        return self.sender.full_name if self.sender else ""


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id: Mapped[str] = mapped_column(ForeignKey("bookings.id"), unique=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    lawyer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    booking: Mapped["Booking"] = relationship("Booking")
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])
    lawyer: Mapped["User"] = relationship("User", foreign_keys=[lawyer_id])

    @property
    def client_name(self) -> str:
        return self.client.full_name if self.client else ""


class UserConsent(Base):
    __tablename__ = "user_consents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(50))  # e.g., "privacy_policy", "terms_of_service"
    consent_version: Mapped[str] = mapped_column(String(20)) # e.g., "v1.0"
    status: Mapped[str] = mapped_column(String(20), default="granted") # "granted", "withdrawn"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User")


class DraftingStatus(str, enum.Enum):
    OPEN = "open"
    PENDING_PAYMENT = "pending_payment"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DraftingRequest(Base):
    __tablename__ = "drafting_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price_minor: Mapped[int] = mapped_column(Integer)
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    drafter_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    status: Mapped[DraftingStatus] = mapped_column(Enum(DraftingStatus), default=DraftingStatus.OPEN)
    agreed_price_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    draft_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    documents: Mapped[list] = mapped_column(JSON, default=list)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    drafter: Mapped["User | None"] = relationship("User", foreign_keys=[drafter_id])
    proposals: Mapped[list["DraftingProposal"]] = relationship("DraftingProposal", back_populates="request", cascade="all, delete-orphan")
    comments: Mapped[list["DraftComment"]] = relationship("DraftComment", back_populates="request", cascade="all, delete-orphan")

    @property
    def creator_name(self) -> str:
        return self.creator.full_name if self.creator else ""

    @property
    def drafter_name(self) -> str:
        return self.drafter.full_name if self.drafter else ""

    @property
    def platform_fee_minor(self) -> int:
        if not self.agreed_price_minor:
            return 0
        return round(self.agreed_price_minor * 0.10)

    @property
    def drafter_amount_minor(self) -> int:
        if not self.agreed_price_minor:
            return 0
        return self.agreed_price_minor - self.platform_fee_minor

    @property
    def auto_approve_at(self) -> datetime | None:
        if self.submitted_at and self.status == DraftingStatus.SUBMITTED:
            return self.submitted_at + timedelta(days=7)
        return None


class DraftingProposal(Base):
    __tablename__ = "drafting_proposals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(ForeignKey("drafting_requests.id", ondelete="CASCADE"), index=True)
    lawyer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount_minor: Mapped[int] = mapped_column(Integer)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    request: Mapped["DraftingRequest"] = relationship("DraftingRequest", back_populates="proposals")
    lawyer: Mapped["User"] = relationship("User")

    @property
    def lawyer_name(self) -> str:
        return self.lawyer.full_name if self.lawyer else ""


class DraftComment(Base):
    __tablename__ = "draft_comments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(ForeignKey("drafting_requests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    selected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    request: Mapped["DraftingRequest"] = relationship("DraftingRequest", back_populates="comments")
    user: Mapped["User"] = relationship("User")

    @property
    def user_name(self) -> str:
        return self.user.full_name if self.user else ""


class PlatformFeedback(Base):
    __tablename__ = "platform_feedback"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rating: Mapped[int] = mapped_column(Integer, default=5)
    comments: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user: Mapped["User | None"] = relationship("User")

    @property
    def user_name(self) -> str:
        return self.user.full_name if self.user else "Anonymous User"

    @property
    def user_email(self) -> str:
        return self.user.email if self.user else "N/A"


class Voucher(Base):
    __tablename__ = "vouchers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    discount_percent: Mapped[int] = mapped_column(Integer, default=20)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    user: Mapped["User"] = relationship("User")


    @property
    def user_email(self) -> str:
        return self.user.email if self.user else "N/A"




