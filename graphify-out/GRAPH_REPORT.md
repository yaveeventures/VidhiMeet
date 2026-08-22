# Graph Report - VidhiMeet  (2026-08-22)

## Corpus Check
- 85 files · ~99,888 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1225 nodes · 3428 edges · 67 communities (54 shown, 13 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 485 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9acccf64`
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
- pdf-annotator.js
- Settings
- NTP Time Synchronization — Compliance Runbook
- setup_domain_ssl.sh
- test_password_reset.py
- firebase-phone-auth.js
- booking_service.py
- Booking
- verify_ntp_compliance
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- LawyerProfile
- graphify
- graphify.md
- test_marketplace.py
- websocket_chat_endpoint
- LawyerBankAccount
- Session
- env.py
- test_bank_account.py
- __init__.py
- forgot_password
- reset_users.py
- logout
- datetime
- Session
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 134 edges
2. `Role` - 57 edges
3. `audit()` - 55 edges
4. `Practice` - 53 edges
5. `LexAPI` - 50 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 41 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
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

## Communities (67 total, 13 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.14
Nodes (7): Ae(), B(), ee(), qt, re(), we(), yr()

### Community 1 - "mr"
Cohesion: 0.06
Nodes (76): $(), k(), ns(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners() (+68 more)

### Community 2 - "je"
Cohesion: 0.17
Nodes (22): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+14 more)

### Community 3 - "lawyer.js"
Cohesion: 0.07
Nodes (68): doAdminLogin(), checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute() (+60 more)

### Community 4 - "app.js"
Cohesion: 0.10
Nodes (15): ar(), br, fn(), hn(), ir(), Kn(), kr(), mr (+7 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 6 - "main.py"
Cohesion: 0.14
Nodes (20): AuditLog, Review, UserConsent, request_erasure(), _cutoff(), _ensure_tz(), log_purge_audit(), _now() (+12 more)

### Community 8 - "processEvent"
Cohesion: 0.16
Nodes (27): DraftComment, DraftingProposal, DraftingRequest, rate_limit_dependency(), accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft() (+19 more)

### Community 9 - "User"
Cohesion: 0.07
Nodes (30): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), http_exception_handler(), integrity_exception_handler(), lifespan(), Exception (+22 more)

### Community 10 - "audit"
Cohesion: 0.08
Nodes (73): AsyncSession, BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, enable_mfa() (+65 more)

### Community 11 - "toast"
Cohesion: 0.12
Nodes (20): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+12 more)

### Community 13 - "sanitize_key"
Cohesion: 0.10
Nodes (6): get_db(), Booking, test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee()

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.06
Nodes (44): as(), Bo(), Bt(), Ds(), ea(), Fo(), Fs(), g() (+36 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.20
Nodes (10): ce(), de(), dt(), ft(), ht(), J(), ke(), processEvent() (+2 more)

### Community 19 - "toast"
Cohesion: 0.19
Nodes (23): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes(), list_drafting_transactions() (+15 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (43): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+35 more)

### Community 21 - "config.py"
Cohesion: 0.20
Nodes (13): calculate_cancellation_policy(), get_daily_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake(), verify_daily_meeting_duration(), evaluate_daily_meeting_logs(), Session (+5 more)

### Community 22 - "calendar.py"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 23 - "er"
Cohesion: 0.25
Nodes (15): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+7 more)

### Community 25 - "models.py"
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 26 - "_e"
Cohesion: 0.18
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 30 - "bookings.py"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 31 - "pdf-annotator.js"
Cohesion: 0.24
Nodes (7): get_settings(), drafting_document_presign(), presign_document(), generate_presigned_post_data(), get_s3_client(), client(), reset_rate_limiter()

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 36 - "test_password_reset.py"
Cohesion: 0.14
Nodes (14): Base, PasswordResetToken, RefreshToken, Voucher, WebhookEvent, Reset password using a valid, single-use, 15-minute reset token.     Hashes new, reset_password(), DeclarativeBase (+6 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.10
Nodes (29): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s). (+21 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.20
Nodes (22): a(), c(), cr(), d(), er(), f(), gn(), gt() (+14 more)

### Community 41 - "SSEClient"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 42 - "README.md"
Cohesion: 0.23
Nodes (10): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+2 more)

### Community 44 - "test_marketplace.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 47 - "LawyerProfile"
Cohesion: 0.15
Nodes (19): LawyerProfile, drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign() (+11 more)

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 54 - "websocket_chat_endpoint"
Cohesion: 0.39
Nodes (4): ConnectionManager, _validate_ws_user_and_booking(), websocket_chat_endpoint(), WebSocket

### Community 55 - "LawyerBankAccount"
Cohesion: 0.22
Nodes (20): Message, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment(), create_booking() (+12 more)

### Community 57 - "env.py"
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 58 - "test_bank_account.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 60 - "forgot_password"
Cohesion: 0.50
Nodes (4): forgot_password(), Request a password reset link.     Anti-enumeration protection: Returns 200 OK r, Sends password reset email containing the secret token/link.     Uses SMTP confi, send_password_reset_email()

### Community 61 - "reset_users.py"
Cohesion: 0.11
Nodes (20): EncryptedString, now(), datetime, _save_ws_message(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense). (+12 more)

### Community 62 - "logout"
Cohesion: 0.67
Nodes (3): logout(), Log out user and revoke current access token (jti) via Redis blocklist., Response

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `toast` to `main.py`, `processEvent`, `User`, `audit`, `sanitize_key`, `LawyerGrid`, `ntp_now`, `config.py`, `calendar.py`, `er`, `pdf-annotator.js`, `test_password_reset.py`, `booking_service.py`, `README.md`, `LawyerProfile`, `websocket_chat_endpoint`, `LawyerBankAccount`, `forgot_password`, `reset_users.py`, `logout`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `s()` connect `verify_ntp_compliance` to `mr`, `je`, `app.js`, `daily-js.js`, `toast`, `calendar.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `lawyer.js` to `mr`, `T`, `daily-js.js`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `VidhiMeet backend package.`, `Sanitize sensitive PII keys and credentials before log rendering.`, `Configure structured JSON logging for production or key-value console logging fo` to the rest of the system?**
  _190 weakly-connected nodes found - possible documentation gaps or missing edges._