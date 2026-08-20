import structlog
from ..config import get_settings
from ..models import Booking

logger = structlog.get_logger("payment_service")
settings = get_settings()


def initiate_refund(booking: Booking, refund_amount_minor: int, reason: str = "Client cancellation refund") -> str:
    """Trigger payment refund fallback."""
    import uuid
    refund_txn_id = f"REF-{uuid.uuid4().hex[:16].upper()}"

    if refund_amount_minor <= 0:
        return refund_txn_id

    logger.info("Initiating refund", booking_id=booking.id, amount=refund_amount_minor, refund_txn_id=refund_txn_id)
    return refund_txn_id

