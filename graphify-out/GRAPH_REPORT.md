# Graph Report - VidhiMeet  (2026-11-05)

## Corpus Check
- 124 files · ~239,453 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2231 nodes · 6278 edges · 105 communities (88 shown, 17 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 939 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e6e225ee`
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
- models.py
- LawyerProfile
- Booking
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
- ntp_time.py
- LawyerProfile
- drafting.py
- 8dcb01bed07f_initial_schema.py
- websocket_chat_endpoint
- LawyerBankAccount
- Session
- env.py
- __init__.py
- Session
- reset_users.py
- test_security_medium.py
- er
- o
- deploy_cloudflare_shield.py
- websocket_chat_endpoint
- deploy_rules.sh
- test_cancellation.py
- test_document_vault.py
- test_password_reset.py
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- escapeHtml
- o
- .then
- test_api.py
- firebase-phone-auth.min.js
- cookie-consent.min.js
- minify_assets.py
- api-client.min.js
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- e2ee.min.js
- __init__.py
- er
- SSEClient
- LawyerProfileUpdate
- BankAccountUpdate
- test_error_handling.py
- Cashfree Payments — Integration Skills
- validate_voucher
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- test_cancellation.py
- 🌐 Domain DNS & SSL/TLS 1.3 — Production Configuration Runbook
- gn
- test_validation_constants.py
- 3. Core Workflow: Onboard Vendor → Split → Settle
- check_domain_ssl.py
- 3. Core Workflow: Web Checkout
- 3. Core Workflow

## God Nodes (most connected - your core abstractions)
1. `User` - 190 edges
2. `Booking` - 85 edges
3. `e()` - 81 edges
4. `n()` - 77 edges
5. `Role` - 75 edges
6. `LawyerProfile` - 74 edges
7. `audit()` - 67 edges
8. `Practice` - 66 edges
9. `t()` - 66 edges
10. `BookingStatus` - 63 edges

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

## Communities (105 total, 17 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.26
Nodes (43): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AdminVoucherOut (+35 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (72): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+64 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (88): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+80 more)

### Community 3 - "lawyer.js"
Cohesion: 0.10
Nodes (17): clean_string(), Trim whitespace and escape HTML control characters to prevent XSS attacks.     R, Sanitize raw user string input without HTML entity encoding to prevent double-es, Sanitize a filename by removing directory traversal patterns, null bytes,     an, sanitize_filename(), sanitize_text(), BankAccountUpdate, DraftingRequestCreate (+9 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 5 - "daily-js.js"
Cohesion: 0.09
Nodes (18): ar(), br, de(), fn(), ft(), ht(), ir(), Kn() (+10 more)

### Community 6 - "main.py"
Cohesion: 0.09
Nodes (21): test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, Simulated tiny drift (0.05s) must set within_tolerance=True., GET /api/v1/admin/ntp-status must return 401 without a valid token., ntp_now() must always return a UTC-aware datetime regardless of server state., ntp_now_ist() must return a datetime in IST (UTC+05:30)., When all NTP servers are unreachable, ntp_now() must fall back to system clock g, check_clock_drift() must return a dict with all required NtpStatus keys., within_tolerance must be a boolean. (+13 more)

### Community 7 - "i"
Cohesion: 0.12
Nodes (35): Review, rate_limit_dependency(), booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+27 more)

### Community 9 - "User"
Cohesion: 0.08
Nodes (3): B(), je(), we()

### Community 10 - "models.py"
Cohesion: 0.21
Nodes (14): be(), bn(), ge(), ie(), me(), ne(), oe(), qn() (+6 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.19
Nodes (11): get_settings(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile, get_public_auth_config(), Public endpoint exposing client authentication configuration (Google OAuth Clien, delete_s3_object(), generate_presigned_post_data() (+3 more)

### Community 12 - "Booking"
Cohesion: 0.05
Nodes (88): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+80 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.18
Nodes (29): a(), c(), ce(), d(), f(), gn(), gt(), hn() (+21 more)

### Community 15 - "calendar.py"
Cohesion: 0.12
Nodes (28): Ae(), an(), Bs(), ct(), dn(), ee(), Et(), fe() (+20 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.13
Nodes (37): create_access_token(), _create_lawyer_profile_with_pan(), _create_user(), _create_verified_bank(), Session, TestClient, Verify payouts are held when lawyer has a verified bank but no PAN on file., Creates a LawyerProfile with a PAN number for the given lawyer user. (+29 more)

### Community 17 - "admin.py"
Cohesion: 0.10
Nodes (49): User, Voucher, admin_metrics(), admin_verify_bank_account(), create_promotional_voucher(), delete_voucher(), force_release_booking_payout(), force_release_draft_payout() (+41 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.39
Nodes (4): ConnectionManager, _validate_ws_user_and_booking(), websocket_chat_endpoint(), WebSocket

### Community 19 - "_cors_response"
Cohesion: 0.13
Nodes (24): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+16 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (72): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+64 more)

### Community 21 - "config.py"
Cohesion: 0.13
Nodes (33): a(), c(), ct(), dn(), Et(), fe(), ft(), h() (+25 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.08
Nodes (47): be(), Bo(), Bt(), ce(), cr(), de(), dt(), er() (+39 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.05
Nodes (51): lifespan(), EncryptedString, Message, now(), PlatformFeedback, datetime, WebhookEvent, authenticate_stream_user() (+43 more)

### Community 25 - "models.py"
Cohesion: 0.17
Nodes (9): cn(), dr(), _e(), nn(), on(), qe(), un(), ur() (+1 more)

### Community 26 - "_cors_response"
Cohesion: 0.06
Nodes (49): trigger_expire_abandoned_bookings(), hash_password(), Hash a raw password using Argon2id (OWASP #1 recommendation)., create_cashfree_order(), expire_abandoned_bookings(), get_cashfree_order(), _get_cf_headers(), initiate_refund() (+41 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 30 - "bookings.py"
Cohesion: 0.11
Nodes (18): 🛡️ **Admin Console & Compliance Engine**, 💼 **Advocate Portal & Practice Management**, 🔍 **Client Portal & Legal Marketplace**, 🏢 Corporate Entity & Legal Notice, ⚙️ Environment Configuration Guide, 🚀 Getting Started, 🌟 Key Platform Capabilities, 📑 **Legal Document Drafting Hub** (+10 more)

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.31
Nodes (5): bn(), N(), sn(), wn(), xe()

### Community 35 - "services.py"
Cohesion: 0.13
Nodes (8): Ae(), br, ee(), gt(), qn(), qt, re(), ue()

### Community 37 - "setup"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 38 - "processEvent"
Cohesion: 0.12
Nodes (12): ar(), fn(), hn(), ir(), kr(), mr, pr(), q() (+4 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.15
Nodes (16): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify structlog processor scrubs sensitive PII fields and credentials from log, Verify scan_document_payload rejects PDF files containing embedded JavaScript tr (+8 more)

### Community 41 - "SSEClient"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 42 - "README.md"
Cohesion: 0.08
Nodes (19): get_validation_rules(), Public endpoint exposing canonical platform validation rules and constraints, BankAccountCreate, Reject registration if the user is under 18 (DPDP Act 2023, Section 9)., RegisterRequest, get_public_validation_rules(), Canonical Validation Constants and Statutory Limits for VidhiMeet. Serves as the, Returns a dictionary of validation rules safe to expose publicly to frontend cli (+11 more)

### Community 43 - "ui-components.js"
Cohesion: 0.38
Nodes (3): BackgroundTaskManager, Any, Enqueue an async background task safely without blocking request completion.

### Community 45 - "cookie-consent.js"
Cohesion: 0.08
Nodes (6): B(), d(), f(), gn(), je(), we()

### Community 46 - "ntp_time.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 48 - "drafting.py"
Cohesion: 0.13
Nodes (32): AsyncSession, DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft() (+24 more)

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.08
Nodes (86): _(), applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), applyAnalyticsConsent(), getSavedConsent() (+78 more)

### Community 62 - "test_security_medium.py"
Cohesion: 0.67
Nodes (3): main(), make_request(), Any

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "o"
Cohesion: 0.05
Nodes (54): as(), at(), Bo(), Bt(), cr(), Ds(), dt(), ea() (+46 more)

### Community 66 - "websocket_chat_endpoint"
Cohesion: 0.18
Nodes (16): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+8 more)

### Community 68 - "test_cancellation.py"
Cohesion: 0.62
Nodes (6): getDocumentTitle(), handleBack(), handleSavePdf(), initReceipt(), loadHtml2PdfLazy(), tryPrint()

### Community 69 - "test_document_vault.py"
Cohesion: 0.05
Nodes (38): 1.1 Product Vision, 1.2 Problem Statement, 1.3 Value Proposition, 1. Executive Summary & Vision, 2.1 Corporate Entity Details, 2.2 Bar Council of India (BCI) Compliance, 2.3 DPDP Act 2023 & Privacy Architecture, 2.4 CERT-In & Forensic Timestamp Compliance (+30 more)

### Community 70 - "test_password_reset.py"
Cohesion: 0.17
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 72 - "escapeHtml"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 74 - "o"
Cohesion: 0.17
Nodes (16): download_lawyer_document(), get_lawyer(), get_my_profile(), lawyer_document_mock_upload(), lawyer_document_presign(), lawyers(), LawyersCache, _mask_pan() (+8 more)

### Community 75 - ".then"
Cohesion: 0.11
Nodes (31): Base, PasswordResetToken, RefreshToken, enable_mfa(), forgot_password(), get_me(), google_auth(), login() (+23 more)

### Community 76 - "test_api.py"
Cohesion: 0.10
Nodes (23): get_db(), FrontendStaticFiles, AuditLog, LawyerProfile, UserConsent, request_erasure(), StaticFiles, test_google_auth_lawyer_registration() (+15 more)

### Community 77 - "firebase-phone-auth.min.js"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and direct verification., Adding a second bank account returns 409 Conflict., Verify endpoint marks account verified and returns audit UTR., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 78 - "cookie-consent.min.js"
Cohesion: 0.62
Nodes (6): getDocumentTitle(), handleBack(), handleSavePdf(), initReceipt(), loadHtml2PdfLazy(), tryPrint()

### Community 79 - "minify_assets.py"
Cohesion: 0.47
Nodes (5): minify_css(), minify_js(), process_assets(), Minify CSS text by stripping comments and excessive whitespace., Minify JS text while preserving strings and regex literals safely.

### Community 80 - "api-client.min.js"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 85 - "__init__.py"
Cohesion: 0.08
Nodes (31): Booking, cashfree_webhook(), Request, Session, Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID)., evaluate_daily_meeting_logs(), Session, Queries Daily.co REST API or room session logs for the booking's room,     calcu (+23 more)

### Community 86 - "er"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 87 - "SSEClient"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

### Community 89 - "BankAccountUpdate"
Cohesion: 0.18
Nodes (16): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, TypedDict, _query_ntp_server() (+8 more)

### Community 90 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 91 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 92 - "validate_voucher"
Cohesion: 0.23
Nodes (16): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), initiate_lawyer_payout(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Dispatches payout to the lawyer for a completed booking or drafting request. (+8 more)

### Community 93 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 94 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 95 - "Cashfree Payments — Integration Skills"
Cohesion: 0.40
Nodes (4): Cashfree Payments — Integration Skills, How to use these skills, Shared Conventions, Skill Map

### Community 96 - "test_cancellation.py"
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 341 - "🌐 Domain DNS & SSL/TLS 1.3 — Production Configuration Runbook"
Cohesion: 0.10
Nodes (20): 1. End-to-End Encryption Architecture, 2.1 Zone DNS Records, 2.2 Global Cloudflare Edge SSL/TLS Settings, 2. Cloudflare DNS Infrastructure, 3.1 Cloudflare Real-IP Restoration, 3.2 Canonical Domain Redirection, 3.3 TLS 1.3 Protocols & Cipher Suite, 3.4 Real-time Protocol Handlers (+12 more)

### Community 487 - "test_validation_constants.py"
Cohesion: 0.22
Nodes (12): Path, apply_cors_policy(), configure_server_side_encryption(), get_s3_client(), load_cors_policy(), main(), Verify that CORS and bucket configuration are readable and active., Load and format CORS configuration from JSON file. (+4 more)

### Community 554 - "3. Core Workflow: Onboard Vendor → Split → Settle"
Cohesion: 0.30
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 561 - "check_domain_ssl.py"
Cohesion: 0.36
Nodes (7): check_dns(), check_security_headers(), check_tls_and_cert(), main(), Resolve IPv4 address for domain., Inspect SSL/TLS certificate, TLS 1.3 negotiation, and expiry., Validate HTTP response security headers.

### Community 579 - "3. Core Workflow: Web Checkout"
Cohesion: 0.17
Nodes (11): 1. Zero-Trust Storage Architecture, 2.1 Option A: Cloudflare R2 (Recommended for Production), 2.2 Option B: AWS S3 with AWS KMS, 2. Cloudflare R2 vs. AWS S3 Configuration, 3. CORS Policy Hardening, 4.1 Running the Provisioning Script, 4. Applying CORS & Encryption Policies, 5. Presigned URL Security & File Validation (+3 more)

### Community 581 - "3. Core Workflow"
Cohesion: 0.20
Nodes (3): any, Settings, BaseSettings

## Knowledge Gaps
- **198 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `e()` connect `8dcb01bed07f_initial_schema.py` to `mr`, `je`, `app.js`, `daily-js.js`, `Booking`, `LawyerGrid`, `calendar.py`, `ntp_now`, `config.py`, `q`, `models.py`, `NTP Time Synchronization — Compliance Runbook`, `services.py`, `setup`, `gn`, `er`, `o`, `test_password_reset.py`, `api-client.min.js`, `SSEClient`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `n()` connect `config.py` to `mr`, `SlidingWindowRateLimiter`, `je`, `app.js`, `setup`, `test_password_reset.py`, `processEvent`, `daily-js.js`, `models.py`, `Booking`, `LawyerGrid`, `calendar.py`, `8dcb01bed07f_initial_schema.py`, `ntp_now`, `q`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `t()` connect `LawyerGrid` to `o`, `je`, `services.py`, `daily-js.js`, `processEvent`, `test_password_reset.py`, `Booking`, `gn`, `calendar.py`, `8dcb01bed07f_initial_schema.py`, `config.py`, `q`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `e()` (e.g. with `renderApps()` and `renderApps()`) actually correct?**
  _`e()` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `n()` (e.g. with `_()` and `money()`) actually correct?**
  _`n()` has 69 INFERRED edges - model-reasoned connections that need verification._