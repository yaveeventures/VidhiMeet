# Graph Report - VidhiMeet  (2026-08-22)

## Corpus Check
- 85 files · ~99,224 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1222 nodes · 3414 edges · 63 communities (49 shown, 14 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 481 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9acccf64`
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
- pdf-annotator.js
- Settings
- NTP Time Synchronization — Compliance Runbook
- LexAPI
- setup_domain_ssl.sh
- test_password_reset.py
- firebase-phone-auth.js
- booking_service.py
- Booking
- verify_ntp_compliance
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- LawyerProfile
- graphify
- graphify.md
- test_marketplace.py
- LawyerBankAccount
- Session
- env.py
- test_bank_account.py
- __init__.py
- reset_users.py
- datetime
- Session
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 134 edges
2. `Role` - 57 edges
3. `audit()` - 55 edges
4. `Practice` - 53 edges
5. `BookingStatus` - 49 edges
6. `LexAPI` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 41 edges

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

## Communities (63 total, 14 thin omitted)

### Community 1 - "mr"
Cohesion: 0.05
Nodes (75): $(), openChatModal(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings (+67 more)

### Community 2 - "je"
Cohesion: 0.12
Nodes (32): as(), cr(), ct(), dn(), er(), Es(), Et(), fe() (+24 more)

### Community 3 - "lawyer.js"
Cohesion: 0.09
Nodes (40): backdrop, booking, bookingView(), content, darken(), escapeHtml(), getColorForName(), getIntakeKeys() (+32 more)

### Community 4 - "app.js"
Cohesion: 0.12
Nodes (11): Ae(), ar(), br, fn(), hn(), ir(), mr, pr() (+3 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (35): $(), auditLogs, colors, disputes, draftingTransactions, escapeHtml(), lawyerMap, mapPracticeToFrontend() (+27 more)

### Community 6 - "main.py"
Cohesion: 0.19
Nodes (16): DPDP Act 2023, Section 8(7) — Trigger data retention purge.      Deletes:     -, trigger_data_retention_purge(), _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens() (+8 more)

### Community 8 - "processEvent"
Cohesion: 0.10
Nodes (42): AsyncSession, DraftComment, DraftingProposal, DraftingRequest, LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out() (+34 more)

### Community 9 - "User"
Cohesion: 0.13
Nodes (16): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), lifespan(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), FastAPI (+8 more)

### Community 10 - "audit"
Cohesion: 0.05
Nodes (105): Base, BookingStatus, DraftingStatus, PasswordResetToken, PlatformFeedback, Practice, ProposalStatus, str (+97 more)

### Community 11 - "toast"
Cohesion: 0.13
Nodes (20): be(), bn(), ge(), ie(), Jn(), le(), me(), N() (+12 more)

### Community 13 - "sanitize_key"
Cohesion: 0.10
Nodes (6): get_db(), Booking, test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only(), test_video_consultation_dual_platform_fee()

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.07
Nodes (43): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), g() (+35 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.13
Nodes (20): Bt(), ce(), de(), dt(), ee(), ft(), ht(), J() (+12 more)

### Community 19 - "toast"
Cohesion: 0.17
Nodes (24): _attemptReconnect(), checkHashRoute(), _clearReconnectOverlay(), close(), closeModal(), downloadBookingIcs(), isRoomActive(), _launchClientDaily() (+16 more)

### Community 20 - "ntp_now"
Cohesion: 0.07
Nodes (37): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+29 more)

### Community 21 - "config.py"
Cohesion: 0.18
Nodes (14): calculate_cancellation_policy(), get_daily_meeting_details(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake(), verify_daily_meeting_duration(), evaluate_daily_meeting_logs(), Session (+6 more)

### Community 22 - "calendar.py"
Cohesion: 0.13
Nodes (22): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+14 more)

### Community 23 - "er"
Cohesion: 0.24
Nodes (11): checkAdminSession(), decideVerification(), handleSaveFees(), loadData(), doAdminLogin(), resolveDispute(), toast(), toggleUserStatus() (+3 more)

### Community 25 - "models.py"
Cohesion: 0.29
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 26 - "_e"
Cohesion: 0.16
Nodes (12): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 27 - "test_rate_limiter.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

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
Cohesion: 0.31
Nodes (6): get_settings(), drafting_document_presign(), generate_presigned_post_data(), get_s3_client(), client(), reset_rate_limiter()

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "LexAPI"
Cohesion: 0.11
Nodes (9): AuditLog, now(), datetime, UserConsent, WebhookEvent, request_erasure(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then, test_dpdpa_consent_enforcement_and_logging() (+1 more)

### Community 36 - "test_password_reset.py"
Cohesion: 0.29
Nodes (6): Test full forgot password -> reset password -> login with new password workflow., Verify that forgot-password returns 200 OK without leaking non-existent user ema, Verify that reusing a reset token or passing an invalid token is rejected with 4, test_forgot_password_flow_and_reset_success(), test_forgot_password_user_enumeration_protection(), test_reset_password_invalid_or_used_token()

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
Cohesion: 0.16
Nodes (15): a(), B(), c(), d(), f(), gn(), or(), p() (+7 more)

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
Cohesion: 0.21
Nodes (18): LawyerProfile, User, drafting_document_mock_upload(), UploadFile, download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload() (+10 more)

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 55 - "LawyerBankAccount"
Cohesion: 0.14
Nodes (25): Message, Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+17 more)

### Community 57 - "env.py"
Cohesion: 0.14
Nodes (14): http_exception_handler(), integrity_exception_handler(), Exception, Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err, Global Fallback Exception Handler for unexpected server failures (500):     - Pr (+6 more)

### Community 58 - "test_bank_account.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 61 - "reset_users.py"
Cohesion: 0.11
Nodes (21): EncryptedString, ConnectionManager, _save_ws_message(), _validate_ws_user_and_booking(), websocket_chat_endpoint(), decrypt_field(), encrypt_field(), _get_fernet_cipher() (+13 more)

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `LawyerProfile` to `LexAPI`, `test_password_reset.py`, `main.py`, `booking_service.py`, `processEvent`, `User`, `audit`, `README.md`, `sanitize_key`, `LawyerGrid`, `ntp_now`, `config.py`, `calendar.py`, `LawyerBankAccount`, `reset_users.py`, `pdf-annotator.js`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `s()` connect `je` to `mr`, `app.js`, `daily-js.js`, `verify_ntp_compliance`, `toast`, `calendar.py`, `9d0be6640444_add_aadhaar_and_profile_picture.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `er` to `mr`, `lawyer.js`, `daily-js.js`, `toast`, `T`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `BookingStatus` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`BookingStatus` has 40 INFERRED edges - model-reasoned connections that need verification._