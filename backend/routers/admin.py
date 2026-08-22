import stripe
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..db import get_db
from ..models import AuditLog, Booking, BookingStatus, DraftingProposal, DraftingRequest, LawyerBankAccount, LawyerProfile, Role, User
from ..ntp_time import check_clock_drift
from ..schemas import AdminPayoutAccountOut, AuditLogOut, BookingOut, DraftingRequestOut, LawyerOut, UserOut, PlatformFeedbackOut
from ..security import require_roles
from ..services import audit

log = structlog.get_logger("admin")
settings = get_settings()

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/metrics")
def admin_metrics(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return {
        "users": db.scalar(select(func.count()).select_from(User)),
        "verified_lawyers": db.scalar(select(func.count()).select_from(LawyerProfile).where(LawyerProfile.verified.is_(True))),
        "bookings": db.scalar(select(func.count()).select_from(Booking)),
        "escrow_minor": db.scalar(select(func.coalesce(func.sum(Booking.amount_minor), 0)).where(
            Booking.status.in_([BookingStatus.PENDING_PAYMENT, BookingStatus.CONFIRMED]))),
    }


@router.patch("/lawyers/{lawyer_id}/verification")
def verify_lawyer(lawyer_id: str, approved: bool = None, status: str = None, admin: User = Depends(require_roles(Role.ADMIN)),
                  db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == lawyer_id))
    if not profile: raise HTTPException(404, "lawyer profile not found")
    
    if status:
        target_status = status.lower()
    elif approved is not None:
        target_status = "approved" if approved else "rejected"
    else:
        raise HTTPException(400, "approved or status parameter required")
    
    profile.verification_status = target_status
    profile.verified = (target_status == "approved")
    if target_status == "approved":
        profile.bar_license_verified = True
        profile.aadhaar_verified = True
    audit(db, admin, "lawyer.verification", "user", lawyer_id, {"status": target_status, "approved": profile.verified})
    db.commit()
    return {"lawyer_id": lawyer_id, "verified": profile.verified, "verification_status": target_status}


@router.patch("/lawyers/{lawyer_id}/documents/verify")
def verify_lawyer_document(lawyer_id: str, doc_type: str, verified: bool = True,
                           admin: User = Depends(require_roles(Role.ADMIN)),
                           db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == lawyer_id))
    if not profile:
        raise HTTPException(404, "Lawyer profile not found")

    if doc_type in ("bar_license", "bar"):
        profile.bar_license_verified = verified
    elif doc_type in ("aadhaar", "id"):
        profile.aadhaar_verified = verified
    else:
        raise HTTPException(400, "Invalid document type")

    audit(db, admin, "lawyer.document_verified", "user", lawyer_id, {"doc_type": doc_type, "verified": verified})
    db.commit()
    return {"status": "success", "lawyer_id": lawyer_id, "doc_type": doc_type, "verified": verified}


@router.get("/lawyers/pending", response_model=list[LawyerOut])
def list_pending_lawyers(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.execute(
        select(LawyerProfile, User).join(User).where(
            or_(
                LawyerProfile.verification_status == "pending",
                LawyerProfile.verification_status.is_(None)
            ),
            LawyerProfile.verified.is_(False)
        )
    ).all()
    return [
        LawyerOut(
            id=u.id,
            full_name=u.full_name,
            practice=p.practice,
            languages=p.languages,
            hourly_fee_minor=p.hourly_fee_minor,
            rating=float(p.rating or 0),
            verified=p.verified,
            verification_status=p.verification_status or "pending",
            bar_number=p.bar_number,
            availability=p.availability or {},
            enrollment_date=p.enrollment_date,
            practice_address=p.practice_address,
            bar_license_url=p.bar_license_url,
            aadhaar_url=p.aadhaar_url,
            bar_license_verified=getattr(p, "bar_license_verified", False),
            aadhaar_verified=getattr(p, "aadhaar_verified", False),
            mobile_number=p.mobile_number,
            created_at=u.created_at
        )
        for p, u in rows
    ]


@router.get("/lawyers/rejected", response_model=list[LawyerOut])
def list_rejected_lawyers(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.execute(
        select(LawyerProfile, User).join(User).where(
            LawyerProfile.verification_status == "rejected"
        )
    ).all()
    return [
        LawyerOut(
            id=u.id,
            full_name=u.full_name,
            practice=p.practice,
            languages=p.languages,
            hourly_fee_minor=p.hourly_fee_minor,
            rating=float(p.rating or 0),
            verified=p.verified,
            verification_status=p.verification_status or "rejected",
            bar_number=p.bar_number,
            availability=p.availability or {},
            enrollment_date=p.enrollment_date,
            practice_address=p.practice_address,
            bar_license_url=p.bar_license_url,
            aadhaar_url=p.aadhaar_url,
            bar_license_verified=getattr(p, "bar_license_verified", False),
            aadhaar_verified=getattr(p, "aadhaar_verified", False),
            mobile_number=p.mobile_number,
            created_at=u.created_at
        )
        for p, u in rows
    ]


@router.get("/users", response_model=list[UserOut])
def list_users(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


@router.patch("/users/{user_id}/active")
def toggle_user_active(user_id: str, active: bool, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "user not found")
    user.active = active
    audit(db, admin, "user.status_change", "user", user_id, {"active": active})
    db.commit()
    return {"user_id": user_id, "active": active}


@router.get("/transactions", response_model=list[BookingOut])
def list_transactions(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return list(db.scalars(select(Booking).order_by(Booking.created_at.desc())).all())


@router.get("/drafting-transactions", response_model=list[DraftingRequestOut])
def list_drafting_transactions(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    """Return all drafting requests for admin transaction monitoring."""
    query = (
        select(DraftingRequest)
        .options(
            selectinload(DraftingRequest.creator),
            selectinload(DraftingRequest.drafter),
            selectinload(DraftingRequest.proposals).selectinload(DraftingProposal.lawyer),
        )
        .order_by(DraftingRequest.created_at.desc())
    )
    return list(db.scalars(query).all())


@router.get("/disputes", response_model=list[BookingOut])
def list_disputes(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return list(db.scalars(
        select(Booking)
        .where(
            or_(
                Booking.status == BookingStatus.DISPUTED,
                Booking.disputed_at.is_not(None),
                Booking.dispute_reason.is_not(None),
                Booking.dispute_category.is_not(None)
            )
        )
        .order_by(Booking.created_at.desc())
    ).all())


@router.patch("/bookings/{booking_id}/resolve")
def resolve_dispute(booking_id: str, outcome: str, strike_lawyer: bool = False, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "booking not found")
    if outcome == "refund":
        booking.status = BookingStatus.REFUNDED
        if settings.stripe_secret_key and booking.stripe_payment_intent_id:
            try:
                stripe.api_key = settings.stripe_secret_key
                stripe.Refund.create(payment_intent=booking.stripe_payment_intent_id)
            except stripe.error.StripeError as exc:
                log.error("Stripe dispute refund failed", booking_id=booking_id, error=str(exc))
        if strike_lawyer:
            lawyer_profile = db.query(LawyerProfile).filter(LawyerProfile.user_id == booking.lawyer_id).first()
            if lawyer_profile:
                lawyer_profile.strike_count = (lawyer_profile.strike_count or 0) + 1
    elif outcome == "release":
        booking.status = BookingStatus.COMPLETED
    else:
        raise HTTPException(400, "invalid outcome")
    audit(db, admin, "booking.dispute_resolved", "booking", booking_id, {
        "outcome": outcome,
        "strike_lawyer": strike_lawyer,
        "auto_resolution_status": booking.auto_resolution_status
    })
    db.commit()
    return {"booking_id": booking_id, "status": booking.status}



@router.get("/audit-logs", response_model=list[AuditLogOut])
def get_audit_logs(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    query = select(AuditLog, User.full_name).outerjoin(User, AuditLog.actor_id == User.id).order_by(AuditLog.created_at.desc())
    rows = db.execute(query).all()
    result = []
    for log, name in rows:
        out = AuditLogOut(
            id=log.id,
            actor_id=log.actor_id,
            actor_name=name or "System",
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            metadata_json=log.metadata_json or {},
            created_at=log.created_at
        )
        result.append(out)
    return result


from ..rate_limiter import rate_limit_dependency


@router.post("/config/fees", dependencies=[Depends(rate_limit_dependency("strict"))])
def update_fees(default_fee: int, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    settings.stripe_platform_fee_percent = default_fee
    audit(db, admin, "config.fees_updated", "settings", None, {"default_fee": default_fee})
    db.commit()
    return {"status": "success", "default_fee": default_fee}


@router.post("/data-retention/purge", dependencies=[Depends(rate_limit_dependency("strict"))])
def trigger_data_retention_purge(
    dry_run: bool = Query(False, description="If true, preview counts without deleting anything."),
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    DPDP Act 2023, Section 8(7) — Trigger data retention purge.

    Deletes:
    - Completed/disputed bookings older than the configured retention window (~7 years default)
    - Cancelled/refunded bookings older than 1 year (default)
    - Expired and revoked refresh tokens
    - Withdrawn user consent records older than 365 days

    Use ?dry_run=true to preview counts without making any changes.
    Every run (live or dry) is logged to the audit trail.
    """
    # Import here to avoid circular imports at module load time
    from scripts.data_retention_purge import run_purge
    audit(db, admin, "system.data_retention_purge_triggered", "system", None,
          {"dry_run": dry_run, "triggered_by": admin.id})
    db.commit()
    results = run_purge(dry_run=dry_run)
    return {"status": "ok", "dry_run": dry_run, "results": results}


@router.get("/ntp-status")
def get_ntp_status(_admin: User = Depends(require_roles(Role.ADMIN))):
    """
    CERT-In / DPDP forensic compliance — NTP clock synchronization status.

    Returns the current clock drift between the application server and the
    authoritative NPL/NIC NTP servers. Use this endpoint to:
    - Verify that timestamps in audit logs, payment records, and video session
      logs are forensically synchronized with Indian government time sources.
    - Detect clock drift exceeding the configured CERT-In alert threshold.
    - Confirm which NTP server (NPL primary / NIC fallback) responded.

    Drift > ±2s triggers a CRITICAL log entry and sets within_tolerance=false.
    """
    return check_clock_drift()


@router.get("/payouts", response_model=list[AdminPayoutAccountOut])
def get_admin_payouts(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    """
    Returns all lawyer payout bank accounts with masked credentials (account number XXXXXX4821 and masked IFSC).
    Raw banking credentials are encrypted at rest and never exposed to admin or developer endpoints.
    """
    accounts = db.scalars(select(LawyerBankAccount).options(selectinload(LawyerBankAccount.user))).all()
    out = []
    for acct in accounts:
        raw_acct = acct.account_number or ""
        raw_ifsc = acct.ifsc_code or ""
        acct_clean = raw_acct.replace(" ", "")
        ifsc_clean = raw_ifsc.replace(" ", "")

        masked_acct = "X" * max(0, len(acct_clean) - 4) + acct_clean[-4:] if len(acct_clean) >= 4 else "XXXX"
        masked_ifsc = "X" * max(0, len(ifsc_clean) - 4) + ifsc_clean[-4:] if len(ifsc_clean) >= 4 else "XXXX"

        out.append(AdminPayoutAccountOut(
            id=acct.id,
            lawyer_id=acct.user_id,
            lawyer_name=acct.user.full_name if acct.user else "Unknown",
            account_holder_name=acct.account_holder_name,
            account_number_masked=masked_acct,
            ifsc_code_masked=masked_ifsc,
            bank_name=acct.bank_name,
            upi_vpa=acct.upi_vpa,
            upi_name=acct.upi_name,
            verified=acct.verified,
            verified_at=acct.verified_at,
            utr=acct.utr,
            created_at=acct.created_at,
        ))
    return out


@router.get("/feedback", response_model=list[PlatformFeedbackOut])
def get_platform_feedback(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    """Returns all submitted platform feedback ordered by newest first."""
    from ..models import PlatformFeedback
    feedbacks = db.scalars(select(PlatformFeedback).order_by(PlatformFeedback.created_at.desc())).all()
    return list(feedbacks)

