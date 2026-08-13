# ⚖️ VidhiMeet — Enterprise Legal Marketplace & Consultation Platform

**VidhiMeet** is a full-stack, enterprise-grade legal services marketplace and consultation platform. It connects clients with verified legal professionals for instant video consultations, document drafting, timezone-aware appointment scheduling, and secure payments.

---

## 🌟 Key Features

### 🔍 **Client Portal & Legal Marketplace**
- **Lawyer Discovery**: Search and filter legal experts by practice area (Family, Corporate, Property, IP, Criminal, Tax), hourly rate, language, location, and verified rating.
- **Intake Forms & Disclaimers**: Practice-specific intake questions and mandatory legal disclaimers captured prior to confirmation.
- **Timezone-Aware Scheduling**: Integrated calendar slot picker supporting multiple timezones.
- **Document Drafting Hub**: Integrated portal for ordering and reviewing custom legal document drafts with revision tracking.

### 💼 **Lawyer Portal**
- **Consultation Management**: View upcoming, in-progress, and past video meetings.
- **Embedded Jitsi Video Rooms**: Secure, zero-installation video consultation room powered by Jitsi Meet API with JWT room tokens.
- **Real-Time Client Chat**: WebSocket-powered live chat during and before consultations.
- **Earnings & Payouts**: Bank account management, UPI VPA verification, transaction history, and payout tracking.
- **Availability Calendar**: Custom block-out times and recurring weekly availability rules.

### 🛡️ **Admin Console**
- **Lawyer Verification**: Review credentials, bar association IDs, and document submissions before badge verification.
- **Dispute & Refund Management**: Track client disputes, issue refunds, and inspect booking audit logs.
- **Financial Analytics & Payouts**: Platform fee management, gross transaction logs, and payout releases.
- **Security & Audit Logs**: Immutable system activity log, active session controls, and rate-limiting monitoring.

---

## 🛠️ Architecture & Tech Stack

```
                     ┌─────────────────────────────────────────┐
                     │          Client / Browser UI            │
                     │  (HTML5 / JS / CSS / Jitsi Video API)   │
                     └────────────────────┬────────────────────┘
                                          │
                                     REST / WS
                                          │
                     ┌────────────────────▼────────────────────┐
                     │           FastAPI Backend               │
                     │  (Async API Routers & Rate Limiter)     │
                     └─────────┬──────────┬───────────┬────────┘
                               │          │           │
          ┌────────────────────┘          │           └────────────────────┐
          ▼                               ▼                                ▼
┌──────────────────┐            ┌──────────────────┐             ┌──────────────────┐
│ PostgreSQL DB    │            │  Redis Service   │             │ PhonePe / Storage│
│ (SQLAlchemy ORM) │            │ (Cache & Limits) │             │ (Payments & S3)  │
└──────────────────┘            └──────────────────┘             └──────────────────┘
```

* **Backend Framework**: Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn async ASGI server.
* **Database & Migration**: PostgreSQL with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) ORM & [Alembic](https://alembic.sqlalchemy.org/) migrations (SQLite supported for dev).
* **Real-time & Caching**: WebSockets for live chat, Server-Sent Events (SSE), and Redis for session caching & rate limiting.
* **Payments & Escrow**: PhonePe Gateway payment workflows with signed checksum webhook verification.
* **Security & Auth**: PBKDF2 password hashing, short-lived JWT tokens, security headers, XSS sanitization, and NTP time verification.
* **Frontend**: Responsive HTML5, Modern CSS custom design system, Vanilla JavaScript ES6+, and Jitsi External API integration.

---

## 📁 Project Structure

```
VidhiMeet/
├── backend/                  # FastAPI Application Core
│   ├── main.py               # Application entry point & middleware config
│   ├── config.py             # Environment settings & validation
│   ├── db.py                 # Database engine & session setup
│   ├── models.py             # SQLAlchemy database models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── security.py           # JWT token generation & password hashing
│   ├── rate_limiter.py       # Sliding-window Redis rate limiter
│   └── routers/              # Modular API Endpoints
│       ├── admin.py          # Admin console management
│       ├── auth.py           # Authentication & registration
│       ├── bank_accounts.py  # Lawyer bank accounts & payouts
│       ├── bookings.py       # Consultation bookings & slot allocation
│       ├── calendar.py       # Lawyer availability calendars
│       ├── drafting.py       # Legal document drafting workflows
│       ├── events.py         # SSE live event notifications
│       ├── lawyers.py        # Lawyer directory & profiles
│       ├── webhooks.py       # Stripe webhook listeners
│       └── websocket_chat.py # Real-time consultation chat socket
├── frontend/                 # Client & Portal Web Assets
│   ├── index.html            # Main Client Portal & Marketplace UI
│   ├── lawyer.html           # Lawyer Dashboard UI
│   ├── admin.html            # Admin Control Panel UI
│   ├── admin-login.html      # Admin Security Login Portal
│   ├── terms.html            # Terms of Service & Legal Disclaimers
│   ├── privacy.html          # Privacy Policy
│   ├── css/                  # App Stylesheets & Design System
│   └── js/                   # Client-side Application Logic
├── migrations/               # Alembic database migration scripts
├── scripts/                  # Seed scripts & utility tools
├── tests/                    # Pytest backend integration test suite
├── docker-compose.yml        # Multi-container Docker orchestrator
├── Dockerfile                # Production container definition
├── requirements.txt          # Python dependencies manifest
└── alembic.ini               # Database migration configuration
```

---

## 🚀 Getting Started

### Prerequisites
* **Python**: 3.11 or higher
* **Docker & Docker Compose** (for containerized setup)
* **PostgreSQL & Redis** (optional for local non-container mode)

---

### Option A: Quickstart with Docker Compose (Recommended)

1. **Clone & Navigate**:
   ```bash
   git clone https://github.com/yaveeventures/VidhiMeet.git
   cd VidhiMeet
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```
   *(Update secret keys and credentials in `.env` as required).*

3. **Launch Stack**:
   ```bash
   docker compose up --build
   ```

4. **Access Applications**:
   * **Marketplace UI**: `http://localhost:8080`
   * **Lawyer Portal**: `http://localhost:8080/lawyer.html`
   * **Admin Console**: `http://localhost:8080/admin.html`
   * **Interactive API Docs**: `http://localhost:8000/docs`

---

### Option B: Local Development Setup

1. **Create & Activate Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run Database Migrations**:
   ```powershell
   alembic upgrade head
   ```

4. **Start FastAPI Backend Server**:
   ```powershell
   uvicorn backend.main:app --reload --port 8000
   ```

5. **Serve Frontend**:
   ```powershell
   python -m http.server 8080 --directory frontend
   ```

---

## 🧪 Testing & Quality Assurance

Run the automated backend test suite using `pytest`:

```powershell
pytest
```

---

## 🔒 Production Hardening & Pre-Deployment Checklist

Before deploying VidhiMeet to production:
- [x] **Cryptographic JWT Secret**: Default `jwt_secret` replaced with a 64-character cryptographically secure secret in `backend/config.py` & `.env`.
- [ ] **Database & Caching**: Deploy PostgreSQL 16 and Redis 7 instances with automated backups, connection pooling, and TLS connections.
- [ ] **Domain & TLS Hardening**: Configure Nginx reverse proxy (`nginx/vidhimeet.conf`) with Let's Encrypt TLS 1.3 SSL certs and set up DNS A records for subdomains (`lawyer.vidhimeet.in`, `admin.vidhimeet.in`).
- [ ] **PhonePe Payment Gateway**: Set live `PHONEPE_MERCHANT_ID`, `PHONEPE_SALT_KEY`, and `PHONEPE_SALT_INDEX` in production `.env` and configure `/api/v1/webhooks/phonepe`.
- [ ] **Video Server Integration**: Configure authenticated Jitsi / Daily.co API tokens (`JITSI_APP_ID`, `JITSI_APP_SECRET`) for secure video room generation.
- [ ] **Private Document Storage**: Use S3/Cloudflare R2 bucket with KMS server-side encryption, CORS restrictions, and presigned URL access limits.
- [ ] **DPDPA & Forensic Compliance**: Verify NTP time sync server connectivity (`time.nplindia.org`) and audit log immutability.

---

## 📄 License & Legal Notice

Copyright © 2026 **Yavee Ventures**. All rights reserved.

> *Disclaimer: VidhiMeet is a platform technology infrastructure for legal service providers. It does not provide legal advice or act as a law firm.*
