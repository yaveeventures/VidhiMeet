import structlog
from fastapi import APIRouter

log = structlog.get_logger("webhooks")

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"], include_in_schema=False)


@router.get("/status")
def webhook_status():
    return {"status": "active", "message": "No external webhook integrations configured"}

