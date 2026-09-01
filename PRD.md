# 📄 Product Requirements Document (PRD)
# VidhiMeet — Enterprise Legal Marketplace & Consultation Platform

**Document Version:** 1.0.0  
**Status:** Approved / Active Production  
**Owner:** Yavee Ventures Private Limited  
**Brand Name:** VidhiMeet  
**Target Market:** India (Nationwide)  
**Primary Domain:** `https://vidhimeet.in`  

---

## 1. Executive Summary & Vision

### 1.1 Product Vision
**VidhiMeet** is a full-stack, enterprise-grade legal marketplace and digital consultation platform designed to democratize access to trusted legal counsel across India. By combining verified advocate onboarding, secure WebRTC video consultations, private document drafting vaults, and strict compliance with the **Digital Personal Data Protection (DPDP) Act 2023** and **Bar Council of India (BCI)** regulations, VidhiMeet bridges the gap between citizens seeking timely legal counsel and verified advocates.

### 1.2 Problem Statement
- **Fragmented Legal Discovery:** Citizens struggle to identify qualified, verified advocates in specialized practice areas without transparent pricing or verified credentials.
- **Geographic & Time Friction:** Physical legal visits incur travel costs, scheduling conflicts, and timezone friction for NRIs and interstate legal matters.
- **Privacy & Security Risks:** Sensitive case documents, Aadhaar cards, and confidential communications are frequently shared over unencrypted channels.
- **Opaque Billing & Payout Disputes:** Lack of automated escrow and clear consultation proof leads to disputes between clients and practitioners.

### 1.3 Value Proposition
- **For Clients:** Transparent hourly fees, verified Bar Council advocates, instant/scheduled encrypted video consultations, and structured document drafting with milestone escrow.
- **For Advocates:** Digital practice management, automated client intake, verified payout settlement to bank/UPI accounts, and BCI-compliant intermediary protection.
- **For Regulators & Enterprise:** Complete audit trails, forensically synchronized timestamps (NTP/CERT-In), and robust data privacy controls.

---

## 2. Legal Entity & Regulatory Compliance

### 2.1 Corporate Entity Details
| Field | Official Value |
| :--- | :--- |
| **Legal Business Entity Name** | YAVEE VENTURES PRIVATE LIMITED |
| **Platform Brand Name** | VidhiMeet |
| **Corporate Identity Number (CIN)** | U74999KA2019PTC131183 |
| **GSTIN** | 29AABCY1943Q1ZM |
| **Registered Office Address** | R.S NO. 212/1K, Plot No.13, Bombay Chawl, Gokak, Belgaum, Karnataka - 591307, India |
| **Support Email** | `support@vidhimeet.in` |
| **Legal Desk** | `legal@vidhimeet.in` |
| **Data Protection Officer (DPO)** | `dpo@vidhimeet.in` |

### 2.2 Bar Council of India (BCI) Compliance
- **Intermediary Shield:** VidhiMeet operates strictly as an intermediary technology platform (Information Technology Act §79). It is **not** a law firm and does not solicit clients or advertise on behalf of advocates.
- **Directory & Verified Credentials:** Advocate listings display objective qualifications, verified Bar Council enrollment numbers, languages, and areas of practice without superlative rankings or promotional solicitations.
- **Independent Fee Setting:** Advocates autonomously establish their consultation fee structures.

### 2.3 DPDP Act 2023 & Privacy Architecture
- **Age Verification (§9):** Age verification is captured at registration ensuring only adult users (18+) create client accounts.
- **Consent Logging (§6):** Granular timestamped consent records (`user_consents` table) tracking versioned privacy policy and terms acceptance with explicit withdrawal mechanics.
- **PII Encryption at Rest:** Aadhaar numbers, bank account numbers, IFSC codes, phone numbers, and identity documents are encrypted using AES-256 (Fernet) at rest.
- **Right to Erasure (§12):** Automated user data erasure workflows that scrub personal identifiable information while preserving immutable financial audit logs for tax compliance.
- **Data Retention Policies (§8(7)):**
  - Completed/Disputed transactions: 7 years (2555 days) for statutory tax and legal auditing.
  - Cancelled/Refunded records: 1 year (365 days).
  - Expired authentication session tokens: 30 days.

### 2.4 CERT-In & Forensic Timestamp Compliance
- **NTP Time Synchronization:** Application startups and critical audit logs synchronize with authoritative Indian time servers (`time.nplindia.org`, `time.nplindia.in`, `time.nic.in`, `pool.ntp.org`).
- **Clock Drift Alerting:** Drift exceeding 2.0 seconds triggers immediate security log alerts to ensure forensic validity in legal proceedings.

---

## 3. User Roles & Personas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                VIDHIMEET ROLES                                  │
├───────────────────────┬─────────────────────────┬───────────────────────────────┤
│ 👤 CLIENT             │ ⚖️ ADVOCATE / LAWYER    │ 🛡️ ADMINISTRATOR              │
├───────────────────────┼─────────────────────────┼───────────────────────────────┤
│ • Search & Filter     │ • Profile Onboarding    │ • Advocate Verification       │
│ • Schedule Meetings   │ • Availability Rules    │ • Dispute Arbitration         │
│ • WebRTC Video Call   │ • Daily.co Video Rooms  │ • Payout Approvals            │
│ • Document Drafting   │ • Document Vault        │ • Audit Trail Review          │
│ • Encrypted Chat      │ • Bank/UPI Payouts      │ • Rate Limiting & Telemetry   │
└───────────────────────┴─────────────────────────┴───────────────────────────────┘
```

### 3.1 Client (Citizen / Business)
- Discovers legal experts across specialized practice areas.
- Completes structured pre-consultation intake questionnaires.
- Books instant or scheduled video consultations with dual-sided payment processing.
- Requests custom legal document drafts (contracts, notices, deeds) with revision controls.

### 3.2 Advocate / Lawyer (Service Provider)
- Submits Bar Council enrollment and identity proof for administrative verification.
- Sets hourly consultation rates, language proficiencies, and recurring weekly availability slots.
- Conducts end-to-end encrypted video consultations directly in the browser via Daily.co.
- Bids on and submits legal document drafting proposals with version tracking.
- Manages verified bank accounts and UPI VPAs for automated platform payouts.

### 3.3 Platform Administrator
- Reviews advocate verification applications, Bar license proofs, and Aadhaar verification.
- Manages the multi-tier dispute matrix and arbitrates contested sessions.
- Authorizes and audits escrow payout releases to legal practitioners.
- Monitors system telemetry, security headers, rate limiting, and compliance logs.

---

## 4. Functional Modules & Requirements

### 4.1 Legal Marketplace & Discovery Engine
1. **Search & Filter Parameters:** Practice area (Property, Corporate, Family, Criminal, IP, Tax, Civil), fee threshold (`max_fee_minor`), spoken languages, and rating.
2. **Public Platform Stats:** Live counters for verified advocates, registered clients, and practice distributions (`/api/v1/public/stats`).
3. **Structured Intake Questions:** Practice-specific pre-consultation questions captured prior to checkout.
4. **Mandatory Disclaimer Acceptance:** Versioned legal disclaimer captured and timestamped prior to payment generation.

### 4.2 Consultation Scheduling & Booking Workflow
```
[Client Discovers Advocate] ──> [Selects Slot & Fills Intake] ──> [Accepts Disclaimer]
                                                                        │
[Video Consultation Active] <── [Payment Captured (Escrow)] <───────────┘
            │
            ├──> [Duration Logged & Monitored]
            │
            └──> [Session Completed] ──> [Dispute Window (24h)] ──> [Payout Release]
```
1. **Timezone-Aware Calendar:** Prevents double-booking through database-enforced unique constraints (`uq_lawyer_slot` on `lawyer_id` and `starts_at`).
2. **Consultation Durations:** Standardized 45-minute slots with real-time countdown.
3. **iCalendar Sync:** Advocates can subscribe to live iCal feeds (`/api/v1/calendar/{token}.ics`) for Google Calendar / Apple Calendar integration.

### 4.3 Secure Video Consultation Engine (Daily.co)
1. **Browser-Native WebRTC:** Zero software installation required; embedded directly into the portal UI.
2. **Ephemeral Meeting Tokens:** Time-bounded, cryptographically signed meeting access tokens generated on-demand for authenticated participants only.
3. **Presence & Duration Tracking:** Logs exact advocate and client join/leave timestamps to provide objective evidence for dispute resolution.

### 4.4 Real-Time Encrypted Chat & Notification Bus
1. **WebSocket Consultation Chat:** Live communication channel between advocate and client linked to booking IDs.
2. **Message Integrity & Salt Encryption:** Dynamic per-booking cryptographic salts (`chat_key_salt`) for chat payload isolation.
3. **Server-Sent Events (SSE):** Real-time booking status notifications, dispute triggers, and draft updates.

### 4.5 Legal Document Drafting & Revision Hub
```
[Client Posts Request] ──> [Lawyers Submit Proposals] ──> [Client Accepts & Pays Escrow]
                                                                    │
[7-Day Auto-Approval] <── [Client Revisions / Feedback] <── [Lawyer Submits Draft]
            │
            └──> [Draft Approved] ──> [Version Freeze & Payout]
```
1. **Custom Drafting Requests:** Clients post specific document needs with description, budget, and reference attachments.
2. **Advocate Counter-Proposals:** Multiple advocates can submit pricing bids and timeline estimates.
3. **Milestone Escrow:** Funds held securely until client approves the completed draft.
4. **Interactive Document Annotations:** Pinpoint page, X/Y coordinate, and text-selection comments (`draft_comments` model).
5. **7-Day Auto-Approval Rule:** If a client does not request revisions or dispute within 7 days of draft submission, the system automatically marks the draft as approved.
6. **Immutable Version Freeze:** Final approved drafts lock all versions and generate an immutable audit trail.
7. **Malware Scanning & Upload Sandbox:** Uploaded PDF/DOCX files undergo macro/JavaScript payload inspection before presigned S3/R2 storage.

### 4.6 Cancellation & Time-Tiered Refund Policy
| Cancellation Scenario | Timing Window | Client Refund | Advocate Compensation / Penalty |
| :--- | :--- | :--- | :--- |
| **Client Cancel** | > 24 hours before session | **100% Full Refund** | Slot freed; no penalty |
| **Client Cancel** | 2 hours to 24 hours before | **50% Partial Refund** | 50% retained for advocate reservation |
| **Client Cancel** | < 2 hours before session | **0% No Refund** | 100% (less platform fee) paid to advocate |
| **Advocate Cancel** | Any time prior to session | **100% Full Refund + 20% Discount Voucher** | Advocate receives strike count; slot relisted |

### 4.7 Three-Step Dispute Resolution Matrix & Intermediary Shield
1. **Step 1: Automated Telemetry Check:**
   - If advocate connected for ≥ 30 minutes and client did not attend: Auto-resolved in favor of advocate.
   - If advocate never connected: Auto-resolved with 100% client refund and advocate warning strike.
2. **Step 2: Mutual Consent Window:** 24-hour window for parties to agree on a rescheduled session.
3. **Step 3: Administrative Arbitration:** Admin inspects Daily.co connection logs, chat transcripts, and document audit records to issue a binding payout or refund decision.

### 4.8 Advocate Onboarding, Verification & Bank Payouts
1. **Onboarding Requirements:** Bar Council Enrollment Number, Bar License Scan, Practice Address, Aadhaar Number, and Mobile Verification.
2. **Identity Masking & Security:** PII fields stored using AES-256 encryption. Admin console displays masked previews (`XXXX-XXXX-1234`).
3. **Bank & UPI Verification:** Supports NEFT/IMPS bank accounts and instant UPI VPA verification with audit trail UTRs.
4. **Strike Management:** Advocates receiving repeated cancellation or no-show strikes face automatic profile suspension.

---

## 5. Economic & Pricing Architecture

```
                       CONSULTATION TRANSACTION FLOW
┌────────────────────────────────────────────────────────────────────────┐
│  Client Total Payment: Base Price + 5% Client Platform Fee (Min ₹35)   │
├────────────────────────────────────────────────────────────────────────┤
│                       HELD IN ESCROW ACCOUNT                           │
├────────────────────────────────────────────────────────────────────────┤
│  Advocate Payout: Base Price - 5% Advocate Platform Fee (Min ₹35)      │
│  Platform Revenue: 10% Total Gross Fee Margin (Client Fee + Lawyer Fee)│
└────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Fee Breakdown
1. **Video Consultations:**
   - **Client Fee:** 5% on top of advocate's base fee (minimum ₹35 / 3500 paise).
   - **Advocate Fee:** 5% deducted from advocate's base fee (minimum ₹35 / 3500 paise).
   - **Net Platform Margin:** 10% total transaction revenue.
2. **Document Drafting:**
   - **Platform Fee:** Flat 10% commission on the agreed draft contract price.
   - **Advocate Share:** 90% of the agreed project price released upon milestone completion.
3. **Voucher Engine:** Generates single-use 20% discount codes (`vouchers` table) for clients affected by advocate cancellations.

---

## 6. Technical Architecture & Tech Stack

```
                          ┌───────────────────────────┐
                          │   Cloudflare CDN & Edge   │
                          │ (WAF, DDoS, SSL/TLS, Caching)
                          └─────────────┬─────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │                             │
                         ▼                             ▼
              ┌─────────────────────┐       ┌─────────────────────┐
              │  Static Web Assets  │       │  FastAPI Backend    │
              │ (HTML5/CSS3/Vanilla)│       │ (Async Uvicorn ASGI)│
              └─────────────────────┘       └──────────┬──────────┘
                                                       │
                 ┌───────────────────┬─────────────────┼───────────────────┐
                 ▼                   ▼                 ▼                   ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
        │ PostgreSQL DB   │ │ Redis Service   │ │ Daily.co API│ │ S3 / Cloudflare │
        │ (SQLAlchemy ORM)│ │ (Rate Limits)   │ │ (WebRTC)    │ │ R2 (Encrypted)  │
        └─────────────────┘ └─────────────────┘ └─────────────┘ └─────────────────┘
```

### 6.1 Technology Stack
- **Backend:** Python 3.11+, FastAPI, Starlette, Uvicorn (ASGI), Pydantic v2.
- **Database & Storage:** PostgreSQL 16 (Production) / SQLite 3 (Dev/Test), SQLAlchemy 2.0 ORM, Alembic Migrations.
- **Document Vault:** AWS S3 / Cloudflare R2 (ap-south-1) with KMS encryption and 15-minute presigned access URLs.
- **Video Engine:** Daily.co REST & WebRTC SDK with ephemeral room tokens.
- **Frontend:** Vanilla HTML5, Custom Design System (CSS3 variables), Modern ES6+ JavaScript, Responsive Desktop/Mobile.
- **Security & Caching:** Redis 7 (sliding-window rate limiting), Argon2id & PBKDF2 password hashing, PyJWT, Cryptography (Fernet AES-256).

### 6.2 Database Entity Schema (High-Level)
| Model | Primary Purpose | Key Fields |
| :--- | :--- | :--- |
| `User` | User identity & authentication | `id`, `email`, `password_hash`, `role`, `date_of_birth`, `mfa_enabled` |
| `LawyerProfile` | Professional credentials & settings | `user_id`, `bar_number`, `practice`, `hourly_fee_minor`, `verified`, `aadhaar_number` |
| `LawyerBankAccount` | Payout destination & UPI verification | `user_id`, `account_number`, `ifsc_code`, `upi_vpa`, `verified`, `utr` |
| `Booking` | Video consultation contracts | `client_id`, `lawyer_id`, `starts_at`, `status`, `amount_minor`, `jitsi_room` |
| `DraftingRequest` | Legal document project workflows | `creator_id`, `drafter_id`, `status`, `price_minor`, `agreed_price_minor`, `draft_file_key` |
| `DraftingProposal` | Lawyer bids on drafting projects | `request_id`, `lawyer_id`, `amount_minor`, `status` |
| `DraftComment` | Collaborative feedback on drafts | `request_id`, `user_id`, `page_number`, `position_x`, `position_y`, `comment` |
| `UserConsent` | DPDP Act consent audit tracking | `user_id`, `consent_type`, `consent_version`, `status`, `withdrawn_at` |
| `AuditLog` | Immutable system event journal | `actor_id`, `action`, `target_type`, `target_id`, `metadata_json`, `created_at` |
| `RefreshToken` | Rotational session management | `user_id`, `token_hash`, `expires_at`, `revoked` |
| `Voucher` | Customer goodwill discounts | `code`, `user_id`, `discount_percent`, `expires_at`, `used` |

---

## 7. Non-Functional Requirements (NFRs)

### 7.1 Security & Cryptography
1. **Authentication:** Argon2id primary password hashing with automatic PBKDF2 verification fallback.
2. **Session Security:** 60-minute short-lived JWT access tokens and 14-day rotational refresh tokens with immediate revocation mechanics.
3. **Two-Factor Authentication (MFA):** RFC 6238 TOTP authenticator app support with QR code provisioning.
4. **HTTP Security Headers:**
   - `Content-Security-Policy` with Daily.co WebRTC frame/connect directives.
   - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
   - `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`.
5. **PII Data Isolation:** Database fields carrying Aadhaar, bank accounts, IFSC, and contact numbers use symmetric encryption at rest.

### 7.2 Rate Limiting & Abuse Prevention
- Tiered sliding-window rate limiting enforced via Redis:
  - **Auth (`/api/v1/auth/*`):** 10 req/min with exponential backoff on repeated failures.
  - **Public Search & Stats:** 60 req/min.
  - **Authenticated Operations:** 200 req/min.
  - **Document Presign & Uploads:** 15 req/min.
  - **Sensitive Operations (Admin/Purge):** 10 req/min.
  - **IP Abuse Lockout:** Automated temporary lockout for repeated 401/403 anomalies.

### 7.3 Performance, Reliability & Availability
- **API Response Latency:** P95 latency < 120ms for all core read/write endpoints.
- **Availability Target:** 99.9% uptime for API gateway and consultation rooms.
- **Document Presign Links:** 15-minute maximum validity window.
- **Automated Test Coverage:** 100% passing test suite across 96+ end-to-end and unit test cases.

---

## 8. Success Metrics & Key Performance Indicators (KPIs)

| Metric Category | Target KPI | Measurement Method |
| :--- | :--- | :--- |
| **Marketplace Growth** | > 25% MoM Gross Merchandise Value (GMV) | Monthly booking fee totals |
| **Advocate Quality** | > 95% Advocate Verification Pass Rate | Admin verification review logs |
| **Consultation Reliability** | < 2.0% Dispute Rate across all sessions | Structured dispute trigger tracking |
| **Consultation Completion** | > 92% Successful 45-minute Video Sessions | Daily.co participant presence logs |
| **Support SLA** | < 24-hour Support Ticket Resolution | Support desk resolution logs |
| **Platform Uptime** | 99.9% Availability | Health check & uptime monitors |

---

## 9. Product Roadmap

### Phase 1: Core Marketplace & Video Platform (Completed ✅)
- Verified advocate onboarding & Bar Council profile verification.
- Timezone-aware booking engine & Daily.co WebRTC video consultation rooms.
- Dual-sided platform commission architecture & bank/UPI payout workflows.
- Real-time encrypted consultation chat & SSE notifications.
- Complete DPDP Act 2023 consent logging, PII encryption at rest, and NTP synchronization.

### Phase 2: Document Drafting & Mobile Optimizations (Current 🚀)
- Multi-advocate bidding on custom legal drafting requests.
- Point-and-click PDF/DOCX annotations and 7-day auto-approval workflows.
- Full mobile-responsive UI with dynamic 404 error handling and SEO sitemaps.
- Automated malware scanning sandbox for client document uploads.

### Phase 3: AI Legal Assistant & Pan-India Expansion (Upcoming 🔮)
- Multilingual voice-enabled intake assistance across 8 Indian regional languages.
- Automated AI document summarization for advocate case briefings.
- Integration with DigiLocker and Bar Council API for instant automated advocate verification.
- Escrow direct-to-bank instant settlement via automated payment gateway webhooks.

---

*VidhiMeet Product Requirements Document — Maintained by Yavee Ventures Private Limited.*
