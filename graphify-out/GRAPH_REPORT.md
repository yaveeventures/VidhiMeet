# Graph Report - VidhiMeet  (2026-08-09)

## Corpus Check
- 82 files · ~96,752 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1200 nodes · 3238 edges · 77 communities (58 shown, 19 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca2b29ac`
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
- PlatformFeedback
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
- websocket_chat_endpoint
- firebase-phone-auth.js
- booking_service.py
- Booking
- verify_ntp_compliance
- register
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- LawyerProfile
- graphify
- graphify.md
- test_marketplace.py
- Session
- LawyerBankAccount
- Session
- env.py
- LexAPI
- __init__.py
- loadMessages
- reset_users.py
- Request
- Session
- processEvent
- toast
- Request
- Session
- datetime
- Session
- Session
- datetime
- Session
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 117 edges
2. `Role` - 51 edges
3. `Practice` - 51 edges
4. `Booking` - 51 edges
5. `audit()` - 51 edges
6. `BookingStatus` - 46 edges
7. `LexAPI` - 46 edges
8. `LawyerProfile` - 42 edges
9. `DraftingStatus` - 42 edges
10. `ProposalStatus` - 42 edges

## Surprising Connections (you probably didn't know these)
- `test_video_consultation_dual_platform_fee()` --calls--> `Booking`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `run_purge()` --calls--> `get_settings()`  [INFERRED]
  scripts/data_retention_purge.py → backend/config.py
- `test_phonepe_verify_webhook_routes_correctly()` --calls--> `get_db()`  [INFERRED]
  tests/test_bank_account.py → backend/db.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py

## Import Cycles
- None detected.

## Communities (77 total, 19 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.19
Nodes (7): be(), le(), oe(), qt, re(), te(), Zt()

### Community 1 - "mr"
Cohesion: 0.10
Nodes (24): aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, chatBackBtn, chatKeys, closeDraftingModal() (+16 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (50): as(), at(), Bo(), Bs(), Bt(), Ds(), ea(), ee() (+42 more)

### Community 3 - "lawyer.js"
Cohesion: 0.09
Nodes (38): backdrop, booking, bookingView(), content, darken(), escapeHtml(), getColorForName(), getIntakeKeys() (+30 more)

### Community 4 - "app.js"
Cohesion: 0.11
Nodes (14): ar(), fn(), hn(), ir(), Kn(), kr(), mr, pr() (+6 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (35): $(), auditLogs, colors, disputes, draftingTransactions, escapeHtml(), lawyerMap, mapPracticeToFrontend() (+27 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 8 - "processEvent"
Cohesion: 0.16
Nodes (26): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+18 more)

### Community 9 - "User"
Cohesion: 0.12
Nodes (33): Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment(), create_booking() (+25 more)

### Community 10 - "audit"
Cohesion: 0.11
Nodes (56): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+48 more)

### Community 11 - "toast"
Cohesion: 0.13
Nodes (9): lifespan(), rate_limit_dependency(), PhonePe webhook with VERIFY- prefix updates LawyerBankAccount, not a Booking., test_phonepe_verify_webhook_routes_correctly(), get_settings(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then, FastAPI, client() (+1 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.13
Nodes (15): get_db(), Booking, WebhookEvent, phonepe_webhook(), Request, Session, stripe_webhook(), _validate_ws_user_and_booking() (+7 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.18
Nodes (24): a(), c(), cr(), d(), er(), f(), gn(), gt() (+16 more)

### Community 19 - "graphify.md"
Cohesion: 0.11
Nodes (27): AsyncSession, Base, AuditLog, Message, now(), datetime, RefreshToken, Review (+19 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (37): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+29 more)

### Community 22 - "ClientRouter"
Cohesion: 0.22
Nodes (5): PlatformFeedback, public_stats(), Public endpoint — no auth required. Returns live platform statistics for the hom, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 23 - "er"
Cohesion: 0.19
Nodes (23): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes(), list_drafting_transactions() (+15 more)

### Community 25 - "LawyerBankAccount"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 26 - "_e"
Cohesion: 0.16
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

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

### Community 35 - "websocket_chat_endpoint"
Cohesion: 0.17
Nodes (24): _attemptReconnect(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal(), downloadBookingIcs(), isRoomActive(), joinMeeting() (+16 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.08
Nodes (39): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), create_access_token(), current_user(), decode_token() (+31 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.12
Nodes (17): B(), bn(), ge(), ie(), Jn(), me(), N(), ne() (+9 more)

### Community 41 - "register"
Cohesion: 0.15
Nodes (19): Ae(), br, ct(), dn(), Et(), fe(), i(), In() (+11 more)

### Community 42 - "README.md"
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 44 - "test_marketplace.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 47 - "LawyerProfile"
Cohesion: 0.15
Nodes (18): LawyerProfile, drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign() (+10 more)

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 54 - "Session"
Cohesion: 0.18
Nodes (17): $(), calculateExperience(), checkLawyerSession(), closeCall(), initIcalPanel(), initLanguageSuggestions(), initLawyerAuth(), joinRoom() (+9 more)

### Community 55 - "LawyerBankAccount"
Cohesion: 0.23
Nodes (14): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., create_phonepe_verification_payment(), add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification() (+6 more)

### Community 57 - "env.py"
Cohesion: 0.14
Nodes (14): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), Verify structlog processor scrubs sensitive PII fields and credentials from log, Verify scan_document_payload rejects PDF files containing embedded JavaScript tr (+6 more)

### Community 58 - "LexAPI"
Cohesion: 0.24
Nodes (11): checkAdminSession(), decideVerification(), handleSaveFees(), loadData(), doAdminLogin(), resolveDispute(), toast(), toggleUserStatus() (+3 more)

### Community 60 - "loadMessages"
Cohesion: 0.27
Nodes (11): openChatModal(), LexE2EE, getChatKey(), getSpecialty(), initRealtimeSync(), loadMessages(), NotificationsManager, renderThreads() (+3 more)

### Community 61 - "reset_users.py"
Cohesion: 0.11
Nodes (20): EncryptedString, ConnectionManager, _save_ws_message(), websocket_chat_endpoint(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense). (+12 more)

### Community 64 - "processEvent"
Cohesion: 0.20
Nodes (10): ce(), de(), dt(), ft(), ht(), J(), ke(), processEvent() (+2 more)

### Community 65 - "toast"
Cohesion: 0.27
Nodes (11): k(), confirmDeleteBankAccount(), handleBankFormSubmit(), handleFileUpload(), handleSaveProfile(), initiateUpiVerification(), loadData(), mapPracticeToBackend() (+3 more)

### Community 67 - "Session"
Cohesion: 0.36
Nodes (10): escapeHtml(), isRoomActive(), loadDraftingPortal(), money(), openUpiVerifyModal(), parseUTCDate(), renderActivity(), renderEarnings() (+2 more)

## Knowledge Gaps
- **66 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `er` to `booking_service.py`, `processEvent`, `User`, `README.md`, `toast`, `LawyerGrid`, `LawyerProfile`, `calendar.py`, `graphify.md`, `ClientRouter`, `env.py`, `reset_users.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `s()` connect `9d0be6640444_add_aadhaar_and_profile_picture.py` to `toast`, `je`, `app.js`, `daily-js.js`, `verify_ntp_compliance`, `register`, `Session`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `LexAPI` to `toast`, `mr`, `lawyer.js`, `websocket_chat_endpoint`, `daily-js.js`, `Session`, `T`, `Session`, `loadMessages`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Booking` (e.g. with `Base` and `admin_metrics()`) actually correct?**
  _`Booking` has 18 INFERRED edges - model-reasoned connections that need verification._