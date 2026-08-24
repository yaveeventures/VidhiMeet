# Graph Report - VidhiMeet  (2026-08-22)

## Corpus Check
- 85 files · ~100,527 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1228 nodes · 3512 edges · 71 communities (57 shown, 14 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 545 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4a564567`
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
- toast
- ntp_now
- config.py
- calendar.py
- er
- PlatformFeedback
- models.py
- _e
- test_rate_limiter.py
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- Request
- Settings
- NTP Time Synchronization — Compliance Runbook
- SlidingWindowRateLimiter
- setup_domain_ssl.sh
- LexAPI
- setup
- toast
- Booking
- verify_ntp_compliance
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- test_auth_rate_limiting
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
- Session
- loadMessages
- processEvent
- escapeHtml
- test_password_reset.py
- websocket_chat_endpoint
- sanitize_key
- Zt
- conftest.py

## God Nodes (most connected - your core abstractions)
1. `User` - 135 edges
2. `Role` - 57 edges
3. `audit()` - 56 edges
4. `Practice` - 53 edges
5. `LexAPI` - 52 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 42 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `reset_rate_limiter()` --calls--> `get_settings()`  [EXTRACTED]
  tests/conftest.py → backend/config.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py

## Import Cycles
- None detected.

## Communities (71 total, 14 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.07
Nodes (82): AsyncSession, Base, BookingStatus, DraftingStatus, PasswordResetToken, Practice, ProposalStatus, str (+74 more)

### Community 1 - "mr"
Cohesion: 0.09
Nodes (40): backdrop, booking, bookingView(), content, darken(), escapeHtml(), getColorForName(), getIntakeKeys() (+32 more)

### Community 2 - "je"
Cohesion: 0.09
Nodes (29): aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings, chatBackBtn, chatKeys, closeDraftingModal() (+21 more)

### Community 3 - "lawyer.js"
Cohesion: 0.07
Nodes (43): as(), at(), Bo(), Bs(), Ds(), ea(), Es(), Fo() (+35 more)

### Community 4 - "app.js"
Cohesion: 0.12
Nodes (35): $(), auditLogs, colors, disputes, draftingTransactions, escapeHtml(), lawyerMap, mapPracticeToFrontend() (+27 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (13): ar(), fn(), hn(), ir(), kr(), mr, pr(), preprocessEvent() (+5 more)

### Community 6 - "main.py"
Cohesion: 0.06
Nodes (47): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+39 more)

### Community 7 - "i"
Cohesion: 0.10
Nodes (29): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s). (+21 more)

### Community 8 - "processEvent"
Cohesion: 0.12
Nodes (39): get_db(), AuditLog, LawyerProfile, User, UserConsent, admin_metrics(), get_admin_payouts(), get_audit_logs() (+31 more)

### Community 10 - "audit"
Cohesion: 0.17
Nodes (24): _attemptReconnect(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal(), downloadBookingIcs(), isRoomActive(), _launchClientDaily() (+16 more)

### Community 11 - "toast"
Cohesion: 0.18
Nodes (27): DraftComment, DraftingProposal, DraftingRequest, enable_mfa(), Verify TOTP code and enable 2FA on the account., accept_drafting_proposal(), accept_drafting_request(), add_draft_comment() (+19 more)

### Community 12 - "Booking"
Cohesion: 0.13
Nodes (17): EncryptedString, _save_ws_message(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense)., validate_participant_access(), Fernet (+9 more)

### Community 13 - "sanitize_key"
Cohesion: 0.10
Nodes (18): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), lifespan(), drafting_document_mock_upload(), UploadFile, Perform deep structural payload inspection on document uploads.     Detects embe (+10 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.10
Nodes (30): get_settings(), rate_limit_dependency(), Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document(), lawyer_document_presign(), calculate_cancellation_policy(), get_daily_meeting_details() (+22 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.09
Nodes (3): Booking, _validate_ws_user_and_booking(), test_video_consultation_dual_platform_fee()

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.16
Nodes (24): Message, Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+16 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.12
Nodes (29): a(), B(), bn(), c(), d(), f(), ge(), gn() (+21 more)

### Community 19 - "toast"
Cohesion: 0.29
Nodes (6): cr(), er(), hr(), lr(), xn(), Zn()

### Community 21 - "config.py"
Cohesion: 0.15
Nodes (21): Ae(), br, ct(), dn(), Et(), fe(), gt(), i() (+13 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "er"
Cohesion: 0.19
Nodes (17): $(), calculateExperience(), checkLawyerSession(), closeCall(), initIcalPanel(), initLanguageSuggestions(), initLawyerAuth(), joinRoom() (+9 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.13
Nodes (23): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+15 more)

### Community 25 - "models.py"
Cohesion: 0.16
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 26 - "_e"
Cohesion: 0.25
Nodes (15): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+7 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 30 - "bookings.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 31 - "Request"
Cohesion: 0.22
Nodes (15): _cors_response(), http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err (+7 more)

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.16
Nodes (6): Settings, Exception, Request, RedisError, SlidingWindowRateLimiter, BaseSettings

### Community 35 - "setup_domain_ssl.sh"
Cohesion: 0.11
Nodes (13): now(), datetime, WebhookEvent, authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream() (+5 more)

### Community 36 - "LexAPI"
Cohesion: 0.24
Nodes (11): checkAdminSession(), decideVerification(), handleSaveFees(), loadData(), doAdminLogin(), resolveDispute(), toast(), toggleUserStatus() (+3 more)

### Community 37 - "setup"
Cohesion: 0.15
Nodes (13): Bt(), ee(), In(), Jn(), Kn(), Mn(), mt(), q() (+5 more)

### Community 38 - "toast"
Cohesion: 0.35
Nodes (11): k(), handleFileUpload(), handleSaveProfile(), initRealtimeSync(), loadData(), mapPracticeToBackend(), NotificationsManager, showUploadProgressModal() (+3 more)

### Community 39 - "Booking"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 41 - "SSEClient"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 42 - "README.md"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 43 - "ui-components.js"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 45 - "cookie-consent.js"
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 46 - "test_auth_rate_limiting"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 63 - "loadMessages"
Cohesion: 0.33
Nodes (9): openChatModal(), LexE2EE, getChatKey(), getSpecialty(), loadMessages(), renderThreads(), selectThread(), sendChatMessage() (+1 more)

### Community 64 - "processEvent"
Cohesion: 0.22
Nodes (10): ce(), de(), dt(), ft(), ht(), J(), ke(), processEvent() (+2 more)

### Community 65 - "escapeHtml"
Cohesion: 0.36
Nodes (10): escapeHtml(), isRoomActive(), loadDraftingPortal(), money(), openUpiVerifyModal(), parseUTCDate(), renderActivity(), renderEarnings() (+2 more)

### Community 66 - "test_password_reset.py"
Cohesion: 0.22
Nodes (8): Verify raw password against stored hash.     Supports Argon2id natively with bac, verify_password(), Test full forgot password -> reset password -> login with new password workflow., Verify that forgot-password returns 200 OK without leaking non-existent user ema, Verify that reusing a reset token or passing an invalid token is rejected with 4, test_forgot_password_flow_and_reset_success(), test_forgot_password_user_enumeration_protection(), test_reset_password_invalid_or_used_token()

### Community 67 - "websocket_chat_endpoint"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 68 - "sanitize_key"
Cohesion: 0.33
Nodes (5): lawyer_document_mock_upload(), UploadFile, Sanitize object storage keys to prevent path traversal.     Ensures relative key, sanitize_key(), test_sanitize_key()

### Community 69 - "Zt"
Cohesion: 0.40
Nodes (5): be(), le(), oe(), te(), Zt()

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LexAPI` connect `LexAPI` to `mr`, `je`, `escapeHtml`, `app.js`, `NTP Time Synchronization — Compliance Runbook`, `toast`, `audit`, `calendar.py`, `er`, `loadMessages`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `User` connect `processEvent` to `main.py`, `test_password_reset.py`, `setup_domain_ssl.sh`, `sanitize_key`, `main.py`, `i`, `toast`, `Booking`, `sanitize_key`, `LawyerGrid`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`, `Request`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `s()` connect `9d0be6640444_add_aadhaar_and_profile_picture.py` to `lawyer.js`, `app.js`, `daily-js.js`, `toast`, `setup`, `toast`, `config.py`, `er`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `HTTPException` (e.g. with `.check()` and `.check_async()`) actually correct?**
  _`HTTPException` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._