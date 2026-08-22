import secrets
from fastapi import HTTPException
from ..config import get_settings
from .s3_client import generate_presigned_post_data

settings = get_settings()

def presign_document(booking_id: str, filename: str, content_type: str) -> dict:
    if not settings.document_bucket:
        raise HTTPException(503, "document storage is not configured")
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")[:120]
    key = f"bookings/{booking_id}/{secrets.token_hex(16)}-{safe_name}"
    expiry = settings.presigned_url_expiry_seconds
    result = generate_presigned_post_data(key, content_type)
    return {"upload": result, "key": key, "expires_in": expiry}
