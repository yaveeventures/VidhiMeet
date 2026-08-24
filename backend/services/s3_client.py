import boto3
from ..config import get_settings


def get_s3_client():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region or "auto"}
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url.strip()
    return boto3.client("s3", **kwargs)


def generate_presigned_post_data(key: str, content_type: str) -> dict:
    settings = get_settings()
    client = get_s3_client()
    expiry = settings.presigned_url_expiry_seconds

    # Cloudflare R2 requires S3 PUT presigned URLs (POST form data returns 501 Not Implemented)
    if settings.s3_endpoint_url:
        url = client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.document_bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expiry
        )
        return {"url": url, "method": "PUT", "fields": {}, "headers": {"Content-Type": content_type}}

    fields = {"Content-Type": content_type, "x-amz-server-side-encryption": "aws:kms"}
    conditions = [
        {"Content-Type": content_type},
        ["content-length-range", 1, settings.max_document_bytes],
        {"x-amz-server-side-encryption": "aws:kms"}
    ]

    result = client.generate_presigned_post(
        Bucket=settings.document_bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=expiry
    )
    result["method"] = "POST"
    return result


def delete_s3_object(key: str) -> bool:
    """Deletes an object from S3/R2 cloud bucket or local mock uploads directory."""
    if not key:
        return False

    import os
    import structlog
    log = structlog.get_logger("s3_client")
    settings = get_settings()

    # Local mock storage deletion
    if not settings.document_bucket:
        file_path = os.path.join("uploads", key)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                log.info("Deleted local mock document file", key=key, path=file_path)
                return True
            except Exception as exc:
                log.warning("Failed to delete local mock file", key=key, error=str(exc))
                return False
        return True

    # Cloud S3 / R2 object deletion
    try:
        client = get_s3_client()
        client.delete_object(Bucket=settings.document_bucket, Key=key)
        log.info("Deleted S3/R2 document object", key=key, bucket=settings.document_bucket)
        return True
    except Exception as exc:
        log.warning("Failed to delete S3/R2 document object", key=key, error=str(exc))
        return False

