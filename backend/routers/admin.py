from datetime import datetime, timezone
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..db import get_db
from ..models import AuditLog, Booking, BookingStatus, DraftingProposal, DraftingRequest, DraftingStatus, LawyerBankAccount, LawyerProfile, Role, User, Voucher
from ..ntp_time import check_clock_drift
from ..schemas import (
    AdminPayoutAccountOut, AdminVoucherOut, AuditLogOut, BookingOut, DraftingRequestOut, LawyerOut,
    PayoutSweepResult, PendingPayoutOut, PlatformFeedbackOut, PromoVoucherCreate, UserOut
)
from ..security import require_roles
from ..services import audit, initiate_refund
from ..services.payout_service import (
    get_pending_payouts, initiate_lawyer_payout, sweep_all_payouts
)
from .lawyers import invalidate_lawyers_cache

log = structlog.get_logger("admin")
settings = get_settings()

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/metrics")
def admin_metrics(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    # Realized escrow funds (funds actually captured and held in escrow pending completion)
    # Excludes PENDING_PAYMENT and CANCELLED
    booking_escrow = db.scalar(
        select(func.coalesce(func.sum(Booking.amount_minor), 0)).where(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS, BookingStatus.DISPUTED])
        )
    ) or 0

    drafting_escrow = db.scalar(
        select(func.coalesce(func.sum(DraftingRequest.price_minor), 0)).where(
            DraftingRequest.status.in_([
                DraftingStatus.IN_PROGRESS,
                DraftingStatus.SUBMITTED,
                DraftingStatus.REVISION_REQUESTED,
            ])
        )
    ) or 0

    pending_bookings = db.scalars(
        select(Booking).where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.payout_status.in_(["pending", "held", "failed"])
        )
    ).all()
    pending_drafts = db.scalars(
        select(DraftingRequest).where(
            DraftingRequest.status == DraftingStatus.COMPLETED,
            DraftingRequest.payout_status.in_(["pending", "held", "failed"])
        )
    ).all()
    pending_payouts_count = len(pending_bookings) + len(pending_drafts)
    pending_payouts_amount_minor = sum(b.lawyer_amount_minor for b in pending_bookings) + sum(d.drafter_amount_minor for d in pending_drafts)

    return {
        "users": db.scalar(select(func.count()).select_from(User)),
        "verified_lawyers": db.scalar(select(func.count()).select_from(LawyerProfile).where(LawyerProfile.verified.is_(True))),
        "bookings": db.scalar(select(func.count()).select_from(Booking)),
        "escrow_minor": booking_escrow + drafting_escrow,
        "pending_payouts_count": pending_payouts_count,
        "pending_payouts_amount_minor": pending_payouts_amount_minor,
    }



@router.patch("/lawyers/{lawyer_id}/verification")
def verify_lawyer(request: Request, lawyer_id: str, approved: bool | None = None, status: str | None = None,
                  rejection_reason: str | None = None,
                  admin: User = Depends(require_roles(Role.ADMIN)),
                  db: Session = Depends(get_db)):
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == lawyer_id))
    if not profile:
        raise HTTPException(404, "lawyer profile not found")
    
    if status:
        target_status = status.lower()
    elif approved is not None:
        target_status = "approved" if approved else "rejected"
    else:
        raise HTTPException(400, "approved or status parameter required")
    
    if target_status == "approved":
        if not profile.bar_license_url or not profile.aadhaar_url:
            raise HTTPException(400, "Cannot approve lawyer without both Bar Council Certificate and Aadhaar / Govt ID on file")
        profile.verification_status = "approved"
        profile.verified = True
        profile.bar_license_verified = True
        profile.aadhaar_verified = True
        profile.verified_at = datetime.now(timezone.utc)
        profile.rejection_reason = None
    else:
        # Rejection or Revocation
        profile.verification_status = "rejected"
        profile.verified = False
        profile.bar_license_verified = False
        profile.aadhaar_verified = False
        profile.verified_at = None
        profile.rejection_reason = (rejection_reason or "").strip() or "Credentials did not meet compliance requirements"

    audit(db, admin, "lawyer.verification", "user", lawyer_id, {
        "status": profile.verification_status,
        "approved": profile.verified,
        "rejection_reason": profile.rejection_reason
    }, request=request)
    db.commit()
    invalidate_lawyers_cache()
    return {
        "lawyer_id": lawyer_id,
        "verified": profile.verified,
        "verification_status": profile.verification_status,
        "rejection_reason": profile.rejection_reason
    }


@router.patch("/lawyers/{lawyer_id}/documents/verify")
def verify_lawyer_document(request: Request, lawyer_id: str, doc_type: str, verified: bool = True,
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

    audit(db, admin, "lawyer.document_verified", "user", lawyer_id, {"doc_type": doc_type, "verified": verified}, request=request)
    db.commit()
    invalidate_lawyers_cache()
    return {"status": "success", "lawyer_id": lawyer_id, "doc_type": doc_type, "verified": verified}


@router.get("/lawyers/{lawyer_id}/verification-dossier")
def get_lawyer_verification_dossier(
    lawyer_id: str,
    _admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    import re
    user = db.get(User, lawyer_id)
    if not user:
        raise HTTPException(404, "Lawyer user not found")
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == lawyer_id))
    if not profile:
        raise HTTPException(404, "Lawyer profile not found")
    bank = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == lawyer_id))

    # Helper for Aadhaar
    raw_aadhaar = profile.aadhaar_number or ""
    aadhaar_clean = raw_aadhaar.replace("-", "").replace(" ", "")
    masked_aadhaar = f"XXXX-XXXX-{aadhaar_clean[-4:]}" if len(aadhaar_clean) == 12 else (raw_aadhaar or "Not provided")

    # Helper for PAN
    raw_pan = profile.pan_number or ""
    pan_clean = raw_pan.strip().upper()
    masked_pan = f"XXXXX{pan_clean[5:]}" if len(pan_clean) == 10 else (raw_pan or "Not provided")

    # Helper for Bank
    bank_data = None
    if bank:
        raw_acct = bank.account_number or ""
        acct_clean = raw_acct.replace(" ", "")
        masked_acct = ("•" * max(0, len(acct_clean) - 4) + acct_clean[-4:]) if len(acct_clean) >= 4 else (raw_acct or "Not provided")

        raw_ifsc = bank.ifsc_code or ""
        ifsc_clean = raw_ifsc.replace(" ", "")
        masked_ifsc = ("•" * max(0, len(ifsc_clean) - 4) + ifsc_clean[-4:]) if len(ifsc_clean) >= 4 else (raw_ifsc or "Not provided")

        bank_data = {
            "id": bank.id,
            "account_holder_name": bank.account_holder_name,
            "bank_name": bank.bank_name,
            "account_number": raw_acct,
            "account_number_masked": masked_acct,
            "ifsc_code": raw_ifsc,
            "ifsc_code_masked": masked_ifsc,
            "upi_vpa": bank.upi_vpa,
            "verified": bank.verified,
            "verification_status": bank.verification_status,
            "upi_name": bank.upi_name,
            "utr": bank.utr,
            "verification_method": bank.verification_method,
            "verified_at": bank.verified_at,
        }

    # Extract years to detect mismatch
    bar_year = None
    if profile.bar_number:
        matches = re.findall(r"\b(19\d{2}|20\d{2})\b", profile.bar_number)
        if matches:
            bar_year = matches[-1]

    enrollment_year = None
    if profile.enrollment_date:
        enr_matches = re.findall(r"\b(19\d{2}|20\d{2})\b", profile.enrollment_date)
        if enr_matches:
            enrollment_year = enr_matches[0] if profile.enrollment_date.startswith(("19", "20")) else enr_matches[-1]

    year_mismatch = bool(bar_year and enrollment_year and bar_year != enrollment_year)

    # Calculate experience
    experience_text = "N/A"
    if profile.enrollment_date:
        try:
            parts = profile.enrollment_date.strip().split("-")
            if len(parts) == 3:
                if len(parts[0]) == 4:
                    enr_dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=timezone.utc)
                else:
                    enr_dt = datetime(int(parts[2]), int(parts[1]), int(parts[0]), tzinfo=timezone.utc)
                now_dt = datetime.now(timezone.utc)
                diff_days = (now_dt - enr_dt).days
                if diff_days >= 0:
                    years = diff_days // 365
                    months = (diff_days % 365) // 30
                    if years > 0:
                        experience_text = f"{years} yr{'s' if years > 1 else ''}" + (f" {months} mo{'s' if months > 1 else ''}" if months > 0 else "")
                    else:
                        experience_text = f"{max(1, months)} month{'s' if months > 1 else ''}"
                else:
                    experience_text = "Future Date (Invalid)"
        except Exception:
            experience_text = "Invalid date format"

    # Standard bar format check
    bar_format_valid = False
    if profile.bar_number:
        bar_format_valid = bool(re.match(r"^[A-Za-z]{1,4}\s*/\s*\d+\s*/\s*(19|20)\d{2}$", profile.bar_number.strip()))

    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "active": user.active,
            "created_at": user.created_at,
        },
        "profile": {
            "id": profile.id,
            "bar_number": profile.bar_number,
            "enrollment_date": profile.enrollment_date,
            "practice": profile.practice if isinstance(profile.practice, list) else [profile.practice],
            "languages": profile.languages or [],
            "hourly_fee_minor": profile.hourly_fee_minor,
            "rating": float(profile.rating or 0),
            "verified": profile.verified,
            "verification_status": profile.verification_status or "pending",
            "verified_at": profile.verified_at,
            "rejection_reason": profile.rejection_reason,
            "practice_address": profile.practice_address,
            "mobile_number": profile.mobile_number,
            "aadhaar_number": raw_aadhaar,
            "aadhaar_number_masked": masked_aadhaar,
            "pan_number": raw_pan,
            "pan_number_masked": masked_pan,
            "bar_license_url": profile.bar_license_url,
            "bar_license_verified": getattr(profile, "bar_license_verified", False),
            "aadhaar_url": profile.aadhaar_url,
            "aadhaar_verified": getattr(profile, "aadhaar_verified", False),
            "availability": profile.availability or {},
        },
        "bank_account": bank_data,
        "checks": {
            "bar_format_valid": bar_format_valid,
            "bar_year": bar_year,
            "enrollment_year": enrollment_year,
            "year_mismatch": year_mismatch,
            "experience_text": experience_text,
        }
    }



@router.get("/lawyers/pending", response_model=list[LawyerOut])
def list_pending_lawyers(search: str | None = None,
                         practice: str | None = None,
                         _admin: User = Depends(require_roles(Role.ADMIN)),
                         db: Session = Depends(get_db)):
    stmt = select(LawyerProfile, User).join(User).where(
        or_(
            LawyerProfile.verification_status == "pending",
            LawyerProfile.verification_status.is_(None)
        ),
        LawyerProfile.verified.is_(False)
    ).order_by(User.created_at.asc())

    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.full_name.ilike(search_term), LawyerProfile.bar_number.ilike(search_term)))

    rows = db.execute(stmt).all()
    out = []
    for p, u in rows:
        out.append(
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
                rejection_reason=getattr(p, "rejection_reason", None),
                verified_at=getattr(p, "verified_at", None),
                created_at=u.created_at
            )
        )
    return out


@router.get("/lawyers/rejected", response_model=list[LawyerOut])
def list_rejected_lawyers(search: str | None = None,
                          _admin: User = Depends(require_roles(Role.ADMIN)),
                          db: Session = Depends(get_db)):
    stmt = select(LawyerProfile, User).join(User).where(
        LawyerProfile.verification_status == "rejected"
    ).order_by(User.created_at.desc())

    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.full_name.ilike(search_term), LawyerProfile.bar_number.ilike(search_term)))

    rows = db.execute(stmt).all()
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
            rejection_reason=getattr(p, "rejection_reason", None),
            verified_at=getattr(p, "verified_at", None),
            created_at=u.created_at
        )
        for p, u in rows
    ]


@router.get("/users", response_model=list[UserOut])
def list_users(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


@router.patch("/users/{user_id}/active")
def toggle_user_active(request: Request, user_id: str, active: bool, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "user not found")
    user.active = active
    audit(db, admin, "user.status_change", "user", user_id, {"active": active}, request=request)
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
def resolve_dispute(request: Request, booking_id: str, outcome: str, strike_lawyer: bool = False, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "booking not found")
    if outcome == "refund":
        booking.status = BookingStatus.REFUNDED
        try:
            initiate_refund(booking, booking.amount_minor, reason="Admin dispute resolution refund")
        except Exception as exc:
            log.error("Dispute refund failed", booking_id=booking_id, error=str(exc))
        if strike_lawyer:
            lawyer_profile = db.query(LawyerProfile).filter(LawyerProfile.user_id == booking.lawyer_id).first()
            if lawyer_profile:
                lawyer_profile.strike_count = (lawyer_profile.strike_count or 0) + 1
    elif outcome == "release":
        now = datetime.now(timezone.utc)
        booking.status = BookingStatus.COMPLETED
        booking.completed_at = booking.completed_at or now
        booking.payout_status = "pending"
        initiate_lawyer_payout(booking, booking.lawyer_id, booking.lawyer_amount_minor, db, entity_type="booking")
    else:
        raise HTTPException(400, "invalid outcome")
    audit(db, admin, "booking.dispute_resolved", "booking", booking_id, {
        "outcome": outcome,
        "strike_lawyer": strike_lawyer,
        "auto_resolution_status": booking.auto_resolution_status
    }, request=request)
    db.commit()
    return {"booking_id": booking_id, "status": booking.status}



@router.get("/audit-logs", response_model=list[AuditLogOut])
def get_audit_logs(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    query = select(AuditLog, User.full_name).outerjoin(User, AuditLog.actor_id == User.id).order_by(AuditLog.created_at.desc())
    rows = db.execute(query).all()
    result = []
    for log, name in rows:
        meta = log.metadata_json or {}
        ip = meta.get("ip_address") if isinstance(meta, dict) else None
        out = AuditLogOut(
            id=log.id,
            actor_id=log.actor_id,
            actor_name=name or "System",
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            metadata_json=meta,
            ip_address=ip or "127.0.0.1",
            created_at=log.created_at
        )
        result.append(out)
    return result


from ..rate_limiter import rate_limit_dependency


@router.post("/config/fees", dependencies=[Depends(rate_limit_dependency("strict"))])
def update_fees(request: Request, default_fee: int, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    settings.platform_fee_percent = default_fee
    audit(db, admin, "config.fees_updated", "settings", None, {"default_fee": default_fee}, request=request)
    db.commit()
    return {"status": "success", "default_fee": default_fee}


@router.post("/data-retention/purge", dependencies=[Depends(rate_limit_dependency("strict"))])
def trigger_data_retention_purge(
    request: Request,
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
          {"dry_run": dry_run, "triggered_by": admin.id}, request=request)
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


@router.get("/payouts/pending", response_model=list[PendingPayoutOut])
def list_pending_payouts(_admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    """
    Returns unified list of bookings and drafting requests awaiting payout release.
    """
    return get_pending_payouts(db)


@router.post("/payouts/sweep", response_model=PayoutSweepResult)
def run_payout_sweep(request: Request, admin: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    """
    Manually triggers escrow release sweep:
    - Automatically releases consultations past the 7-day dispute window
    - Retries pending/held drafting request payouts
    """
    res = sweep_all_payouts(db)
    audit(db, admin, "admin.payout_sweep_executed", "payout", None, res, request=request)
    db.commit()
    return res


@router.post("/payouts/bookings/{booking_id}/release")
def force_release_booking_payout(
    booking_id: str,
    request: Request,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Admin override: Force-release escrow payout for a specific completed booking to lawyer's bank account.
    """
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(400, f"Cannot release payout for booking in status {booking.status}")

    res = initiate_lawyer_payout(booking, booking.lawyer_id, booking.lawyer_amount_minor, db, entity_type="booking")
    audit(db, admin, "admin.payout_force_released", "booking", booking_id, {
        "lawyer_id": booking.lawyer_id,
        "amount_minor": booking.lawyer_amount_minor,
        "result": res,
    }, request=request)
    db.commit()
    return {"booking_id": booking_id, "payout": res}


@router.post("/payouts/drafts/{draft_id}/release")
def force_release_draft_payout(
    draft_id: str,
    request: Request,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Admin override: Force-release payout for a completed drafting request to drafter's bank account.
    """
    draft = db.get(DraftingRequest, draft_id)
    if not draft:
        raise HTTPException(404, "Drafting request not found")
    if draft.status != DraftingStatus.COMPLETED:
        raise HTTPException(400, f"Cannot release payout for draft in status {draft.status}")

    res = initiate_lawyer_payout(draft, draft.drafter_id, draft.drafter_amount_minor, db, entity_type="draft")
    audit(db, admin, "admin.payout_force_released", "drafting_request", draft_id, {
        "drafter_id": draft.drafter_id,
        "amount_minor": draft.drafter_amount_minor,
        "result": res,
    }, request=request)
    db.commit()
    return {"draft_id": draft_id, "payout": res}


# ── Promotional Vouchers ──────────────────────────────────────────────────────

@router.get("/vouchers", response_model=list[AdminVoucherOut])
def list_vouchers(
    _admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    List all vouchers (promotional campaigns and cancellation vouchers) with stats.
    """
    query = select(Voucher).order_by(Voucher.created_at.desc())
    return list(db.scalars(query).all())


@router.post("/vouchers", response_model=AdminVoucherOut, status_code=201)
def create_promotional_voucher(
    payload: PromoVoucherCreate,
    request: Request,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Create a new promotional discount voucher with admin-chosen discount %.
    """
    existing = db.scalar(select(Voucher).where(func.upper(Voucher.code) == payload.code.upper()))
    if existing:
        raise HTTPException(400, f"A voucher with code '{payload.code}' already exists.")

    expires_at = payload.expires_at
    if not expires_at:
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    elif expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(422, "Expiry date must be in the future.")

    voucher = Voucher(
        code=payload.code.upper(),
        discount_percent=payload.discount_percent,
        expires_at=expires_at,
        is_promotional=True,
        max_uses=payload.max_uses,
        times_used=0,
        is_active=True,
        description=payload.description,
        created_by=admin.id,
        used=False
    )
    db.add(voucher)
    db.flush()

    audit(db, admin, "admin.voucher_created", "voucher", voucher.id, {
        "code": voucher.code,
        "discount_percent": voucher.discount_percent,
        "max_uses": voucher.max_uses,
        "expires_at": voucher.expires_at.isoformat(),
        "description": voucher.description
    }, request=request)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.patch("/vouchers/{voucher_id}/toggle", response_model=AdminVoucherOut)
def toggle_voucher_status(
    voucher_id: str,
    active: bool = Query(...),
    request: Request = None,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Toggle active / paused status of a promotional voucher.
    """
    voucher = db.get(Voucher, voucher_id)
    if not voucher:
        raise HTTPException(404, "Voucher not found.")

    voucher.is_active = active
    audit(db, admin, "admin.voucher_status_toggled", "voucher", voucher.id, {
        "code": voucher.code,
        "is_active": active
    }, request=request)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.delete("/vouchers/{voucher_id}")
def delete_voucher(
    voucher_id: str,
    request: Request = None,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Delete a promotional voucher.
    """
    voucher = db.get(Voucher, voucher_id)
    if not voucher:
        raise HTTPException(404, "Voucher not found.")

    code = voucher.code
    db.delete(voucher)
    audit(db, admin, "admin.voucher_deleted", "voucher", voucher_id, {
        "code": code
    }, request=request)
    db.commit()
    return {"message": f"Voucher '{code}' deleted successfully", "id": voucher_id}

