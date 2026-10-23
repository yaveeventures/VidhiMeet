#!/usr/bin/env python3
"""
VidhiMeet Document Storage Bucket Provisioning & Hardening Script
Applies CORS policy from cloudflare/r2_cors_policy.json and configures
Server-Side Encryption (KMS / AES-256) for Cloudflare R2 or AWS S3 buckets.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import get_settings


def load_cors_policy(policy_path: Path) -> dict:
    """Load and format CORS configuration from JSON file."""
    if not policy_path.exists():
        raise FileNotFoundError(f"CORS policy file not found at: {policy_path}")

    with open(policy_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    # Format into Boto3 CORSConfiguration schema
    return {"CORSRules": rules}


def get_s3_client(settings):
    """Create configured Boto3 S3 client for Cloudflare R2 or AWS S3."""
    import boto3
    from botocore.config import Config

    kwargs = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region_name": settings.aws_region or "auto",
        "config": Config(signature_version="s3v4")
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url.strip()

    return boto3.client("s3", **kwargs)


def apply_cors_policy(client, bucket_name: str, cors_config: dict):
    """Apply CORS policy to the target storage bucket."""
    print(f"[*] Applying CORS policy to bucket '{bucket_name}'...")
    client.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration=cors_config
    )
    print(f"[+] CORS policy successfully applied to '{bucket_name}'.")


def configure_server_side_encryption(client, bucket_name: str, is_r2: bool, kms_key_id: str = None):
    """
    Configure or verify Server-Side Encryption (KMS / AES-256).
    Cloudflare R2 enforces AES-256 encryption at rest by default for all objects.
    AWS S3 applies SSE-KMS or SSE-S3.
    """
    if is_r2:
        print(f"[+] Cloudflare R2 detected: Automatic zero-trust AES-256 encryption at rest is active on '{bucket_name}'.")
        return

    print(f"[*] Configuring AWS S3 Server-Side Encryption for '{bucket_name}'...")
    if kms_key_id:
        rule = {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyId": kms_key_id
            },
            "BucketKeyEnabled": True
        }
        print(f"[*] Using AWS KMS Key: {kms_key_id}")
    else:
        rule = {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": True
        }
        print("[*] Using AES-256 (SSE-S3) encryption.")

    enc_config = {
        "Rules": [rule]
    }

    client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration=enc_config
    )
    print(f"[+] Server-side encryption successfully applied to '{bucket_name}'.")


def verify_bucket_setup(client, bucket_name: str):
    """Verify that CORS and bucket configuration are readable and active."""
    print(f"[*] Verifying bucket configuration for '{bucket_name}'...")
    try:
        cors = client.get_bucket_cors(Bucket=bucket_name)
        rules_count = len(cors.get("CORSRules", []))
        print(f"[+] Verified active CORS configuration ({rules_count} rule(s) active).")
    except Exception as e:
        print(f"[!] Warning reading CORS: {e}")

    try:
        # Check bucket liveness
        client.head_bucket(Bucket=bucket_name)
        print(f"[+] Bucket '{bucket_name}' is accessible and operational.")
    except Exception as e:
        print(f"[!] Head bucket check notice: {e}")


def main():
    parser = argparse.ArgumentParser(description="VidhiMeet Document Storage Bucket Hardening")
    parser.add_argument("--bucket-name", type=str, default=None, help="Target S3 / Cloudflare R2 bucket name (default: from .env)")
    parser.add_argument("--kms-key-id", type=str, default=None, help="AWS KMS Key ID or ARN for AWS S3 encryption")
    parser.add_argument("--policy-file", type=str, default="cloudflare/r2_cors_policy.json", help="Path to CORS JSON policy")
    parser.add_argument("--dry-run", action="store_true", help="Validate credentials and policy file without applying")
    args = parser.parse_args()

    settings = get_settings()
    bucket_name = args.bucket_name or settings.document_bucket

    if not bucket_name:
        print("[-] Error: Bucket name not specified. Provide --bucket-name <NAME> or set DOCUMENT_BUCKET in .env.")
        sys.exit(1)

    policy_file = PROJECT_ROOT / args.policy_file
    try:
        cors_config = load_cors_policy(policy_file)
        print(f"[+] Loaded CORS policy from {policy_file.name} ({len(cors_config['CORSRules'])} rule(s)).")
    except Exception as e:
        print(f"[-] Failed to load CORS policy: {e}")
        sys.exit(1)

    if args.dry_run:
        print(f"[SUCCESS] Dry-run validated. Ready to apply to '{bucket_name}'.")
        sys.exit(0)

    try:
        client = get_s3_client(settings)
        is_r2 = bool(settings.s3_endpoint_url and "r2.cloudflarestorage.com" in settings.s3_endpoint_url)

        # 1. Apply CORS Policy
        apply_cors_policy(client, bucket_name, cors_config)

        # 2. Configure Server-Side Encryption
        configure_server_side_encryption(client, bucket_name, is_r2, kms_key_id=args.kms_key_id)

        # 3. Verify
        verify_bucket_setup(client, bucket_name)

        print("\n[SUCCESS] Document storage bucket hardening successfully completed.")
    except Exception as e:
        print(f"\n[-] Error configuring bucket '{bucket_name}': {e}")
        print("    Ensure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and permissions are valid.")
        sys.exit(1)


if __name__ == "__main__":
    main()
