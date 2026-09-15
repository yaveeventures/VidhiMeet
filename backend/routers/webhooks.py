import json
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Booking, BookingStatus
from ..services.payment_service import verify_cashfree_signature

log = structlog.get_logger("webhooks")

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"], include_in_schema=False)


@router.get("/status")
def webhook_status():
    return {"status": "active", "message": "Cashfree PG webhook integration active"}


@router.post("/cashfree")
async def cashfree_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID).
    """
    raw_body = await request.body()
    timestamp = request.headers.get("x-webhook-timestamp", "")
    signature = request.headers.get("x-webhook-signature", "")

    if not verify_cashfree_signature(raw_body, timestamp, signature):
        log.warning("Cashfree webhook signature verification failed", timestamp=timestamp)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception as exc:
        log.error("Failed to parse Cashfree webhook JSON", error=str(exc))
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type", "")
    log.info("Cashfree webhook received", event_type=event_type)

    # 1. Handle Cashfree Reverse Penny Drop (RPD) verification webhooks
    data = payload.get("data", {})
    verification_id = None
    if isinstance(data, dict):
        verification_id = data.get("verification_id") or (data.get("verification") or {}).get("verification_id")
    if not verification_id:
        verification_id = payload.get("verification_id")

    if verification_id or "RPD" in event_type or "REVERSE_PENNY" in event_type:
        v_id = verification_id or payload.get("verification_id")
        if v_id:
            from ..models import LawyerBankAccount
            from datetime import datetime, timezone
            acct = db.scalar(select(LawyerBankAccount).where(LawyerBankAccount.verification_id == v_id))
            if acct:
                remitter = data.get("remitter_details") or data.get("account_details") or data or payload
                status = (data.get("status") or payload.get("status") or "").upper()
                if status in ("SUCCESS", "VERIFIED") or "SUCCESS" in event_type:
                    acct.verified = True
                    acct.verified_at = datetime.now(timezone.utc)
                    acct.verification_status = "verified"
                    acct.verification_method = "reverse_penny_drop"
                    if remitter.get("utr"):
                        acct.utr = remitter.get("utr")
                    acc_num = remitter.get("account_number") or remitter.get("bank_account")
                    if acc_num and acc_num != "PENDING":
                        acct.account_number = acc_num
                    if remitter.get("ifsc") and remitter.get("ifsc") != "PENDING":
                        acct.ifsc_code = remitter.get("ifsc").upper()
                    if remitter.get("name_at_bank") or remitter.get("account_holder_name"):
                        acct.account_holder_name = remitter.get("name_at_bank") or remitter.get("account_holder_name")
                    if remitter.get("bank_name") and remitter.get("bank_name") != "Pending UPI Verification":
                        acct.bank_name = remitter.get("bank_name")
                    if remitter.get("vpa") or remitter.get("upi_id"):
                        acct.upi_vpa = remitter.get("vpa") or remitter.get("upi_id")
                    db.commit()
                    log.info("Lawyer bank account verified via Cashfree RPD webhook", verification_id=v_id, user_id=acct.user_id)
                    return {"status": "OK", "event": "rpd_verified"}

    # 2. Extract order_id for Payment Gateway bookings
    order_id = None
    if isinstance(data, dict):
        if "order" in data and isinstance(data["order"], dict):
            order_id = data["order"].get("order_id")
        elif "order_id" in data:
            order_id = data.get("order_id")
    if not order_id:
        order_id = payload.get("order_id")

    if not order_id:
        log.warning("No order_id or verification_id found in Cashfree webhook payload", payload=payload)
        return {"status": "ignored", "reason": "no_identifying_id"}

    booking = db.scalar(select(Booking).where(Booking.cashfree_order_id == order_id))
    if not booking:
        log.info("No booking matches Cashfree order_id", order_id=order_id)
        return {"status": "ignored", "reason": "booking_not_found"}

    if event_type in ("PAYMENT_SUCCESS_WEBHOOK", "ORDER_PAID"):
        if booking.status == BookingStatus.PENDING_PAYMENT:
            booking.status = BookingStatus.CONFIRMED
            db.commit()
            log.info("Booking confirmed via Cashfree webhook", booking_id=booking.id, order_id=order_id)

    return {"status": "OK"}
