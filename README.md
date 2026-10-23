# ⚖️ VidhiMeet — Enterprise Legal Marketplace & Consultation Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Cashfree](https://img.shields.io/badge/Payments-Cashfree%20PG%20%26%20Payouts-00A859?style=flat)](https://www.cashfree.com/)
[![Daily.co](https://img.shields.io/badge/Video-Daily.co%20WebRTC-4560F7?style=flat)](https://www.daily.co/)
[![Compliance](https://img.shields.io/badge/Compliance-DPDP%20Act%202023%20%7C%20BCI-2D3748?style=flat)](https://vidhimeet.in)
[![License](https://img.shields.io/badge/License-Proprietary%20%26%20Confidential-blue?style=flat)](#-license--legal-notice)

**VidhiMeet** is a full-stack, enterprise-grade legal marketplace and digital consultation platform designed for the Indian legal ecosystem. Developed and operated by **Yavee Ventures Private Limited**, VidhiMeet connects citizens with verified advocates for encrypted video consultations, milestone-based legal document drafting, automated GST-compliant invoicing, and secure escrow payments.

The platform is engineered to comply with the **Digital Personal Data Protection (DPDP) Act 2023**, the **Bar Council of India (BCI)** non-solicitation guidelines under the Information Technology Act §79, and **CERT-In** cyber security directives with authoritative NTP forensic timestamping.

---

## 🌟 Key Platform Capabilities

### 🔍 **Client Portal & Legal Marketplace**
- **Advocate Discovery**: Search and filter verified advocates by practice area (Family, Corporate, Property, Intellectual Property, Criminal, Tax, Labour, Cyber Law), language proficiency, city/court, experience, and transparent hourly rates.
- **Intake Forms & Disclaimers**: Practice-specific intake questionnaire and mandatory client engagement disclaimers before checkout.
- **Timezone-Aware Slot Booking**: Real-time calendar slot picker accommodating Indian Standard Time (IST) and international NRI clients.
- **Promotional & Credit Vouchers**: Integrated promotional code engine with discount validation and credit tracking.
- **Client Document Vault**: Private document storage for sharing case filings, contracts, and evidence with presigned expiring access.

### 💼 **Advocate Portal & Practice Management**
- **Consultation Dashboard**: Track upcoming, active, completed, and rescheduled consultation appointments.
- **Embedded Daily.co Video Rooms**: Zero-installation, end-to-end encrypted video meeting rooms with countdown timers, waiting rooms, and meeting access tokens.
- **Real-Time Consultation Chat**: High-performance WebSocket consultation chat for in-meeting messaging and document exchange.
- **Availability & Calendar Rules**: Customizable weekly recurring availability schedules and ad-hoc slot blocking.
- **Earnings, Escrow & Cashfree Payouts**: Real-time earnings ledger, escrow release tracking, automated bank account IFSC validation, UPI VPA verification, and direct payouts.

### 📑 **Legal Document Drafting Hub**
- **Structured Drafting Workflows**: Order, review, and collaborate on custom legal contracts, notices, and agreements with milestone-based escrow protection.
- **Draft Versioning & Revisions**: Transparent revision tracking with automated advocate submission alerts and client approval gates.
- **Private S3 / Cloudflare R2 Vault**: Zero-trust document storage with KMS/Fernet AES-256 encryption at rest, malware antivirus validation, and 15-minute presigned access links.

### 🛡️ **Admin Console & Compliance Engine**
- **Advocate Verification & Bar ID Review**: Manual verification gate for Bar Council enrollment certificates, IDs, and professional credentials before issuing verified advocate badges.
- **Dispute & Refund Workflow**: Dispute window management (7 days), evidence inspection, and automated one-click refunds via Cashfree.
- **Financial Analytics & Payout Batches**: Platform commission management (configurable percentage), transaction audit logs, and payout releases.
- **Immutable Security & Audit Trails**: Tamper-proof activity logs, active user session management, and sliding-window Redis rate-limit monitoring.

### 🇮🇳 **Statutory & Regulatory Compliance**
- **DPDP Act 2023 (§6, §9, §12, §8(7))**:
  - Explicit versioned consent capture and audit logging (`user_consents`).
  - Mandatory age verification preventing minor account creation without parental authorization.
  - Right to Erasure / Account deletion workflow with PII anonymization.
  - Automated statutory data retention purger (7 years for completed tax/legal transactions, 1 year for cancelled orders, 30 days for expired session tokens).
- **CERT-In Forensic Timestamping**: NTP clock synchronization with official Indian timekeepers (**National Physical Laboratory / NPL India** and **NIC**), preventing time-drift tampering in audit logs.
- **Bar Council of India (BCI) Intermediary Architecture**: Operates strictly as a neutral technology intermediary under §79 of the Information Technology Act 2000, avoiding client solicitation, lawyer rating manipulation, or advertising.

---

## 🛠️ System Architecture & Tech Stack

```
                              ┌──────────────────────────────────────────────┐
                              │            Cloudflare Edge Network           │
                              │ (DNS, SSL/TLS 1.3, WAF Shield, Bot Defense)  │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                             HTTPS / WSS (IST)
                                                     │
                              ┌──────────────────────▼───────────────────────┐
                              │               Nginx Reverse Proxy            │
                              │     (SSL Termination, HTTP/2, Static Cache)  │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FastAPI Backend (Uvicorn ASGI)                                │
│                                                                                                    │
│  ┌───────────────────────┐  ┌────────────────────────┐  ┌───────────────────────┐  ┌─────────────┐ │
│  │   Auth & RBAC JWT     │  │   Sliding Rate Limiter │  │  NTP Forensic Time    │  │ Event Bus   │ │
│  │ (PBKDF2 / Fernet PII) │  │  (Redis Sliding Window)│  │ (NPL / NIC Reference) │  │ (SSE / WS)  │ │
│  └───────────────────────┘  └────────────────────────┘  └───────────────────────┘  └─────────────┘ │
│                                                                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                  Service Layer                                                │ │
│  │ • PaymentService (Cashfree PG)       • PayoutService (Cashfree Direct / UPI)                 │ │
│  │ • BookingService & DisputeService    • InvoiceService (GST SAC Invoicing)                    │ │
│  │ • DraftingService & S3Client         • ComplianceService & MalwareScanner                    │ │
│  └───────────────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────┬───────────────────────────────┬──────────────────────────────┬──────────────────────┘
               │                               │                              │
               ▼                               ▼                              ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────────┐
│        PostgreSQL 16         │ │           Redis 7            │ │     Cloudflare R2 / AWS S3       │
│  (SQLAlchemy 2.0 / Alembic)  │ │ (Session Cache, Token TTL,   │ │ (Encrypted Document Vault,       │
│  Encrypted PII / Audit Logs  │ │  Sliding Window Rate Limits) │ │  Malware-Scanned Presigned URLs) │
└──────────────────────────────┘ └──────────────────────────────┘ └──────────────────────────────────┘
```

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) | High-performance async ASGI application with Pydantic v2 schemas |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | Production asynchronous HTTP/1.1 and WebSockets server |
| **Primary Database** | [PostgreSQL 16](https://www.postgresql.org/) | Relational database with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/) migrations (SQLite supported for local dev) |
| **Cache & Rate Limiting** | [Redis 7](https://redis.io/) | Sliding-window per-IP/account rate limiter with exponential auth backoff |
| **Payment Gateway** | [Cashfree Payments](https://www.cashfree.com/) | Indian PG (Cards, UPI, Net Banking) with HMAC SHA-256 webhook verification |
| **Disbursements & Payouts** | Cashfree Payouts API | Automated IMPS/NEFT bank transfers & UPI VPA verification for advocate settlements |
| **Video Consultations** | [Daily.co](https://www.daily.co/) WebRTC API | Low-latency, encrypted video meeting rooms with token authentication |
| **Document Storage** | Cloudflare R2 / AWS S3 | Encrypted object storage with expiring presigned download/upload links |
| **Real-time Messaging** | WebSockets & SSE | Bi-directional consultation chat and Server-Sent Event notifications |
| **Antivirus & File Safety** | Custom Magic Byte & ClamAV Scanner | Upload file validation, MIME verification, and malware rejection |
| **Time Synchronization** | NTP (`ntplib`) | Clock sync with NPL India (`time.nplindia.org`) & NIC (`time.nic.in`) |
| **Frontend** | Vanilla ES6+ JS, Semantic HTML5, CSS | Modern, lightweight, responsive UI with zero heavy framework bloat |

---

## 📁 Repository Structure

```
VidhiMeet/
├── backend/                         # FastAPI Application Core
│   ├── main.py                      # Application lifespan, middleware, routers, & exception handlers
│   ├── config.py                    # Pydantic BaseSettings, environment validation, & defaults
│   ├── db.py                        # SQLAlchemy engine, session factories, & DB dependency
│   ├── models.py                    # SQLAlchemy ORM database models (User, Booking, Invoice, etc.)
│   ├── schemas.py                   # Pydantic v2 validation schemas
│   ├── security.py                  # JWT tokens, PBKDF2 password hashing, & Fernet encryption
│   ├── rate_limiter.py              # Redis sliding-window rate limiter with exponential backoff
│   ├── logging_config.py            # Structlog JSON and console logger configuration
│   ├── ntp_time.py                  # Indian NPL/NIC NTP time sync client for audit logs
│   ├── sanitizer.py                 # HTML/XSS input sanitization utilities
│   ├── tasks.py                     # Background task helpers
│   ├── validation_constants.py      # Indian IFSC, PAN, GSTIN, UPI, and Bar ID regex patterns
│   ├── routers/                     # API Router Endpoints
│   │   ├── admin.py                 # Admin console management, advocate verification & dispute resolution
│   │   ├── auth.py                  # Authentication, registration, OTP, Google OAuth, & refresh tokens
│   │   ├── bank_accounts.py         # Advocate bank account management & IFSC verification
│   │   ├── bookings.py              # Consultation booking, slot allocation, reschedule, & cancellations
│   │   ├── calendar.py              # Advocate availability scheduling & block-out slots
│   │   ├── drafting.py              # Legal document drafting orders, milestone reviews, & revisions
│   │   ├── events.py                # Server-Sent Events (SSE) notification streams
│   │   ├── lawyers.py               # Advocate directory search, filters, & public profiles
│   │   ├── public.py                # Public statistics, platform status, & contact endpoints
│   │   ├── webhooks.py              # Cashfree PG webhook handler with HMAC signature validation
│   │   └── websocket_chat.py        # Real-time WebSocket consultation chat
│   └── services/                    # Business Logic Layer
│       ├── auth_service.py          # User authentication and session lifecycle
│       ├── booking_service.py       # Booking creation, slot checking, and status transitions
│       ├── compliance_service.py    # DPDP consent tracking and audit log recording
│       ├── dispute_service.py       # Dispute window validation and claim workflows
│       ├── drafting_service.py      # Document drafting milestone management
│       ├── event_bus.py             # In-memory and distributed event dispatching
│       ├── invoice_service.py       # GST-compliant tax invoicing, PDF generation & SAC codes
│       ├── malware_scanner.py       # Uploaded document magic-byte and malware scanning
│       ├── payment_service.py       # Cashfree PG order creation, signature verification, & refunds
│       ├── payout_service.py        # Cashfree Payouts, bank transfers, & UPI VPA validation
│       └── s3_client.py             # Cloudflare R2 / AWS S3 client with presigned URLs
├── cloudflare/                      # Cloudflare Edge Infrastructure
│   ├── main.tf                      # Terraform configuration for DNS, SSL, WAF, & Rate Limits
│   ├── deploy_rules.sh              # Cloudflare edge rule deployment script
│   └── r2_cors_policy.json          # Cloudflare R2 storage bucket CORS policy
├── frontend/                        # Client & Portal Web Assets
│   ├── index.html                   # Client Marketplace & Advocate Discovery UI
│   ├── lawyer.html                  # Advocate Portal & Practice Management UI
│   ├── admin.html                   # Admin Control Panel UI
│   ├── admin-login.html             # Secure Admin Authentication Gateway
│   ├── about.html                   # About VidhiMeet & Yavee Ventures
│   ├── contact.html                 # Customer & Advocate Support Desk
│   ├── terms.html                   # Terms of Service & BCI Intermediary Disclaimers
│   ├── privacy.html                 # Privacy Policy (DPDP Act 2023 Compliant)
│   ├── cancellation-refund.html     # Cancellation & Refund Policy
│   ├── shipping-delivery.html       # Digital Service Delivery & Fulfillment Policy
│   ├── 404.html                     # Custom Responsive 404 Error Page
│   ├── css/                         # Custom CSS Design System
│   │   └── styles.css               # Core design tokens, dark mode, & responsive styles
│   ├── js/                          # Client-Side Application Logic
│   │   ├── app.js                   # Client portal logic, slot booking, & Cashfree checkout
│   │   ├── lawyer.js                # Advocate dashboard logic, meeting management, & payouts
│   │   └── admin.js                 # Admin management logic, verification, & analytics
│   ├── images/                      # Optimized image assets and illustrations
│   ├── robots.txt                   # Search crawler directives
│   ├── sitemap.xml                  # Canonical XML sitemap
│   └── BingSiteAuth.xml             # Bing Webmaster Tools site verification
├── migrations/                      # Alembic Database Migrations
│   ├── env.py                       # Alembic migration runtime environment
│   └── versions/                    # Timestamped database migration revisions
├── nginx/                           # Reverse Proxy Configuration
│   └── vidhimeet.conf               # Nginx virtual host with TLS 1.3, CSP headers, & HTTP/2
├── scripts/                         # Maintenance, Compliance & Ops Utilities
│   ├── data_retention_purge.py      # DPDP statutory data retention purging cron utility
│   ├── deploy_cloudflare_shield.py  # Automated Cloudflare WAF & rate-limiting deployment
│   ├── disable_cloudflare_beacon.py # Cloudflare beacon.min.js disabler for clean Lighthouse audits
│   ├── minify_assets.py             # Frontend JS/CSS asset minification script
│   ├── ntp_sync_check.py            # NTP server connectivity & time drift diagnostic tool
│   ├── reset_users.py               # Database user testing & password reset utility
│   ├── seed.py                      # Development database seeding script
│   └── setup_domain_ssl.sh          # Automated Let's Encrypt Certbot SSL provisioning
├── tests/                           # Pytest Automated Test Suite
│   ├── test_api.py                  # API endpoint integration tests
│   ├── test_cashfree.py             # Cashfree PG order creation & webhook verification tests
│   ├── test_cancellation.py         # Booking cancellation & automated refund policy tests
│   ├── test_compliance.py           # DPDP consent logging, age check, & erasure tests
│   ├── test_dispute_workflow.py     # Dispute window & resolution workflow tests
│   ├── test_document_vault.py       # S3/R2 presigned URL & malware rejection tests
│   ├── test_invoicing.py            # GST invoice calculation & PDF generation tests
│   ├── test_ntp.py                  # NTP synchronization & time drift tolerance tests
│   ├── test_promotional_vouchers.py # Discount voucher validation & usage limits tests
│   ├── test_realtime.py             # SSE & WebSocket consultation chat tests
│   ├── test_security_critical.py    # Rate limiter, XSS sanitization, & JWT auth tests
│   └── test_validation_constants.py # Regex validation for IFSC, GSTIN, PAN, & Bar IDs
├── docker-compose.yml               # Multi-container Docker orchestrator (App, DB, Redis)
├── Dockerfile                       # Multi-stage production container image
├── requirements.txt                 # Pinned Python package dependencies manifest
├── alembic.ini                      # Database migration configuration
└── PRD.md                           # Comprehensive Product Requirements Document
```

---

## 🚀 Getting Started

### Prerequisites
* **Python**: 3.11 or higher
* **PostgreSQL**: 16+ (or SQLite for quick local development)
* **Redis**: 7+ (for sliding rate limits and session caching)
* **Docker & Docker Compose**: Optional, recommended for containerized testing

---

### Option A: Local Development Setup (Recommended)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yaveeventures/VidhiMeet.git
   cd VidhiMeet
   ```

2. **Create and Activate a Virtual Environment**:
   * **PowerShell (Windows)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   * **Bash (Linux / macOS)**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   *(Update `.env` with your JWT secret, database credentials, Cashfree sandbox keys, and Daily.co credentials).*

5. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Seed Initial Development Data (Optional)**:
   ```bash
   python scripts/seed.py
   ```

7. **Start the FastAPI Backend**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

8. **Serve the Frontend**:
   ```bash
   python -m http.server 8080 --directory frontend
   ```

9. **Access Local Instances**:
   * 🌐 **Client Marketplace**: [http://localhost:8080](http://localhost:8080)
   * ⚖️ **Advocate Portal**: [http://localhost:8080/lawyer.html](http://localhost:8080/lawyer.html)
   * 🛡️ **Admin Console**: [http://localhost:8080/admin.html](http://localhost:8080/admin.html)
   * 📑 **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * 🩺 **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option B: Containerized Setup (Docker Compose)

Launch the complete stack (FastAPI, PostgreSQL 16, Redis 7) with a single command:

```bash
docker compose up --build
```

To stop containers:
```bash
docker compose down
```

---

## ⚙️ Environment Configuration Guide

Key variables defined in `.env` (refer to `.env.example` for template):

| Environment Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Runtime environment (`development`, `staging`, `production`) | `development` |
| `DATABASE_URL` | PostgreSQL or SQLite connection URI | `postgresql+psycopg://user:pass@localhost:5432/vidhimeet` |
| `REDIS_URL` | Redis instance connection URI | `redis://localhost:6379/0` |
| `JWT_SECRET` | 64+ char cryptographic secret for signing access tokens | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowed domains | `https://vidhimeet.in,https://lawyer.vidhimeet.in` |
| `CASHFREE_APP_ID` | Cashfree Payment Gateway App ID | `TEST...` (Sandbox) or live production App ID |
| `CASHFREE_SECRET_KEY` | Cashfree Payment Gateway Secret Key | Your Cashfree PG API Secret Key |
| `CASHFREE_MODE` | Payment Gateway operational mode | `sandbox` or `production` |
| `CASHFREE_PAYOUT_APP_ID` | Cashfree Payouts API Client ID | For advocate settlement bank/UPI transfers |
| `CASHFREE_PAYOUT_SECRET_KEY`| Cashfree Payouts API Secret Key | For advocate settlement disbursements |
| `DAILY_API_KEY` | Daily.co WebRTC Video API Key | Private API token for room/token creation |
| `DAILY_DOMAIN` | Daily.co domain identifier | e.g. `vidhimeet` (resolves to `vidhimeet.daily.co`) |
| `S3_ENDPOINT_URL` | Cloudflare R2 or AWS S3 endpoint URL | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |
| `DOCUMENT_BUCKET` | S3 / R2 storage bucket name | `vidhimeet-documents` |
| `DATA_ENCRYPTION_KEY` | Fernet 32-byte URL-safe base64 key for PII at rest | Generated via `Fernet.generate_key()` |
| `NTP_SERVERS` | Authoritative NTP server list | `time.nplindia.org,time.nplindia.in,time.nic.in` |

---

## 🧪 Testing & Quality Assurance

VidhiMeet includes an extensive automated test suite covering authentication, payments, escrow, compliance, and security:

```powershell
# Run the complete test suite
pytest

# Run tests with verbose output and coverage
pytest -v --cov=backend

# Run specific functional suites
pytest tests/test_cashfree.py           # Cashfree PG orders & signature verification
pytest tests/test_security_critical.py  # Rate limiting, XSS & JWT tamper tests
pytest tests/test_compliance.py         # DPDP consent logging & erasure tests
pytest tests/test_invoicing.py          # GST tax calculation & PDF generation
pytest tests/test_dispute_workflow.py   # Dispute window and cancellation policies
```

### Operational Utility Scripts

| Script | Purpose |
| :--- | :--- |
| `python scripts/check_domain_ssl.py` | Audits domain DNS resolution, TLS 1.3 negotiation, Let's Encrypt / Cloudflare certificate validity, and HSTS headers. |
| `python scripts/configure_storage_bucket.py` | Applies CORS whitelist policy and KMS/AES-256 server-side encryption to Cloudflare R2 / AWS S3 document buckets. |
| `python scripts/db_snapshot.py` | Performs automated daily snapshots of PostgreSQL & Redis with SHA-256 integrity checksums, cloud S3/R2 upload, and 30-day retention pruning. |
| `python scripts/ntp_sync_check.py` | Validates clock synchronization with Indian NPL/NIC NTP servers and reports time drift. |
| `python scripts/data_retention_purge.py` | Cron script enforcing DPDP Act §8(7) data retention schedules across database tables. |
| `python scripts/deploy_cloudflare_shield.py` | Deploys Cloudflare WAF firewall rules, rate limiting, and bot challenges. |
| `python scripts/disable_cloudflare_beacon.py` | Disables automated Cloudflare RUM beacon injection to maintain 100/100 Lighthouse performance. |
| `python scripts/minify_assets.py` | Generates minified production assets for frontend stylesheets and scripts. |

---

## 🔒 Production Hardening & Pre-Deployment Checklist

Before deploying VidhiMeet to production environments:

- [x] **Cryptographic Secret Rotation**: Replaced development `JWT_SECRET` and `DATA_ENCRYPTION_KEY` with cryptographically secure production keys.
- [x] **Cashfree Production Activation**: Configured live Cashfree credentials (`CASHFREE_APP_ID`, `CASHFREE_SECRET_KEY`) and set `CASHFREE_MODE=production`.
- [x] **Cashfree Webhook Signature Verification**: Enabled HMAC SHA-256 verification on `/api/v1/webhooks/cashfree` using raw request payloads and timestamps.
- [x] **BCI & Intermediary Compliance**: Verified advocate directory non-solicitation language and terms of service under IT Act §79.
- [x] **DPDPA Retention Automation**: Configured daily cron executing `python scripts/data_retention_purge.py`.
- [x] **CERT-In NTP Clock Sync**: Verified operational connectivity to `time.nplindia.org` via `python scripts/ntp_sync_check.py`.
- [x] **Database & Redis Cluster**: Configured PostgreSQL 16 connection pooling (`QueuePool` / `NullPool` for transaction poolers), TLS in-transit encryption (`sslmode=require`), Redis 7 connection pooling & `rediss://` TLS, and automated daily snapshots via [`scripts/db_snapshot.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/scripts/db_snapshot.py) (see [Database & Redis Runbook](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/docs/database_redis_cluster.md)).
- [x] **Domain DNS & SSL/TLS 1.3**: Configured Cloudflare DNS records (Apex, www, lawyer, admin), Strict TLS 1.3 edge encryption, Cloudflare real-IP restoration, and Nginx reverse proxy ([nginx/vidhimeet.conf](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/nginx/vidhimeet.conf)) with Let's Encrypt multi-SAN SSL (see [Domain & SSL Runbook](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/docs/domain_dns_ssl_setup.md)).
- [x] **Document Storage Bucket**: Applied KMS/AES-256 server-side encryption and CORS policy ([cloudflare/r2_cors_policy.json](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/cloudflare/r2_cors_policy.json)) to the private document vault (see [Document Vault Runbook](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/docs/document_vault_storage.md)).

---

## 🏢 Corporate Entity & Legal Notice

**VidhiMeet** is a proprietary software platform owned and operated by:

**YAVEE VENTURES PRIVATE LIMITED**  
*Corporate Identity Number (CIN):* U74999KA2019PTC131183  
*GSTIN:* 29AABCY1943Q1ZM  
*Registered Office:* R.S NO. 212/1K, Plot No.13, Bombay Chawl, Gokak, Belgaum, Karnataka - 591307, India  
*Official Inquiries:* `support@vidhimeet.in` | `legal@vidhimeet.in` | `dpo@vidhimeet.in`  
*Website:* [https://vidhimeet.in](https://vidhimeet.in)

> **Legal Disclaimer**: VidhiMeet operates strictly as an intermediary technology platform under Section 79 of the Information Technology Act, 2000. VidhiMeet does not provide legal advice, does not solicit legal business or advertise on behalf of advocates, and does not act as a law firm. Engagement of legal services and consultation advice is strictly between the independent verified advocate and the client.

---

Copyright © 2026 **Yavee Ventures Private Limited**. All rights reserved.
