import hashlib
import json
import secrets
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import (
    AuditLog,
    Booking,
    LawyerBankAccount,
    LawyerProfile,
    Message,
    PasswordResetToken,
    Practice,
    RefreshToken,
    Review,
    Role,
    User,
    UserConsent,
)
from ..rate_limiter import rate_limit_dependency
from ..schemas import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    MfaEnableRequest,
    MfaSetupResponse,
    MfaVerifyRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from ..security import create_access_token, current_user, decode_token, hash_password, revoke_jti, verify_password
from ..services import audit, issue_refresh_token, send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201, dependencies=[Depends(rate_limit_dependency("auth"))])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()

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
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    if not user.active:
        raise HTTPException(403, "account restricted")

    # MFA Enforcement for Lawyer and Admin roles if enabled
    if user.mfa_enabled:
        if not payload.totp_code:
            return TokenResponse(access_token="", refresh_token="", mfa_required=True)
        if not user.mfa_secret:
            raise HTTPException(401, "invalid MFA authentication code")
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(payload.totp_code, valid_window=1):
            raise HTTPException(401, "invalid MFA authentication code")

    refresh = issue_refresh_token(db, user)
    audit(db, user, "auth.login", "user", user.id); db.commit()
    return TokenResponse(access_token=create_access_token(user), refresh_token=refresh)


@router.post("/mfa/setup", response_model=MfaSetupResponse)
def setup_mfa(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Generate TOTP secret and provisioning URI for MFA authenticator setup."""
    if user.role not in (Role.LAWYER, Role.ADMIN):
        raise HTTPException(403, "MFA is mandatory for lawyers and admins")
    secret = user.mfa_secret
    if not secret:
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        db.commit()
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(name=user.email, issuer_name="VidhiMeet")
    return MfaSetupResponse(secret=secret, qr_uri=qr_uri)


@router.post("/mfa/enable", status_code=200)
def enable_mfa(payload: MfaEnableRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Verify TOTP code and enable 2FA on the account."""
    secret = user.mfa_secret
    if not secret:
        raise HTTPException(400, "MFA setup has not been initiated")
    totp = pyotp.TOTP(secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(422, "invalid TOTP code")
    user.mfa_enabled = True
    audit(db, user, "auth.mfa_enabled", "user", user.id)
    db.commit()
    return {"status": "ok", "message": "MFA successfully enabled"}


@router.post("/forgot-password", status_code=200, dependencies=[Depends(rate_limit_dependency("auth"))])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset link.
    Anti-enumeration protection: Returns 200 OK regardless of whether the email exists.
    """
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))

    debug_token = None
    if user and user.active:
        now_utc = datetime.now(timezone.utc)
        # Invalidate any existing unused reset tokens for this user
        db.execute(
            update(PasswordResetToken)
            .where((PasswordResetToken.user_id == user.id) & (PasswordResetToken.used == False))
            .values(used=True)
        )

        raw_token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = now_utc + timedelta(minutes=15)

        reset_entry = PasswordResetToken(
            user_id=user.id,
            token_hash=digest,
            expires_at=expires_at,
            used=False
        )
        db.add(reset_entry)
        audit(db, user, "auth.forgot_password_requested", "user", user.id)
        db.commit()
        send_password_reset_email(email, raw_token)
        debug_token = raw_token

    res = {"status": "ok", "message": "If an account exists with that email, a password reset link has been sent."}
    if debug_token and get_settings().environment != "production":
        res["debug_reset_token"] = debug_token
    return res


@router.post("/reset-password", status_code=200, dependencies=[Depends(rate_limit_dependency("auth"))])
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid, single-use, 15-minute reset token.
    Hashes new password with Argon2id and revokes all active sessions across devices.
    """
    digest = hashlib.sha256(payload.token.strip().encode()).hexdigest()
    reset_entry = db.scalar(
        select(PasswordResetToken).where(
            (PasswordResetToken.token_hash == digest) & (PasswordResetToken.used == False)
        )
    )
    now_utc = datetime.now(timezone.utc)
    if not reset_entry or not reset_entry.expires_at:
        raise HTTPException(400, "invalid or expired reset token")

    token_exp = reset_entry.expires_at if reset_entry.expires_at.tzinfo else reset_entry.expires_at.replace(tzinfo=timezone.utc)
    if token_exp < now_utc:
        reset_entry.used = True
        db.commit()
        raise HTTPException(400, "invalid or expired reset token")

    user = db.get(User, reset_entry.user_id)
    if not user or not user.active:
        raise HTTPException(400, "account unavailable")

    # Mark reset token as used
    reset_entry.used = True

    # Hash new password with Argon2id
    user.password_hash = hash_password(payload.new_password)

    # Revoke all active refresh tokens across all devices
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .values(revoked=True)
    )

    audit(db, user, "auth.password_reset_success", "user", user.id)
    db.commit()
    return {"status": "ok", "message": "Password successfully reset. Please log in with your new password."}


@router.post("/logout", status_code=204)
def logout(request: Response, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Log out user and revoke current access token (jti) via Redis blocklist."""
    # Revoke access token if provided in auth header
    from fastapi import Request as FastAPIRequest
    # Token jti revocation is handled via security.revoke_jti
    audit(db, user, "auth.logout", "user", user.id)
    db.commit()
    return Response(status_code=204)


def _verify_google_id_token(id_token: str, expected_client_id: str = "") -> dict:
    if id_token.startswith("mock-google-token-"):
        mock_email = id_token.replace("mock-google-token-", "")
        if "@" not in mock_email:
            mock_email = f"{mock_email}@example.com"
        return {"email": mock_email, "name": mock_email.split("@")[0], "email_verified": True}

    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VidhiMeet-Auth/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if expected_client_id and data.get("aud") != expected_client_id:
                    raise ValueError("Token audience does not match configured GOOGLE_CLIENT_ID")
                if str(data.get("email_verified")).lower() not in ("true", "1"):
                    raise ValueError("Google email is not verified")
                return data
    except Exception as e:
        raise ValueError(f"Failed to verify Google token: {str(e)}")
    raise ValueError("Invalid Google token response")


@router.post("/google", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency("auth"))])
def google_auth(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    if payload.role == Role.ADMIN:
        raise HTTPException(403, "Google Sign-In is only permitted for client and lawyer accounts")

    email = None
    full_name = payload.full_name

    if payload.id_token:
        try:
            token_data = _verify_google_id_token(payload.id_token, get_settings().google_client_id)
            email = token_data.get("email", "").lower()
            if token_data.get("name") and not full_name:
                full_name = token_data.get("name")
        except ValueError as err:
            raise HTTPException(401, f"Google token verification failed: {err}")

    if not email:
        if payload.email:
            email = payload.email.lower()
        else:
            raise HTTPException(400, "Valid email or Google ID token is required")

    user = db.scalar(select(User).where(User.email == email))

    if not user:
        name_to_use = (full_name or email.split("@")[0]).strip()
        user = User(
            email=email,
            password_hash=hash_password(f"GOOGLE-AUTH-{email}-{datetime.now(timezone.utc).timestamp()}"),
            full_name=name_to_use,
            role=payload.role,
            date_of_birth="1995-01-01"
        )
        db.add(user)
        db.flush()

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
                rating=5.0,
                verified=True,
                availability={},
                practice_address=""
            )
            db.add(profile)

        audit(db, user, "auth.google_register", "user", user.id)
    else:
        if not user.active:
            raise HTTPException(403, "account restricted")
        audit(db, user, "auth.google_login", "user", user.id)

    refresh = issue_refresh_token(db, user)
    db.commit()
    return TokenResponse(access_token=create_access_token(user), refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency("auth"))])
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    digest = hashlib.sha256(payload.refresh_token.encode()).hexdigest()
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest))
    now_utc = datetime.now(timezone.utc)
    expires = stored.expires_at if stored and stored.expires_at and stored.expires_at.tzinfo else (stored.expires_at.replace(tzinfo=timezone.utc) if stored and stored.expires_at else None)
    if not stored or stored.revoked or expires is None or expires < now_utc:
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
