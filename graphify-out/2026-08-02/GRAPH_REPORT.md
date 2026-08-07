# Graph Report - New project  (2026-08-02)

## Corpus Check
- 67 files · ~67,420 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 975 nodes · 2878 edges · 47 communities (38 shown, 9 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.58)
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
- er
- ui-components.js
- .must_be_adult
- public.py
- test_auth_rate_limiting
- conftest.py

## God Nodes (most connected - your core abstractions)
1. `User` - 110 edges
2. `audit()` - 52 edges
3. `Role` - 47 edges
4. `Practice` - 44 edges
5. `Booking` - 42 edges
6. `LexAPI` - 42 edges
7. `LawyerProfile` - 41 edges
8. `BookingStatus` - 39 edges
9. `je()` - 39 edges
10. `i()` - 34 edges

## Surprising Connections (you probably didn't know these)
- `reset_rate_limiter()` --calls--> `get_settings()`  [EXTRACTED]
  tests/conftest.py → backend/config.py
- `test_lawyer_complete_booking_duration_restriction()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_meeting_token_endpoint()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_verified_reviews_only()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_phonepe_verify_webhook_routes_correctly()` --indirect_call--> `User`  [INFERRED]
  tests/test_bank_account.py → backend/models.py

## Import Cycles
- None detected.

## Communities (47 total, 9 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.09
Nodes (32): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+24 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (56): $(), openChatModal(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn (+48 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (48): as(), Bo(), Bt(), Ds(), dt(), ea(), Fo(), Fs() (+40 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (57): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay(), close(), content (+49 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (22): ar(), ce(), de(), fn(), ft(), hn(), ht(), ir() (+14 more)

### Community 5 - "daily-js.js"
Cohesion: 0.08
Nodes (55): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+47 more)

### Community 6 - "main.py"
Cohesion: 0.16
Nodes (20): create_access_token(), hash_password(), TestClient, Session, test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s)., Verify that drafting document presign returns 15-minute expiry (900s). (+12 more)

### Community 9 - "Base"
Cohesion: 0.11
Nodes (21): get_db(), LawyerProfile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign(), lawyers() (+13 more)

### Community 10 - "audit"
Cohesion: 0.18
Nodes (24): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+16 more)

### Community 12 - "T"
Cohesion: 0.12
Nodes (20): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+12 more)

### Community 13 - "qt"
Cohesion: 0.16
Nodes (26): an(), at(), Bs(), ct(), dn(), Es(), Et(), fe() (+18 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 22 - "Booking"
Cohesion: 0.13
Nodes (22): get_settings(), rate_limit_dependency(), create_booking(), Request, get_daily_meeting_details(), get_jitsi_meeting_details(), Return browser-embeddable Jitsi meeting details scoped to a booking., validate_intake() (+14 more)

### Community 23 - "er"
Cohesion: 0.06
Nodes (39): Settings, check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server() (+31 more)

### Community 24 - "models.py"
Cohesion: 0.10
Nodes (51): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, Sanitize a filename by removing directory traversal patterns, null bytes,     an, Sanitize object storage keys to prevent path traversal.     Ensures relative key (+43 more)

### Community 25 - "processEvent"
Cohesion: 0.15
Nodes (11): Base, EncryptedString, Message, WebhookEvent, decrypt_field(), encrypt_field(), _get_fernet_cipher(), DeclarativeBase (+3 more)

### Community 26 - "_e"
Cohesion: 0.18
Nodes (9): cn(), dr(), _e(), nn(), on(), qe(), un(), ur() (+1 more)

### Community 27 - "money"
Cohesion: 0.20
Nodes (17): Review, _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents() (+9 more)

### Community 28 - "T"
Cohesion: 0.50
Nodes (4): health(), public_stats(), Session, Public endpoint — no auth required. Returns live platform statistics for the hom

### Community 30 - "test_drafting.py"
Cohesion: 0.12
Nodes (8): Ae(), B(), br, ee(), qt, re(), we(), yr()

### Community 31 - "pdf-annotator.js"
Cohesion: 0.19
Nodes (10): Configure structured JSON logging for production or key-value console logging fo, setup_logging(), lifespan(), Request, security_headers_and_rate_limit(), phonepe_webhook(), Request, Session (+2 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.32
Nodes (18): User, booking_for_participant(), complete_booking(), confirm_document(), confirm_payment(), create_review(), dispute_booking(), document_upload() (+10 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 34 - "gn"
Cohesion: 0.18
Nodes (25): a(), c(), cr(), d(), er(), f(), gn(), gt() (+17 more)

### Community 36 - "qt"
Cohesion: 0.14
Nodes (20): Booking, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), list_disputes(), list_drafting_transactions(), list_pending_lawyers() (+12 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "ntp_sync_check.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): HttpUser, MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid. Simulates

### Community 42 - "er"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for LawyerGrid Marketplace. Valid, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 44 - ".must_be_adult"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 45 - "public.py"
Cohesion: 0.24
Nodes (14): AsyncSession, AuditLog, RefreshToken, UserConsent, login(), Session, refresh(), register() (+6 more)

### Community 46 - "test_auth_rate_limiting"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

## Knowledge Gaps
- **57 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `data_retention_purge.py` to `main.py`, `qt`, `main.py`, `Base`, `audit`, `.must_be_adult`, `public.py`, `test_auth_rate_limiting`, `Booking`, `er`, `processEvent`, `T`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `s()` connect `gn` to `mr`, `je`, `app.js`, `daily-js.js`, `T`, `qt`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `daily-js.js` to `mr`, `gn`, `lawyer.js`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 10 INFERRED edges - model-reasoned connections that need verification._