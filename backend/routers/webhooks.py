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

    # Extract order_id across potential Cashfree payload shapes
    data = payload.get("data", {})
    order_id = None
    if isinstance(data, dict):
        if "order" in data and isinstance(data["order"], dict):
            order_id = data["order"].get("order_id")
        elif "order_id" in data:
            order_id = data.get("order_id")
    if not order_id:
        order_id = payload.get("order_id")

    if not order_id:
        log.warning("No order_id found in Cashfree webhook payload", payload=payload)
        return {"status": "ignored", "reason": "no_order_id"}

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
