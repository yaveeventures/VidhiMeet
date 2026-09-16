# Graph Report - VidhiMeet  (2026-09-16)

## Corpus Check
- 119 files · ~195,845 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2065 nodes · 5521 edges · 94 communities (75 shown, 19 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fb8314cd`
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
- N
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
- test_error_handling.py
- deploy_cloudflare_shield.py
- websocket_chat_endpoint
- deploy_rules.sh
- security.py
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
- Settings
- User
- public.py
- LawyerProfileUpdate
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills
- Cashfree Payments — Integration Skills

## God Nodes (most connected - your core abstractions)
1. `User` - 165 edges
2. `Role` - 70 edges
3. `Booking` - 70 edges
4. `LawyerProfile` - 68 edges
5. `audit()` - 64 edges
6. `Practice` - 62 edges
7. `BookingStatus` - 58 edges
8. `DraftingStatus` - 53 edges
9. `ProposalStatus` - 49 edges
10. `create_access_token()` - 44 edges

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

## Communities (94 total, 19 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.25
Nodes (42): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+34 more)

### Community 1 - "mr"
Cohesion: 0.06
Nodes (69): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+61 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (27): EncryptedString, ConnectionManager, _save_ws_message(), websocket_chat_endpoint(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense). (+19 more)

### Community 4 - "app.js"
Cohesion: 0.09
Nodes (51): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+43 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (13): ar(), fn(), ft(), hn(), ir(), J(), kr(), mr (+5 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (47): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, TypedDict, _query_ntp_server() (+39 more)

### Community 7 - "i"
Cohesion: 0.06
Nodes (37): as(), be(), Bt(), ce(), de(), dr(), dt(), Es() (+29 more)

### Community 9 - "User"
Cohesion: 0.07
Nodes (12): B(), bn(), je(), Jn(), N(), sn(), we(), wn() (+4 more)

### Community 10 - "N"
Cohesion: 0.10
Nodes (34): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+26 more)

### Community 11 - "LawyerProfile"
Cohesion: 0.06
Nodes (63): lifespan(), create_access_token(), hash_password(), Hash a raw password using Argon2id (OWASP #1 recommendation)., test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), GET /api/v1/admin/ntp-status must return 200 with the expected keys for an admin, test_admin_ntp_status_endpoint_accessible_by_admin() (+55 more)

### Community 12 - "Booking"
Cohesion: 0.06
Nodes (89): $(), aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, calculateExperience(), calculateProfileCompleteness() (+81 more)

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (33): _auth(), Tests for Cashfree Reverse Penny Drop (RPD) bank account verification.  All test, Polling status before payment returns PENDING / verified=False., Polling status without a verification_id and no account returns 400., Simulating payment via mock-complete marks account verified., After mock-complete, bank account record has real account/IFSC, not PENDING., Mock-complete with no active session returns 400., Polling status after mock-complete returns SUCCESS and account details. (+25 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.07
Nodes (42): get_settings(), rate_limit_dependency(), drafting_document_mock_upload(), drafting_document_presign(), UploadFile, download_lawyer_document(), get_my_profile(), invalidate_lawyers_cache() (+34 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.17
Nodes (25): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+17 more)

### Community 17 - "admin.py"
Cohesion: 0.12
Nodes (38): User, admin_metrics(), force_release_booking_payout(), force_release_draft_payout(), get_admin_payouts(), get_audit_logs(), get_lawyer_verification_dossier(), get_ntp_status() (+30 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.14
Nodes (25): a(), c(), cr(), d(), ee(), er(), f(), gn() (+17 more)

### Community 19 - "_cors_response"
Cohesion: 0.07
Nodes (36): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception (+28 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (67): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), checkSessionExpiryNotice(), _clearReconnectOverlay(), close() (+59 more)

### Community 21 - "config.py"
Cohesion: 0.13
Nodes (26): Ae(), an(), br, ct(), dn(), Et(), fe(), he() (+18 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.07
Nodes (53): a(), be(), Bo(), Bt(), ce(), cr(), de(), dt() (+45 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.14
Nodes (21): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+13 more)

### Community 25 - "models.py"
Cohesion: 0.20
Nodes (7): cn(), _e(), nn(), on(), qe(), un(), ze()

### Community 26 - "_cors_response"
Cohesion: 0.08
Nodes (40): AsyncSession, Base, AuditLog, Message, now(), PasswordResetToken, datetime, RefreshToken (+32 more)

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
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "services.py"
Cohesion: 0.13
Nodes (11): get_db(), FrontendStaticFiles, LawyerProfile, public_stats(), Public endpoint — no auth required. Returns live platform statistics for the hom, StaticFiles, test_google_auth_lawyer_registration(), test_lawyer_complete_booking_duration_restriction() (+3 more)

### Community 37 - "setup"
Cohesion: 0.09
Nodes (51): $(), appPracticeSelect, appSearchInput, appSortSelect, auditLogs, colors, decideVerification(), disputes (+43 more)

### Community 38 - "processEvent"
Cohesion: 0.10
Nodes (14): Ae(), ar(), br, fn(), ft(), hn(), ir(), kr() (+6 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "test_escrow_payout.py"
Cohesion: 0.23
Nodes (16): _call_cashfree_transfer(), get_payout_api_base_url(), get_pending_payouts(), initiate_lawyer_payout(), Any, Session, Cashfree Payouts and Escrow Release Service. Manages automated and administrativ, Dispatches payout to the lawyer for a completed booking or drafting request. (+8 more)

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
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 62 - "Booking"
Cohesion: 0.12
Nodes (31): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+23 more)

### Community 63 - "er"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 64 - "test_error_handling.py"
Cohesion: 0.07
Nodes (20): clean_string(), Trim whitespace and escape HTML control characters to prevent XSS attacks.     R, Sanitize raw user string input without HTML entity encoding to prevent double-es, sanitize_text(), BankAccountUpdate, DraftingRequestCreate, DraftSubmit, MessageCreate (+12 more)

### Community 66 - "websocket_chat_endpoint"
Cohesion: 0.09
Nodes (21): Booking, cashfree_webhook(), Request, Session, Handle Cashfree PG Webhook events (e.g. PAYMENT_SUCCESS_WEBHOOK, ORDER_PAID)., _validate_ws_user_and_booking(), create_cashfree_order(), get_cashfree_order() (+13 more)

### Community 68 - "security.py"
Cohesion: 0.11
Nodes (18): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+10 more)

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
Cohesion: 0.57
Nodes (6): applyAnalyticsConsent(), getSavedConsent(), gtag(), init(), injectDOM(), saveConsent()

### Community 79 - "minify_assets.py"
Cohesion: 0.47
Nodes (5): minify_css(), minify_js(), process_assets(), Minify CSS text by stripping comments and excessive whitespace., Minify JS text while preserving strings and regex literals safely.

### Community 80 - "api-client.min.js"
Cohesion: 0.36
Nodes (12): checkInactivity(), ensureModalElement(), getLimits(), getStoredActiveTime(), hideWarningModal(), isCallImmune(), LexAPI, performLogout() (+4 more)

### Community 86 - "User"
Cohesion: 0.13
Nodes (31): Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment(), create_booking() (+23 more)

### Community 87 - "public.py"
Cohesion: 0.09
Nodes (19): PlatformFeedback, get_validation_rules(), health(), Session, Public endpoint allowing users to submit platform feedback., Public endpoint exposing canonical platform validation rules and constraints, submit_feedback(), BankAccountCreate (+11 more)

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
- **170 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+165 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `admin.py` to `websocket_chat_endpoint`, `services.py`, `security.py`, `lawyer.js`, `main.py`, `test_escrow_payout.py`, `LawyerProfile`, `LawyerGrid`, `check_clock_drift`, `_cors_response`, `User`, `public.py`, `PlatformFeedback`, `_cors_response`, `80394484e25e_add_phonepe_transaction_id.py`, `Booking`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `check_clock_drift()` connect `main.py` to `LawyerProfile`, `admin.py`, `_cors_response`, `LawyerGrid`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `LawyerGrid` to `SlidingWindowRateLimiter`, `websocket_chat_endpoint`, `security.py`, `main.py`, `test_escrow_payout.py`, `LawyerProfile`, `check_clock_drift`, `admin.py`, `_cors_response`, `Settings`, `User`, `_cors_response`, `T`, `Booking`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `LawyerProfile` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`LawyerProfile` has 43 INFERRED edges - model-reasoned connections that need verification._