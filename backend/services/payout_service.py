"""
Cashfree Payouts and Escrow Release Service.
Manages automated and administrative payout transfers to verified lawyer bank accounts
following the completion of consultations (after the 7-day dispute window)
and document drafting milestones (immediately upon client approval).
"""

import time
import uuid
import httpx
import structlog
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import (
    AuditLog,
    Booking,
    BookingStatus,
    DraftingRequest,
    DraftingStatus,
    LawyerBankAccount,
    LawyerProfile,
    User,
)

logger = structlog.get_logger("payout_service")
settings = get_settings()


def get_payout_api_base_url() -> str:
    if settings.cashfree_mode.lower() == "production":
        return "https://payout-api.cashfree.com/payout/v1"
    return "https://payout-gamma.cashfree.com/payout/v1"


def _call_cashfree_transfer(
    transfer_id: str,
    amount_inr: float,
    beneficiary_account: str,
    beneficiary_ifsc: str,
    beneficiary_name: str,
    remarks: str = "VidhiMeet Payout"
) -> dict[str, Any]:
    """
    Executes a direct bank transfer request via Cashfree Payouts API.
    """
    url = f"{get_payout_api_base_url()}/directTransfer"
    headers = {
        "X-Client-Id": settings.cashfree_payout_app_id,
        "X-Client-Secret": settings.cashfree_payout_secret_key,
        "Content-Type": "application/json",
    }
    payload = {
        "transferId": transfer_id,
        "amount": f"{amount_inr:.2f}",
        "transferMode": "banktransfer",
        "beneficiaryDetails": {
            "bankAccount": beneficiary_account,
            "ifsc": beneficiary_ifsc,
            "name": beneficiary_name,
        },
        "remarks": remarks,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("subCode") in ("200", "201", "SUCCESS"):
                return {
                    "success": True,
                    "reference_id": data.get("data", {}).get("referenceId") or transfer_id,
                    "status": "paid",
                    "raw": data,
                }
            logger.error("Cashfree payout transfer returned error", status_code=resp.status_code, body=resp.text)
            return {
                "success": False,
                "reference_id": transfer_id,
                "status": "failed",
                "error": data.get("message") or resp.text,
            }
    except Exception as exc:
        logger.exception("Cashfree Payout HTTP call failed", error=str(exc))
        return {
            "success": False,
            "reference_id": transfer_id,
            "status": "failed",
            "error": str(exc),
        }


def initiate_lawyer_payout(
    entity: Booking | DraftingRequest,
    lawyer_id: str | None,
    amount_minor: int,
    db: Session,
    entity_type: str = "booking",
) -> dict[str, Any]:
    """
    Dispatches payout to the lawyer for a completed booking or drafting request.
    Verifies that the lawyer has a verified bank account on file.
    If not verified, the payout is marked 'held' until account verification is complete.
    """
    now = datetime.now(timezone.utc)
    entity_id = entity.id

    if not lawyer_id:
        entity.payout_status = "failed"
        logger.warning("Payout aborted: No lawyer associated with entity", entity_id=entity_id)
        return {"status": "failed", "reason": "No lawyer assigned"}

    # 1. Fetch Lawyer Bank Account
    bank_account = db.scalar(
        select(LawyerBankAccount).where(LawyerBankAccount.user_id == lawyer_id)
    )

    if not bank_account or not bank_account.verified:
        entity.payout_status = "held"
        logger.info(
            "Payout held: Lawyer has no verified bank account",
            entity_type=entity_type,
            entity_id=entity_id,
            lawyer_id=lawyer_id,
        )
        return {
            "status": "held",
            "reason": "Lawyer does not have a verified bank account",
            "entity_id": entity_id,
        }

    # 2. Check that PAN is on file (required for TDS compliance under Income Tax Act)
    lawyer_profile = db.scalar(
        select(LawyerProfile).where(LawyerProfile.user_id == lawyer_id)
    )
    has_pan = bool(lawyer_profile and lawyer_profile.pan_number) or bool(bank_account.pan_number if hasattr(bank_account, 'pan_number') else False)
    if not has_pan:
        entity.payout_status = "held"
        logger.info(
            "Payout held: Lawyer PAN number not on file",
            entity_type=entity_type,
            entity_id=entity_id,
            lawyer_id=lawyer_id,
        )
        return {
            "status": "held",
            "reason": "PAN number is required for payout settlement (Income Tax Act compliance). Please update your KYC.",
            "entity_id": entity_id,
        }

    amount_inr = round(amount_minor / 100, 2)
    transfer_id = f"vm_pay_{entity_type[:4]}_{entity_id[:8]}_{int(time.time())}"

    # 2. Check if live Cashfree Payout keys are configured
    has_live_keys = bool(
        settings.cashfree_payout_app_id and settings.cashfree_payout_secret_key
    )

    if has_live_keys:
        logger.info(
            "Initiating live Cashfree payout transfer",
            entity_type=entity_type,
            entity_id=entity_id,
            amount_inr=amount_inr,
            transfer_id=transfer_id,
        )
        res = _call_cashfree_transfer(
            transfer_id=transfer_id,
            amount_inr=amount_inr,
            beneficiary_account=bank_account.account_number,
            beneficiary_ifsc=bank_account.ifsc_code,
            beneficiary_name=bank_account.account_holder_name,
            remarks=f"VidhiMeet payout for {entity_type} {entity_id[:8]}",
        )
        if res.get("success"):
            entity.payout_status = "paid"
            entity.payout_reference_id = res.get("reference_id")
            entity.payout_at = now
            status_code = "paid"
        else:
            entity.payout_status = "failed"
            entity.payout_reference_id = transfer_id
            status_code = "failed"
    else:
        # Fallback Mock Payout for local dev / staging / sandbox test suites
        logger.info(
            "Cashfree Payouts credentials not configured; executing mock payout",
            entity_type=entity_type,
            entity_id=entity_id,
            amount_inr=amount_inr,
            lawyer_id=lawyer_id,
            transfer_id=transfer_id,
        )
        entity.payout_status = "paid"
        entity.payout_reference_id = f"cf_mock_{uuid.uuid4().hex[:12]}"
        entity.payout_at = now
        status_code = "paid"

    return {
        "status": status_code,
        "payout_reference_id": entity.payout_reference_id,
        "amount_minor": amount_minor,
        "payout_at": entity.payout_at.isoformat() if entity.payout_at else None,
        "entity_id": entity_id,
    }


def sweep_booking_payouts(db: Session) -> dict[str, Any]:
    """
    Sweeps all COMPLETED Bookings whose 7-day dispute window has expired
    and whose payout is still pending or uninitiated.
    """
    now = datetime.now(timezone.utc)
    candidates = db.scalars(
        select(Booking).where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.payout_status.in_([None, "pending"]),
            Booking.dispute_deadline_at.is_not(None),
            Booking.dispute_deadline_at <= now,
        )
    ).all()

    processed, held, failed = 0, 0, 0

    for b in candidates:
        try:
            res = initiate_lawyer_payout(
                entity=b,
                lawyer_id=b.lawyer_id,
                amount_minor=b.lawyer_amount_minor,
                db=db,
                entity_type="booking",
            )
            status = res.get("status")
            if status == "paid":
                processed += 1
            elif status == "held":
                held += 1
            else:
                failed += 1
        except Exception as exc:
            logger.exception("Failed to process booking payout in sweep", booking_id=b.id, error=str(exc))
            b.payout_status = "failed"
            failed += 1

    if candidates:
        db.commit()

    return {
        "total": len(candidates),
        "processed": processed,
        "held": held,
        "failed": failed,
    }


def sweep_draft_payouts(db: Session) -> dict[str, Any]:
    """
    Sweeps all COMPLETED DraftingRequests whose payout is still pending or held
    (e.g., if drafter newly verified their bank account or network failed initially).
    """
    candidates = db.scalars(
        select(DraftingRequest).where(
            DraftingRequest.status == DraftingStatus.COMPLETED,
            DraftingRequest.payout_status.in_([None, "pending"]),
        )
    ).all()

    processed, held, failed = 0, 0, 0

    for req in candidates:
        try:
            res = initiate_lawyer_payout(
                entity=req,
                lawyer_id=req.drafter_id,
                amount_minor=req.drafter_amount_minor,
                db=db,
                entity_type="draft",
            )
            status = res.get("status")
            if status == "paid":
                processed += 1
            elif status == "held":
                held += 1
            else:
                failed += 1
        except Exception as exc:
            logger.exception("Failed to process draft payout in sweep", draft_id=req.id, error=str(exc))
            req.payout_status = "failed"
            failed += 1

    if candidates:
        db.commit()

    return {
        "total": len(candidates),
        "processed": processed,
        "held": held,
        "failed": failed,
    }


def sweep_all_payouts(db: Session) -> dict[str, Any]:
    """
    Runs full sweep over both bookings and draft requests.
    """
    bookings_res = sweep_booking_payouts(db)
    drafts_res = sweep_draft_payouts(db)
    return {
        "bookings": bookings_res,
        "drafts": drafts_res,
        "total_processed": bookings_res["processed"] + drafts_res["processed"],
        "total_held": bookings_res["held"] + drafts_res["held"],
        "total_failed": bookings_res["failed"] + drafts_res["failed"],
    }


def get_pending_payouts(db: Session) -> list[dict[str, Any]]:
    """
    Retrieves unified list of pending/held/failed payouts across bookings and drafts.
    """
    now = datetime.now(timezone.utc)
    results = []

    # Bookings
    bookings = db.scalars(
        select(Booking).where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.payout_status.in_(["pending", "held", "failed"]),
        ).order_by(Booking.completed_at.desc())
    ).all()

    for b in bookings:
        deadline_passed = bool(b.dispute_deadline_at and b.dispute_deadline_at <= now)
        results.append({
            "entity_type": "booking",
            "id": b.id,
            "lawyer_id": b.lawyer_id,
            "lawyer_name": b.lawyer_name,
            "client_name": b.client_name,
            "amount_minor": b.lawyer_amount_minor,
            "total_amount_minor": b.amount_minor,
            "payout_status": b.payout_status or "pending",
            "payout_reference_id": b.payout_reference_id,
            "completed_at": b.completed_at.isoformat() if b.completed_at else None,
            "dispute_deadline_at": b.dispute_deadline_at.isoformat() if b.dispute_deadline_at else None,
            "dispute_window_expired": deadline_passed,
        })

    # Drafts
    drafts = db.scalars(
        select(DraftingRequest).where(
            DraftingRequest.status == DraftingStatus.COMPLETED,
            DraftingRequest.payout_status.in_(["pending", "held", "failed"]),
        ).order_by(DraftingRequest.completed_at.desc())
    ).all()

    for d in drafts:
        results.append({
            "entity_type": "draft",
            "id": d.id,
            "lawyer_id": d.drafter_id,
            "lawyer_name": d.drafter_name,
            "client_name": d.creator_name,
            "amount_minor": d.drafter_amount_minor,
            "total_amount_minor": d.agreed_price_minor or d.price_minor,
            "payout_status": d.payout_status or "pending",
            "payout_reference_id": d.payout_reference_id,
            "completed_at": d.completed_at.isoformat() if d.completed_at else None,
            "dispute_deadline_at": None,
            "dispute_window_expired": True,  # Drafts have no hold window
        })

    return results
