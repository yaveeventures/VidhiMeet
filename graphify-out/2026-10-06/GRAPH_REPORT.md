# Graph Report - VidhiMeet  (2026-09-28)

## Corpus Check
- 124 files · ~224,377 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2163 nodes · 6149 edges · 92 communities (74 shown, 18 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 941 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3b947377`
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
- test_cancellation.py
- test_document_vault.py
- test_password_reset.py
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- escapeHtml
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
- test_error_handling.py
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- setup_mfa

## God Nodes (most connected - your core abstractions)
1. `User` - 187 edges
2. `Booking` - 82 edges
3. `e()` - 82 edges
4. `Role` - 75 edges
5. `n()` - 75 edges
6. `LawyerProfile` - 74 edges
7. `audit()` - 67 edges
8. `Practice` - 66 edges
9. `t()` - 66 edges
10. `BookingStatus` - 62 edges

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

## Communities (92 total, 18 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (105): AsyncSession, BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, enable_mfa() (+97 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (71): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+63 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (74): add(), bindTimeSelectListeners(), calculateExperience(), calculateProfileCompleteness(), checkLawyerSession(), checkSessionExpiryNotice(), checkWelcomeModal(), closeCall() (+66 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 5 - "daily-js.js"
Cohesion: 0.14
Nodes (9): Ae(), ar(), br, fn(), ft(), ir(), mr, pr() (+1 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (47): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, TypedDict, _query_ntp_server() (+39 more)

### Community 7 - "i"
Cohesion: 0.11
Nodes (36): Message, Review, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+28 more)

### Community 9 - "User"
Cohesion: 0.07
Nodes (14): B(), bn(), je(), Jn(), N(), qn(), sn(), ue() (+6 more)

### Community 10 - "models.py"
Cohesion: 0.15
Nodes (28): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+20 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.05
Nodes (54): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the in-memory + Redis revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin (+46 more)

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (74): add(), bindTimeSelectListeners(), calculateExperience(), calculateProfileCompleteness(), checkLawyerSession(), checkSessionExpiryNotice(), checkWelcomeModal(), closeCall() (+66 more)

### Community 13 - "main.py"
Cohesion: 0.06
Nodes (46): Booking, cashfree_webhook(), Request, Session, Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID)., _validate_ws_user_and_booking(), evaluate_daily_meeting_logs(), Session (+38 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.22
Nodes (19): ct(), dn(), Et(), fe(), i(), In(), It(), jt() (+11 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.16
Nodes (32): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Sweeps all COMPLETED Bookings whose 7-day dispute window has expired     and who, Sweeps all COMPLETED DraftingRequests whose payout is still pending or held (+24 more)

### Community 17 - "admin.py"
Cohesion: 0.10
Nodes (46): User, admin_metrics(), admin_verify_bank_account(), create_promotional_voucher(), delete_voucher(), force_release_booking_payout(), force_release_draft_payout(), get_admin_payouts() (+38 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.30
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 19 - "_cors_response"
Cohesion: 0.29
Nodes (8): Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify scan_document_payload rejects PDF files containing embedded JavaScript tr, Verify scan_document_payload rejects Office document archives containing VBA mac, Verify scan_document_payload accepts clean PDF files., test_malware_scanner_accepts_clean_pdf(), test_malware_scanner_rejects_malicious_pdf_js(), test_malware_scanner_rejects_vba_macro_binaries()

### Community 20 - "ntp_now"
Cohesion: 0.06
Nodes (73): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+65 more)

### Community 21 - "config.py"
Cohesion: 0.14
Nodes (39): Bt(), ct(), dn(), ee(), Et(), fe(), gt(), hn() (+31 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.07
Nodes (53): a(), be(), Bo(), Bt(), ce(), cr(), de(), dt() (+45 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.08
Nodes (30): get_db(), LawyerProfile, booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold() (+22 more)

### Community 25 - "models.py"
Cohesion: 0.18
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 26 - "_cors_response"
Cohesion: 0.05
Nodes (61): Base, FrontendStaticFiles, lifespan(), AuditLog, EncryptedString, now(), PasswordResetToken, PlatformFeedback (+53 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.29
Nodes (8): ce(), de(), dt(), ht(), ke(), processEvent(), ut(), X()

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
Cohesion: 0.50
Nodes (7): Voucher, _auth_header(), _create_user(), test_100_percent_free_promotional_voucher(), test_admin_create_promotional_voucher(), test_client_cannot_create_voucher(), test_validate_and_apply_promotional_voucher()

### Community 35 - "services.py"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 37 - "setup"
Cohesion: 0.08
Nodes (56): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+48 more)

### Community 38 - "processEvent"
Cohesion: 0.10
Nodes (14): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+6 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and direct verification., Adding a second bank account returns 409 Conflict., Verify endpoint marks account verified and returns audit UTR., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

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
Cohesion: 0.08
Nodes (86): _(), applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), applyAnalyticsConsent(), getSavedConsent() (+78 more)

### Community 62 - "Booking"
Cohesion: 0.20
Nodes (18): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+10 more)

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "o"
Cohesion: 0.05
Nodes (63): as(), at(), be(), Bo(), Bs(), cr(), dr(), Ds() (+55 more)

### Community 66 - "websocket_chat_endpoint"
Cohesion: 0.09
Nodes (22): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception (+14 more)

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
Cohesion: 0.62
Nodes (6): getDocumentTitle(), handleBack(), handleSavePdf(), initReceipt(), loadHtml2PdfLazy(), tryPrint()

### Community 79 - "minify_assets.py"
Cohesion: 0.47
Nodes (5): minify_css(), minify_js(), process_assets(), Minify CSS text by stripping comments and excessive whitespace., Minify JS text while preserving strings and regex literals safely.

### Community 80 - "api-client.min.js"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 85 - "__init__.py"
Cohesion: 0.07
Nodes (43): get_settings(), rate_limit_dependency(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile, Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document() (+35 more)

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

### Community 97 - "setup_mfa"
Cohesion: 0.15
Nodes (12): a(), c(), d(), f(), gn(), J(), or(), p() (+4 more)

## Knowledge Gaps
- **146 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+141 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `e()` connect `8dcb01bed07f_initial_schema.py` to `mr`, `je`, `app.js`, `User`, `Booking`, `LawyerGrid`, `calendar.py`, `ntp_now`, `config.py`, `q`, `models.py`, `test_rate_limiter.py`, `NTP Time Synchronization — Compliance Runbook`, `setup`, `er`, `o`, `test_password_reset.py`, `.then`, `SSEClient`, `api-client.min.js`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `n()` connect `config.py` to `o`, `mr`, `setup_mfa`, `app.js`, `setup`, `test_password_reset.py`, `processEvent`, `daily-js.js`, `User`, `gn`, `cookie-consent.js`, `LawyerGrid`, `8dcb01bed07f_initial_schema.py`, `ntp_now`, `q`, `models.py`, `test_rate_limiter.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `t()` connect `config.py` to `o`, `setup_mfa`, `je`, `processEvent`, `test_password_reset.py`, `User`, `gn`, `.then`, `Booking`, `LawyerGrid`, `calendar.py`, `8dcb01bed07f_initial_schema.py`, `q`, `models.py`, `test_rate_limiter.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 67 inferred relationships involving `e()` (e.g. with `renderApps()` and `renderApps()`) actually correct?**
  _`e()` has 67 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 48 INFERRED edges - model-reasoned connections that need verification._