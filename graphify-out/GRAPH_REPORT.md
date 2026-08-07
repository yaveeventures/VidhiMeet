# Graph Report - LawyerGrid  (2026-08-06)

## Corpus Check
- 69 files · ~71,272 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1028 nodes · 2554 edges · 72 communities (46 shown, 26 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 500 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- main.py
- i
- o
- Base
- audit
- Session
- Booking
- qt
- LawyerGrid
- 268d55c084cf_add_mobile_number.py
- check_clock_drift
- 8dcb01bed07f_initial_schema.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- graphify.md
- graphify.md
- __init__.py
- ClientRouter
- er
- models.py
- gn
- _e
- er
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- pdf-annotator.js
- data_retention_purge.py
- NTP Time Synchronization — Compliance Runbook
- reset_users.py
- qt
- firebase-phone-auth.js
- booking_service.py
- Booking
- sanitize_key
- register
- ui-components.js
- cookie-consent.js
- graphify
- graphify.md
- __init__.py
- Session
- Session
- datetime
- Session
- Session
- Request
- Session
- Request
- Session
- UploadFile
- Session
- UploadFile
- ntp_time.py
- Request
- Session
- Session
- Session
- datetime
- Session
- test_error_handling.py
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 52 edges
2. `audit()` - 42 edges
3. `LexAPI` - 41 edges
4. `je()` - 39 edges
5. `Practice` - 36 edges
6. `BookingStatus` - 35 edges
7. `Role` - 34 edges
8. `i()` - 34 edges
9. `DraftingStatus` - 33 edges
10. `ProposalStatus` - 33 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_settings()`  [INFERRED]
  tests/test_bank_account.py → backend/config.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `test_phonepe_verify_webhook_routes_correctly()` --indirect_call--> `User`  [INFERRED]
  tests/test_bank_account.py → backend/models.py
- `test_dpdpa_consent_enforcement_and_logging()` --indirect_call--> `User`  [INFERRED]
  tests/test_compliance.py → backend/models.py

## Import Cycles
- None detected.

## Communities (72 total, 26 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (55): $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn, chatKeys (+47 more)

### Community 2 - "je"
Cohesion: 0.07
Nodes (38): as(), Bo(), Ds(), dt(), ea(), Fo(), Fs(), g() (+30 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (61): checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay() (+53 more)

### Community 4 - "app.js"
Cohesion: 0.10
Nodes (16): Ae(), ar(), br, fn(), ft(), ht(), ir(), kr() (+8 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (41): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+33 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 8 - "o"
Cohesion: 0.19
Nodes (12): EncryptedString, current_user(), decode_token(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), optional_user(), require_roles() (+4 more)

### Community 9 - "Base"
Cohesion: 0.11
Nodes (25): AsyncSession, RefreshToken, login(), refresh(), register(), issue_refresh_token(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix() (+17 more)

### Community 10 - "audit"
Cohesion: 0.13
Nodes (24): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+16 more)

### Community 11 - "Session"
Cohesion: 0.12
Nodes (48): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+40 more)

### Community 12 - "Booking"
Cohesion: 0.19
Nodes (16): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+8 more)

### Community 13 - "qt"
Cohesion: 0.16
Nodes (26): an(), at(), Bs(), ct(), dn(), Es(), Et(), fe() (+18 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 15 - "268d55c084cf_add_mobile_number.py"
Cohesion: 0.22
Nodes (5): PlatformFeedback, get_platform_feedback(), Returns all submitted platform feedback ordered by newest first., Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.08
Nodes (23): get_db(), Booking, LawyerProfile, PhonePe webhook with VERIFY- prefix updates LawyerBankAccount, not a Booking., test_phonepe_verify_webhook_routes_correctly(), test_get_booking_by_id(), test_phonepe_webhook_verification(), admin_metrics() (+15 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 19 - "graphify.md"
Cohesion: 0.11
Nodes (13): Base, AuditLog, now(), datetime, UserConsent, WebhookEvent, phonepe_webhook(), stripe_webhook() (+5 more)

### Community 20 - "graphify.md"
Cohesion: 0.08
Nodes (27): check_clock_drift(), NtpStatus, Compare the system clock against the first reachable NTP server.      Returns a, Run CERT-In / DPDP compliant NTP clock drift check., verify_ntp_compliance(), test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, Simulated tiny drift (0.05s) must set within_tolerance=True., GET /api/v1/admin/ntp-status must return 401 without a valid token. (+19 more)

### Community 21 - "__init__.py"
Cohesion: 0.11
Nodes (17): B(), bn(), ge(), ie(), Jn(), me(), N(), ne() (+9 more)

### Community 23 - "er"
Cohesion: 0.20
Nodes (7): create_booking(), Request, get_jitsi_meeting_details(), Return browser-embeddable Jitsi meeting details scoped to a booking., validate_intake(), create_payment_intent(), create_phonepe_payment()

### Community 24 - "models.py"
Cohesion: 0.13
Nodes (15): download_drafting_document(), drafting_document_mock_upload(), drafting_document_presign(), download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign() (+7 more)

### Community 25 - "gn"
Cohesion: 0.09
Nodes (39): a(), Bt(), c(), ce(), d(), de(), ee(), f() (+31 more)

### Community 26 - "_e"
Cohesion: 0.18
Nodes (9): cn(), dr(), _e(), nn(), on(), qe(), un(), ur() (+1 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 30 - "bookings.py"
Cohesion: 0.14
Nodes (11): rate_limit_dependency(), Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting() (+3 more)

### Community 31 - "pdf-annotator.js"
Cohesion: 0.12
Nodes (18): http_exception_handler(), integrity_exception_handler(), lifespan(), Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err, Global Fallback Exception Handler for unexpected server failures (500):     - Pr (+10 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.26
Nodes (5): get_settings(), Request, SlidingWindowRateLimiter, client(), reset_rate_limiter()

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 35 - "reset_users.py"
Cohesion: 0.18
Nodes (7): be(), le(), oe(), qt, re(), te(), Zt()

### Community 36 - "qt"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.21
Nodes (24): Message, Review, User, booking_for_participant(), complete_booking(), confirm_document(), confirm_payment(), create_review() (+16 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid. Simulates, HttpUser

### Community 40 - "sanitize_key"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for LawyerGrid Marketplace. Valid, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 41 - "register"
Cohesion: 0.29
Nodes (6): cr(), er(), hr(), lr(), xn(), Zn()

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 72 - "ntp_time.py"
Cohesion: 0.21
Nodes (11): _get_servers(), ntp_now(), ntp_now_ist(), _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t, Return the current NPL/NIC-sourced time in Indian Standard Time (UTC+5:30)., Send a single NTP client request to *host* and return the transmit     timestamp, Return the ordered list of NTP servers from settings. (+3 more)

### Community 81 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

## Knowledge Gaps
- **59 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `gn` to `mr`, `je`, `daily-js.js`, `register`, `qt`, `__init__.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `data_retention_purge.py` to `booking_service.py`, `main.py`, `ntp_time.py`, `8dcb01bed07f_initial_schema.py`, `graphify.md`, `graphify.md`, `models.py`, `er`, `bookings.py`, `pdf-annotator.js`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `User` connect `booking_service.py` to `main.py`, `o`, `Base`, `8dcb01bed07f_initial_schema.py`, `graphify.md`, `er`, `models.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `audit()` (e.g. with `login()` and `refresh()`) actually correct?**
  _`audit()` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LawyerGrid backend package.`, `Configure structured JSON logging for production or key-value console logging fo`, `HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an` to the rest of the system?**
  _144 weakly-connected nodes found - possible documentation gaps or missing edges._