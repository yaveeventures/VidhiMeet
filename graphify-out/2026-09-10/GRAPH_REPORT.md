# Graph Report - VidhiMeet  (2026-09-10)

## Corpus Check
- 103 files · ~171,370 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1826 nodes · 4869 edges · 85 communities (69 shown, 16 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 583 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a28d2f5`
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
- services.py
- _cors_response
- setup
- processEvent
- Booking
- test_rate_limiter.py
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
- Session
- er
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- deploy_cloudflare_shield.py
- test_password_reset.py
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
- test_error_handling.py
- e2ee.min.js

## God Nodes (most connected - your core abstractions)
1. `User` - 141 edges
2. `Role` - 60 edges
3. `audit()` - 56 edges
4. `Practice` - 54 edges
5. `LawyerProfile` - 51 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `get_settings()` - 39 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
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

## Communities (85 total, 16 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.11
Nodes (55): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+47 more)

### Community 1 - "mr"
Cohesion: 0.06
Nodes (68): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+60 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (83): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+75 more)

### Community 3 - "lawyer.js"
Cohesion: 0.07
Nodes (23): EncryptedString, ConnectionManager, _save_ws_message(), _validate_ws_user_and_booking(), websocket_chat_endpoint(), Reject registration if the user is under 18 (DPDP Act 2023, Section 9)., decrypt_field(), encrypt_field() (+15 more)

### Community 4 - "app.js"
Cohesion: 0.10
Nodes (46): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+38 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (15): ar(), fn(), ft(), hn(), ir(), J(), Kn(), kr() (+7 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (39): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+31 more)

### Community 7 - "i"
Cohesion: 0.05
Nodes (78): get_db(), AuditLog, PasswordResetToken, RefreshToken, UserConsent, enable_mfa(), forgot_password(), google_auth() (+70 more)

### Community 8 - "processEvent"
Cohesion: 0.29
Nodes (8): ce(), de(), dt(), ht(), ke(), processEvent(), ut(), X()

### Community 10 - "N"
Cohesion: 0.19
Nodes (13): be(), ge(), ie(), le(), me(), ne(), oe(), qn() (+5 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.08
Nodes (7): Booking, now(), datetime, test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee()

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (83): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+75 more)

### Community 13 - "sanitize_key"
Cohesion: 0.14
Nodes (14): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify structlog processor scrubs sensitive PII fields and credentials from log, Verify scan_document_payload rejects PDF files containing embedded JavaScript tr (+6 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.14
Nodes (9): get_settings(), Settings, Sends password reset email containing the secret token/link.     Uses Resend HTT, send_password_reset_email(), presign_document(), generate_presigned_post_data(), BaseSettings, client() (+1 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.15
Nodes (28): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+20 more)

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.11
Nodes (30): Base, Message, Review, Voucher, WebhookEvent, booking_for_participant(), cancel_booking(), cancellation_preview() (+22 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.20
Nodes (22): a(), bn(), c(), d(), f(), gn(), gt(), Jn() (+14 more)

### Community 19 - "toast"
Cohesion: 0.12
Nodes (16): FrontendStaticFiles, lifespan(), Calendar Integration Router — VidhiMeet  Provides RFC 5545-compliant iCal endpoi, authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream() (+8 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (66): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+58 more)

### Community 21 - "config.py"
Cohesion: 0.11
Nodes (28): Ae(), at(), B(), br, Bs(), ct(), dn(), ee() (+20 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.07
Nodes (53): a(), be(), Bo(), Bt(), ce(), cr(), de(), dt() (+45 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.13
Nodes (18): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+10 more)

### Community 25 - "models.py"
Cohesion: 0.12
Nodes (15): an(), cn(), _e(), he(), In(), nn(), on(), pe() (+7 more)

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

### Community 31 - "_cors_response"
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

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
Cohesion: 0.17
Nodes (16): AsyncSession, issue_refresh_token(), Session, calculate_cancellation_policy(), get_daily_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake() (+8 more)

### Community 36 - "_cors_response"
Cohesion: 0.18
Nodes (16): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+8 more)

### Community 37 - "setup"
Cohesion: 0.10
Nodes (46): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+38 more)

### Community 38 - "processEvent"
Cohesion: 0.10
Nodes (14): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+6 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_rate_limiter.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 41 - "SSEClient"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 42 - "README.md"
Cohesion: 0.46
Nodes (7): _clearRecaptcha(), confirmOtp(), _friendlyError(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 43 - "ui-components.js"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

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

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "9b17288bd3cf_add_cancellation_fields_and_vouchers.py"
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 66 - "test_password_reset.py"
Cohesion: 0.11
Nodes (43): LawyerProfile, User, rate_limit_dependency(), admin_metrics(), get_admin_payouts(), get_audit_logs(), get_platform_feedback(), list_disputes() (+35 more)

### Community 68 - "sanitize_key"
Cohesion: 0.05
Nodes (52): as(), Bo(), Bt(), cr(), dr(), Ds(), ea(), er() (+44 more)

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

### Community 81 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

## Knowledge Gaps
- **153 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `test_password_reset.py` to `lawyer.js`, `services.py`, `main.py`, `i`, `LawyerProfile`, `sanitize_key`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `toast`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`, `_cors_response`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `_launchDaily()` connect `je` to `mr`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `_launchDaily()` connect `Booking` to `mr`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `LawyerProfile` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`LawyerProfile` has 32 INFERRED edges - model-reasoned connections that need verification._