# 📁 Document Vault Storage & Encryption — Production Runbook

**Standard**: DPDP Act 2023 (§8 — Reasonable Security Safeguards) · ISO/IEC 27001 · FIPS 140-2  
**Scope**: Private cloud document vaults (Cloudflare R2 / AWS S3), KMS/AES-256 server-side encryption, CORS policies, presigned expiring URLs, and antivirus/malware validation.

---

## 1. Zero-Trust Storage Architecture

VidhiMeet operates a **Private-by-Default, Zero-Public-Access** document repository. Sensitive files—including advocate bar council enrollment certificates, identity proofs, client contracts, and dispute evidence—are never stored in public web roots.

```
┌─────────────────────────────────┐
│       Client / Advocate UI      │
└────────────────┬────────────────┘
                 │
                 │ 1. Request Upload Presign (Auth JWT Required)
                 ▼
┌─────────────────────────────────┐
│         FastAPI Backend         │
│  • Enforces 10MB Size Limit     │
│  • Generates 15-Min Signed URL  │
│  • Requires KMS / AES-256 SSE   │
└────────────────┬────────────────┘
                 │
                 │ 2. Direct Browser-to-Cloud Upload (15-Min TTL)
                 │    Headers: Content-Type, CORS Checked
                 ▼
┌─────────────────────────────────┐
│     Cloudflare R2 / AWS S3      │
│  • Server-Side AES-256 / KMS    │
│  • CORS Whitelist Restricted    │
│  • Public Access BLOCKED        │
└────────────────┬────────────────┘
                 │
                 │ 3. Confirm Upload & Anti-Malware Inspection
                 ▼
┌─────────────────────────────────┐
│      Malware / MIME Scanner     │
│   (Rejects Macro/Executable PDF)│
└─────────────────────────────────┘
```

---

## 2. Cloudflare R2 vs. AWS S3 Configuration

### 2.1 Option A: Cloudflare R2 (Recommended for Production)
* **Zero Egress Fees**: Eliminates bandwidth costs for downloading legal case files.
* **Automatic Encryption at Rest**: Cloudflare R2 automatically encrypts all stored objects using **AES-256** (FIPS 140-2 compliant) before writing to disk.
* **Endpoint Format**: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
* **Terraform Resource**:
  ```hcl
  resource "cloudflare_r2_bucket" "documents_bucket" {
    account_id = var.cloudflare_account_id
    name       = "vidhimeet-documents"
    location   = "APAC"
  }
  ```

### 2.2 Option B: AWS S3 with AWS KMS
* **Customer-Managed Encryption**: Apply an AWS KMS Customer Master Key (CMK) for regulatory sovereignty.
* **SSE-KMS Enforcement**: Configures bucket encryption policy using `aws:kms` algorithm and bucket key caching.

---

## 3. CORS Policy Hardening

Defined in [`cloudflare/r2_cors_policy.json`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/cloudflare/r2_cors_policy.json):

```json
[
  {
    "AllowedOrigins": [
      "https://vidhimeet.in",
      "https://www.vidhimeet.in",
      "https://lawyer.vidhimeet.in",
      "https://admin.vidhimeet.in"
    ],
    "AllowedMethods": [
      "GET",
      "PUT",
      "POST",
      "HEAD"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "ETag",
      "Content-Type"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

### Security Properties:
- **Strict Origin Whitelist**: Restricts direct browser uploads and downloads exclusively to verified VidhiMeet subdomains.
- **Header Exposure**: Exposes `ETag` and `Content-Type` for frontend checksum and progress validation.
- **Preflight Cache**: Caches preflight `OPTIONS` requests for 1 hour (`3600` seconds) to minimize latency.

---

## 4. Applying CORS & Encryption Policies

VidhiMeet includes an automated configuration utility: [`scripts/configure_storage_bucket.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/scripts/configure_storage_bucket.py).

### 4.1 Running the Provisioning Script

```powershell
# 1. Dry-run validation (validates credentials and policy syntax)
python scripts/configure_storage_bucket.py --bucket-name vidhimeet-documents --dry-run

# 2. Apply to Cloudflare R2 bucket:
python scripts/configure_storage_bucket.py --bucket-name vidhimeet-documents

# 3. Apply to AWS S3 with custom AWS KMS Key ID:
python scripts/configure_storage_bucket.py --bucket-name vidhimeet-documents --kms-key-id "arn:aws:kms:ap-south-1:123456789012:key/your-key-uuid"
```

---

## 5. Presigned URL Security & File Validation

Implemented across [`backend/services/s3_client.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/backend/services/s3_client.py) and [`backend/services/malware_scanner.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/backend/services/malware_scanner.py):

1. **Short-Lived Expiry**: Presigned URLs expire after **15 minutes (900 seconds)** (`PRESIGNED_URL_EXPIRY_SECONDS=900`), preventing link re-use or unauthorized leakage.
2. **Payload Size Restrictions**: Enforces maximum upload ceiling of **10MB** (`MAX_DOCUMENT_BYTES=10485760`).
3. **Malware & Magic Byte Scanning**:
   - Rejects executable binaries disguised as documents.
   - Inspects PDF streams for embedded JavaScript (`/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFiles`).
   - Scans Microsoft Office documents for VBA macros.
4. **Re-Upload Overwrite & Old Version Purge**: Re-uploading a document automatically removes the superseded file from the cloud bucket, enforcing storage hygiene.

---

## 6. Pre-Deployment Verification Checklist

- [x] **CORS Policy Configured**: Applied [`cloudflare/r2_cors_policy.json`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/cloudflare/r2_cors_policy.json) restricting access to `vidhimeet.in` domains.
- [x] **Server-Side Encryption Enabled**: Verified AES-256 encryption at rest (Cloudflare R2 default / AWS KMS).
- [x] **Presigned URL Expiry Tested**: Verified 15-minute token expiry in [`tests/test_document_vault.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/tests/test_document_vault.py).
- [x] **Malware Defense Verified**: Automated test suite validates rejection of malicious PDF scripts and macros.
