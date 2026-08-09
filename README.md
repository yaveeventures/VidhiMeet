# VidhiMeet

A full-stack legal marketplace foundation with:

- Family, corporate, and property-law discovery
- Availability, rating, and price filtering
- Mandatory practice-specific intake forms
- Timezone-aware scheduling
- Escrow/payment summary and mandatory legal disclaimer
- Embedded browser-based Jitsi Meet consultation room
- Lawyer dashboard for consultations, availability, messages, documents, earnings, and verification
- Admin console for lawyer approvals, disputes, users, transactions, fees, payouts, security, and audit activity

## Production architecture

- FastAPI application with versioned APIs and strict role-based access
- PostgreSQL transactional storage and Redis service provision
- PBKDF2 password hashing and short-lived signed access tokens
- Practice-specific validated intake and mandatory disclaimer recording
- Stripe Connect payment-intent and signed, idempotent webhook handling
- Booking-scoped JWT Jitsi room provisioning
- KMS-encrypted S3 presigned uploads with content type and size controls
- Security headers, restricted CORS, immutable audit records, health checks, and non-root containers

## Local static preview

Serve this directory with any static server:

```powershell
python -m http.server 8080
```

Open `http://localhost:8080`.

Lawyer portal: `http://localhost:8080/lawyer.html`

Admin console: `http://localhost:8080/admin.html`

## Full-stack development

1. Copy `.env.example` to `.env`.
2. Replace every placeholder secret. Generate secrets with a cryptographically secure password manager.
3. Set `POSTGRES_PASSWORD` and `REDIS_PASSWORD` in `.env`; update the matching database and Redis URLs.
4. Start the stack:

```powershell
docker compose up --build
```

5. Apply migrations automatically on startup and open `http://localhost:8080`.

For local non-container development:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\uvicorn backend.main:app --reload
```

## Required before launch

- Use managed PostgreSQL and Redis with private networking, backups, and point-in-time recovery.
- Put the service behind a TLS-terminating load balancer/WAF and managed secrets store.
- Configure Stripe Connect accounts, production webhooks, refunds, disputes, and reconciliation.
- Deploy a JWT-secured Jitsi installation or JaaS tenant; never use anonymous public rooms.
- Configure a private S3 bucket with KMS, malware scanning, retention rules, and regional residency.
- Add email/OTP verification, MFA for lawyers/admins, refresh-token rotation, and account recovery.
- Conduct threat modelling, penetration testing, accessibility testing, and jurisdiction-specific legal/privacy review.
- Establish incident response, deletion/export workflows, monitoring, alerting, and compliance evidence.

## Production note

This is a functional front-end prototype. Production requires authenticated APIs, PostgreSQL and Redis, restricted object storage, Stripe Connect webhooks, calendar-provider integrations, audit logging, and JWT-protected Jitsi rooms. Compliance claims require jurisdiction-specific legal and security review.
