from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import LawyerBankAccount, Role, User
from ..schemas import BankAccountCreate, BankAccountOut, BankAccountUpdate
from ..security import require_roles
from ..services import audit, create_phonepe_verification_payment

router = APIRouter(tags=["bank-accounts"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_account(raw: str) -> str:
    """Return account number masked to last-4: e.g. 'XXXXXX4821'"""
    clean = (raw or "").replace(" ", "")
    return "X" * max(0, len(clean) - 4) + clean[-4:] if len(clean) >= 4 else "XXXX"


def _mask_ifsc(raw: str) -> str:
    """Return IFSC code masked to last-4: e.g. 'XXXXXXX1234'"""
    clean = (raw or "").replace(" ", "")
    return "X" * max(0, len(clean) - 4) + clean[-4:] if len(clean) >= 4 else "XXXX"


def _bank_account_out(acct: LawyerBankAccount) -> BankAccountOut:
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
        created_at=acct.created_at,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/api/v1/lawyers/me/bank-account", response_model=BankAccountOut)
def get_bank_account(user: User = Depends(require_roles(Role.LAWYER)), db: Session = Depends(get_db)):
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "no bank account on record")
    return _bank_account_out(acct)


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
    audit(db, user, "bank_account.created", "lawyer_bank_account", user.id,
          {"bank_name": acct.bank_name, "ifsc": acct.ifsc_code})
    db.commit()
    db.refresh(acct)
    return _bank_account_out(acct)


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
    if changed_sensitive:
        # Reset verification — account details changed
        acct.verified = False
        acct.verified_at = None
        acct.utr = None
        acct.upi_name = None
        acct.phonepe_txn_id = None
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
    """Initiate a ₹1 PhonePe Reverse Penny Drop to verify the lawyer's UPI identity."""
    acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.user_id == user.id))
    if not acct:
        raise HTTPException(404, "add a bank account before initiating verification")
    if acct.verified:
        return {"already_verified": True, "message": "account is already verified",
                "utr": acct.utr, "upi_vpa": acct.upi_vpa}

    payment_url = create_phonepe_verification_payment(acct, str(request.base_url))
    db.commit()  # persist phonepe_txn_id written by the service

    if payment_url:
        audit(db, user, "bank_account.verify_initiated", "lawyer_bank_account", user.id,
              {"txn_id": acct.phonepe_txn_id})
        db.commit()
        return {"payment_url": payment_url, "amount": 1, "currency": "INR",
                "message": "Complete ₹1 UPI payment to verify your identity"}
    else:
        # Demo / no-credentials mode: auto-verify immediately
        acct.verified = True
        acct.verified_at = datetime.now(timezone.utc)
        acct.utr = f"DEMO-{acct.id[:12].upper()}"
        acct.upi_name = acct.account_holder_name
        audit(db, user, "bank_account.verify_demo", "lawyer_bank_account", user.id)
        db.commit()
        return {"demo_verified": True, "message": "Demo mode: account marked verified instantly",
                "utr": acct.utr}
