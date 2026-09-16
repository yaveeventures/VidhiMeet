# Graph Report - VidhiMeet  (2026-09-15)

## Corpus Check
- 117 files · ~192,420 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2055 nodes · 5503 edges · 98 communities (80 shown, 18 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 624 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1a3cfa8`
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
- N
- LawyerProfile
- Booking
- main.py
- LawyerGrid
- calendar.py
- check_clock_drift
- 8dcb01bed07f_initial_schema.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- _cors_response
- ntp_now
- config.py
- calendar.py
- q
- PlatformFeedback
- models.py
- bank_accounts.py
- test_rate_limiter.py
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- setup
- Settings
- NTP Time Synchronization — Compliance Runbook
- SlidingWindowRateLimiter
- services.py
- validation-rules.min.js
- setup
- processEvent
- Booking
- test_escrow_payout.py
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- test_sql_safety.py
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
- Booking
- er
- test_error_handling.py
- deploy_cloudflare_shield.py
- test_password_reset.py
- deploy_rules.sh
- test_security_medium.py
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
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- e2ee.min.js
- Settings
- User
- test_sanitizer.py
- RegisterRequest
- decode_token
- admin.py
- Cashfree Payments — Integration Skills
- get_client_ip
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills

## God Nodes (most connected - your core abstractions)
1. `User` - 164 edges
2. `Role` - 70 edges
3. `Booking` - 70 edges
4. `LawyerProfile` - 65 edges
5. `audit()` - 64 edges
6. `Practice` - 62 edges
7. `BookingStatus` - 58 edges
8. `DraftingStatus` - 53 edges
9. `ProposalStatus` - 49 edges
10. `get_settings()` - 43 edges

## Surprising Connections (you probably didn't know these)
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py
- `test_cancelled_slot_relisting()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py
- `test_client_cancel_between_2h_and_24h_partial_refund()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py

## Import Cycles
- None detected.

## Communities (98 total, 18 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.25
Nodes (42): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+34 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (67): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+59 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 3 - "lawyer.js"
Cohesion: 0.11
Nodes (20): EncryptedString, _save_ws_message(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense)., validate_participant_access(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then (+12 more)

### Community 4 - "app.js"
Cohesion: 0.09
Nodes (51): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+43 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (13): ar(), fn(), ft(), hn(), ir(), J(), kr(), mr (+5 more)

### Community 6 - "main.py"
Cohesion: 0.06
Nodes (49): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+41 more)

### Community 7 - "i"
Cohesion: 0.06
Nodes (39): as(), be(), Bt(), ce(), de(), dr(), dt(), Es() (+31 more)

### Community 8 - "processEvent"
Cohesion: 0.39
Nodes (4): ConnectionManager, _validate_ws_user_and_booking(), websocket_chat_endpoint(), WebSocket

### Community 9 - "User"
Cohesion: 0.07
Nodes (12): B(), bn(), je(), Jn(), N(), sn(), we(), wn() (+4 more)

### Community 10 - "N"
Cohesion: 0.11
Nodes (32): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+24 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.07
Nodes (58): create_access_token(), hash_password(), Hash a raw password using Argon2id (OWASP #1 recommendation)., test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin, test_admin_ntp_status_endpoint_accessible_by_admin(), Verify that non-admin accounts cannot access payout list. (+50 more)

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (33): _auth(), Tests for Cashfree Reverse Penny Drop (RPD) bank account verification.  All test, Polling status before payment returns PENDING / verified=False., Polling status without a verification_id and no account returns 400., Simulating payment via mock-complete marks account verified., After mock-complete, bank account record has real account/IFSC, not PENDING., Mock-complete with no active session returns 400., Polling status after mock-complete returns SUCCESS and account details. (+25 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.06
Nodes (44): get_settings(), rate_limit_dependency(), drafting_document_mock_upload(), UploadFile, Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document(), get_my_profile() (+36 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.15
Nodes (28): AsyncSession, DraftComment, DraftingProposal, DraftingRequest, force_release_draft_payout(), Admin override: Force-release payout for a completed drafting request to drafter, accept_drafting_proposal(), accept_drafting_request() (+20 more)

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.10
Nodes (21): Booking, resolve_dispute(), cashfree_webhook(), Request, Session, Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID)., create_cashfree_order(), get_cashfree_order() (+13 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.14
Nodes (25): a(), c(), cr(), d(), ee(), er(), f(), gn() (+17 more)

### Community 19 - "_cors_response"
Cohesion: 0.19
Nodes (16): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+8 more)

### Community 20 - "ntp_now"
Cohesion: 0.06
Nodes (69): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+61 more)

### Community 21 - "config.py"
Cohesion: 0.13
Nodes (26): Ae(), an(), br, ct(), dn(), Et(), fe(), he() (+18 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.07
Nodes (53): a(), be(), Bo(), Bt(), ce(), cr(), de(), dt() (+45 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.13
Nodes (22): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+14 more)

### Community 25 - "models.py"
Cohesion: 0.20
Nodes (7): cn(), _e(), nn(), on(), qe(), un(), ze()

### Community 26 - "bank_accounts.py"
Cohesion: 0.13
Nodes (21): admin_metrics(), force_release_booking_payout(), list_disputes(), list_drafting_transactions(), list_pending_payouts(), list_transactions(), list_users(), Request (+13 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Lawyer can delete their bank account., Adding a second bank account returns 409 Conflict., Verify endpoint now delegates to RPD; returns verification_id and qr_code in moc, Calling /verify without a bank account now initiates RPD (auto-link flow)., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag; verification done via RPD mock-complete., Lawyer can add a bank account; account number is masked in response. (+7 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 30 - "bookings.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "services.py"
Cohesion: 0.07
Nodes (46): Base, AuditLog, now(), PasswordResetToken, PlatformFeedback, datetime, RefreshToken, UserConsent (+38 more)

### Community 37 - "setup"
Cohesion: 0.09
Nodes (51): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+43 more)

### Community 38 - "processEvent"
Cohesion: 0.10
Nodes (14): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+6 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.23
Nodes (16): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), initiate_lawyer_payout(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Dispatches payout to the lawyer for a completed booking or drafting request. (+8 more)

### Community 41 - "SSEClient"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 42 - "README.md"
Cohesion: 0.46
Nodes (7): _clearRecaptcha(), confirmOtp(), _friendlyError(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 43 - "ui-components.js"
Cohesion: 0.38
Nodes (3): BackgroundTaskManager, Any, Enqueue an async background task safely without blocking request completion.

### Community 45 - "cookie-consent.js"
Cohesion: 0.08
Nodes (10): B(), bn(), c(), je(), N(), s(), sn(), we() (+2 more)

### Community 46 - "test_sql_safety.py"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 62 - "Booking"
Cohesion: 0.12
Nodes (31): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+23 more)

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 66 - "test_password_reset.py"
Cohesion: 0.15
Nodes (9): get_db(), FrontendStaticFiles, LawyerProfile, StaticFiles, test_google_auth_lawyer_registration(), test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only() (+1 more)

### Community 68 - "test_security_medium.py"
Cohesion: 0.13
Nodes (16): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), lifespan(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), FastAPI (+8 more)

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
Cohesion: 0.17
Nodes (11): d(), f(), ge(), gn(), ie(), me(), ne(), qn() (+3 more)

### Community 75 - ".then"
Cohesion: 0.27
Nodes (3): gt(), qt, re()

### Community 76 - "SSEClient"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 77 - "firebase-phone-auth.min.js"
Cohesion: 0.46
Nodes (7): _clearRecaptcha(), confirmOtp(), _friendlyError(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 78 - "cookie-consent.min.js"
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 79 - "minify_assets.py"
Cohesion: 0.47
Nodes (5): minify_css(), minify_js(), process_assets(), Minify CSS text by stripping comments and excessive whitespace., Minify JS text while preserving strings and regex literals safely.

### Community 80 - "api-client.min.js"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 86 - "User"
Cohesion: 0.14
Nodes (33): Message, Review, User, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking() (+25 more)

### Community 87 - "test_sanitizer.py"
Cohesion: 0.09
Nodes (14): clean_string(), Trim whitespace and escape HTML control characters to prevent XSS attacks.     R, Sanitize raw user string input without HTML entity encoding to prevent double-es, sanitize_text(), BankAccountUpdate, DraftingRequestCreate, LawyerProfileUpdate, MessageCreate (+6 more)

### Community 88 - "RegisterRequest"
Cohesion: 0.08
Nodes (17): get_validation_rules(), Public endpoint exposing canonical platform validation rules and constraints, BankAccountCreate, Reject registration if the user is under 18 (DPDP Act 2023, Section 9)., RegisterRequest, get_public_validation_rules(), Canonical Validation Constants and Statutory Limits for VidhiMeet. Serves as the, Returns a dictionary of validation rules safe to expose publicly to frontend cli (+9 more)

### Community 89 - "decode_token"
Cohesion: 0.16
Nodes (14): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+6 more)

### Community 90 - "admin.py"
Cohesion: 0.20
Nodes (10): get_admin_payouts(), get_audit_logs(), get_platform_feedback(), list_pending_lawyers(), list_rejected_lawyers(), Returns all lawyer payout bank accounts with masked credentials (account number, Returns all submitted platform feedback ordered by newest first., lawyers() (+2 more)

### Community 91 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 92 - "get_client_ip"
Cohesion: 0.40
Nodes (5): get_client_ip(), Request, Extract real client IP prioritizing Cloudflare and reverse-proxy headers., Verify get_client_ip correctly prioritizes Cloudflare and reverse proxy headers., test_get_client_ip_priority()

### Community 93 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 94 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 95 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 96 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

## Knowledge Gaps
- **170 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+165 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `lawyer.js`, `main.py`, `processEvent`, `LawyerProfile`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `_cors_response`, `PlatformFeedback`, `bank_accounts.py`, `80394484e25e_add_phonepe_transaction_id.py`, `services.py`, `test_escrow_payout.py`, `Booking`, `test_password_reset.py`, `test_security_medium.py`, `decode_token`, `admin.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `LawyerProfile` connect `test_password_reset.py` to `main.py`, `services.py`, `test_security_medium.py`, `admin.py`, `main.py`, `test_escrow_payout.py`, `LawyerProfile`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `_cors_response`, `User`, `PlatformFeedback`, `bank_accounts.py`, `80394484e25e_add_phonepe_transaction_id.py`, `Booking`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `LawyerGrid` to `SlidingWindowRateLimiter`, `lawyer.js`, `services.py`, `main.py`, `test_escrow_payout.py`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `_cors_response`, `Settings`, `User`, `admin.py`, `T`, `Booking`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `LawyerProfile` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`LawyerProfile` has 40 INFERRED edges - model-reasoned connections that need verification._