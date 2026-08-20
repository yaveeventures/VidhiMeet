# Graph Report - VidhiMeet  (2026-08-20)

## Corpus Check
- 83 files · ~96,808 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1210 nodes · 3349 edges · 69 communities (54 shown, 15 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 490 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3d0aabc`
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
- setup_domain_ssl.sh
- toast
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
- calendar.py
- LawyerBankAccount
- Session
- env.py
- test_bank_account.py
- __init__.py
- LexAPI
- reset_users.py
- Request
- Request
- Session
- datetime
- Session
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 128 edges
2. `Role` - 56 edges
3. `Practice` - 53 edges
4. `audit()` - 53 edges
5. `BookingStatus` - 48 edges
6. `Booking` - 47 edges
7. `LexAPI` - 47 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 40 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `reset_rate_limiter()` --calls--> `get_settings()`  [EXTRACTED]
  tests/conftest.py → backend/config.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py

## Import Cycles
- None detected.

## Communities (69 total, 15 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.18
Nodes (7): be(), le(), oe(), qt, re(), te(), Zt()

### Community 1 - "mr"
Cohesion: 0.06
Nodes (72): $(), openChatModal(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings (+64 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (40): as(), ce(), cr(), de(), dr(), dt(), er(), ft() (+32 more)

### Community 3 - "lawyer.js"
Cohesion: 0.09
Nodes (38): backdrop, booking, bookingView(), content, darken(), escapeHtml(), getColorForName(), getIntakeKeys() (+30 more)

### Community 4 - "app.js"
Cohesion: 0.12
Nodes (10): Ae(), ar(), br, fn(), ir(), mr, pr(), q() (+2 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (35): $(), auditLogs, colors, disputes, draftingTransactions, escapeHtml(), lawyerMap, mapPracticeToFrontend() (+27 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 8 - "processEvent"
Cohesion: 0.15
Nodes (25): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+17 more)

### Community 10 - "audit"
Cohesion: 0.10
Nodes (59): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+51 more)

### Community 11 - "toast"
Cohesion: 0.20
Nodes (23): Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document(), confirm_payment() (+15 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.09
Nodes (10): get_db(), AuditLog, Booking, _validate_ws_user_and_booking(), test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee() (+2 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 19 - "graphify.md"
Cohesion: 0.18
Nodes (9): B(), bn(), Jn(), N(), sn(), we(), wn(), xe() (+1 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (37): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+29 more)

### Community 21 - "__init__.py"
Cohesion: 0.23
Nodes (10): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+2 more)

### Community 22 - "ClientRouter"
Cohesion: 0.11
Nodes (30): AsyncSession, PasswordResetToken, RefreshToken, UserConsent, enable_mfa(), forgot_password(), google_auth(), login() (+22 more)

### Community 23 - "er"
Cohesion: 0.19
Nodes (23): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes(), list_drafting_transactions() (+15 more)

### Community 25 - "LawyerBankAccount"
Cohesion: 0.25
Nodes (15): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+7 more)

### Community 26 - "_e"
Cohesion: 0.21
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 27 - "er"
Cohesion: 0.12
Nodes (27): Bo(), Ds(), ea(), Fo(), Fs(), Go(), h(), Ho() (+19 more)

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
Cohesion: 0.29
Nodes (3): PlatformFeedback, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 32 - "data_retention_purge.py"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "LexAPI"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 36 - "toast"
Cohesion: 0.17
Nodes (24): _attemptReconnect(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal(), downloadBookingIcs(), isRoomActive(), joinMeeting() (+16 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.10
Nodes (29): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that booking document presign returns 15-minute expiry (900s). (+21 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.14
Nodes (27): a(), Bt(), c(), d(), ee(), f(), gn(), gt() (+19 more)

### Community 41 - "register"
Cohesion: 0.16
Nodes (24): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+16 more)

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
Cohesion: 0.16
Nodes (20): LawyerProfile, Rotate (invalidate) the lawyer's iCal token and issue a new one., rotate_ical_token(), drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm() (+12 more)

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 54 - "calendar.py"
Cohesion: 0.16
Nodes (19): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+11 more)

### Community 55 - "LawyerBankAccount"
Cohesion: 0.20
Nodes (14): get_settings(), rate_limit_dependency(), calculate_cancellation_policy(), get_daily_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake(), verify_daily_meeting_duration() (+6 more)

### Community 57 - "env.py"
Cohesion: 0.07
Nodes (30): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), http_exception_handler(), integrity_exception_handler(), lifespan(), Exception (+22 more)

### Community 58 - "test_bank_account.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 60 - "LexAPI"
Cohesion: 0.24
Nodes (11): checkAdminSession(), decideVerification(), handleSaveFees(), loadData(), doAdminLogin(), resolveDispute(), toast(), toggleUserStatus() (+3 more)

### Community 61 - "reset_users.py"
Cohesion: 0.10
Nodes (24): Base, EncryptedString, Message, now(), datetime, WebhookEvent, _save_ws_message(), decrypt_field() (+16 more)

### Community 66 - "Request"
Cohesion: 0.32
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `er` to `booking_service.py`, `processEvent`, `README.md`, `toast`, `LawyerGrid`, `LawyerProfile`, `calendar.py`, `__init__.py`, `calendar.py`, `ClientRouter`, `LawyerBankAccount`, `LawyerBankAccount`, `reset_users.py`, `env.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `s()` connect `verify_ntp_compliance` to `mr`, `je`, `daily-js.js`, `register`, `graphify.md`, `er`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `LexAPI` to `mr`, `lawyer.js`, `toast`, `daily-js.js`, `T`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `User` (e.g. with `Base` and `forgot_password()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `audit()` (e.g. with `AuditLog` and `ntp_now()`) actually correct?**
  _`audit()` has 2 INFERRED edges - model-reasoned connections that need verification._