# Graph Report - LawyerGrid  (2026-08-07)

## Corpus Check
- 71 files · ~74,804 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1056 nodes · 2710 edges · 70 communities (43 shown, 27 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 528 edges (avg confidence: 0.63)
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
- main.py
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
- Session
- Session
- Request
- Session
- Request
- Session
- UploadFile
- Session
- UploadFile
- Request
- Session
- Session
- Session
- datetime
- Session
- test_error_handling.py
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 63 edges
2. `audit()` - 45 edges
3. `Practice` - 43 edges
4. `LexAPI` - 42 edges
5. `BookingStatus` - 40 edges
6. `Booking` - 40 edges
7. `Role` - 39 edges
8. `je()` - 39 edges
9. `DraftingStatus` - 37 edges
10. `ProposalStatus` - 37 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_settings()`  [INFERRED]
  tests/test_bank_account.py → backend/config.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_db()`  [INFERRED]
  tests/test_bank_account.py → backend/db.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `test_phonepe_verify_webhook_routes_correctly()` --indirect_call--> `User`  [INFERRED]
  tests/test_bank_account.py → backend/models.py

## Import Cycles
- None detected.

## Communities (70 total, 27 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (59): $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn, chatKeys (+51 more)

### Community 2 - "je"
Cohesion: 0.13
Nodes (26): Bo(), Ds(), ea(), Fo(), Fs(), Go(), h(), Ho() (+18 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (63): checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay() (+55 more)

### Community 4 - "app.js"
Cohesion: 0.10
Nodes (18): ar(), fn(), ft(), hn(), ht(), ir(), J(), Kn() (+10 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (41): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+33 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 8 - "o"
Cohesion: 0.21
Nodes (11): EncryptedString, current_user(), decode_token(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), optional_user(), require_roles() (+3 more)

### Community 9 - "Base"
Cohesion: 0.14
Nodes (19): test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s)., Verify that drafting document presign returns 15-minute expiry (900s)., Verify that a document access token issued > 15 minutes ago (900s) is rejected w, test_booking_document_presign_expiry(), test_drafting_document_presign_expiry(), test_expired_document_access_link_rejection() (+11 more)

### Community 10 - "audit"
Cohesion: 0.16
Nodes (20): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+12 more)

### Community 11 - "Session"
Cohesion: 0.10
Nodes (57): BookingStatus, DraftingStatus, PlatformFeedback, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut (+49 more)

### Community 12 - "Booking"
Cohesion: 0.08
Nodes (32): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+24 more)

### Community 13 - "qt"
Cohesion: 0.05
Nodes (48): as(), be(), Bt(), ct(), dr(), dt(), fe(), g() (+40 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.08
Nodes (30): LawyerProfile, download_drafting_document(), drafting_document_mock_upload(), drafting_document_presign(), download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload() (+22 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.09
Nodes (13): get_db(), Booking, WebhookEvent, phonepe_webhook(), stripe_webhook(), test_get_booking_by_id(), test_phonepe_webhook_verification(), list_disputes() (+5 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 19 - "graphify.md"
Cohesion: 0.11
Nodes (18): AsyncSession, Base, AuditLog, Message, now(), datetime, RefreshToken, UserConsent (+10 more)

### Community 20 - "graphify.md"
Cohesion: 0.06
Nodes (48): Voucher, check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server() (+40 more)

### Community 21 - "__init__.py"
Cohesion: 0.18
Nodes (9): B(), bn(), Jn(), N(), sn(), we(), wn(), xe() (+1 more)

### Community 23 - "er"
Cohesion: 0.18
Nodes (18): create_booking(), Request, calculate_cancellation_policy(), get_daily_meeting_details(), get_jitsi_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, Return browser-embeddable Jitsi meeting details scoped to a booking. (+10 more)

### Community 24 - "models.py"
Cohesion: 0.15
Nodes (4): get_settings(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then, client(), reset_rate_limiter()

### Community 25 - "gn"
Cohesion: 0.23
Nodes (21): a(), c(), ce(), d(), de(), f(), gn(), gt() (+13 more)

### Community 26 - "_e"
Cohesion: 0.18
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 30 - "bookings.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 31 - "pdf-annotator.js"
Cohesion: 0.14
Nodes (14): http_exception_handler(), integrity_exception_handler(), Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err, Global Fallback Exception Handler for unexpected server failures (500):     - Pr, security_headers_and_rate_limit() (+6 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "main.py"
Cohesion: 0.21
Nodes (5): lifespan(), rate_limit_dependency(), Configure structured JSON logging for production or key-value console logging fo, setup_logging(), FastAPI

### Community 36 - "qt"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.30
Nodes (19): Review, User, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+11 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid. Simulates, HttpUser

### Community 40 - "sanitize_key"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for LawyerGrid Marketplace. Valid, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 41 - "register"
Cohesion: 0.12
Nodes (20): Ae(), at(), br, Bs(), cr(), dn(), ee(), er() (+12 more)

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 81 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

## Knowledge Gaps
- **59 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `gn` to `mr`, `app.js`, `daily-js.js`, `register`, `qt`, `__init__.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `User` connect `booking_service.py` to `main.py`, `o`, `Base`, `Booking`, `LawyerGrid`, `8dcb01bed07f_initial_schema.py`, `graphify.md`, `graphify.md`, `er`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `lawyer.js` to `mr`, `T`, `daily-js.js`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `audit()` (e.g. with `login()` and `refresh()`) actually correct?**
  _`audit()` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `BookingStatus` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`BookingStatus` has 34 INFERRED edges - model-reasoned connections that need verification._