"""
data_retention_purge.py
-----------------------
DPDP Act 2023, Section 8(7) — Data Retention Purge

Deletes personal data that has outlived its retention period:

  * Completed / disputed bookings (+ their messages, reviews)
      -> purged after RETENTION_COMPLETED_DAYS (default 2555 = ~7 years)
  * Cancelled / refunded bookings (+ their messages, reviews)
      -> purged after RETENTION_CANCELLED_DAYS (default 365 = 1 year)
  * Expired / revoked refresh tokens
      -> purged after RETENTION_TOKEN_DAYS past their expiry (default 30)
  * Withdrawn user consents
      -> purged 365 days after withdrawal

Usage:
    python -m scripts.data_retention_purge           # live run
    python -m scripts.data_retention_purge --dry-run # preview counts only

Designed to be called from cron (e.g. daily at 02:00) or via the admin API.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone

# Bootstrap path so we can import backend when run from project root
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select, and_, delete
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.db import SessionLocal
from backend.models import (
    AuditLog, Booking, BookingStatus, Message, RefreshToken,
    Review, UserConsent,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("purge")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _cutoff(days: int) -> datetime:
    return _now() - timedelta(days=days)


def _ensure_tz(dt: datetime) -> datetime:
    """Return a timezone-aware datetime (assumes UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Booking purge
# ---------------------------------------------------------------------------

def purge_expired_bookings(db: Session, settings, dry_run: bool) -> dict:
    """
    Hard-delete bookings (+ their messages and reviews) whose status and age
    exceed the configured retention window.

    Completed / Disputed  -> retention_completed_days  (default ~7 years)
    Cancelled / Refunded  -> retention_cancelled_days  (default 1 year)

    Audit logs are NOT deleted; actor_id is left intact so the compliance
    trail is preserved without being tied to purged records.
    """
    terminal_statuses = {
        BookingStatus.COMPLETED, BookingStatus.DISPUTED,
        BookingStatus.CANCELLED, BookingStatus.REFUNDED,
    }

    completed_cutoff = _cutoff(settings.retention_completed_days)
    cancelled_cutoff = _cutoff(settings.retention_cancelled_days)

    stats = {"bookings": 0, "messages": 0, "reviews": 0}

    all_expired = db.scalars(
        select(Booking).where(Booking.status.in_(terminal_statuses))
    ).all()

    to_delete_ids: list[str] = []
    for booking in all_expired:
        created = _ensure_tz(booking.created_at)
        if booking.status in (BookingStatus.COMPLETED, BookingStatus.DISPUTED):
            if created < completed_cutoff:
                to_delete_ids.append(booking.id)
        else:  # CANCELLED / REFUNDED
            if created < cancelled_cutoff:
                to_delete_ids.append(booking.id)

    if not to_delete_ids:
        log.info("No expired bookings found.")
        return stats

    log.info(
        "%s %d expired booking(s) (+ messages & reviews).",
        "[DRY-RUN] Would delete" if dry_run else "Deleting",
        len(to_delete_ids),
    )

    if dry_run:
        stats["bookings"] = len(to_delete_ids)
        return stats

    # Chunk deletions to avoid SQLite IN() length limits
    CHUNK = 500
    for i in range(0, len(to_delete_ids), CHUNK):
        chunk = to_delete_ids[i: i + CHUNK]

        msg_del = db.execute(delete(Message).where(Message.booking_id.in_(chunk)))
        stats["messages"] += msg_del.rowcount

        rev_del = db.execute(delete(Review).where(Review.booking_id.in_(chunk)))
        stats["reviews"] += rev_del.rowcount

        bk_del = db.execute(delete(Booking).where(Booking.id.in_(chunk)))
        stats["bookings"] += bk_del.rowcount

    db.commit()
    log.info(
        "Purged: %d booking(s), %d message(s), %d review(s).",
        stats["bookings"], stats["messages"], stats["reviews"],
    )
    return stats


# ---------------------------------------------------------------------------
# Token purge
# ---------------------------------------------------------------------------

def purge_expired_tokens(db: Session, settings, dry_run: bool) -> dict:
    """
    Hard-delete refresh tokens that expired more than retention_token_days ago
    OR that were explicitly revoked (safe to drop anytime).
    """
    token_cutoff = _cutoff(settings.retention_token_days)
    stats = {"tokens": 0}

    expired = db.scalars(
        select(RefreshToken).where(
            (RefreshToken.expires_at < token_cutoff) | (RefreshToken.revoked.is_(True))
        )
    ).all()

    count = len(expired)
    log.info(
        "%s %d expired/revoked refresh token(s).",
        "[DRY-RUN] Would delete" if dry_run else "Deleting",
        count,
    )

    if dry_run:
        stats["tokens"] = count
        return stats

    for token in expired:
        db.delete(token)
    db.commit()
    stats["tokens"] = count
    return stats


# ---------------------------------------------------------------------------
# Withdrawn consent purge
# ---------------------------------------------------------------------------

def purge_withdrawn_consents(db: Session, dry_run: bool) -> dict:
    """
    Delete UserConsent records whose status is 'withdrawn' and whose
    withdrawn_at timestamp is older than 365 days.
    """
    consent_cutoff = _cutoff(365)
    stats = {"consents": 0}

    old_withdrawn = db.scalars(
        select(UserConsent).where(
            and_(
                UserConsent.status == "withdrawn",
                UserConsent.withdrawn_at < consent_cutoff,
            )
        )
    ).all()

    count = len(old_withdrawn)
    log.info(
        "%s %d withdrawn consent record(s) older than 365 days.",
        "[DRY-RUN] Would delete" if dry_run else "Deleting",
        count,
    )

    if dry_run:
        stats["consents"] = count
        return stats

    for record in old_withdrawn:
        db.delete(record)
    db.commit()
    stats["consents"] = count
    return stats


# ---------------------------------------------------------------------------
# Audit log entry
# ---------------------------------------------------------------------------

def log_purge_audit(db: Session, results: dict, dry_run: bool):
    """Write a system-level audit entry so every purge run is traceable."""
    if dry_run:
        return
    db.add(
        AuditLog(
            actor_id=None,
            action="system.data_retention_purge",
            target_type="system",
            target_id=None,
            metadata_json={**results, "run_at": _now().isoformat()},
        )
    )
    db.commit()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_purge(dry_run: bool = False) -> dict:
    settings = get_settings()
    db: Session = SessionLocal()
    try:
        log.info(
            "=== DPDP Data Retention Purge %s=== started",
            "[DRY-RUN] " if dry_run else "",
        )
        results: dict = {}
        results.update(purge_expired_bookings(db, settings, dry_run))
        results.update(purge_expired_tokens(db, settings, dry_run))
        results.update(purge_withdrawn_consents(db, dry_run))
        log_purge_audit(db, results, dry_run)
        log.info("=== Purge complete. Results: %s ===", results)
        return results
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DPDP Section 8(7) Data Retention Purge — delete expired personal data."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview counts without actually deleting anything.",
    )
    args = parser.parse_args()
    run_purge(dry_run=args.dry_run)
