# Graph Report - VidhiMeet  (2026-08-24)

## Corpus Check
- 88 files · ~102,630 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1237 nodes · 3534 edges · 69 communities (53 shown, 16 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 545 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `652727f3`
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
- sanitize_text
- PlatformFeedback
- models.py
- _e
- test_rate_limiter.py
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- _cors_response
- Settings
- NTP Time Synchronization — Compliance Runbook
- SlidingWindowRateLimiter
- setup_domain_ssl.sh
- test_rate_limiter.py
- setup
- processEvent
- Booking
- verify_ntp_compliance
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- test_error_handling.py
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
- er
- deploy_cloudflare_shield.py
- test_password_reset.py
- deploy_rules.sh
- sanitize_key

## God Nodes (most connected - your core abstractions)
1. `User` - 137 edges
2. `Role` - 58 edges
3. `audit()` - 56 edges
4. `Practice` - 53 edges
5. `LexAPI` - 52 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `LawyerProfile` - 44 edges
9. `DraftingStatus` - 44 edges
10. `ProposalStatus` - 44 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py

## Import Cycles
- None detected.

## Communities (69 total, 16 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.21
Nodes (41): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+33 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (64): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal() (+56 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (80): $(), doAdminLogin(), checkInactivity(), LexAPI, openChatModal(), k(), v(), LexE2EE (+72 more)

### Community 3 - "lawyer.js"
Cohesion: 0.07
Nodes (41): as(), at(), Bo(), dr(), Ds(), ea(), Es(), Fo() (+33 more)

### Community 4 - "app.js"
Cohesion: 0.11
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 5 - "daily-js.js"
Cohesion: 0.10
Nodes (11): ar(), br, fn(), ir(), kr(), mr, pr(), q() (+3 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (39): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+31 more)

### Community 7 - "i"
Cohesion: 0.09
Nodes (33): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin (+25 more)

### Community 8 - "processEvent"
Cohesion: 0.13
Nodes (27): PlatformFeedback, User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_platform_feedback(), list_disputes(), list_drafting_transactions() (+19 more)

### Community 10 - "audit"
Cohesion: 0.20
Nodes (10): bn(), Jn(), N(), preprocessEvent(), sn(), te(), wn(), xe() (+2 more)

### Community 11 - "toast"
Cohesion: 0.15
Nodes (31): AsyncSession, DraftComment, DraftingProposal, DraftingRequest, enable_mfa(), Verify TOTP code and enable 2FA on the account., accept_drafting_proposal(), accept_drafting_request() (+23 more)

### Community 12 - "Booking"
Cohesion: 0.39
Nodes (4): ConnectionManager, _validate_ws_user_and_booking(), websocket_chat_endpoint(), WebSocket

### Community 13 - "sanitize_key"
Cohesion: 0.14
Nodes (14): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify structlog processor scrubs sensitive PII fields and credentials from log, Verify scan_document_payload rejects PDF files containing embedded JavaScript tr (+6 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.15
Nodes (19): get_settings(), calculate_cancellation_policy(), get_daily_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake(), verify_daily_meeting_duration(), evaluate_daily_meeting_logs() (+11 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.08
Nodes (13): Base, get_db(), AuditLog, Booking, UserConsent, request_erasure(), DeclarativeBase, test_lawyer_complete_booking_duration_restriction() (+5 more)

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.18
Nodes (22): Message, Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+14 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.14
Nodes (29): a(), Bt(), c(), d(), ee(), f(), gn(), gt() (+21 more)

### Community 21 - "config.py"
Cohesion: 0.14
Nodes (21): Ae(), B(), Bs(), ct(), dn(), Et(), fe(), i() (+13 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "sanitize_text"
Cohesion: 0.07
Nodes (17): BankAccountCreate, DraftingRequestCreate, MessageCreate, Reject registration if the user is under 18 (DPDP Act 2023, Section 9)., RegisterRequest, ReviewCreate, Trim whitespace and escape HTML control characters to prevent XSS attacks.     R, sanitize_text() (+9 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 25 - "models.py"
Cohesion: 0.18
Nodes (12): an(), be(), cn(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 26 - "_e"
Cohesion: 0.19
Nodes (18): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+10 more)

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

### Community 31 - "_cors_response"
Cohesion: 0.22
Nodes (15): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+7 more)

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
Cohesion: 0.07
Nodes (34): lifespan(), EncryptedString, now(), datetime, WebhookEvent, rate_limit_dependency(), authenticate_stream_user(), Request (+26 more)

### Community 36 - "test_rate_limiter.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 37 - "setup"
Cohesion: 0.24
Nodes (11): ge(), ie(), le(), me(), ne(), oe(), qn(), ue() (+3 more)

### Community 38 - "processEvent"
Cohesion: 0.22
Nodes (10): ce(), de(), dt(), ft(), ht(), J(), ke(), processEvent() (+2 more)

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
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 46 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 63 - "er"
Cohesion: 0.29
Nodes (6): cr(), er(), hr(), lr(), xn(), Zn()

### Community 66 - "test_password_reset.py"
Cohesion: 0.15
Nodes (25): PasswordResetToken, RefreshToken, forgot_password(), google_auth(), login(), logout(), Session, Generate TOTP secret and provisioning URI for MFA authenticator setup. (+17 more)

### Community 68 - "sanitize_key"
Cohesion: 0.18
Nodes (16): LawyerProfile, drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign() (+8 more)

## Knowledge Gaps
- **68 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `processEvent` to `test_password_reset.py`, `setup_domain_ssl.sh`, `sanitize_key`, `main.py`, `i`, `toast`, `Booking`, `cookie-consent.js`, `LawyerGrid`, `sanitize_key`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `je` to `mr`, `app.js`, `calendar.py`, `NTP Time Synchronization — Compliance Runbook`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `s()` connect `9d0be6640444_add_aadhaar_and_profile_picture.py` to `je`, `lawyer.js`, `app.js`, `audit`, `config.py`, `er`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `HTTPException` (e.g. with `.check()` and `.check_async()`) actually correct?**
  _`HTTPException` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._