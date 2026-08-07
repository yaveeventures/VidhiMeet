# Graph Report - New project  (2026-07-31)

## Corpus Check
- 65 files · ~64,410 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 957 nodes · 2791 edges · 48 communities (40 shown, 8 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 354 edges (avg confidence: 0.58)
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
- T
- qt
- LawyerGrid
- check_clock_drift
- graphify.md
- graphify.md
- __init__.py
- Booking
- er
- models.py
- processEvent
- _e
- money
- T
- test_drafting.py
- pdf-annotator.js
- data_retention_purge.py
- NTP Time Synchronization — Compliance Runbook
- gn
- SlidingWindowRateLimiter
- qt
- firebase-phone-auth.js
- ntp_sync_check.py
- Booking
- br
- er
- ui-components.js
- .must_be_adult
- public.py
- test_auth_rate_limiting
- test_ip_abuse_lockout

## God Nodes (most connected - your core abstractions)
1. `User` - 106 edges
2. `audit()` - 52 edges
3. `Role` - 44 edges
4. `Practice` - 42 edges
5. `LexAPI` - 41 edges
6. `je()` - 39 edges
7. `Booking` - 37 edges
8. `LawyerProfile` - 36 edges
9. `BookingStatus` - 35 edges
10. `i()` - 34 edges

## Surprising Connections (you probably didn't know these)
- `test_lawyer_complete_booking_duration_restriction()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_meeting_token_endpoint()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_verified_reviews_only()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_phonepe_verify_webhook_routes_correctly()` --indirect_call--> `User`  [INFERRED]
  tests/test_bank_account.py → backend/models.py
- `test_dpdpa_consent_enforcement_and_logging()` --indirect_call--> `User`  [INFERRED]
  tests/test_compliance.py → backend/models.py

## Import Cycles
- None detected.

## Communities (48 total, 8 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.11
Nodes (17): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., PhonePe webhook with VERIFY- prefix updates LawyerBankAccount, not a Booking., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response. (+9 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (62): $(), checkAdminSession(), checkInactivity(), LexAPI, openChatModal(), LexE2EE, aadhaarFileEl, barLicenceFileEl (+54 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (47): as(), be(), Bt(), ce(), cr(), d(), de(), dt() (+39 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (53): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay(), close(), content (+45 more)

### Community 4 - "app.js"
Cohesion: 0.12
Nodes (10): Ae(), ar(), br, fn(), ir(), mr, pr(), q() (+2 more)

### Community 5 - "daily-js.js"
Cohesion: 0.13
Nodes (35): $(), auditLogs, colors, decideVerification(), disputes, draftingTransactions, escapeHtml(), handleSaveFees() (+27 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (16): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+8 more)

### Community 9 - "Base"
Cohesion: 0.14
Nodes (20): rate_limit_dependency(), download_drafting_document(), drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload() (+12 more)

### Community 10 - "audit"
Cohesion: 0.18
Nodes (23): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+15 more)

### Community 11 - "Session"
Cohesion: 0.23
Nodes (16): Bo(), Ds(), ea(), Fo(), Fs(), Go(), Ho(), Ko() (+8 more)

### Community 12 - "T"
Cohesion: 0.20
Nodes (12): bn(), ge(), ie(), me(), ne(), qn(), sn(), ue() (+4 more)

### Community 13 - "qt"
Cohesion: 0.15
Nodes (26): at(), Bs(), ct(), dn(), Es(), Et(), fe(), ft() (+18 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 22 - "Booking"
Cohesion: 0.23
Nodes (14): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+6 more)

### Community 23 - "er"
Cohesion: 0.09
Nodes (21): test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, Simulated tiny drift (0.05s) must set within_tolerance=True., GET /api/v1/admin/ntp-status must return 401 without a valid token., ntp_now() must always return a UTC-aware datetime regardless of server state., ntp_now_ist() must return a datetime in IST (UTC+05:30)., When all NTP servers are unreachable, ntp_now() must fall back to system clock g, check_clock_drift() must return a dict with all required NtpStatus keys., within_tolerance must be a boolean. (+13 more)

### Community 24 - "models.py"
Cohesion: 0.09
Nodes (57): Base, BookingStatus, DraftingStatus, EncryptedString, Practice, ProposalStatus, RefreshToken, Role (+49 more)

### Community 25 - "processEvent"
Cohesion: 0.12
Nodes (8): get_settings(), reset_rate_limiter(), Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_rate_limiting(), test_disabled_rate_limiter_setting(), test_ip_abuse_lockout()

### Community 26 - "_e"
Cohesion: 0.16
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 27 - "money"
Cohesion: 0.14
Nodes (23): AsyncSession, login(), Session, register(), create_access_token(), hash_password(), verify_password(), issue_refresh_token() (+15 more)

### Community 30 - "test_drafting.py"
Cohesion: 0.18
Nodes (4): B(), qt, re(), we()

### Community 31 - "pdf-annotator.js"
Cohesion: 0.16
Nodes (12): get_db(), AuditLog, LawyerProfile, UserConsent, request_erasure(), test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only() (+4 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.08
Nodes (49): Booking, Message, now(), datetime, Review, booking_for_participant(), complete_booking(), confirm_document() (+41 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 34 - "gn"
Cohesion: 0.14
Nodes (27): a(), c(), f(), gn(), gt(), h(), hn(), is() (+19 more)

### Community 36 - "qt"
Cohesion: 0.22
Nodes (20): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), list_disputes(), list_drafting_transactions(), list_pending_lawyers() (+12 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "ntp_sync_check.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): HttpUser, MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid. Simulates

### Community 40 - "br"
Cohesion: 0.24
Nodes (15): changePage(), changeZoom(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt(), renderAnnotatorModalContent(), renderCommentsList() (+7 more)

### Community 42 - "er"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for LawyerGrid Marketplace. Valid, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 44 - ".must_be_adult"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 45 - "public.py"
Cohesion: 0.18
Nodes (10): Configure structured JSON logging for production or key-value console logging fo, setup_logging(), lifespan(), Request, security_headers_and_rate_limit(), health(), public_stats(), Session (+2 more)

### Community 46 - "test_auth_rate_limiting"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 47 - "test_ip_abuse_lockout"
Cohesion: 0.60
Nodes (4): phonepe_webhook(), Request, Session, stripe_webhook()

## Knowledge Gaps
- **57 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `qt` to `data_retention_purge.py`, `main.py`, `main.py`, `Base`, `audit`, `.must_be_adult`, `public.py`, `test_auth_rate_limiting`, `er`, `models.py`, `processEvent`, `money`, `pdf-annotator.js`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `s()` connect `gn` to `mr`, `je`, `daily-js.js`, `T`, `qt`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `mr` to `br`, `lawyer.js`, `daily-js.js`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 28 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LawyerGrid backend package.`, `Configure structured JSON logging for production or key-value console logging fo`, `One-per-lawyer bank account for payout and UPI identity verification.` to the rest of the system?**
  _130 weakly-connected nodes found - possible documentation gaps or missing edges._