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
    from_email = getattr(settings, "smtp_from_email", "") or "no-reply@vidhimeet.in"
    reset_url = f"https://vidhimeet.in/?token={raw_token}"
    msg = EmailMessage()
    msg["Subject"] = "VidhiMeet — Password Reset Request"
    msg["From"] = from_email
    msg["To"] = to_email

    plain_text = (
        f"Hello,\n\n"
        f"A password reset request was received for your VidhiMeet account.\n"
        f"Click the link below (or enter the token on the site) to set a new password:\n\n"
        f"Reset Link: {reset_url}\n"
        f"Token: {raw_token}\n\n"
        f"This link and token expire in 15 minutes.\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\nVidhiMeet Security Team"
    )
    msg.set_content(plain_text)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px 12px; color: #1e293b; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 32px 28px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
    .header {{ text-align: center; margin-bottom: 24px; }}
    .brand {{ font-size: 22px; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; }}
    .btn {{ display: inline-block; background-color: #1e3a8a; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 15px; margin: 16px 0; }}
    .token-box {{ background-color: #f1f5f9; border: 1px dashed #94a3b8; padding: 12px; font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 15px; word-break: break-all; margin: 12px 0; text-align: center; border-radius: 8px; font-weight: 600; color: #0f172a; }}
    .footer {{ font-size: 12px; color: #64748b; text-align: center; margin-top: 28px; padding-top: 20px; border-top: 1px solid #f1f5f9; line-height: 1.5; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <span class="brand">⚖️ VidhiMeet</span>
    </div>
    <p>Hello,</p>
    <p>We received a request to reset your password for your VidhiMeet account. Click the button below to set a new password:</p>
    <p style="text-align: center;">
      <a href="{reset_url}" class="btn" target="_blank">Reset Password</a>
    </p>
    <p style="font-size: 14px; margin-top: 20px;">Or enter this reset token manually on the reset password screen:</p>
    <div class="token-box">{raw_token}</div>
    <p style="font-size: 13px; color: #64748b; margin-top: 16px;">⏳ This link and token will expire in <strong>15 minutes</strong>.</p>
    <p style="font-size: 13px; color: #64748b;">If you did not request a password reset, you can safely ignore this email.</p>
    <div class="footer">
      <p>VidhiMeet Security Team<br>Encrypted & CERT-In Compliant Legal Consultations</p>
    </div>
  </div>
</body>
</html>"""
    msg.add_alternative(html_content, subtype="html")

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
