# Graph Report - VidhiMeet  (2026-09-19)

## Corpus Check
- 123 files · ~209,606 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2142 nodes · 5791 edges · 93 communities (75 shown, 18 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 666 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18e42d42`
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
- User
- LawyerProfile
- Booking
- main.py
- LawyerGrid
- calendar.py
- check_clock_drift
- admin.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- _cors_response
- ntp_now
- config.py
- calendar.py
- q
- PlatformFeedback
- models.py
- _cors_response
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
- o
- deploy_cloudflare_shield.py
- websocket_chat_endpoint
- deploy_rules.sh
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
- __init__.py
- test_cashfree.py
- Settings
- test_error_handling.py
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills

## God Nodes (most connected - your core abstractions)
1. `User` - 187 edges
2. `Booking` - 82 edges
3. `Role` - 76 edges
4. `LawyerProfile` - 72 edges
5. `Practice` - 68 edges
6. `audit()` - 67 edges
7. `BookingStatus` - 64 edges
8. `DraftingStatus` - 57 edges
9. `ProposalStatus` - 53 edges
10. `create_access_token()` - 50 edges

## Surprising Connections (you probably didn't know these)
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py
- `test_cancelled_slot_relisting()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py
- `test_client_cancel_between_2h_and_24h_partial_refund()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py
- `test_client_cancel_more_than_24h_full_refund()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py

## Import Cycles
- None detected.

## Communities (93 total, 18 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.06
Nodes (91): BookingStatus, DraftingStatus, PlatformFeedback, Practice, ProposalStatus, str, Role, Validate a promotional or rebooking voucher code and return the discounted break (+83 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (70): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+62 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 3 - "lawyer.js"
Cohesion: 0.30
Nodes (7): bn(), c(), N(), s(), sn(), wn(), xe()

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (55): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+47 more)

### Community 5 - "daily-js.js"
Cohesion: 0.13
Nodes (12): ar(), fn(), ft(), hn(), ir(), J(), Kn(), mr (+4 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (47): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, TypedDict, _query_ntp_server() (+39 more)

### Community 7 - "i"
Cohesion: 0.05
Nodes (40): as(), be(), ce(), de(), dr(), dt(), Es(), g() (+32 more)

### Community 9 - "User"
Cohesion: 0.07
Nodes (10): B(), bn(), je(), N(), sn(), we(), wn(), Ws() (+2 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.04
Nodes (78): get_db(), LawyerProfile, Rotate (invalidate) the lawyer's iCal token and issue a new one., rotate_ical_token(), public_stats(), Public endpoint — no auth required. Returns live platform statistics for the hom, create_access_token(), hash_password() (+70 more)

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (33): _auth(), Tests for Cashfree Reverse Penny Drop (RPD) bank account verification.  All test, Polling status before payment returns PENDING / verified=False., Polling status without a verification_id and no account returns 400., Simulating payment via mock-complete marks account verified., After mock-complete, bank account record has real account/IFSC, not PENDING., Mock-complete with no active session returns 400., Polling status after mock-complete returns SUCCESS and account details. (+25 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.11
Nodes (34): DraftComment, DraftingProposal, DraftingRequest, now(), datetime, logout(), Response, Log out user and revoke current access token (jti) via Redis blocklist. (+26 more)

### Community 17 - "admin.py"
Cohesion: 0.10
Nodes (45): User, Voucher, admin_metrics(), create_promotional_voucher(), delete_voucher(), force_release_booking_payout(), force_release_draft_payout(), get_admin_payouts() (+37 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.14
Nodes (25): a(), Bt(), c(), cr(), d(), ee(), er(), f() (+17 more)

### Community 19 - "_cors_response"
Cohesion: 0.22
Nodes (6): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Verify structlog processor scrubs sensitive PII fields and credentials from log, test_structlog_pii_scrubbing_processor()

### Community 20 - "ntp_now"
Cohesion: 0.06
Nodes (72): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+64 more)

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
Cohesion: 0.16
Nodes (19): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+11 more)

### Community 25 - "models.py"
Cohesion: 0.20
Nodes (7): cn(), _e(), nn(), on(), qe(), un(), ze()

### Community 26 - "_cors_response"
Cohesion: 0.04
Nodes (78): AsyncSession, Base, FrontendStaticFiles, lifespan(), AuditLog, EncryptedString, Message, PasswordResetToken (+70 more)

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
Cohesion: 0.30
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "services.py"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 37 - "setup"
Cohesion: 0.08
Nodes (55): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+47 more)

### Community 38 - "processEvent"
Cohesion: 0.09
Nodes (17): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+9 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.16
Nodes (32): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Sweeps all COMPLETED Bookings whose 7-day dispute window has expired     and who, Sweeps all COMPLETED DraftingRequests whose payout is still pending or held (+24 more)

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
Nodes (6): B(), d(), f(), gn(), je(), we()

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
Cohesion: 0.10
Nodes (37): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+29 more)

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "o"
Cohesion: 0.11
Nodes (32): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+24 more)

### Community 66 - "websocket_chat_endpoint"
Cohesion: 0.18
Nodes (16): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+8 more)

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

### Community 85 - "__init__.py"
Cohesion: 0.10
Nodes (30): get_settings(), download_drafting_document(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile, Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document() (+22 more)

### Community 87 - "test_cashfree.py"
Cohesion: 0.05
Nodes (74): Booking, Review, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+66 more)

### Community 90 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 91 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

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
- **172 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `admin.py` to `main.py`, `main.py`, `test_escrow_payout.py`, `LawyerProfile`, `check_clock_drift`, `__init__.py`, `test_cashfree.py`, `PlatformFeedback`, `_cors_response`, `80394484e25e_add_phonepe_transaction_id.py`, `Booking`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `_launchDaily()` connect `Booking` to `ntp_now`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Role` connect `main.py` to `test_escrow_payout.py`, `LawyerProfile`, `check_clock_drift`, `admin.py`, `__init__.py`, `test_cashfree.py`, `PlatformFeedback`, `_cors_response`, `Booking`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `LawyerProfile` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`LawyerProfile` has 44 INFERRED edges - model-reasoned connections that need verification._