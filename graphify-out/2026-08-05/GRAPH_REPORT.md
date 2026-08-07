# Graph Report - LawyerGrid  (2026-08-05)

## Corpus Check
- 67 files · ~69,489 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 994 nodes · 2500 edges · 71 communities (42 shown, 29 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 498 edges (avg confidence: 0.63)
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
- 268d55c084cf_add_mobile_number.py
- check_clock_drift
- 8dcb01bed07f_initial_schema.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- graphify.md
- graphify.md
- __init__.py
- er
- models.py
- gn
- _e
- T
- 80394484e25e_add_phonepe_transaction_id.py
- test_drafting.py
- pdf-annotator.js
- data_retention_purge.py
- NTP Time Synchronization — Compliance Runbook
- gn
- qt
- firebase-phone-auth.js
- ntp_sync_check.py
- Booking
- sanitize_key
- ui-components.js
- public.py
- Settings
- graphify
- graphify.md
- __init__.py
- Request
- datetime
- Request
- Session
- Request
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
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 50 edges
2. `audit()` - 42 edges
3. `LexAPI` - 41 edges
4. `je()` - 39 edges
5. `Practice` - 36 edges
6. `Role` - 35 edges
7. `BookingStatus` - 34 edges
8. `i()` - 34 edges
9. `DraftingStatus` - 33 edges
10. `ProposalStatus` - 33 edges

## Surprising Connections (you probably didn't know these)
- `reset_rate_limiter()` --calls--> `get_settings()`  [INFERRED]
  tests/conftest.py → backend/config.py
- `run_purge()` --calls--> `get_settings()`  [INFERRED]
  scripts/data_retention_purge.py → backend/config.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_settings()`  [INFERRED]
  tests/test_bank_account.py → backend/config.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_db()`  [INFERRED]
  tests/test_bank_account.py → backend/db.py
- `test_7day_auto_approval_window()` --calls--> `get_db()`  [INFERRED]
  tests/test_drafting.py → backend/db.py

## Import Cycles
- None detected.

## Communities (71 total, 29 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (58): $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn, chatKeys (+50 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (36): as(), Bt(), de(), dr(), dt(), ee(), g(), h() (+28 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (61): checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay() (+53 more)

### Community 4 - "app.js"
Cohesion: 0.14
Nodes (8): Ae(), ar(), br, fn(), ir(), mr, pr(), Wt()

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (40): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+32 more)

### Community 6 - "main.py"
Cohesion: 0.06
Nodes (41): Message, Review, booking_for_participant(), complete_booking(), confirm_document(), confirm_payment(), create_review(), dispute_booking() (+33 more)

### Community 7 - "i"
Cohesion: 0.08
Nodes (4): B(), je(), we(), xe()

### Community 9 - "Base"
Cohesion: 0.11
Nodes (26): create_access_token(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), hash_password(), require_roles(), register(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then (+18 more)

### Community 10 - "audit"
Cohesion: 0.16
Nodes (20): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+12 more)

### Community 11 - "Session"
Cohesion: 0.09
Nodes (54): BookingStatus, DraftingStatus, EncryptedString, PlatformFeedback, Practice, ProposalStatus, str, Role (+46 more)

### Community 12 - "T"
Cohesion: 0.13
Nodes (19): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+11 more)

### Community 13 - "qt"
Cohesion: 0.12
Nodes (32): at(), Bs(), ct(), dn(), Es(), Et(), fe(), ft() (+24 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 15 - "268d55c084cf_add_mobile_number.py"
Cohesion: 0.19
Nodes (16): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+8 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.18
Nodes (24): AuditLog, User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes() (+16 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 19 - "graphify.md"
Cohesion: 0.11
Nodes (15): Booking, now(), datetime, UserConsent, WebhookEvent, get_db(), phonepe_webhook(), stripe_webhook() (+7 more)

### Community 20 - "graphify.md"
Cohesion: 0.09
Nodes (21): test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, Simulated tiny drift (0.05s) must set within_tolerance=True., GET /api/v1/admin/ntp-status must return 401 without a valid token., ntp_now() must always return a UTC-aware datetime regardless of server state., ntp_now_ist() must return a datetime in IST (UTC+05:30)., When all NTP servers are unreachable, ntp_now() must fall back to system clock g, check_clock_drift() must return a dict with all required NtpStatus keys., within_tolerance must be a boolean. (+13 more)

### Community 23 - "er"
Cohesion: 0.09
Nodes (26): get_settings(), check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+18 more)

### Community 24 - "models.py"
Cohesion: 0.23
Nodes (16): Bo(), Ds(), ea(), Fo(), Fs(), Go(), Ho(), Ko() (+8 more)

### Community 25 - "gn"
Cohesion: 0.19
Nodes (24): a(), c(), ce(), cr(), d(), er(), f(), gn() (+16 more)

### Community 26 - "_e"
Cohesion: 0.18
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 31 - "pdf-annotator.js"
Cohesion: 0.13
Nodes (12): AsyncSession, RefreshToken, verify_password(), Configure structured JSON logging for production or key-value console logging fo, setup_logging(), lifespan(), rate_limit_dependency(), login() (+4 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.25
Nodes (6): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_rate_limiting(), test_disabled_rate_limiter_setting(), test_ip_abuse_lockout()

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "gn"
Cohesion: 0.33
Nodes (4): In(), q(), setupOnce(), W()

### Community 36 - "qt"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid. Simulates, HttpUser

### Community 40 - "sanitize_key"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for LawyerGrid Marketplace. Valid, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 45 - "public.py"
Cohesion: 0.16
Nodes (16): LawyerProfile, health(), public_stats(), Session, Public endpoint — no auth required. Returns live platform statistics for the hom, current_user(), decode_token(), optional_user() (+8 more)

## Knowledge Gaps
- **58 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `gn` to `mr`, `je`, `daily-js.js`, `T`, `qt`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `lawyer.js` to `mr`, `T`, `daily-js.js`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `p()` connect `gn` to `je`, `lawyer.js`, `app.js`, `qt`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `User` (e.g. with `Base` and `public_stats()`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `audit()` (e.g. with `login()` and `refresh()`) actually correct?**
  _`audit()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LawyerGrid backend package.`, `Configure structured JSON logging for production or key-value console logging fo`, `One-per-lawyer bank account for payout and UPI identity verification.` to the rest of the system?**
  _134 weakly-connected nodes found - possible documentation gaps or missing edges._