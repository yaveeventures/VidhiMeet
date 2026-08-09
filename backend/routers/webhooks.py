import hashlib
import json
import secrets

import stripe
import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Booking, BookingStatus, LawyerBankAccount, WebhookEvent
from ..services import audit

log = structlog.get_logger("webhooks")
settings = get_settings()

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"], include_in_schema=False)


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(alias="Stripe-Signature"),
                         db: Session = Depends(get_db)):
    if not settings.stripe_webhook_secret:
        raise HTTPException(503, "webhook not configured")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(400, "invalid webhook") from exc
    if db.get(WebhookEvent, event["id"]):
        return {"received": True, "duplicate": True}
    db.add(WebhookEvent(provider_id=event["id"], event_type=event["type"]))
    obj = event["data"]["object"]
    booking = db.scalar(select(Booking).where(Booking.stripe_payment_intent_id == obj.get("id")))
    if booking and event["type"] == "payment_intent.succeeded":
        booking.status = BookingStatus.CONFIRMED
    elif booking and event["type"] == "payment_intent.payment_failed":
        booking.status = BookingStatus.CANCELLED
    audit(db, None, f"stripe.{event['type']}", "booking", booking.id if booking else None)
    db.commit()
    return {"received": True}


@router.post("/phonepe")
async def phonepe_webhook(request: Request, x_verify: str = Header(alias="X-VERIFY"), db: Session = Depends(get_db)):
    import base64
    import json

    if not settings.phonepe_salt_key:
        raise HTTPException(503, "webhook not configured")

    payload_bytes = await request.body()
    payload_str = payload_bytes.decode("utf-8")

    hash_input_1 = payload_str + settings.phonepe_salt_key
    expected_hash_1 = hashlib.sha256(hash_input_1.encode("utf-8")).hexdigest()
    expected_verify_1 = f"{expected_hash_1}###{settings.phonepe_salt_index}"

    try:
        body_json = json.loads(payload_str)
        base64_response = body_json.get("response", "")
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        base64_response = ""

    hash_input_2 = base64_response + settings.phonepe_salt_key
    expected_hash_2 = hashlib.sha256(hash_input_2.encode("utf-8")).hexdigest()
    expected_verify_2 = f"{expected_hash_2}###{settings.phonepe_salt_index}"

    verified = secrets.compare_digest(x_verify.lower(), expected_verify_1.lower()) or secrets.compare_digest(x_verify.lower(), expected_verify_2.lower())

    if not verified:
        raise HTTPException(400, "invalid signature")

    try:
        decoded_bytes = base64.b64decode(base64_response)
        response_data = json.loads(decoded_bytes.decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "invalid payload encoding") from exc

    event_id = response_data.get("data", {}).get("transactionId", secrets.token_hex(8))
    if db.get(WebhookEvent, event_id):
        return {"received": True, "duplicate": True}

    db.add(WebhookEvent(provider_id=event_id, event_type="phonepe." + response_data.get("code", "unknown")))

    data_obj = response_data.get("data", {})
    txn_id = data_obj.get("merchantTransactionId")
    code = response_data.get("code")
    utr = data_obj.get("transactionId", "")
    vpa = data_obj.get("paymentInstrument", {}).get("vpa") or \
          data_obj.get("paymentInstrument", {}).get("upiTransactionId") or None

    # Route to bank-account UPI verification if transaction ID has VERIFY- prefix
    if txn_id and txn_id.startswith("VERIFY-"):
        bank_acct = db.scalar(select(LawyerBankAccount).where(
            LawyerBankAccount.phonepe_txn_id == txn_id
        ))
        if bank_acct:
            if code == "PAYMENT_SUCCESS":
                bank_acct.verified = True
                from datetime import datetime, timezone
                bank_acct.verified_at = datetime.now(timezone.utc)
                bank_acct.utr = utr or event_id
                bank_acct.upi_name = (
                    data_obj.get("paymentInstrument", {}).get("name")
                    or bank_acct.account_holder_name
                )
                if vpa:
                    bank_acct.upi_vpa = vpa
            elif code in ("PAYMENT_ERROR", "PAYMENT_DECLINED"):
                # Leave verified=False; lawyer can retry
                pass
            audit(db, None, f"phonepe.verify.{code}", "lawyer_bank_account", bank_acct.user_id,
                  {"utr": utr, "vpa": vpa})
        db.commit()
        return {"received": True}

    # Standard booking payment path
    booking = db.scalar(select(Booking).where(Booking.phonepe_transaction_id == txn_id))
    if booking:
        if code == "PAYMENT_SUCCESS":
            booking.status = BookingStatus.CONFIRMED
        elif code == "PAYMENT_ERROR":
            booking.status = BookingStatus.CANCELLED
        audit(db, None, f"phonepe.{code}", "booking", booking.id)

    db.commit()
    return {"received": True}
