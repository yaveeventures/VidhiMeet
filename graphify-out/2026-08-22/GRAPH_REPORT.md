# Graph Report - VidhiMeet  (2026-08-22)

## Corpus Check
- 85 files · ~100,407 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1226 nodes · 3441 edges · 60 communities (48 shown, 12 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 486 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `926f707a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- main.py
- i
- processEvent
- User
- audit
- toast
- Booking
- sanitize_key
- LawyerGrid
- calendar.py
- check_clock_drift
- 8dcb01bed07f_initial_schema.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- toast
- ntp_now
- config.py
- calendar.py
- er
- PlatformFeedback
- models.py
- _e
- test_rate_limiter.py
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- Request
- Settings
- NTP Time Synchronization — Compliance Runbook
- SlidingWindowRateLimiter
- setup_domain_ssl.sh
- Booking
- verify_ntp_compliance
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- test_auth_rate_limiting
- LawyerProfile
- phonepe_webhook
- 8dcb01bed07f_initial_schema.py
- websocket_chat_endpoint
- LawyerBankAccount
- Session
- env.py
- __init__.py
- Session
- reset_users.py
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 135 edges
2. `Role` - 57 edges
3. `audit()` - 56 edges
4. `Practice` - 53 edges
5. `LexAPI` - 52 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 42 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py
- `test_cancelled_slot_relisting()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py

## Import Cycles
- None detected.

## Communities (60 total, 12 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.06
Nodes (89): Base, AuditLog, BookingStatus, DraftingStatus, PasswordResetToken, Practice, ProposalStatus, str (+81 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (68): doAdminLogin(), checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute() (+60 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (74): $(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience() (+66 more)

### Community 3 - "lawyer.js"
Cohesion: 0.06
Nodes (44): as(), Bo(), Bt(), Ds(), dt(), ea(), Fo(), Fs() (+36 more)

### Community 4 - "app.js"
Cohesion: 0.11
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 5 - "daily-js.js"
Cohesion: 0.09
Nodes (20): ar(), de(), fn(), ft(), hn(), ht(), ir(), J() (+12 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (43): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+35 more)

### Community 7 - "i"
Cohesion: 0.10
Nodes (27): create_access_token(), hash_password(), Hash a raw password using Argon2id (OWASP #1 recommendation)., test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s)., Verify that drafting document presign returns 15-minute expiry (900s)., Verify that a document access token issued > 15 minutes ago (900s) is rejected w (+19 more)

### Community 8 - "processEvent"
Cohesion: 0.15
Nodes (32): LawyerProfile, User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes() (+24 more)

### Community 10 - "audit"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 11 - "toast"
Cohesion: 0.13
Nodes (30): AsyncSession, DraftComment, DraftingProposal, DraftingRequest, logout(), Log out user and revoke current access token (jti) via Redis blocklist., accept_drafting_proposal(), accept_drafting_request() (+22 more)

### Community 12 - "Booking"
Cohesion: 0.07
Nodes (24): EncryptedString, Message, ConnectionManager, _save_ws_message(), _validate_ws_user_and_booking(), websocket_chat_endpoint(), decrypt_field(), encrypt_field() (+16 more)

### Community 13 - "sanitize_key"
Cohesion: 0.14
Nodes (14): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify structlog processor scrubs sensitive PII fields and credentials from log, Verify scan_document_payload rejects PDF files containing embedded JavaScript tr (+6 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.17
Nodes (15): get_settings(), rate_limit_dependency(), download_drafting_document(), Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document(), lawyer_document_mock_upload(), lawyer_document_presign() (+7 more)

### Community 15 - "calendar.py"
Cohesion: 0.14
Nodes (8): Ae(), B(), br, ee(), qt, re(), we(), yr()

### Community 16 - "check_clock_drift"
Cohesion: 0.08
Nodes (7): Booking, now(), datetime, test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee()

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.11
Nodes (35): Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+27 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.12
Nodes (20): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+12 more)

### Community 19 - "toast"
Cohesion: 0.17
Nodes (24): a(), c(), ce(), cr(), d(), er(), f(), gn() (+16 more)

### Community 21 - "config.py"
Cohesion: 0.15
Nodes (27): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+19 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "er"
Cohesion: 0.33
Nodes (4): drafting_document_presign(), Sanitize a filename by removing directory traversal patterns, null bytes,     an, sanitize_filename(), test_sanitize_filename()

### Community 24 - "PlatformFeedback"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 25 - "models.py"
Cohesion: 0.16
Nodes (12): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 26 - "_e"
Cohesion: 0.25
Nodes (15): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+7 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 30 - "bookings.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 31 - "Request"
Cohesion: 0.11
Nodes (20): http_exception_handler(), integrity_exception_handler(), lifespan(), Exception, Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+12 more)

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "setup_domain_ssl.sh"
Cohesion: 0.15
Nodes (14): get_db(), authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token() (+6 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 41 - "SSEClient"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 42 - "README.md"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 43 - "ui-components.js"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 45 - "cookie-consent.js"
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 46 - "test_auth_rate_limiting"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `processEvent` to `main.py`, `setup_domain_ssl.sh`, `main.py`, `i`, `toast`, `Booking`, `sanitize_key`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `er`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`, `Request`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `mr` to `NTP Time Synchronization — Compliance Runbook`, `je`, `app.js`, `calendar.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `s()` connect `toast` to `je`, `lawyer.js`, `app.js`, `daily-js.js`, `9d0be6640444_add_aadhaar_and_profile_picture.py`, `config.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `VidhiMeet backend package.`, `Sanitize sensitive PII keys and credentials before log rendering.`, `Configure structured JSON logging for production or key-value console logging fo` to the rest of the system?**
  _190 weakly-connected nodes found - possible documentation gaps or missing edges._