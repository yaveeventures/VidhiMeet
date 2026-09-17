from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import LawyerBankAccount, LawyerProfile, Role, User
from ..schemas import (
    BankAccountCreate,
    BankAccountOut,
    BankAccountUpdate,
    RpdInitiateResponse,
    RpdStatusResponse,
)
from ..security import require_roles
from ..services import (
    audit,
    initiate_reverse_penny_drop,
    get_reverse_penny_drop_status,
    mock_complete_reverse_penny_drop,
)

import structlog

router = APIRouter(tags=["bank-accounts"])
logger = structlog.get_logger("bank_accounts")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_account(raw: str) -> str:
    """Return account number masked to last-4: e.g. 'XXXXXX4821'"""
    clean = (raw or "").replace(" ", "")
    return "X" * max(0, len(clean) - 4) + clean[-4:] if len(clean) >= 4 else "XXXX"


def _mask_ifsc(raw: str) -> str:
    """Return IFSC code masked to last-4: e.g. 'XXXXXXX1234'"""
    clean = (raw or "").replace(" ", "")
    return "X" * max(0, len(clean) - 4) + clean[-4:] if len(clean) >= 4 else "XXXX"


def _mask_pan(raw: str | None) -> str | None:
    if not raw:
        return None
    clean = raw.strip().upper()
    if len(clean) == 10:
        return f"XXXXX{clean[5:]}"
    return "XXXXXXXXXX"


def _bank_account_out(acct: LawyerBankAccount, profile: LawyerProfile | None = None) -> BankAccountOut:
    if profile is None and acct and acct.user:
        profile = getattr(acct.user, "lawyer_profile", None)
    pan_masked = _mask_pan(profile.pan_number) if profile else None
    has_pan = bool(profile and profile.pan_number)

    return BankAccountOut(
        id=acct.id,
        account_holder_name=acct.account_holder_name,
        account_number_masked=_mask_account(acct.account_number),
        ifsc_code=acct.ifsc_code,
        ifsc_code_masked=_mask_ifsc(acct.ifsc_code),
        bank_name=acct.bank_name,
        upi_vpa=acct.upi_vpa,
        upi_name=acct.upi_name,
        verified=acct.verified,
        verified_at=acct.verified_at,
        utr=acct.utr,
        verification_status=acct.verification_status or ("verified" if acct.verified else "unverified"),
        verification_method=acct.verification_method or "reverse_penny_drop",
        verification_id=acct.verification_id,
        pan_number_masked=pan_masked,
        has_pan=has_pan,
        created_at=acct.created_at,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/api/v1/lawyers/me/bank-account", response_model=BankAccountOut)
def get_bank_account(user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "no bank account on record")
    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    return _bank_account_out(acct, profile=profile)


@router.post("/api/v1/lawyers/me/bank-account", response_model=BankAccountOut, status_code=201)
def add_bank_account(payload: BankAccountCreate, user: User = Depends(require_roles(Role.LAWYER)),
                     db: Session = Depends(get_db)):
    if db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id)):
        raise HTTPException(409, "bank account already exists — use PUT to update")
    acct = LawyerBankAccount(
        user_id=user.id,
        account_holder_name=payload.account_holder_name.strip(),
        account_number=payload.account_number.strip(),
        ifsc_code=payload.ifsc_code.strip().upper(),
        bank_name=payload.bank_name.strip(),
        upi_vpa=payload.upi_vpa.strip() if payload.upi_vpa else None,
    )
    db.add(acct)

    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if payload.pan_number and profile:
        profile.pan_number = payload.pan_number.strip().upper()

    audit(db, user, "bank_account.created", "lawyer_bank_account", user.id,
          {"bank_name": acct.bank_name, "ifsc": acct.ifsc_code})
    db.commit()
    db.refresh(acct)
    return _bank_account_out(acct, profile=profile)


@router.put("/api/v1/lawyers/me/bank-account", response_model=BankAccountOut)
def update_bank_account(payload: BankAccountUpdate, user: User = Depends(require_roles(Role.LAWYER)),
                        db: Session = Depends(get_db)):
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "no bank account on record — use POST to create")
    changed_sensitive = False
    if payload.account_holder_name is not None:
        acct.account_holder_name = payload.account_holder_name.strip()
    if payload.account_number is not None and payload.account_number.strip() != acct.account_number:
        acct.account_number = payload.account_number.strip()
        changed_sensitive = True
    if payload.ifsc_code is not None and payload.ifsc_code.strip().upper() != acct.ifsc_code:
        acct.ifsc_code = payload.ifsc_code.strip().upper()
        changed_sensitive = True
    if payload.bank_name is not None:
        acct.bank_name = payload.bank_name.strip()
    if payload.upi_vpa is not None:
        acct.upi_vpa = payload.upi_vpa.strip() or None

    profile = db.scalar(select(LawyerProfile).where(LawyerProfile.user_id == user.id))
    if payload.pan_number and profile:
        profile.pan_number = payload.pan_number.strip().upper()

    if changed_sensitive:
        # Reset verification — account details changed
        acct.verified = False
        acct.verified_at = None
        acct.utr = None
        acct.upi_name = None
        acct.verification_txn_id = None
    audit(db, user, "bank_account.updated", "lawyer_bank_account", user.id,
          {"reset_verification": changed_sensitive})
    db.commit()
    db.refresh(acct)
    return _bank_account_out(acct)


@router.delete("/api/v1/lawyers/me/bank-account", status_code=204)
def delete_bank_account(user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "no bank account on record")
    audit(db, user, "bank_account.deleted", "lawyer_bank_account", user.id)
    db.delete(acct)
    db.commit()
    return Response(status_code=204)


@router.post("/api/v1/lawyers/me/bank-account/reverse-penny-drop/initiate", response_model=RpdInitiateResponse)
def rpd_initiate(user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    """
    Initiate Cashfree Reverse Penny Drop (RPD) to add or verify a lawyer's bank account.
    Returns a ₹1 UPI payment request (QR code, payment link, UPI intent).
    """
    try:
        acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    except Exception as db_err:
        logger.error("Failed to query lawyer_bank_accounts", user_id=user.id, error=str(db_err))
        raise HTTPException(500, detail="Database error accessing bank account. Please ensure database migrations have been executed.")

    if acct and acct.verified:
        raise HTTPException(400, "Bank account is already verified")

    try:
        rpd_data = initiate_reverse_penny_drop(user)
    except ValueError as ve:
        logger.warning("Cashfree RPD validation failed", user_id=user.id, error=str(ve))
        raise HTTPException(400, detail=str(ve))
    except Exception as exc:
        logger.error("Cashfree RPD initiation exception", user_id=user.id, error=str(exc))
        raise HTTPException(502, detail=f"Cashfree verification service unavailable: {str(exc)}")

    verification_id = rpd_data["verification_id"]

    try:
        if acct:
            acct.verification_id = verification_id
            acct.reference_id = rpd_data.get("reference_id")
            acct.verification_method = "reverse_penny_drop"
            acct.verification_status = "pending"
        else:
            # Create a pending placeholder record so verification_id is tracked
            acct = LawyerBankAccount(
                user_id=user.id,
                account_holder_name=user.full_name or "Advocate",
                account_number="PENDING",
                ifsc_code="PENDING",
                bank_name="Pending UPI Verification",
                verification_id=verification_id,
                reference_id=rpd_data.get("reference_id"),
                verification_method="reverse_penny_drop",
                verification_status="pending",
                verified=False,
            )
            db.add(acct)

        audit(db, user, "bank_account.rpd_initiated", "lawyer_bank_account", user.id,
              {"verification_id": verification_id})
        db.commit()
    except Exception as db_commit_err:
        db.rollback()
        logger.error("Failed to persist RPD session to database", user_id=user.id, error=str(db_commit_err))
        raise HTTPException(500, detail="Database error saving verification record. Please run the Supabase migration script.")

    return RpdInitiateResponse(
        verification_id=verification_id,
        reference_id=rpd_data.get("reference_id"),
        status=rpd_data.get("status", "PENDING"),
        payment_link=rpd_data.get("payment_link"),
        qr_code=rpd_data.get("qr_code"),
        upi_intent=rpd_data.get("upi_intent"),
        valid_upto=rpd_data.get("valid_upto"),
        amount=1.0,
        currency="INR",
        is_mock=rpd_data.get("is_mock", False),
        message="Scan UPI QR code or click UPI app link to complete ₹1 verification.",
    )


@router.get("/api/v1/lawyers/me/bank-account/reverse-penny-drop/status", response_model=RpdStatusResponse)
def rpd_status(verification_id: str | None = None,
               user: User = Depends(require_roles(Role.LAWYER)),
               db: Session = Depends(get_db)):
    """
    Check status of Cashfree Reverse Penny Drop request.
    When successful, automatically extracts and verifies remitter bank account details.
    """
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    v_id = verification_id or (acct.verification_id if acct else None)
    if not v_id:
        raise HTTPException(400, "No active verification ID found for this account")

    result = get_reverse_penny_drop_status(v_id)
    is_success = result.get("status") == "SUCCESS" and result.get("verified", False)

    if is_success:
        now_dt = datetime.now(timezone.utc)
        utr = result.get("utr") or f"UTR-{v_id}"
        acc_num = result.get("account_number") or "0000000000"
        ifsc = (result.get("ifsc") or "HDFC0001234").upper()
        holder = result.get("account_holder_name") or user.full_name or "Advocate"
        b_name = result.get("bank_name") or "Verified Bank"
        upi_vpa = result.get("upi_vpa")
        upi_name = result.get("upi_name") or holder

        if acct:
            acct.verified = True
            acct.verified_at = now_dt
            acct.utr = utr
            acct.verification_status = "verified"
            acct.verification_method = "reverse_penny_drop"
            if acc_num and acc_num != "PENDING":
                acct.account_number = acc_num
            if ifsc and ifsc != "PENDING":
                acct.ifsc_code = ifsc
            if holder:
                acct.account_holder_name = holder
            if b_name and b_name != "Pending UPI Verification":
                acct.bank_name = b_name
            if upi_vpa:
                acct.upi_vpa = upi_vpa
            if upi_name:
                acct.upi_name = upi_name
        else:
            acct = LawyerBankAccount(
                user_id=user.id,
                account_holder_name=holder,
                account_number=acc_num,
                ifsc_code=ifsc,
                bank_name=b_name,
                upi_vpa=upi_vpa,
                upi_name=upi_name,
                verified=True,
                verified_at=now_dt,
                utr=utr,
                verification_id=v_id,
                verification_method="reverse_penny_drop",
                verification_status="verified",
            )
            db.add(acct)

        audit(db, user, "bank_account.rpd_verified", "lawyer_bank_account", user.id,
              {"utr": utr, "bank_name": acct.bank_name})
        db.commit()
        db.refresh(acct)

        return RpdStatusResponse(
            verification_id=v_id,
            status="SUCCESS",
            verified=True,
            utr=acct.utr,
            account_holder_name=acct.account_holder_name,
            bank_name=acct.bank_name,
            account_number_masked=_mask_account(acct.account_number),
            ifsc_code=acct.ifsc_code,
            upi_vpa=acct.upi_vpa,
            message="Bank account verified successfully via Cashfree Reverse Penny Drop.",
        )

    return RpdStatusResponse(
        verification_id=v_id,
        status=result.get("status", "PENDING"),
        verified=False,
        utr=None,
        account_holder_name=None,
        bank_name=None,
        account_number_masked=None,
        ifsc_code=None,
        upi_vpa=None,
        message=result.get("message", "Awaiting UPI payment confirmation."),
    )


@router.post("/api/v1/lawyers/me/bank-account/reverse-penny-drop/mock-complete")
def rpd_mock_complete(payload: dict | None = None,
                      user: User = Depends(require_roles(Role.LAWYER)),
                      db: Session = Depends(get_db)):
    """
    Test/Development simulation endpoint:
    Simulates successful ₹1 UPI payment and bank details extraction for testing.
    """
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    v_id = (payload or {}).get("verification_id") or (acct.verification_id if acct else None)
    if not v_id:
        raise HTTPException(400, "No active verification ID found to simulate")

    custom_account = (payload or {}).get("account_number") or "50100498765432"
    custom_ifsc = (payload or {}).get("ifsc") or "HDFC0001234"
    custom_name = (payload or {}).get("name") or user.full_name or "Advocate Legal"

    mock_complete_reverse_penny_drop(v_id, custom_account, custom_ifsc, custom_name)
    return rpd_status(v_id, user, db)


@router.post("/api/v1/lawyers/me/bank-account/verify")
def initiate_upi_verification(request: Request, user: User = Depends(require_roles(Role.LAWYER)),
                              db: Session = Depends(get_db)):
    """
    Verify lawyer bank account details.
    Seamlessly triggers or returns Cashfree Reverse Penny Drop session.
    """
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        # If no bank account exists yet, initiate RPD so details are auto-fetched
        rpd = rpd_initiate(user, db)
        return {
            "already_verified": False,
            "verification_id": rpd.verification_id,
            "payment_link": rpd.payment_link,
            "qr_code": rpd.qr_code,
            "upi_intent": rpd.upi_intent,
            "message": "Initiate ₹1 UPI payment to auto-link and verify bank account."
        }
    if acct.verified:
        return {"already_verified": True, "message": "account is already verified",
                "utr": acct.utr, "upi_vpa": acct.upi_vpa}

    rpd = rpd_initiate(user, db)
    return {
        "already_verified": False,
        "verification_id": rpd.verification_id,
        "payment_link": rpd.payment_link,
        "qr_code": rpd.qr_code,
        "upi_intent": rpd.upi_intent,
        "message": "Initiate ₹1 UPI payment to verify bank account."
    }
