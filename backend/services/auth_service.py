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
