# Graph Report - VidhiMeet  (2026-09-04)

## Corpus Check
- 101 files · ~163,891 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1792 nodes · 4767 edges · 83 communities (66 shown, 17 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 576 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92e756b1`
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
- q
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
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- deploy_cloudflare_shield.py
- deploy_rules.sh
- sanitize_key
- test_document_vault.py
- test_password_reset.py
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- escapeHtml
- logout
- gn
- .then
- SSEClient
- firebase-phone-auth.min.js
- cookie-consent.min.js
- minify_assets.py
- api-client.min.js
- e2ee.min.js

## God Nodes (most connected - your core abstractions)
1. `User` - 138 edges
2. `Role` - 59 edges
3. `audit()` - 56 edges
4. `Practice` - 53 edges
5. `BookingStatus` - 49 edges
6. `Booking` - 48 edges
7. `LawyerProfile` - 44 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `je()` - 39 edges

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

## Communities (83 total, 17 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.10
Nodes (59): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+51 more)

### Community 1 - "mr"
Cohesion: 0.06
Nodes (68): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+60 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (78): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+70 more)

### Community 3 - "lawyer.js"
Cohesion: 0.06
Nodes (38): as(), be(), ce(), de(), dr(), dt(), Es(), g() (+30 more)

### Community 4 - "app.js"
Cohesion: 0.11
Nodes (42): $(), auditLogs, colors, decideVerification(), disputes, draftingTransactions, escapeHtml(), handleSaveFees() (+34 more)

### Community 5 - "daily-js.js"
Cohesion: 0.13
Nodes (12): ar(), fn(), ft(), hn(), ir(), J(), Kn(), mr (+4 more)

### Community 6 - "main.py"
Cohesion: 0.06
Nodes (49): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+41 more)

### Community 7 - "i"
Cohesion: 0.07
Nodes (45): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), create_access_token(), current_user(), decode_token() (+37 more)

### Community 8 - "processEvent"
Cohesion: 0.10
Nodes (54): DraftingProposal, DraftingRequest, LawyerProfile, User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_platform_feedback() (+46 more)

### Community 9 - "User"
Cohesion: 0.07
Nodes (12): B(), bn(), je(), Jn(), N(), sn(), we(), wn() (+4 more)

### Community 10 - "audit"
Cohesion: 0.08
Nodes (40): AsyncSession, Base, get_db(), AuditLog, DraftComment, now(), PasswordResetToken, datetime (+32 more)

### Community 11 - "toast"
Cohesion: 0.30
Nodes (7): bn(), c(), N(), s(), sn(), wn(), xe()

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (78): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+70 more)

### Community 13 - "sanitize_key"
Cohesion: 0.07
Nodes (34): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), _cors_response(), FrontendStaticFiles, http_exception_handler(), integrity_exception_handler() (+26 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.08
Nodes (36): get_settings(), rate_limit_dependency(), download_drafting_document(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile, Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf() (+28 more)

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.10
Nodes (33): Booking, Message, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+25 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.14
Nodes (25): a(), Bt(), c(), cr(), d(), ee(), er(), f() (+17 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (66): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+58 more)

### Community 21 - "config.py"
Cohesion: 0.12
Nodes (28): Ae(), an(), br, ct(), dn(), Et(), fe(), he() (+20 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.08
Nodes (50): a(), be(), Bo(), Bt(), ce(), cr(), de(), dt() (+42 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 25 - "models.py"
Cohesion: 0.20
Nodes (7): cn(), _e(), nn(), on(), qe(), un(), ze()

### Community 26 - "_e"
Cohesion: 0.23
Nodes (16): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+8 more)

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
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "setup_domain_ssl.sh"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 37 - "setup"
Cohesion: 0.11
Nodes (42): $(), auditLogs, colors, decideVerification(), disputes, draftingTransactions, escapeHtml(), handleSaveFees() (+34 more)

### Community 38 - "processEvent"
Cohesion: 0.09
Nodes (17): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+9 more)

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
Cohesion: 0.08
Nodes (6): B(), d(), f(), gn(), je(), we()

### Community 46 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "9b17288bd3cf_add_cancellation_fields_and_vouchers.py"
Cohesion: 0.14
Nodes (17): EncryptedString, _save_ws_message(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense)., validate_participant_access(), Fernet (+9 more)

### Community 68 - "sanitize_key"
Cohesion: 0.11
Nodes (32): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+24 more)

### Community 69 - "test_document_vault.py"
Cohesion: 0.05
Nodes (38): 1.1 Product Vision, 1.2 Problem Statement, 1.3 Value Proposition, 1. Executive Summary & Vision, 2.1 Corporate Entity Details, 2.2 Bar Council of India (BCI) Compliance, 2.3 DPDP Act 2023 & Privacy Architecture, 2.4 CERT-In & Forensic Timestamp Compliance (+30 more)

### Community 70 - "test_password_reset.py"
Cohesion: 0.17
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 72 - "escapeHtml"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 73 - "logout"
Cohesion: 0.22
Nodes (19): ct(), dn(), Et(), fe(), i(), In(), It(), jt() (+11 more)

### Community 74 - "gn"
Cohesion: 0.31
Nodes (8): ge(), ie(), me(), ne(), qn(), ue(), ye(), z()

### Community 75 - ".then"
Cohesion: 0.27
Nodes (3): gt(), qt, re()

### Community 76 - "SSEClient"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 77 - "firebase-phone-auth.min.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 78 - "cookie-consent.min.js"
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 79 - "minify_assets.py"
Cohesion: 0.47
Nodes (5): minify_css(), minify_js(), process_assets(), Minify CSS text by stripping comments and excessive whitespace., Minify JS text while preserving strings and regex literals safely.

### Community 80 - "api-client.min.js"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

## Knowledge Gaps
- **147 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+142 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `processEvent` to `9b17288bd3cf_add_cancellation_fields_and_vouchers.py`, `main.py`, `i`, `audit`, `sanitize_key`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `_launchDaily()` connect `Booking` to `mr`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `_launchDaily()` connect `je` to `mr`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `BookingStatus` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`BookingStatus` has 40 INFERRED edges - model-reasoned connections that need verification._