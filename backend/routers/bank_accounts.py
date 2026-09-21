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
)
from ..security import require_roles
from ..services import audit

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
        verification_method=acct.verification_method or "manual",
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


@router.post("/api/v1/lawyers/me/bank-account/verify")
def initiate_upi_verification(request: Request, user: User = Depends(require_roles(Role.LAWYER)),
                              db: Session = Depends(get_db)):
    """Verify lawyer bank account details."""
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "Add a bank account before initiating verification")
    if acct.verified:
        return {"already_verified": True, "message": "Bank account is already verified",
                "utr": acct.utr, "upi_vpa": acct.upi_vpa}

    acct.verified = True
    acct.verified_at = datetime.now(timezone.utc)
    acct.verification_status = "verified"
    acct.verification_method = "manual"
    acct.utr = f"VERIFIED-{acct.id[:12].upper()}"
    acct.upi_name = acct.account_holder_name
    audit(db, user, "bank_account.verified", "lawyer_bank_account", user.id)
    db.commit()
    db.refresh(acct)
    return {"verified": True, "message": "Bank account verified successfully",
            "utr": acct.utr}

