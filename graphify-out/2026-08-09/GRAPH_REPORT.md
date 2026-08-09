# Graph Report - VidhiMeet  (2026-08-09)

## Corpus Check
- 82 files · ~96,534 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1199 nodes · 3076 edges · 74 communities (50 shown, 24 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 524 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee2f1da6`
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
- graphify.md
- ntp_now
- __init__.py
- ClientRouter
- er
- LawyerBankAccount
- _e
- er
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- pdf-annotator.js
- data_retention_purge.py
- NTP Time Synchronization — Compliance Runbook
- LexAPI
- firebase-phone-auth.js
- booking_service.py
- Booking
- verify_ntp_compliance
- register
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- graphify
- graphify.md
- test_marketplace.py
- Session
- Session
- env.py
- __init__.py
- reset_users.py
- Request
- Session
- Request
- Session
- Session
- UploadFile
- datetime
- Request
- Session
- Session
- test_security_medium.py
- Session
- Session
- datetime
- Session
- test_error_handling.py
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 95 edges
2. `Role` - 49 edges
3. `audit()` - 48 edges
4. `Practice` - 47 edges
5. `LexAPI` - 46 edges
6. `BookingStatus` - 43 edges
7. `DraftingStatus` - 42 edges
8. `ProposalStatus` - 42 edges
9. `Booking` - 39 edges
10. `je()` - 39 edges

## Surprising Connections (you probably didn't know these)
- `test_video_consultation_dual_platform_fee()` --calls--> `Booking`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_settings()`  [INFERRED]
  tests/test_bank_account.py → backend/config.py
- `test_dpdpa_consent_enforcement_and_logging()` --calls--> `get_db()`  [INFERRED]
  tests/test_compliance.py → backend/db.py
- `test_right_to_erasure()` --calls--> `get_db()`  [INFERRED]
  tests/test_compliance.py → backend/db.py
- `test_7day_auto_approval_window()` --calls--> `get_db()`  [INFERRED]
  tests/test_drafting.py → backend/db.py

## Import Cycles
- None detected.

## Communities (74 total, 24 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.14
Nodes (8): Ae(), B(), br, ee(), qt, re(), we(), yr()

### Community 1 - "mr"
Cohesion: 0.06
Nodes (75): $(), doAdminLogin(), checkInactivity(), LexAPI, openChatModal(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS (+67 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (44): as(), Bo(), Bt(), Ds(), dt(), ea(), Fo(), Fs() (+36 more)

### Community 3 - "lawyer.js"
Cohesion: 0.06
Nodes (64): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal() (+56 more)

### Community 4 - "app.js"
Cohesion: 0.09
Nodes (20): ar(), de(), fn(), ft(), hn(), ht(), ir(), J() (+12 more)

### Community 5 - "daily-js.js"
Cohesion: 0.10
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 6 - "main.py"
Cohesion: 0.09
Nodes (20): BaseSettings, _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents() (+12 more)

### Community 8 - "processEvent"
Cohesion: 0.16
Nodes (26): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+18 more)

### Community 9 - "User"
Cohesion: 0.09
Nodes (39): Message, Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+31 more)

### Community 10 - "audit"
Cohesion: 0.11
Nodes (55): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+47 more)

### Community 11 - "toast"
Cohesion: 0.13
Nodes (14): Run CERT-In / DPDP compliant NTP clock drift check., verify_ntp_compliance(), check_clock_drift() must return a dict with all required NtpStatus keys., within_tolerance must be a boolean., When all NTP servers fail, within_tolerance must be False and server must be 'un, test_check_clock_drift_all_servers_unreachable(), test_check_clock_drift_returns_expected_keys(), test_check_clock_drift_within_tolerance_type() (+6 more)

### Community 12 - "Booking"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 13 - "sanitize_key"
Cohesion: 0.13
Nodes (15): drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign(), lawyers() (+7 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.08
Nodes (26): Booking, LawyerProfile, PhonePe webhook with VERIFY- prefix updates LawyerBankAccount, not a Booking., test_phonepe_verify_webhook_routes_correctly(), test_get_booking_by_id(), test_phonepe_webhook_verification(), admin_metrics(), list_disputes() (+18 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.17
Nodes (24): a(), c(), ce(), cr(), d(), er(), f(), gn() (+16 more)

### Community 19 - "graphify.md"
Cohesion: 0.11
Nodes (14): AuditLog, now(), datetime, UserConsent, WebhookEvent, request_erasure(), phonepe_webhook(), stripe_webhook() (+6 more)

### Community 20 - "ntp_now"
Cohesion: 0.12
Nodes (15): test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, Simulated tiny drift (0.05s) must set within_tolerance=True., GET /api/v1/admin/ntp-status must return 401 without a valid token., ntp_now() must always return a UTC-aware datetime regardless of server state., ntp_now_ist() must return a datetime in IST (UTC+05:30)., When all NTP servers are unreachable, ntp_now() must fall back to system clock g, drift_seconds must be a float., Simulated large drift (10s) must set within_tolerance=False. (+7 more)

### Community 22 - "ClientRouter"
Cohesion: 0.22
Nodes (5): PlatformFeedback, get_platform_feedback(), Returns all submitted platform feedback ordered by newest first., Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 23 - "er"
Cohesion: 0.14
Nodes (8): _get_servers(), ntp_now_ist(), _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t, Return the current NPL/NIC-sourced time in Indian Standard Time (UTC+5:30)., Send a single NTP client request to *host* and return the transmit     timestamp, Return the ordered list of NTP servers from settings., rate_limit_dependency()

### Community 25 - "LawyerBankAccount"
Cohesion: 0.19
Nodes (16): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+8 more)

### Community 26 - "_e"
Cohesion: 0.16
Nodes (12): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 27 - "er"
Cohesion: 0.14
Nodes (19): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+11 more)

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
Cohesion: 0.14
Nodes (14): http_exception_handler(), integrity_exception_handler(), Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err, Global Fallback Exception Handler for unexpected server failures (500):     - Pr, security_headers_and_rate_limit() (+6 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "LexAPI"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.07
Nodes (55): AsyncSession, RefreshToken, User, enable_mfa(), google_auth(), login(), logout(), Session (+47 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.12
Nodes (20): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+12 more)

### Community 41 - "register"
Cohesion: 0.15
Nodes (27): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+19 more)

### Community 42 - "README.md"
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 44 - "test_marketplace.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 57 - "env.py"
Cohesion: 0.24
Nodes (8): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), lifespan(), FastAPI, Verify structlog processor scrubs sensitive PII fields and credentials from log, test_structlog_pii_scrubbing_processor()

### Community 61 - "reset_users.py"
Cohesion: 0.07
Nodes (23): EncryptedString, ConnectionManager, _save_ws_message(), _validate_ws_user_and_booking(), websocket_chat_endpoint(), decrypt_field(), encrypt_field(), _get_fernet_cipher() (+15 more)

### Community 76 - "test_security_medium.py"
Cohesion: 0.25
Nodes (8): Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify scan_document_payload rejects PDF files containing embedded JavaScript tr, Verify scan_document_payload rejects Office document archives containing VBA mac, Verify scan_document_payload accepts clean PDF files., test_malware_scanner_accepts_clean_pdf(), test_malware_scanner_rejects_malicious_pdf_js(), test_malware_scanner_rejects_vba_macro_binaries()

## Knowledge Gaps
- **66 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `9d0be6640444_add_aadhaar_and_profile_picture.py` to `mr`, `je`, `app.js`, `daily-js.js`, `verify_ntp_compliance`, `register`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `User` connect `booking_service.py` to `processEvent`, `User`, `README.md`, `sanitize_key`, `LawyerGrid`, `calendar.py`, `graphify.md`, `env.py`, `reset_users.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `mr` to `lawyer.js`, `T`, `daily-js.js`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `audit()` (e.g. with `add_bank_account()` and `delete_bank_account()`) actually correct?**
  _`audit()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 40 INFERRED edges - model-reasoned connections that need verification._