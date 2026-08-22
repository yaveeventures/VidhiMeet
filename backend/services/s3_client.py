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

    fields = {"Content-Type": content_type}
    conditions = [
        {"Content-Type": content_type},
        ["content-length-range", 1, settings.max_document_bytes]
    ]

    # AWS S3 uses KMS encryption headers; Cloudflare R2 / MinIO auto-encrypt at rest without KMS headers
    if not settings.s3_endpoint_url:
        fields["x-amz-server-side-encryption"] = "aws:kms"
        conditions.append({"x-amz-server-side-encryption": "aws:kms"})

    result = client.generate_presigned_post(
        Bucket=settings.document_bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=expiry
    )
    return result
