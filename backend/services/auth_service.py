import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_settings
from ..models import AuditLog, RefreshToken, User
from ..ntp_time import ntp_now

settings = get_settings()

def audit(db: Session | AsyncSession, actor: User | None, action: str, target_type: str, target_id: str | None, metadata=None):
    """Record a security/compliance event with an NPL/NIC NTP-sourced timestamp."""
    audit_entry = AuditLog(
        actor_id=actor.id if actor else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata or {},
        created_at=ntp_now(),  # CERT-In compliant: timestamp from NPL/NIC NTP
    )
    db.add(audit_entry)


def issue_refresh_token(db: Session | AsyncSession, user: User) -> str:
    raw = secrets.token_urlsafe(48)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=digest,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)
    ))
    return raw


import smtplib
from email.message import EmailMessage
import structlog

logger = structlog.get_logger(__name__)

def send_password_reset_email(to_email: str, raw_token: str):
    """
    Sends password reset email containing the secret token/link.
    Uses SMTP configuration or logs dispatch event in development mode.
    """
    reset_url = f"https://vidhimeet.in/reset-password?token={raw_token}"
    msg = EmailMessage()
    msg["Subject"] = "VidhiMeet — Password Reset Request"
    msg["From"] = "no-reply@vidhimeet.in"
    msg["To"] = to_email
    msg.set_content(
        f"Hello,\n\n"
        f"A password reset request was received for your VidhiMeet account.\n"
        f"Click the link below (or enter the token) to set a new password:\n\n"
        f"Reset Link: {reset_url}\n"
        f"Token: {raw_token}\n\n"
        f"This link expires in 15 minutes.\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\nVidhiMeet Security Team"
    )

    smtp_server = getattr(settings, "smtp_server", "")
    smtp_port = getattr(settings, "smtp_port", 587)
    smtp_user = getattr(settings, "smtp_user", "")
    smtp_password = getattr(settings, "smtp_password", "")

    if smtp_server and smtp_user:
        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            logger.info("Password reset email sent via SMTP", recipient=to_email)
        except Exception as err:
            logger.error("Failed to send password reset email via SMTP", error=str(err))
    else:
        logger.info("Password reset email generated (SMTP not configured)", recipient=to_email, reset_url=reset_url)
