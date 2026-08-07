import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    AuditLog, Booking, LawyerProfile, Message, Practice, RefreshToken, Review, Role, User,
    UserConsent, LawyerBankAccount
)
from ..schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from ..security import create_access_token, current_user, hash_password, verify_password
from ..rate_limiter import rate_limit_dependency
from ..services import audit, issue_refresh_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201, dependencies=[Depends(rate_limit_dependency("auth"))])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if not payload.consent_privacy_policy or not payload.consent_terms:
        raise HTTPException(422, "consent to both privacy policy and terms is mandatory under DPDPA")

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "account already exists")
    user = User(email=email, password_hash=hash_password(payload.password),
                full_name=payload.full_name.strip(), role=payload.role,
                date_of_birth=payload.date_of_birth.isoformat())
    db.add(user); db.flush()

    # Log consents for DPDPA compliance
    db.add(UserConsent(user_id=user.id, consent_type="privacy_policy", consent_version="v1.0", status="granted"))
    db.add(UserConsent(user_id=user.id, consent_type="terms_of_service", consent_version="v1.0", status="granted"))
    db.flush()

    if payload.role == Role.LAWYER:
        profile = LawyerProfile(
            user_id=user.id,
            practice=[payload.practice] if payload.practice else [Practice.PROPERTY],
            bar_number=payload.bar_number or f"PENDING-{user.id[:8].upper()}",
            languages=["English"],
            hourly_fee_minor=100000,
            rating=0.0,
            verified=False,
            availability={},
            enrollment_date=payload.enrollment_date,
            practice_address=""
        )
        db.add(profile)

    audit(db, user, "auth.register", "user", user.id)
    refresh = issue_refresh_token(db, user); db.commit()
    return TokenResponse(access_token=create_access_token(user), refresh_token=refresh)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency("auth"))])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    print(f"DEBUG LOGIN ATTEMPT: {email}", flush=True)
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    if not user.active:
        raise HTTPException(403, "account restricted")
    refresh = issue_refresh_token(db, user)
    audit(db, user, "auth.login", "user", user.id); db.commit()
    return TokenResponse(access_token=create_access_token(user), refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency("auth"))])
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    digest = hashlib.sha256(payload.refresh_token.encode()).hexdigest()
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest))
    now_utc = datetime.now(timezone.utc)
    expires = stored.expires_at if stored and stored.expires_at.tzinfo else (stored.expires_at.replace(tzinfo=timezone.utc) if stored else None)
    if not stored or stored.revoked or expires < now_utc:
        raise HTTPException(401, "refresh token invalid or expired")
    user = db.get(User, stored.user_id)
    if not user or not user.active:
        raise HTTPException(401, "account unavailable")
    # Rotate: revoke old token, issue a fresh one
    stored.revoked = True
    new_refresh = issue_refresh_token(db, user)
    audit(db, user, "auth.refresh", "user", user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(user), refresh_token=new_refresh)


@router.delete("/erasure", status_code=204)
def request_erasure(user: User = Depends(current_user), db: Session = Depends(get_db)):
    # DPDPA Right to Erasure
    audit(db, user, "auth.erasure_request", "user", user.id)
    db.flush()

    uid = user.id

    # 1. Anonymize AuditLogs to preserve audit trails without tracking identity
    db.execute(
        update(AuditLog).where(AuditLog.actor_id == uid).values(actor_id=None)
    )

    # 2. Get all bookings involving this user
    bookings = db.scalars(
        select(Booking).where((Booking.client_id == uid) | (Booking.lawyer_id == uid))
    ).all()

    booking_ids = [b.id for b in bookings]
    if booking_ids:
        # Delete messages in those bookings
        db.execute(
            delete(Message).where(Message.booking_id.in_(booking_ids))
        )
        # Delete reviews in those bookings
        db.execute(
            delete(Review).where(Review.booking_id.in_(booking_ids))
        )
        # Delete bookings
        db.execute(
            delete(Booking).where(Booking.id.in_(booking_ids))
        )

    # 3. Clean up any leftover reviews or messages
    db.execute(
        delete(Message).where(Message.sender_id == uid)
    )
    db.execute(
        delete(Review).where((Review.client_id == uid) | (Review.lawyer_id == uid))
    )

    # 4. Delete user consents
    db.execute(
        delete(UserConsent).where(UserConsent.user_id == uid)
    )

    # 5. Delete refresh tokens
    db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == uid)
    )

    # 6. Delete lawyer profile (if lawyer)
    db.execute(
        delete(LawyerProfile).where(LawyerProfile.user_id == uid)
    )

    # 7. Delete user account
    db.execute(
        delete(User).where(User.id == uid)
    )

    db.commit()
    return Response(status_code=204)
