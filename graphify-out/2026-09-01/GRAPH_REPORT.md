# Graph Report - VidhiMeet  (2026-09-01)

## Corpus Check
- 89 files · ~110,708 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1281 nodes · 3524 edges · 72 communities (53 shown, 19 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `61613abc`
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
- q
- PlatformFeedback
- models.py
- _e
- test_rate_limiter.py
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- _cors_response
- Settings
- NTP Time Synchronization — Compliance Runbook
- SlidingWindowRateLimiter
- setup_domain_ssl.sh
- test_rate_limiter.py
- setup
- processEvent
- Booking
- verify_ntp_compliance
- SSEClient
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- test_error_handling.py
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
- er
- 9b17288bd3cf_add_cancellation_fields_and_vouchers.py
- deploy_cloudflare_shield.py
- test_password_reset.py
- deploy_rules.sh
- sanitize_key
- test_document_vault.py
- test_password_reset.py

## God Nodes (most connected - your core abstractions)
1. `User` - 138 edges
2. `Role` - 59 edges
3. `audit()` - 56 edges
4. `Practice` - 53 edges
5. `LexAPI` - 52 edges
6. `BookingStatus` - 49 edges
7. `Booking` - 48 edges
8. `LawyerProfile` - 44 edges
9. `DraftingStatus` - 44 edges
10. `ProposalStatus` - 44 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_key()` --calls--> `sanitize_key()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_cancelled_slot_relisting()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py
- `test_client_cancel_between_2h_and_24h_partial_refund()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py
- `test_client_cancel_more_than_24h_full_refund()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py

## Import Cycles
- None detected.

## Communities (72 total, 19 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.10
Nodes (58): BookingStatus, DraftingStatus, Practice, ProposalStatus, str, Role, AdminPayoutAccountOut, AuditLogOut (+50 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (68): doAdminLogin(), checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute() (+60 more)

### Community 2 - "je"
Cohesion: 0.06
Nodes (75): $(), k(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings (+67 more)

### Community 3 - "lawyer.js"
Cohesion: 0.06
Nodes (48): as(), Bo(), Bt(), dr(), Ds(), ea(), Fo(), Fs() (+40 more)

### Community 4 - "app.js"
Cohesion: 0.11
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (15): ar(), fn(), ft(), hn(), ir(), J(), Kn(), kr() (+7 more)

### Community 6 - "main.py"
Cohesion: 0.07
Nodes (39): check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t (+31 more)

### Community 7 - "i"
Cohesion: 0.11
Nodes (27): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., revoke_jti(), test_dispute_intermediary_shield(), test_dispute_workflow_matrix(), Verify that non-admin accounts cannot access payout list. (+19 more)

### Community 8 - "processEvent"
Cohesion: 0.12
Nodes (36): get_db(), LawyerProfile, User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback() (+28 more)

### Community 11 - "toast"
Cohesion: 0.16
Nodes (26): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+18 more)

### Community 12 - "Booking"
Cohesion: 0.48
Nodes (3): ConnectionManager, websocket_chat_endpoint(), WebSocket

### Community 13 - "sanitize_key"
Cohesion: 0.14
Nodes (16): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), lifespan(), Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload(), FastAPI (+8 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.12
Nodes (13): Booking, create_booking(), Request, _validate_ws_user_and_booking(), calculate_cancellation_policy(), datetime, Calculate refund and penalty breakdown based on policy matrix:     - Lawyer Canc, validate_intake() (+5 more)

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.19
Nodes (22): Message, Voucher, rate_limit_dependency(), booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking(), confirm_document() (+14 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.21
Nodes (21): a(), bn(), c(), d(), f(), gn(), gt(), Jn() (+13 more)

### Community 21 - "config.py"
Cohesion: 0.11
Nodes (28): Ae(), at(), B(), br, Bs(), ct(), dn(), ee() (+20 more)

### Community 22 - "calendar.py"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 23 - "q"
Cohesion: 0.12
Nodes (13): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+5 more)

### Community 24 - "PlatformFeedback"
Cohesion: 0.13
Nodes (22): booking_ics(), _build_ics_calendar(), _build_vevent(), _escape(), _fmt_dt(), _fold(), get_ical_token(), lawyer_ical_feed() (+14 more)

### Community 25 - "models.py"
Cohesion: 0.12
Nodes (15): an(), cn(), _e(), he(), In(), nn(), on(), pe() (+7 more)

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

### Community 31 - "_cors_response"
Cohesion: 0.16
Nodes (18): _cors_response(), FrontendStaticFiles, http_exception_handler(), integrity_exception_handler(), Exception, Request, Standardized HTTP Exception Handler:     - Private Layer: Log operational client, Validation Exception Handler:     - Private Layer: Log detailed field errors to (+10 more)

### Community 32 - "Settings"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 34 - "SlidingWindowRateLimiter"
Cohesion: 0.29
Nodes (4): Exception, Request, RedisError, SlidingWindowRateLimiter

### Community 35 - "setup_domain_ssl.sh"
Cohesion: 0.14
Nodes (17): EncryptedString, _save_ws_message(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense)., validate_participant_access(), Fernet (+9 more)

### Community 36 - "test_rate_limiter.py"
Cohesion: 0.17
Nodes (10): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff(), test_auth_rate_limiting(), test_configurable_tier_thresholds() (+2 more)

### Community 37 - "setup"
Cohesion: 0.19
Nodes (13): be(), ge(), ie(), le(), me(), ne(), oe(), qn() (+5 more)

### Community 38 - "processEvent"
Cohesion: 0.29
Nodes (8): ce(), de(), dt(), ht(), ke(), processEvent(), ut(), X()

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
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 46 - "test_error_handling.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 47 - "LawyerProfile"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 49 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 64 - "9b17288bd3cf_add_cancellation_fields_and_vouchers.py"
Cohesion: 0.17
Nodes (15): Helper to write a mock PDF file when serving local document downloads., _write_mock_pdf(), download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign(), lawyers() (+7 more)

### Community 66 - "test_password_reset.py"
Cohesion: 0.09
Nodes (40): AsyncSession, Base, AuditLog, PasswordResetToken, PlatformFeedback, RefreshToken, Review, UserConsent (+32 more)

### Community 68 - "sanitize_key"
Cohesion: 0.27
Nodes (8): get_settings(), presign_document(), delete_s3_object(), generate_presigned_post_data(), get_s3_client(), Deletes an object from S3/R2 cloud bucket or local mock uploads directory., client(), reset_rate_limiter()

### Community 69 - "test_document_vault.py"
Cohesion: 0.05
Nodes (38): 1.1 Product Vision, 1.2 Problem Statement, 1.3 Value Proposition, 1. Executive Summary & Vision, 2.1 Corporate Entity Details, 2.2 Bar Council of India (BCI) Compliance, 2.3 DPDP Act 2023 & Privacy Architecture, 2.4 CERT-In & Forensic Timestamp Compliance (+30 more)

### Community 70 - "test_password_reset.py"
Cohesion: 0.40
Nodes (4): cr(), er(), hr(), lr()

## Knowledge Gaps
- **97 isolated node(s):** `deploy_rules.sh script`, `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `processEvent` to `9b17288bd3cf_add_cancellation_fields_and_vouchers.py`, `test_password_reset.py`, `setup_domain_ssl.sh`, `i`, `toast`, `sanitize_key`, `LawyerGrid`, `cookie-consent.js`, `check_clock_drift`, `8dcb01bed07f_initial_schema.py`, `q`, `PlatformFeedback`, `_e`, `80394484e25e_add_phonepe_transaction_id.py`, `_cors_response`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `s()` connect `9d0be6640444_add_aadhaar_and_profile_picture.py` to `je`, `lawyer.js`, `app.js`, `daily-js.js`, `test_password_reset.py`, `config.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `mr` to `NTP Time Synchronization — Compliance Runbook`, `je`, `app.js`, `calendar.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `User` (e.g. with `FrontendStaticFiles` and `lifespan()`) actually correct?**
  _`User` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `Role` (e.g. with `FrontendStaticFiles` and `Base`) actually correct?**
  _`Role` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `VidhiMeet backend package.`, `Sanitize sensitive PII keys and credentials before log rendering.`, `Configure structured JSON logging for production or key-value console logging fo` to the rest of the system?**
  _223 weakly-connected nodes found - possible documentation gaps or missing edges._