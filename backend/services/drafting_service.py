import secrets
import boto3
from fastapi import HTTPException
from ..config import get_settings

settings = get_settings()

def presign_document(booking_id: str, filename: str, content_type: str) -> dict:
    if not settings.document_bucket:
        raise HTTPException(503, "document storage is not configured")
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")[:120]
    key = f"bookings/{booking_id}/{secrets.token_hex(16)}-{safe_name}"
    client = boto3.client("s3", region_name=settings.aws_region)
    expiry = settings.presigned_url_expiry_seconds
    result = client.generate_presigned_post(
        settings.document_bucket, key,
        Fields={"Content-Type": content_type, "x-amz-server-side-encryption": "aws:kms"},
        Conditions=[{"Content-Type": content_type}, {"x-amz-server-side-encryption": "aws:kms"},
                    ["content-length-range", 1, settings.max_document_bytes]], ExpiresIn=expiry)
    return {"upload": result, "key": key, "expires_in": expiry}
