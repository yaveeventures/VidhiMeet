# Graph Report - VidhiMeet  (2026-11-05)

## Corpus Check
- 124 files · ~239,376 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2229 nodes · 6276 edges · 103 communities (83 shown, 20 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 939 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f228e6f`
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

## Communities (103 total, 20 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.23
Nodes (45): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AdminVoucherOut (+37 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (72): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+64 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (88): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+80 more)

### Community 3 - "lawyer.js"
Cohesion: 0.10
Nodes (20): clean_string(), Trim whitespace and escape HTML control characters to prevent XSS attacks.     R, Sanitize raw user string input without HTML entity encoding to prevent double-es, Sanitize a filename by removing directory traversal patterns, null bytes,     an, Sanitize object storage keys to prevent path traversal.     Ensures relative key, sanitize_filename(), sanitize_key(), sanitize_text() (+12 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (10): ar(), ir(), Kn(), kr(), mr, pr(), q(), sr() (+2 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (45): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, TypedDict, _query_ntp_server() (+37 more)

### Community 7 - "i"
Cohesion: 0.11
Nodes (37): Message, Review, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+29 more)

### Community 9 - "User"
Cohesion: 0.09
Nodes (4): B(), ft(), je(), we()

### Community 10 - "models.py"
Cohesion: 0.14
Nodes (15): bn(), ge(), ie(), Jn(), me(), N(), ne(), qn() (+7 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.09
Nodes (34): get_settings(), LawyerProfile, rate_limit_dependency(), accept_drafting_request(), download_drafting_document(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile (+26 more)

### Community 12 - "Booking"
Cohesion: 0.05
Nodes (88): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+80 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.23
Nodes (18): a(), c(), ce(), d(), f(), fn(), gn(), gt() (+10 more)

### Community 15 - "calendar.py"
Cohesion: 0.13
Nodes (23): cr(), er(), Es(), Et(), h(), hr(), i(), ia() (+15 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.15
Nodes (34): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), initiate_lawyer_payout(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Dispatches payout to the lawyer for a completed booking or drafting request. (+26 more)

### Community 17 - "admin.py"
Cohesion: 0.08
Nodes (53): PlatformFeedback, User, admin_metrics(), admin_verify_bank_account(), create_promotional_voucher(), delete_voucher(), force_release_booking_payout(), force_release_draft_payout() (+45 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 19 - "_cors_response"
Cohesion: 0.18
Nodes (19): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+11 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (72): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+64 more)

### Community 21 - "config.py"
Cohesion: 0.11
Nodes (43): a(), Bt(), c(), ct(), dn(), ee(), Et(), fe() (+35 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.07
Nodes (47): be(), Bo(), ce(), cr(), de(), dt(), er(), Fo() (+39 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.05
Nodes (60): Base, Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), FrontendStaticFiles, lifespan(), EncryptedString (+52 more)

### Community 25 - "models.py"
Cohesion: 0.18
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 26 - "_cors_response"
Cohesion: 0.05
Nodes (54): create_access_token(), hash_password(), Hash a raw password using Argon2id (OWASP #1 recommendation)., test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin, test_admin_ntp_status_endpoint_accessible_by_admin(), Verify that non-admin accounts cannot access payout list. (+46 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.13
Nodes (22): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+14 more)

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
Cohesion: 0.24
Nodes (7): bn(), Jn(), N(), sn(), wn(), xe(), yn()

### Community 37 - "setup"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 38 - "processEvent"
Cohesion: 0.15
Nodes (8): Ae(), ar(), br, fn(), ir(), mr, pr(), Wt()

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.50
Nodes (7): Voucher, _auth_header(), _create_user(), test_100_percent_free_promotional_voucher(), test_admin_create_promotional_voucher(), test_client_cannot_create_voucher(), test_validate_and_apply_promotional_voucher()

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
Cohesion: 0.19
Nodes (19): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), add_draft_comment(), approve_draft(), cancel_drafting_request(), check_and_process_auto_approvals() (+11 more)

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
Nodes (46): as(), be(), Bt(), ct(), de(), dn(), dr(), dt() (+38 more)

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
Nodes (22): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+14 more)

### Community 75 - ".then"
Cohesion: 0.09
Nodes (44): AsyncSession, AuditLog, RefreshToken, UserConsent, enable_mfa(), forgot_password(), get_me(), google_auth() (+36 more)

### Community 76 - "test_api.py"
Cohesion: 0.15
Nodes (7): get_db(), test_google_auth_lawyer_registration(), test_lawyer_complete_booking_duration_restriction(), test_lawyer_period_availability_booking(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee()

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
Cohesion: 0.06
Nodes (45): Booking, cashfree_webhook(), Request, Session, Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID)., _validate_ws_user_and_booking(), calculate_tax_breakdown(), generate_client_receipt_html() (+37 more)

### Community 86 - "er"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 87 - "SSEClient"
Cohesion: 0.16
Nodes (4): E2EE, SoundNotifier, SSEClient, WebSocketChatClient

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

### Community 341 - "🌐 Domain DNS & SSL/TLS 1.3 — Production Configuration Runbook"
Cohesion: 0.10
Nodes (20): 1. End-to-End Encryption Architecture, 2.1 Zone DNS Records, 2.2 Global Cloudflare Edge SSL/TLS Settings, 2. Cloudflare DNS Infrastructure, 3.1 Cloudflare Real-IP Restoration, 3.2 Canonical Domain Redirection, 3.3 TLS 1.3 Protocols & Cipher Suite, 3.4 Real-time Protocol Handlers (+12 more)

### Community 430 - "gn"
Cohesion: 0.14
Nodes (6): Ae(), br, ee(), qt, re(), yr()

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

## Knowledge Gaps
- **198 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `e()` connect `8dcb01bed07f_initial_schema.py` to `mr`, `je`, `app.js`, `models.py`, `Booking`, `LawyerGrid`, `ntp_now`, `config.py`, `q`, `models.py`, `NTP Time Synchronization — Compliance Runbook`, `services.py`, `setup`, `gn`, `er`, `o`, `test_password_reset.py`, `o`, `api-client.min.js`, `SSEClient`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `n()` connect `config.py` to `o`, `mr`, `SlidingWindowRateLimiter`, `je`, `app.js`, `setup`, `test_password_reset.py`, `processEvent`, `daily-js.js`, `models.py`, `Booking`, `LawyerGrid`, `calendar.py`, `8dcb01bed07f_initial_schema.py`, `ntp_now`, `q`, `models.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `User` connect `admin.py` to `main.py`, `i`, `test_escrow_payout.py`, `.then`, `LawyerProfile`, `test_api.py`, `firebase-phone-auth.min.js`, `drafting.py`, `check_clock_drift`, `_cors_response`, `__init__.py`, `PlatformFeedback`, `_cors_response`, `test_rate_limiter.py`, `validate_voucher`, `80394484e25e_add_phonepe_transaction_id.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `e()` (e.g. with `renderApps()` and `renderApps()`) actually correct?**
  _`e()` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `n()` (e.g. with `_()` and `money()`) actually correct?**
  _`n()` has 69 INFERRED edges - model-reasoned connections that need verification._